import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/staging/items7_8_age_followup_20260715/clean_sakhalin_1890_ru_v3_20260712_items7_8_staged_v3.csv"
INSPECTION = ROOT / "data/review/origin_place_item12_20260715/owner_workbook_inspection.ndjson"
REVIEW = ROOT / "data/review/origin_place_item12_20260715/owner_response"
STAGE = ROOT / "data/staging/origin_place_item12_20260715"
QA = ROOT / "outputs/qa/origin_place_item12_20260715"
OUTPUT = STAGE / "clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_staged.csv"


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    inspection = json.loads(INSPECTION.read_text(encoding="utf-8"))
    table = inspection["preview"]
    header = ["" if v is None else str(v) for v in table[0]]
    workbook_rows = [dict(zip(header, ["" if v is None else str(v) for v in row])) for row in table[1:]]
    mapping = {r["origin_place"]: r["origin_place_norm_proposed"] for r in workbook_rows}
    if len(mapping) != 109:
        raise ValueError(f"Expected 109 exact mapping values, found {len(mapping)}")

    REVIEW.mkdir(parents=True, exist_ok=True)
    STAGE.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)

    approved_rows = []
    for r in workbook_rows:
        approved_rows.append({
            "origin_place": r["origin_place"],
            "record_count": r["record_count"],
            "classification": r["classification"],
            "origin_place_norm_approved": r["origin_place_norm_proposed"],
            "owner_note": r["owner_note"],
        })
    write_csv(REVIEW / "origin_place_norm_approved_mapping.csv", approved_rows, list(approved_rows[0]))

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        source_fields = reader.fieldnames
        source_rows = list(reader)
    if "origin_place_norm" in source_fields:
        raise ValueError("Source already contains origin_place_norm")
    if any(r.get("origin_place", "") not in mapping for r in source_rows):
        raise ValueError("One or more source values are absent from the approved mapping")

    insert_at = source_fields.index("origin_place") + 1
    output_fields = source_fields[:insert_at] + ["origin_place_norm"] + source_fields[insert_at:]
    staged = []
    diffs = []
    category_counts = Counter()
    normalized_counts = Counter()
    classification_by_value = {r["origin_place"]: r["classification"] for r in workbook_rows}
    for row in source_rows:
        source_value = row.get("origin_place", "")
        normalized = mapping[source_value]
        out = dict(row)
        out["origin_place_norm"] = normalized
        staged.append(out)
        classification = classification_by_value[source_value]
        category_counts[classification] += 1
        if classification != "russian_administrative":
            normalized_counts[(classification, normalized)] += 1
        if source_value != normalized:
            diffs.append({
                "person_id": row.get("person_id", ""),
                "page_number": row.get("page_number", ""),
                "origin_place": source_value,
                "origin_place_norm": normalized,
                "classification": classification,
            })

    write_csv(OUTPUT, staged, output_fields)
    write_csv(QA / "origin_place_item12_diff.csv", diffs, list(diffs[0]))
    summary_rows = [
        {"classification": c, "origin_place_norm": v, "record_count": n}
        for (c, v), n in sorted(normalized_counts.items(), key=lambda x: (x[0][0], -x[1], x[0][1]))
    ]
    write_csv(REVIEW / "nonstandard_category_summary.csv", summary_rows, list(summary_rows[0]))

    # Verify that adding the derived column did not alter any source field.
    non_target_changes = 0
    for before, after in zip(source_rows, staged):
        for field in source_fields:
            if before.get(field, "") != after.get(field, ""):
                non_target_changes += 1
    qa = {
        "source": str(SOURCE.relative_to(ROOT)),
        "staged_output": str(OUTPUT.relative_to(ROOT)),
        "row_count": len(staged),
        "source_column_count": len(source_fields),
        "staged_column_count": len(output_fields),
        "origin_place_preserved": all(a["origin_place"] == b["origin_place"] for a, b in zip(source_rows, staged)),
        "approved_mapping_distinct_values": len(mapping),
        "unmapped_records": 0,
        "origin_place_norm_blank_records": sum(not r["origin_place_norm"] for r in staged),
        "records_where_normalized_differs_from_source": len(diffs),
        "non_target_changes": non_target_changes,
        "classification_record_counts": dict(sorted(category_counts.items())),
        "canonical_data_modified": False,
    }
    (QA / "origin_place_item12_staging_qa.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
