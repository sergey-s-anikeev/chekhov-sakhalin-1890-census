import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/staging/origin_place_item12_20260715/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_staged.csv"
STAGE = ROOT / "data/staging/marriage_status_item16_20260716"
REVIEW = ROOT / "data/review/marriage_status_item16_20260715/owner_response"
QA = ROOT / "outputs/qa/marriage_status_item16_20260716"
OUTPUT = STAGE / "clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_partial_staged.csv"

DUAL_LOCATION = {"женат на родине и на сахалине"}
CONTRADICTORY_STATUS = {
    "женат на сахалине. вдов",
    "женат на родине. холост",
    "женат на сахалине. холост",
}


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def append_comment(existing, phrase):
    if not phrase:
        return existing
    old_location_phrases = {
        "женат в сибири", "женат на амуре", "женат в усть-каре",
        "женат на каре", "женат в николаевске", "женат во владивостоке",
    }
    if existing.strip().casefold() in old_location_phrases:
        return phrase
    if phrase.casefold() in existing.casefold():
        return existing
    return f"{existing}; {phrase}" if existing else phrase


def derive(row):
    value = row.get("marriage_status", "")
    lower = value.casefold()
    comments = row.get("comments", "")
    alone = "Одинок" if any(x in lower for x in ("одинок", "одинока", "одинокий")) else ""
    location = ""
    comment_phrase = ""
    unresolved_reason = ""

    if lower in DUAL_LOCATION:
        marriage = ""
        unresolved_reason = "Dual location: owner will decide separately"
    elif lower in CONTRADICTORY_STATUS:
        marriage = ""
        unresolved_reason = "Contradictory marital states"
        if "на родине" in lower:
            location = "На родине"
        elif "на сахалине" in lower:
            location = "На Сахалине"
    elif lower.startswith("женат"):
        if "на родине" in lower:
            marriage, location = "Женат на родине", "На родине"
        elif "на сахалине" in lower:
            marriage, location = "Женат на Сахалине", "На Сахалине"
        else:
            marriage = "Женат в другом регионе"
            if "на каре" in lower:
                location, comment_phrase = "Кара", "Женат на Каре"
            elif "в николаевске" in lower:
                location, comment_phrase = "Николаевск", "Женат в Николаевске"
            elif "во владивостоке" in lower:
                location, comment_phrase = "Владивосток", "Женат во Владивостоке"
            elif "в другом месте" in lower:
                c = comments.casefold()
                if "сибир" in c:
                    location, comment_phrase = "Сибирь", "Женат в Сибири"
                elif "амур" in c:
                    location, comment_phrase = "Амур", "Женат на Амуре"
                elif "усть-кар" in c or "на каре" in c:
                    location, comment_phrase = "Кара", "Женат на Каре"
                else:
                    location = "Другое"
    elif lower.startswith("холост"):
        marriage = "Холост"
    elif lower.startswith("вдов"):
        marriage = "Вдов"
    elif lower == "девица":
        marriage = "Девица"
    else:
        marriage = ""

    return marriage, alone, location, append_comment(comments, comment_phrase), unresolved_reason


def main():
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        source_fields = reader.fieldnames
        source_rows = list(reader)
    for field in ("marriage_status_norm", "living_alone_status", "spouse_location_norm"):
        if field in source_fields:
            raise ValueError(f"Source already contains {field}")

    insert_at = source_fields.index("marriage_status") + 1
    new_fields = ["marriage_status_norm", "living_alone_status", "spouse_location_norm"]
    output_fields = source_fields[:insert_at] + new_fields + source_fields[insert_at:]
    staged, diff, unresolved = [], [], []
    counts = {field: Counter() for field in new_fields}
    comment_changes = 0
    for before in source_rows:
        marriage, alone, location, comments, reason = derive(before)
        after = dict(before)
        after.update({
            "marriage_status_norm": marriage,
            "living_alone_status": alone,
            "spouse_location_norm": location,
            "comments": comments,
        })
        staged.append(after)
        for field in new_fields:
            counts[field][after[field]] += 1
        if before.get("comments", "") != comments:
            comment_changes += 1
        if marriage or alone or location or before.get("comments", "") != comments:
            diff.append({
                "person_id": before.get("person_id", ""),
                "page_number": before.get("page_number", ""),
                "marriage_status": before.get("marriage_status", ""),
                "marriage_status_norm": marriage,
                "living_alone_status": alone,
                "spouse_location_norm": location,
                "comments_before": before.get("comments", ""),
                "comments_after": comments,
            })
        if reason:
            unresolved.append({
                "person_id": before.get("person_id", ""),
                "page_number": before.get("page_number", ""),
                "marriage_status": before.get("marriage_status", ""),
                "marriage_status_norm_proposed": marriage,
                "living_alone_status_proposed": alone,
                "spouse_location_norm_proposed": location,
                "comments": comments,
                "unresolved_reason": reason,
                "owner_decision": "",
                "owner_note": "",
            })

    write_csv(OUTPUT, staged, output_fields)
    write_csv(QA / "marriage_status_item16_partial_diff.csv", diff, list(diff[0]))
    write_csv(REVIEW / "marriage_status_unresolved_cases.csv", unresolved, list(unresolved[0]))

    non_target_changes = 0
    permitted = {"comments"}
    for before, after in zip(source_rows, staged):
        for field in source_fields:
            if field not in permitted and before.get(field, "") != after.get(field, ""):
                non_target_changes += 1
    qa = {
        "source": str(SOURCE.relative_to(ROOT)),
        "staged_output": str(OUTPUT.relative_to(ROOT)),
        "row_count": len(staged),
        "source_column_count": len(source_fields),
        "staged_column_count": len(output_fields),
        "unique_person_ids": len({r["person_id"] for r in staged}),
        "living_alone_status_odnok_records": counts["living_alone_status"]["Одинок"],
        "marriage_status_norm_counts": dict(sorted(counts["marriage_status_norm"].items())),
        "spouse_location_norm_counts": dict(sorted(counts["spouse_location_norm"].items())),
        "comment_changes": comment_changes,
        "unresolved_records": len(unresolved),
        "dual_location_records_left_unresolved": sum(r["unresolved_reason"].startswith("Dual") for r in unresolved),
        "non_target_changes": non_target_changes,
        "canonical_data_modified": False,
    }
    QA.mkdir(parents=True, exist_ok=True)
    (QA / "marriage_status_item16_partial_qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
