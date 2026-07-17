from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/staging/arrival_year_item21_20260717/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_item21_staged.csv"
REVIEW = ROOT / "data/review/raw_age_recognition_item22_20260717/raw_age_semantic_mismatch_review.csv"
STAGE_DIR = ROOT / "data/staging/raw_age_recognition_item22_20260717"
OUTPUT = STAGE_DIR / "clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_items21_22_staged.csv"
QA_DIR = ROOT / "outputs/qa/raw_age_recognition_item22_20260717"
DIFF = QA_DIR / "raw_age_item22_applied_diff.csv"
QA = QA_DIR / "raw_age_item22_staging_qa.json"

EXCLUDED_NAME_MISMATCH_IDS = {"P004306", "P005959", "P006718"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)

    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        assert fieldnames is not None
        rows = list(reader)
    with REVIEW.open("r", encoding="utf-8-sig", newline="") as handle:
        review_rows = list(csv.DictReader(handle))

    proposals = {row["person_id"]: row for row in review_rows}
    if set(proposals) & EXCLUDED_NAME_MISMATCH_IDS != EXCLUDED_NAME_MISMATCH_IDS:
        raise ValueError("One or more excluded name-mismatch records are absent from review input")
    approved = {key: value for key, value in proposals.items() if key not in EXCLUDED_NAME_MISMATCH_IDS}
    if len(approved) != 15:
        raise ValueError(f"Expected 15 approved records; found {len(approved)}")

    before_ids = [row["person_id"] for row in rows]
    diffs = []
    seen = set()
    for row in rows:
        proposal = approved.get(row["person_id"])
        if proposal is None:
            continue
        seen.add(row["person_id"])
        for field, proposal_field in (
            ("age", "semantic_expected_age"),
            ("age_months", "semantic_expected_age_months"),
        ):
            new_value = proposal[proposal_field]
            old_value = row[field]
            if old_value != new_value:
                diffs.append(
                    {
                        "person_id": row["person_id"],
                        "source_position_id": row["source_position_id"],
                        "name_raw": row["name_raw"],
                        "raw_age": proposal["raw_age"],
                        "field": field,
                        "old_value": old_value,
                        "new_value": new_value,
                        "reason": "Owner-validated raw age semantics",
                    }
                )
                row[field] = new_value
    if seen != set(approved):
        raise ValueError(f"Approved IDs missing from staged input: {sorted(set(approved) - seen)}")

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with DIFF.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(diffs[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(diffs)

    qa = {
        "input": str(INPUT.relative_to(ROOT)),
        "output": str(OUTPUT.relative_to(ROOT)),
        "row_count": len(rows),
        "column_count": len(fieldnames),
        "identifier_order_unchanged": before_ids == [row["person_id"] for row in rows],
        "duplicate_person_ids": len(rows) - len(set(before_ids)),
        "approved_record_count": len(approved),
        "excluded_name_mismatch_ids": sorted(EXCLUDED_NAME_MISMATCH_IDS),
        "changed_cell_count": len(diffs),
        "changed_record_count": len({row["person_id"] for row in diffs}),
        "changed_fields": dict(
            (field, sum(1 for row in diffs if row["field"] == field)) for field in ("age", "age_months")
        ),
        "input_sha256": sha256(INPUT),
        "output_sha256": sha256(OUTPUT),
    }
    QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if len(rows) != 7446 or qa["duplicate_person_ids"] != 0:
        raise ValueError("Row-count or identifier uniqueness QA failed")
    if qa["changed_cell_count"] != 17 or qa["changed_record_count"] != 15:
        raise ValueError(f"Unexpected change counts: {qa}")


if __name__ == "__main__":
    main()
