from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/staging/comments_initial_capitalization_item24_20260718/clean_sakhalin_1890_ru_v4_20260717_item24_comments_staged.csv"
STAGE_DIR = ROOT / "data/staging/comments_initial_capitalization_item24_20260718_v2"
OUTPUT = STAGE_DIR / "clean_sakhalin_1890_ru_v4_20260717_item24_comments_staged_v2.csv"
QA_DIR = ROOT / "outputs/qa/comments_initial_capitalization_item24_20260718_v2"
DIFF = QA_DIR / "comments_item24_followup_diff.csv"
QA = QA_DIR / "comments_item24_followup_qa.json"

PERSON_ID = "P004464"
BEFORE = "В доме. Пешкова"
AFTER = "В доме Пешкова"


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
        fields = reader.fieldnames
        assert fields is not None
        rows = list(reader)

    targets = [row for row in rows if row["person_id"] == PERSON_ID]
    if len(targets) != 1 or targets[0]["comments"] != BEFORE:
        raise ValueError("Expected one exact P004464 comment target")
    targets[0]["comments"] = AFTER

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    diff_row = {
        "person_id": PERSON_ID,
        "source_position_id": targets[0]["source_position_id"],
        "page_number": targets[0]["page_number"],
        "name_raw": targets[0]["name_raw"],
        "comments_before": BEFORE,
        "comments_after": AFTER,
    }
    with DIFF.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(diff_row), lineterminator="\n")
        writer.writeheader()
        writer.writerow(diff_row)

    qa = {
        "input": str(INPUT.relative_to(ROOT)),
        "output": str(OUTPUT.relative_to(ROOT)),
        "row_count": len(rows),
        "column_count": len(fields),
        "changed_record_count": 1,
        "changed_cell_count": 1,
        "changed_fields": ["comments"],
        "corrected_person_id": PERSON_ID,
        "old_value_remaining_count": sum(row["comments"] == BEFORE for row in rows),
        "input_sha256": digest(INPUT),
        "output_sha256": digest(OUTPUT),
    }
    QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if len(rows) != 7446 or qa["old_value_remaining_count"] != 0:
        raise ValueError(f"QA failed: {qa}")


if __name__ == "__main__":
    main()
