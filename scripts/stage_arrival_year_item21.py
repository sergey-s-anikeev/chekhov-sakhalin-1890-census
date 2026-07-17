from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/staging/comments_numeric_cleanup_20260717/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_staged.csv"
STAGE_DIR = ROOT / "data/staging/arrival_year_item21_20260717"
OUTPUT = STAGE_DIR / "clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_item21_staged.csv"
QA_DIR = ROOT / "outputs/qa/arrival_year_item21_20260717"
DIFF = QA_DIR / "arrival_year_item21_applied_diff.csv"
QA = QA_DIR / "arrival_year_item21_staging_qa.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)

    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        assert fieldnames is not None
        rows = list(reader)

    before_ids = [row["person_id"] for row in rows]
    target = [row for row in rows if row["person_id"] == "P005199"]
    if len(target) != 1:
        raise ValueError(f"Expected one P005199 row; found {len(target)}")
    if target[0]["age"] != "2":
        raise ValueError(f"Expected P005199 age 2; found {target[0]['age']!r}")

    before = target[0]["age"]
    target[0]["age"] = "25"

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    with DIFF.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["person_id", "source_position_id", "field", "old_value", "new_value", "reason"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow(
            {
                "person_id": "P005199",
                "source_position_id": target[0]["source_position_id"],
                "field": "age",
                "old_value": before,
                "new_value": "25",
                "reason": "Owner-confirmed recognition and cleanup error",
            }
        )

    conflicts = [
        row
        for row in rows
        if row["arrival_year"].strip() and row["origin_place"].strip().casefold() == "на сахалине".casefold()
    ]
    changed_fields = []
    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        originals = list(csv.DictReader(handle))
    for old, new in zip(originals, rows):
        for field in fieldnames:
            if old[field] != new[field]:
                changed_fields.append((new["person_id"], field, old[field], new[field]))

    qa = {
        "input": str(INPUT.relative_to(ROOT)),
        "output": str(OUTPUT.relative_to(ROOT)),
        "row_count": len(rows),
        "column_count": len(fieldnames),
        "identifier_order_unchanged": before_ids == [row["person_id"] for row in rows],
        "duplicate_person_ids": len(rows) - len(set(before_ids)),
        "changed_cell_count": len(changed_fields),
        "changed_fields": sorted({field for _, field, _, _ in changed_fields}),
        "changed_person_ids": sorted({person_id for person_id, _, _, _ in changed_fields}),
        "arrival_year_origin_on_sakhalin_conflict_count": len(conflicts),
        "arrival_year_origin_on_sakhalin_conflict_ids": [row["person_id"] for row in conflicts],
        "input_sha256": digest(INPUT),
        "output_sha256": digest(OUTPUT),
    }
    QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if len(rows) != 7446 or qa["duplicate_person_ids"] != 0:
        raise ValueError("Row-count or identifier uniqueness QA failed")
    if changed_fields != [("P005199", "age", "2", "25")]:
        raise ValueError(f"Unexpected changes: {changed_fields}")


if __name__ == "__main__":
    main()
