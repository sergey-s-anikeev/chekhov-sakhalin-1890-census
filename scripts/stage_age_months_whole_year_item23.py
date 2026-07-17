from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/staging/raw_age_recognition_item22_20260717/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_items21_22_staged.csv"
STAGE_DIR = ROOT / "data/staging/age_months_whole_year_item23_20260717"
OUTPUT = STAGE_DIR / "clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_items21_22_23_staged.csv"
REVIEW_DIR = ROOT / "data/review/age_months_whole_year_item23_20260717"
QA_DIR = ROOT / "outputs/qa/age_months_whole_year_item23_20260717"
DIFF = QA_DIR / "age_months_whole_year_item23_diff.csv"
QA = QA_DIR / "age_months_whole_year_item23_qa.json"

WHOLE_YEAR_MONTHS = {"1": "12", "2": "24"}


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def main() -> None:
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)

    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        assert fieldnames is not None
        rows = list(reader)

    before_ids = [row["person_id"] for row in rows]
    precise_before = {
        row["person_id"]: row["age_months"]
        for row in rows
        if row["age"] in WHOLE_YEAR_MONTHS and row["age_months"]
    }
    diffs = []
    for row in rows:
        if row["age"] in WHOLE_YEAR_MONTHS and not row["age_months"]:
            new_value = WHOLE_YEAR_MONTHS[row["age"]]
            diffs.append(
                {
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "page_number": row["page_number"],
                    "name_raw": row["name_raw"],
                    "age": row["age"],
                    "age_months_before": "",
                    "age_months_after": new_value,
                    "basis": "derived_from_whole_completed_year_age",
                }
            )
            row["age_months"] = new_value

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    for path in (DIFF, REVIEW_DIR / "whole_year_age_months_affected_records.csv"):
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(diffs[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(diffs)

    precise_after = {
        row["person_id"]: row["age_months"]
        for row in rows
        if row["person_id"] in precise_before
    }
    qa = {
        "input": str(INPUT.relative_to(ROOT)),
        "output": str(OUTPUT.relative_to(ROOT)),
        "rule": "If age is exactly 1 or 2 completed years and age_months is blank, derive 12 or 24 respectively; preserve explicit precise values.",
        "row_count": len(rows),
        "column_count": len(fieldnames),
        "identifier_order_unchanged": before_ids == [row["person_id"] for row in rows],
        "duplicate_person_ids": len(rows) - len(set(before_ids)),
        "changed_cell_count": len(diffs),
        "changed_record_count": len(diffs),
        "filled_by_age": {
            age: sum(1 for row in diffs if row["age"] == age) for age in WHOLE_YEAR_MONTHS
        },
        "preexisting_precise_value_count": len(precise_before),
        "preexisting_precise_values_unchanged": precise_before == precise_after,
        "remaining_blank_age_months_for_age_1_or_2": sum(
            1 for row in rows if row["age"] in WHOLE_YEAR_MONTHS and not row["age_months"]
        ),
        "input_sha256": digest(INPUT),
        "output_sha256": digest(OUTPUT),
    }
    QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if len(rows) != 7446 or qa["duplicate_person_ids"] != 0:
        raise ValueError("Row-count or identifier uniqueness QA failed")
    if qa["changed_cell_count"] != 316 or not qa["preexisting_precise_values_unchanged"]:
        raise ValueError(f"Unexpected change profile: {qa}")
    if qa["remaining_blank_age_months_for_age_1_or_2"] != 0:
        raise ValueError("Some whole-year age 1/2 records remain without age_months")


if __name__ == "__main__":
    main()
