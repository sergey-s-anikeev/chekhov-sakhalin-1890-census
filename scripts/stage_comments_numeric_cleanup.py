from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/staging/occupation_item18_20260717/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_staged.csv"
STAGING_DIR = ROOT / "data/staging/comments_numeric_cleanup_20260717"
REVIEW_DIR = ROOT / "data/review/comments_numeric_cleanup_20260717"
QA_DIR = ROOT / "outputs/qa/comments_numeric_cleanup_20260717"
OUTPUT = STAGING_DIR / "clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_staged.csv"

PURE_NUMBER = re.compile(r"^\d+$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with BASE.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        if not fieldnames or "comments" not in fieldnames:
            raise ValueError("The base file does not contain a comments field")
        source_rows = list(reader)

    staged_rows: list[dict[str, str]] = []
    diff_rows: list[dict[str, str]] = []
    mixed_rows: list[dict[str, str]] = []

    for source in source_rows:
        staged = source.copy()
        comment = source["comments"]
        trimmed = comment.strip()
        if trimmed and PURE_NUMBER.fullmatch(trimmed):
            staged["comments"] = ""
            diff_rows.append(
                {
                    "person_id": source["person_id"],
                    "source_position_id": source["source_position_id"],
                    "page_number": source["page_number"],
                    "comments_before": comment,
                    "comments_after": "",
                    "reason": "pure_numeric_comment",
                }
            )
        elif any(character.isdigit() for character in comment):
            mixed_rows.append(
                {
                    "person_id": source["person_id"],
                    "source_position_id": source["source_position_id"],
                    "page_number": source["page_number"],
                    "comments": comment,
                }
            )
        staged_rows.append(staged)

    write_csv(OUTPUT, fieldnames, staged_rows)
    write_csv(
        REVIEW_DIR / "pure_numeric_comments_inventory.csv",
        ["person_id", "source_position_id", "page_number", "comments_before", "comments_after", "reason"],
        diff_rows,
    )
    write_csv(
        REVIEW_DIR / "mixed_text_number_comments_preserved.csv",
        ["person_id", "source_position_id", "page_number", "comments"],
        mixed_rows,
    )
    write_csv(
        QA_DIR / "comments_numeric_cleanup_diff.csv",
        ["person_id", "source_position_id", "page_number", "comments_before", "comments_after", "reason"],
        diff_rows,
    )

    changed_fields: set[str] = set()
    changed_rows = 0
    for before, after in zip(source_rows, staged_rows, strict=True):
        row_changed = False
        for field in fieldnames:
            if before[field] != after[field]:
                changed_fields.add(field)
                row_changed = True
        changed_rows += int(row_changed)

    qa = {
        "base_file": str(BASE.relative_to(ROOT)).replace("\\", "/"),
        "output_file": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "rule": "Blank comments only when stripped content matches ^[0-9]+$.",
        "rows_before": len(source_rows),
        "rows_after": len(staged_rows),
        "columns_before": len(fieldnames),
        "columns_after": len(fieldnames),
        "changed_rows": changed_rows,
        "pure_numeric_comments_removed": len(diff_rows),
        "mixed_text_number_comments_preserved": len(mixed_rows),
        "changed_fields": sorted(changed_fields),
        "person_id_order_preserved": [row["person_id"] for row in source_rows]
        == [row["person_id"] for row in staged_rows],
        "source_position_id_order_preserved": [row["source_position_id"] for row in source_rows]
        == [row["source_position_id"] for row in staged_rows],
        "remaining_pure_numeric_comments": sum(
            bool(PURE_NUMBER.fullmatch(row["comments"].strip())) for row in staged_rows if row["comments"].strip()
        ),
        "mixed_text_number_comments_unchanged": all(
            source_rows[index]["comments"] == staged_rows[index]["comments"]
            for index in range(len(source_rows))
            if any(character.isdigit() for character in source_rows[index]["comments"])
            and not PURE_NUMBER.fullmatch(source_rows[index]["comments"].strip())
        ),
        "base_sha256": sha256(BASE),
        "output_sha256": sha256(OUTPUT),
    }
    QA_DIR.mkdir(parents=True, exist_ok=True)
    with (QA_DIR / "comments_numeric_cleanup_qa.json").open("w", encoding="utf-8") as handle:
        json.dump(qa, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(json.dumps(qa, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
