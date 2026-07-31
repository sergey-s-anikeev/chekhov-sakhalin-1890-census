from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/processed/clean_sakhalin_1890_ru_v4_20260717.csv"
STAGE_DIR = ROOT / "data/staging/comments_initial_capitalization_item24_20260718"
OUTPUT = STAGE_DIR / "clean_sakhalin_1890_ru_v4_20260717_item24_comments_staged.csv"
REVIEW_DIR = ROOT / "data/review/comments_initial_capitalization_item24_20260718"
QA_DIR = ROOT / "outputs/qa/comments_initial_capitalization_item24_20260718"
DIFF = QA_DIR / "comments_initial_capitalization_diff.csv"
QA = QA_DIR / "comments_initial_capitalization_qa.json"

LOWERCASE_RUSSIAN_START = re.compile(r"^[а-яё]")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)

    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        assert fields is not None
        rows = list(reader)

    before_ids = [row["person_id"] for row in rows]
    diffs = []
    for row in rows:
        before = row["comments"]
        if LOWERCASE_RUSSIAN_START.match(before):
            after = before[0].upper() + before[1:]
            row["comments"] = after
            diffs.append(
                {
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "page_number": row["page_number"],
                    "name_raw": row["name_raw"],
                    "comments_before": before,
                    "comments_after": after,
                }
            )

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    for path in (DIFF, REVIEW_DIR / "affected_comments.csv"):
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(diffs[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(diffs)

    qa = {
        "input": str(INPUT.relative_to(ROOT)),
        "output": str(OUTPUT.relative_to(ROOT)),
        "rule": "Uppercase only the first character when comments begins with a lowercase Russian letter.",
        "row_count": len(rows),
        "column_count": len(fields),
        "changed_record_count": len(diffs),
        "changed_cell_count": len(diffs),
        "changed_fields": ["comments"],
        "identifier_order_unchanged": before_ids == [row["person_id"] for row in rows],
        "remaining_lowercase_russian_initials": sum(bool(LOWERCASE_RUSSIAN_START.match(row["comments"])) for row in rows),
        "input_sha256": digest(INPUT),
        "output_sha256": digest(OUTPUT),
    }
    QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if len(rows) != 7446 or len(diffs) != 53:
        raise ValueError(f"Unexpected row/change counts: {qa}")
    if qa["remaining_lowercase_russian_initials"] != 0:
        raise ValueError("Lowercase Russian initial comments remain")


if __name__ == "__main__":
    main()
