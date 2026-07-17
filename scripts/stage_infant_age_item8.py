"""Stage the minimal approved-for-review Item 8 precise-age schema proposal."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/staging/age_item7_20260713/clean_sakhalin_1890_ru_v3_20260712_age_item7_staged.csv"
PROPOSAL = ROOT / "data/review/infant_age_item8_20260713/infant_age_extraction_proposal.csv"
STAGING_DIR = ROOT / "data/staging/infant_age_item8_20260713"
QA_DIR = ROOT / "outputs/qa/infant_age_item8_20260713"
STAGED = STAGING_DIR / "clean_sakhalin_1890_ru_v3_20260712_items7_8_staged.csv"
DIFF = QA_DIR / "infant_age_item8_diff.csv"
QA_JSON = QA_DIR / "infant_age_item8_staging_qa.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header: {path}")
        return reader.fieldnames, list(reader)


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source_columns, source_rows = read_csv(SOURCE)
    _, proposal_rows = read_csv(PROPOSAL)
    if any(row["review_required"] == "YES" for row in proposal_rows):
        raise ValueError("Proposal contains unresolved extraction cases")
    if len(proposal_rows) != 307:
        raise ValueError(f"Expected 307 proposal rows, found {len(proposal_rows)}")
    proposal_by_id = {row["person_id"]: row for row in proposal_rows}
    if len(proposal_by_id) != len(proposal_rows):
        raise ValueError("Proposal contains duplicate person_id values")

    staged_columns = []
    for column in source_columns:
        staged_columns.append(column)
        if column == "age":
            staged_columns.extend(["age_months", "age_text_raw"])

    staged_rows = []
    diffs = []
    for source_row in source_rows:
        staged_row = source_row.copy()
        proposal = proposal_by_id.get(source_row["person_id"])
        staged_row["age_months"] = proposal["age_months_proposed"] if proposal else ""
        staged_row["age_text_raw"] = proposal["age_text_raw_proposed"] if proposal else ""
        staged_rows.append(staged_row)
        if staged_row["age_months"]:
            diffs.append(
                {
                    "person_id": source_row["person_id"],
                    "source_position_id": source_row["source_position_id"],
                    "page_number": source_row["page_number"],
                    "field": "age_months",
                    "before": "",
                    "after": staged_row["age_months"],
                }
            )
        if staged_row["age_text_raw"]:
            diffs.append(
                {
                    "person_id": source_row["person_id"],
                    "source_position_id": source_row["source_position_id"],
                    "page_number": source_row["page_number"],
                    "field": "age_text_raw",
                    "before": "",
                    "after": staged_row["age_text_raw"],
                }
            )

    write_csv(STAGED, staged_columns, staged_rows)
    write_csv(
        DIFF,
        ["person_id", "source_position_id", "page_number", "field", "before", "after"],
        diffs,
    )

    check_columns, check_rows = read_csv(STAGED)
    source_by_id = {row["person_id"]: row for row in source_rows}
    non_target_changes = []
    for row in check_rows:
        source_row = source_by_id[row["person_id"]]
        for column in source_columns:
            if row[column] != source_row[column]:
                non_target_changes.append({"person_id": row["person_id"], "field": column})
    month_rows = [row for row in check_rows if row["age_months"]]
    text_rows = [row for row in check_rows if row["age_text_raw"]]
    submonth_text_rows = [
        row for row in text_rows if "недел" in row["age_text_raw"].lower() or "дн" in row["age_text_raw"].lower()
    ]
    completed_year_mismatches = [
        row["person_id"] for row in month_rows if int(row["age"]) != int(row["age_months"]) // 12
    ]

    qa = {
        "item": 8,
        "status": "staged proposal for owner review",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "staged": str(STAGED.relative_to(ROOT)).replace("\\", "/"),
        "source_record_count": len(source_rows),
        "staged_record_count": len(check_rows),
        "source_column_count": len(source_columns),
        "staged_column_count": len(check_columns),
        "new_columns": ["age_months", "age_text_raw"],
        "new_columns_immediately_after_age": check_columns[check_columns.index("age") + 1 : check_columns.index("age") + 3]
        == ["age_months", "age_text_raw"],
        "age_months_nonblank_count": len(month_rows),
        "age_text_raw_nonblank_count": len(text_rows),
        "submonth_text_with_blank_age_months_count": sum(not row["age_months"] for row in submonth_text_rows),
        "completed_year_consistency_mismatch_count": len(completed_year_mismatches),
        "comments_unchanged": all(
            row["comments"] == source_by_id[row["person_id"]]["comments"] for row in check_rows
        ),
        "age_unchanged": all(row["age"] == source_by_id[row["person_id"]]["age"] for row in check_rows),
        "person_id_order_unchanged": [row["person_id"] for row in source_rows]
        == [row["person_id"] for row in check_rows],
        "source_position_id_order_unchanged": [row["source_position_id"] for row in source_rows]
        == [row["source_position_id"] for row in check_rows],
        "non_target_change_count": len(non_target_changes),
        "diff_row_count": len(diffs),
        "source_sha256": sha256(SOURCE),
        "proposal_sha256": sha256(PROPOSAL),
        "staged_sha256": sha256(STAGED),
        "diff_sha256": sha256(DIFF),
    }
    if not all(
        [
            qa["source_record_count"] == qa["staged_record_count"] == 7446,
            qa["staged_column_count"] == qa["source_column_count"] + 2,
            qa["new_columns_immediately_after_age"],
            qa["age_months_nonblank_count"] == 290,
            qa["age_text_raw_nonblank_count"] == 307,
            qa["submonth_text_with_blank_age_months_count"] == 17,
            qa["completed_year_consistency_mismatch_count"] == 0,
            qa["comments_unchanged"],
            qa["age_unchanged"],
            qa["person_id_order_unchanged"],
            qa["source_position_id_order_unchanged"],
            qa["non_target_change_count"] == 0,
            qa["diff_row_count"] == 597,
        ]
    ):
        raise ValueError(json.dumps(qa, ensure_ascii=False, indent=2))

    QA_DIR.mkdir(parents=True, exist_ok=True)
    QA_JSON.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
