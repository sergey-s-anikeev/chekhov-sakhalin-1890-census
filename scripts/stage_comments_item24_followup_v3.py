from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/staging/comments_initial_capitalization_item24_20260718_v2/clean_sakhalin_1890_ru_v4_20260717_item24_comments_staged_v2.csv"
STAGE_DIR = ROOT / "data/staging/comments_initial_capitalization_item24_20260718_v3"
OUTPUT = STAGE_DIR / "clean_sakhalin_1890_ru_v4_20260717_item24_comments_staged_v3.csv"
QA_DIR = ROOT / "outputs/qa/comments_initial_capitalization_item24_20260718_v3"
DIFF = QA_DIR / "comments_item24_followup_v3_diff.csv"
QA = QA_DIR / "comments_item24_followup_v3_qa.json"

CORRECTIONS = {
    "P000911": ("Живет у Ннеразборчиво", "Живет у Н."),
    "P004407": ("У Кас тера", "У Кастера"),
}


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

    diffs = []
    seen = set()
    for row in rows:
        correction = CORRECTIONS.get(row["person_id"])
        if correction is None:
            continue
        before, after = correction
        if row["comments"] != before:
            raise ValueError(f"Unexpected source comment for {row['person_id']}: {row['comments']!r}")
        seen.add(row["person_id"])
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
    if seen != set(CORRECTIONS):
        raise ValueError(f"Missing correction targets: {sorted(set(CORRECTIONS) - seen)}")

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
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
        "column_count": len(fields),
        "changed_record_count": len(diffs),
        "changed_cell_count": len(diffs),
        "changed_fields": ["comments"],
        "corrected_person_ids": sorted(seen),
        "input_sha256": digest(INPUT),
        "output_sha256": digest(OUTPUT),
    }
    QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if len(rows) != 7446 or len(diffs) != 2:
        raise ValueError(f"QA failed: {qa}")


if __name__ == "__main__":
    main()
