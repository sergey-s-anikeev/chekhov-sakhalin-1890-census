import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/staging/marriage_status_item16_20260716_v2/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_staged.csv"
INSPECTION = ROOT / "data/review/occupation_review_20260716/owner_all_values_inspection.ndjson"
REVIEW = ROOT / "data/review/occupation_review_20260716/owner_response"
STAGE = ROOT / "data/staging/occupation_item18_20260717"
QA = ROOT / "outputs/qa/occupation_item18_20260717"
OUTPUT = STAGE / "clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_staged.csv"


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def append_comment(existing, addition):
    if not addition:
        return existing
    if addition.casefold() in existing.casefold():
        return existing
    return f"{existing}; {addition}" if existing else addition


def main():
    inspection = json.loads(INSPECTION.read_text(encoding="utf-8"))
    table = inspection["preview"]
    header = ["" if v is None else str(v) for v in table[0]]
    review_rows = [dict(zip(header, ["" if v is None else str(v) for v in row])) for row in table[1:]]
    if len(review_rows) != 171:
        raise ValueError(f"Expected 171 occupation values, found {len(review_rows)}")

    approved = {}
    comment_additions = {}
    approved_rows = []
    explicit_decision_values = set()
    for row in review_rows:
        source_value = row["occupation"]
        decision = row["owner_decision"].strip()
        approved_value = decision if decision else row["occupation_norm_proposed"]
        approved[source_value] = approved_value
        note = row["owner_note"].strip()
        addition = ""
        if "Move full text" in note:
            marker = "comments`"
            if marker in note and note.split(marker, 1)[1].strip():
                addition = note.split(marker, 1)[1].strip()
            else:
                addition = source_value
            comment_additions[source_value] = addition
        if decision:
            explicit_decision_values.add(source_value)
        approved_rows.append({
            "occupation": source_value,
            "record_count": row["record_count"],
            "occupation_group": row["occupation_group"],
            "occupation_norm_approved": approved_value,
            "owner_decision_explicit": "Yes" if decision else "No — proposal confirmed",
            "owner_note": note,
            "comment_addition": addition,
        })
    if len(approved) != 171:
        raise ValueError("Approved occupation mapping is not one-to-one by exact source value")

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        source_fields = reader.fieldnames
        source_rows = list(reader)
    if "occupation_norm" in source_fields:
        raise ValueError("Source already contains occupation_norm")
    missing = sorted({r["occupation"] for r in source_rows} - approved.keys())
    if missing:
        raise ValueError(f"Unmapped occupation values: {missing}")

    insert_at = source_fields.index("occupation") + 1
    output_fields = source_fields[:insert_at] + ["occupation_norm"] + source_fields[insert_at:]
    staged, diff, comment_diff = [], [], []
    norm_counts = Counter()
    for before in source_rows:
        source_value = before["occupation"]
        normalized = approved[source_value]
        comments_after = append_comment(before.get("comments", ""), comment_additions.get(source_value, ""))
        after = dict(before)
        after["occupation_norm"] = normalized
        after["comments"] = comments_after
        staged.append(after)
        norm_counts[normalized] += 1
        if normalized != source_value or comments_after != before.get("comments", ""):
            diff.append({
                "person_id": before.get("person_id", ""),
                "page_number": before.get("page_number", ""),
                "occupation": source_value,
                "occupation_norm": normalized,
                "comments_before": before.get("comments", ""),
                "comments_after": comments_after,
            })
        if comments_after != before.get("comments", ""):
            comment_diff.append({
                "person_id": before.get("person_id", ""),
                "page_number": before.get("page_number", ""),
                "occupation": source_value,
                "occupation_norm": normalized,
                "comments_before": before.get("comments", ""),
                "comments_after": comments_after,
            })

    write_csv(OUTPUT, staged, output_fields)
    write_csv(REVIEW / "occupation_norm_approved_mapping.csv", approved_rows, list(approved_rows[0]))
    write_csv(QA / "occupation_item18_diff.csv", diff, list(diff[0]))
    write_csv(QA / "occupation_item18_comment_transfers.csv", comment_diff, list(comment_diff[0]))

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
        "approved_distinct_values": len(approved),
        "explicit_owner_decision_values": len(explicit_decision_values),
        "confirmed_proposal_values": len(approved) - len(explicit_decision_values),
        "unmapped_records": 0,
        "occupation_source_preserved": all(a["occupation"] == b["occupation"] for a, b in zip(source_rows, staged)),
        "occupation_norm_blank_records": norm_counts[""],
        "occupation_norm_nonblank_records": len(staged) - norm_counts[""],
        "records_where_norm_differs_from_source": sum(r["occupation_norm"] != r["occupation"] for r in staged),
        "comment_transfers": len(comment_diff),
        "non_target_changes": non_target_changes,
        "canonical_data_modified": False,
    }
    QA.mkdir(parents=True, exist_ok=True)
    (QA / "occupation_item18_qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
