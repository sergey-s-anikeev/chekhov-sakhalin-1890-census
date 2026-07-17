import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/staging/origin_place_item12_20260715/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_staged.csv"
STAGE = ROOT / "data/staging/marriage_status_item16_20260716_v2"
REVIEW = ROOT / "data/review/marriage_status_item16_20260715/owner_response"
QA = ROOT / "outputs/qa/marriage_status_item16_20260716_v2"
OUTPUT = STAGE / "clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_staged.csv"


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
    comment_phrase = ""

    if lower == "женат на родине и на сахалине":
        marriage = "Женат на родине и на Сахалине"
    elif lower == "женат на сахалине. вдов":
        marriage = "Женат на Сахалине; Вдов"
    elif lower == "женат на родине. холост":
        marriage = "Женат на родине"
    elif lower == "женат на сахалине. холост":
        marriage = "Женат на Сахалине"
    elif lower.startswith("женат"):
        if "на родине" in lower:
            marriage = "Женат на родине"
        elif "на сахалине" in lower:
            marriage = "Женат на Сахалине"
        else:
            marriage = "Женат в другом регионе"
            if "на каре" in lower:
                comment_phrase = "Женат на Каре"
            elif "в николаевске" in lower:
                comment_phrase = "Женат в Николаевске"
            elif "во владивостоке" in lower:
                comment_phrase = "Женат во Владивостоке"
            elif "в другом месте" in lower:
                c = comments.casefold()
                if "сибир" in c:
                    comment_phrase = "Женат в Сибири"
                elif "амур" in c:
                    comment_phrase = "Женат на Амуре"
                elif "усть-кар" in c or "на каре" in c:
                    comment_phrase = "Женат на Каре"
    elif lower.startswith("холост") or lower == "девица":
        marriage = "Холост"
    elif lower.startswith("вдов"):
        marriage = "Вдов"
    else:
        marriage = ""
    return marriage, alone, append_comment(comments, comment_phrase)


def main():
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        source_fields = reader.fieldnames
        source_rows = list(reader)
    forbidden = {"marriage_status_norm", "living_alone_status", "spouse_location_norm"}
    if forbidden.intersection(source_fields):
        raise ValueError("The Item 12 source unexpectedly contains Item 16 derived columns")

    insert_at = source_fields.index("marriage_status") + 1
    new_fields = ["marriage_status_norm", "living_alone_status"]
    output_fields = source_fields[:insert_at] + new_fields + source_fields[insert_at:]
    staged, diffs, decisions = [], [], []
    counts = {field: Counter() for field in new_fields}
    comment_changes = 0
    for before in source_rows:
        marriage, alone, comments = derive(before)
        after = dict(before)
        after.update({"marriage_status_norm": marriage, "living_alone_status": alone, "comments": comments})
        staged.append(after)
        counts["marriage_status_norm"][marriage] += 1
        counts["living_alone_status"][alone] += 1
        if before.get("comments", "") != comments:
            comment_changes += 1
        if marriage or alone or before.get("comments", "") != comments:
            diffs.append({
                "person_id": before.get("person_id", ""),
                "page_number": before.get("page_number", ""),
                "marriage_status": before.get("marriage_status", ""),
                "marriage_status_norm": marriage,
                "living_alone_status": alone,
                "comments_before": before.get("comments", ""),
                "comments_after": comments,
            })

    for source_value in sorted({r["marriage_status"] for r in source_rows}):
        example = next(r for r in source_rows if r["marriage_status"] == source_value)
        marriage, alone, _ = derive(example)
        decisions.append({
            "marriage_status": source_value,
            "record_count": sum(r["marriage_status"] == source_value for r in source_rows),
            "marriage_status_norm_approved": marriage,
            "living_alone_status_approved": alone,
        })

    write_csv(OUTPUT, staged, output_fields)
    write_csv(QA / "marriage_status_item16_final_diff.csv", diffs, list(diffs[0]))
    write_csv(REVIEW / "marriage_status_item16_approved_mapping.csv", decisions, list(decisions[0]))

    non_target_changes = 0
    for before, after in zip(source_rows, staged):
        for field in source_fields:
            if field != "comments" and before.get(field, "") != after.get(field, ""):
                non_target_changes += 1
    qa = {
        "source": str(SOURCE.relative_to(ROOT)),
        "staged_output": str(OUTPUT.relative_to(ROOT)),
        "row_count": len(staged),
        "source_column_count": len(source_fields),
        "staged_column_count": len(output_fields),
        "unique_person_ids": len({r["person_id"] for r in staged}),
        "spouse_location_norm_created": "spouse_location_norm" in output_fields,
        "living_alone_status_odnok_records": counts["living_alone_status"]["Одинок"],
        "marriage_status_norm_counts": dict(sorted(counts["marriage_status_norm"].items())),
        "comment_changes": comment_changes,
        "unresolved_records": 0,
        "non_target_changes": non_target_changes,
        "canonical_data_modified": False,
    }
    QA.mkdir(parents=True, exist_ok=True)
    (QA / "marriage_status_item16_final_qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
