import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/staging/origin_place_item12_20260715/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_staged.csv"
REVIEW = ROOT / "data/review/marriage_status_item16_20260715"
QA = ROOT / "outputs/qa/marriage_status_item16_20260715"

CONTRADICTORY = {
    "женат на Сахалине. вдов",
    "женат на родине. холост",
    "женат на Сахалине. холост",
    "женат на родине и на Сахалине",
}
NAMED_OR_OTHER = {
    "женат в другом месте",
    "женат на каре",
    "женат в николаевске",
    "женат во владивостоке",
}


def propose(value):
    lower = value.casefold()
    living_alone = "Одинок" if any(x in lower for x in ("одинок", "одинока", "одинокий")) else ""

    if value == "" or value == "одинок":
        marriage_norm = ""
    elif lower in {v.casefold() for v in CONTRADICTORY}:
        marriage_norm = ""
    elif lower.startswith("женат"):
        marriage_norm = "Женат"
    elif lower.startswith("холост"):
        marriage_norm = "Холост"
    elif lower.startswith("вдов"):
        marriage_norm = "Вдов"
    elif lower == "девица":
        marriage_norm = "Девица"
    else:
        marriage_norm = ""

    if "на родине и на сахалине" in lower:
        spouse_location = ""
    elif "на родине" in lower:
        spouse_location = "На родине"
    elif "на сахалине" in lower:
        spouse_location = "На Сахалине"
    elif "на каре" in lower:
        spouse_location = "Кара"
    elif "в николаевске" in lower:
        spouse_location = "Николаевск"
    elif "во владивостоке" in lower:
        spouse_location = "Владивосток"
    elif "в другом месте" in lower:
        spouse_location = "Другое"
    else:
        spouse_location = ""

    if value == "одинок":
        return marriage_norm, living_alone, spouse_location, "Yes", "Living-alone statement does not establish marital status"
    if lower in {v.casefold() for v in CONTRADICTORY}:
        return marriage_norm, living_alone, spouse_location, "Yes", "Contradictory marital state or spouse location; preserve source and decide manually"
    if value in NAMED_OR_OTHER:
        return marriage_norm, living_alone, spouse_location, "Yes", "Named or unspecified alternative spouse location; review individually"
    return marriage_norm, living_alone, spouse_location, "No", "Direct mapping from explicit wording"


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def record_location_proposal(value, comments, default):
    if value != "женат в другом месте":
        return default
    lower = comments.casefold()
    if "сибир" in lower:
        return "Сибирь"
    if "амур" in lower:
        return "Амур"
    if "усть-кар" in lower:
        return "Кара"
    return default


def main():
    REVIEW.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    grouped = defaultdict(list)
    for row in rows:
        grouped[row.get("marriage_status", "")].append(row)

    proposal = []
    focused = []
    for value, matches in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        marriage, alone, location, required, reason = propose(value)
        pages = []
        for row in matches:
            page = row.get("page_number", "")
            if page and page not in pages:
                pages.append(page)
            if len(pages) >= 5:
                break
        proposal.append({
            "marriage_status": value,
            "record_count": len(matches),
            "marriage_status_norm_proposed": marriage,
            "living_alone_status_proposed": alone,
            "spouse_location_norm_proposed": location,
            "review_required": required,
            "review_reason": reason,
            "representative_person_ids": "; ".join(r.get("person_id", "") for r in matches[:5]),
            "representative_page_numbers": "; ".join(pages),
            "owner_decision": "",
            "owner_note": "",
        })
        if required == "Yes":
            for row in matches:
                record_location = record_location_proposal(value, row.get("comments", ""), location)
                focused.append({
                    "person_id": row.get("person_id", ""),
                    "page_number": row.get("page_number", ""),
                    "marriage_status": value,
                    "marriage_status_norm_proposed": marriage,
                    "living_alone_status_proposed": alone,
                    "spouse_location_norm_record_proposed": record_location,
                    "sex": row.get("sex", ""),
                    "family_status_norm": row.get("family_status_norm", ""),
                    "legal_status_norm": row.get("legal_status_norm", ""),
                    "comments": row.get("comments", ""),
                })

    write_csv(REVIEW / "marriage_status_mapping_proposal.csv", proposal, list(proposal[0]))
    write_csv(REVIEW / "marriage_status_focused_review.csv", focused, list(focused[0]))
    summary = {
        "source": str(SOURCE.relative_to(ROOT)),
        "row_count": len(rows),
        "distinct_values_including_blank": len(grouped),
        "blank_marriage_status_records": len(grouped.get("", [])),
        "explicit_living_alone_records": sum(1 for r in rows if propose(r.get("marriage_status", ""))[1] == "Одинок"),
        "focused_review_distinct_values": sum(r["review_required"] == "Yes" for r in proposal),
        "focused_review_records": len(focused),
        "proposed_marriage_status_norm_counts": {},
        "proposed_spouse_location_norm_counts": {},
        "record_level_spouse_location_override_counts": {},
        "status": "mapping proposal only; no staged or canonical data modified",
    }
    for key in ("marriage_status_norm_proposed", "spouse_location_norm_proposed"):
        counts = defaultdict(int)
        for p in proposal:
            counts[p[key]] += int(p["record_count"])
        summary["proposed_" + key.replace("_proposed", "") + "_counts"] = dict(sorted(counts.items()))
    override_counts = defaultdict(int)
    for row in focused:
        if row["marriage_status"] == "женат в другом месте":
            override_counts[row["spouse_location_norm_record_proposed"]] += 1
    summary["record_level_spouse_location_override_counts"] = dict(sorted(override_counts.items()))
    (QA / "marriage_status_item16_profile.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (REVIEW / "README.md").write_text(
        "# Item 16 — marriage status and spouse-location proposal\n\n"
        "The source-facing `marriage_status` remains unchanged. Proposed derived fields are "
        "`marriage_status_norm`, `living_alone_status`, and `spouse_location_norm`. "
        "Blank derived values mean not explicitly established. Contradictory and named-location forms are held for owner review.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
