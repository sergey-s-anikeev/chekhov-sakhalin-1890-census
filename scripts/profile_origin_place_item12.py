import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/staging/items7_8_age_followup_20260715/clean_sakhalin_1890_ru_v3_20260712_items7_8_staged_v3.csv"
REVIEW = ROOT / "data/review/origin_place_item12_20260715"
QA = ROOT / "outputs/qa/origin_place_item12_20260715"

TRANSIT = {"по пути", "В пути следования", "На пути"}
FOREIGN_SUBJECT = {
    "Прусскоподданный", "Прусскоподданная", "Прусскоподданый",
    "Прусско-подданный", "Персидский подданный", "Австрийский подданный",
    "Турецко-подданный",
}
FOREIGN_STATE = {"Румынское королевство", "Китай", "Бухарский эмират"}
IMPERIAL_TERRITORY = {"Великое княжество Финляндское", "Царство Польское"}
EXCEPTIONAL = {"На Сахалине", "Усть-Кара", "Бродяга", "Сибирь", "из Чибисани", "не помнит"}


def classify(value):
    if value == "":
        return "blank", "", "Yes", "No explicit origin value; retain blank"
    if value.casefold() in {v.casefold() for v in TRANSIT}:
        return "transit", "В пути", "Yes", "Three source expressions can share one analytical category"
    if value in FOREIGN_SUBJECT:
        proposed = {
            "Прусскоподданный": "Прусский подданный",
            "Прусскоподданная": "Прусская подданная",
            "Прусскоподданый": "Прусский подданный",
            "Прусско-подданный": "Прусский подданный",
            "Персидский подданный": "Персидский подданный",
            "Австрийский подданный": "Австрийский подданный",
            "Турецко-подданный": "Турецкий подданный",
        }[value]
        return "foreign_subjecthood", proposed, "Yes", "Subjecthood is not a Russian administrative origin; review individually"
    if value in FOREIGN_STATE:
        return "foreign_state", value, "Yes", "Foreign-state or polity value; review individually"
    if value in IMPERIAL_TERRITORY:
        return "imperial_territory", value, "Yes", "Higher-level imperial territory rather than a governorate/oblast"
    if value in EXCEPTIONAL or value.casefold() == "на сахалине":
        return "exceptional_non_administrative", value, "Yes", "Not a standard governorate/oblast origin; review individually"
    if value.endswith(" губерния") or value.endswith(" область") or value == "Область Войска Донского":
        return "russian_administrative", value, "No", "Standard source administrative unit; retain as stated"
    return "unclassified", value, "Yes", "No rule assigned; manual review required"


def main():
    REVIEW.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    grouped = defaultdict(list)
    for row in rows:
        grouped[row.get("origin_place", "")].append(row)

    proposal = []
    exception_records = []
    class_records = defaultdict(int)
    class_values = defaultdict(int)
    for value, matches in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        classification, proposed, review_required, reason = classify(value)
        class_records[classification] += len(matches)
        class_values[classification] += 1
        ids = [r.get("person_id", "") for r in matches[:5]]
        pages = []
        for r in matches:
            page = r.get("page_number", "")
            if page and page not in pages:
                pages.append(page)
            if len(pages) == 5:
                break
        proposal.append({
            "origin_place": value,
            "record_count": len(matches),
            "classification": classification,
            "origin_place_norm_proposed": proposed,
            "review_required": review_required,
            "review_reason": reason,
            "representative_person_ids": "; ".join(ids),
            "representative_page_numbers": "; ".join(pages),
            "owner_decision": "",
            "owner_note": "",
        })
        if review_required == "Yes" and value != "":
            for r in matches:
                exception_records.append({
                    "person_id": r.get("person_id", ""),
                    "page_number": r.get("page_number", ""),
                    "origin_place": value,
                    "classification": classification,
                    "origin_place_norm_proposed": proposed,
                    "age": r.get("age", ""),
                    "sex": r.get("sex", ""),
                    "legal_status_norm": r.get("legal_status_norm", ""),
                    "family_status_norm": r.get("family_status_norm", ""),
                    "comments": r.get("comments", ""),
                })

    def write_csv(path, records, fields):
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(records)

    write_csv(REVIEW / "origin_place_mapping_proposal.csv", proposal, list(proposal[0]))
    write_csv(REVIEW / "origin_place_exception_records.csv", exception_records, list(exception_records[0]))

    summary = {
        "source": str(SOURCE.relative_to(ROOT)),
        "row_count": len(rows),
        "distinct_values_including_blank": len(grouped),
        "blank_records": len(grouped.get("", [])),
        "classification_record_counts": dict(sorted(class_records.items())),
        "classification_distinct_value_counts": dict(sorted(class_values.items())),
        "proposed_automatic_change_count": 0,
        "status": "mapping proposal only; no staged or canonical data modified",
    }
    (QA / "origin_place_item12_profile.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# Item 12 — origin_place profile and proposed review policy",
        "",
        f"Source: `{summary['source']}` ({len(rows):,} records; {len(grouped)} distinct values including blank).",
        "",
        "## Proposed policy",
        "",
        "- Preserve `origin_place` exactly as the source-facing field.",
        "- Add/use a separate normalized field only after owner approval.",
        "- Map `по пути`, `В пути следования`, and `На пути` to analytical value `В пути`.",
        "- Treat foreign subjecthood separately from Russian administrative origin; do not infer country from ethnicity, religion, or name.",
        "- Retain standard governorate/oblast values as written; review higher-level territories and exceptional values individually.",
        "- Leave blank values blank.",
        "",
        "No dataset fields were changed in this profiling step.",
    ]
    (REVIEW / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
