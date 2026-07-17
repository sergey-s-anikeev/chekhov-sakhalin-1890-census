"""Apply approved Item 7 age feedback to a versioned staged canonical-v3 copy."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/clean_sakhalin_1890_ru_v3_20260712.csv"
DEFAULT_REVIEW = Path("C:/Users/User/Downloads/age_review.csv")
STAGING_DIR = ROOT / "data/staging/age_item7_20260713"
REVIEW_OUTPUT_DIR = ROOT / "data/review/age_item7_20260713/owner_response"
QA_DIR = ROOT / "outputs/qa/age_item7_20260713"
STAGED = STAGING_DIR / "clean_sakhalin_1890_ru_v3_20260712_age_item7_staged.csv"
CORRECTIONS = REVIEW_OUTPUT_DIR / "age_corrections_approved.csv"
DIFF = QA_DIR / "age_item7_applied_diff.csv"
QA_JSON = QA_DIR / "age_item7_staging_qa.json"
REMAINING_REVIEW = REVIEW_OUTPUT_DIR.parent / "age_0_18_remaining_under_review_after_feedback.csv"
CONFIRMED_REVIEW = REVIEW_OUTPUT_DIR / "remaining_50_review_decisions.csv"
BLANK_AGE_REVIEW = REVIEW_OUTPUT_DIR.parent / "blank_age_review.csv"
BLANK_AGE_DECISIONS = REVIEW_OUTPUT_DIR / "blank_age_review_decisions.csv"

COMMENT_PERSON_ID = "P002570"
COMMENT_TEXT = "Владеет участком № 33"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path, delimiter: str = ",") -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError(f"No header found in {path}")
        return reader.fieldnames, list(reader)


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    args = parser.parse_args()
    review_path = args.review.resolve()

    source_columns, source_rows = read_csv(SOURCE)
    review_columns, review_rows = read_csv(review_path, delimiter=";")
    required_review_columns = {"person_id", "age", "age_new"}
    missing = required_review_columns - set(review_columns)
    if missing:
        raise ValueError(f"Review file is missing required columns: {sorted(missing)}")

    source_by_id = {row["person_id"]: row for row in source_rows}
    if len(source_by_id) != len(source_rows):
        raise ValueError("Canonical source contains duplicate person_id values")
    review_ids = [row["person_id"] for row in review_rows]
    if len(set(review_ids)) != len(review_ids):
        raise ValueError("Review file contains duplicate person_id values")
    unknown_ids = sorted(set(review_ids) - set(source_by_id))
    if unknown_ids:
        raise ValueError(f"Review file contains unknown person_id values: {unknown_ids}")

    corrections: list[dict[str, str]] = []
    for review_row in review_rows:
        age_new = review_row["age_new"].strip()
        if not age_new:
            continue
        if not age_new.isdigit() or not 0 <= int(age_new) <= 120:
            raise ValueError(f"Invalid age_new for {review_row['person_id']}: {age_new!r}")
        source_row = source_by_id[review_row["person_id"]]
        if review_row["age"].strip() != source_row["age"].strip():
            raise ValueError(
                f"Review/source age mismatch for {review_row['person_id']}: "
                f"review={review_row['age']!r}, source={source_row['age']!r}"
            )
        if age_new == source_row["age"].strip():
            raise ValueError(f"age_new does not change age for {review_row['person_id']}")
        corrections.append(
            {
                "person_id": review_row["person_id"],
                "source_position_id": source_row["source_position_id"],
                "page_number": source_row["page_number"],
                "name_raw": source_row["name_raw"],
                "age_before": source_row["age"],
                "age_approved": age_new,
            }
        )

    correction_by_id = {row["person_id"]: row["age_approved"] for row in corrections}
    remaining_review_rows = []
    for review_row in review_rows:
        if review_row["person_id"] in correction_by_id:
            continue
        reasons = [value.strip() for value in review_row.get("review_reasons", "").split(";") if value.strip()]
        if review_row["age"].strip() == "0" and reasons == ["AGE_ZERO_VERIFY_SOURCE"]:
            continue
        remaining_review_rows.append({key: value for key, value in review_row.items() if key != "age_new"})
    staged_rows = [row.copy() for row in source_rows]
    diffs: list[dict[str, str]] = []
    for row in staged_rows:
        person_id = row["person_id"]
        if person_id in correction_by_id:
            before = row["age"]
            after = correction_by_id[person_id]
            row["age"] = after
            diffs.append(
                {
                    "person_id": person_id,
                    "source_position_id": row["source_position_id"],
                    "page_number": row["page_number"],
                    "name_raw": row["name_raw"],
                    "field": "age",
                    "before": before,
                    "after": after,
                }
            )
        if person_id == COMMENT_PERSON_ID:
            if row["comments"] not in ("", COMMENT_TEXT):
                raise ValueError(
                    f"Refusing to overwrite nonblank comments for {COMMENT_PERSON_ID}: {row['comments']!r}"
                )
            before = row["comments"]
            row["comments"] = COMMENT_TEXT
            if before != COMMENT_TEXT:
                diffs.append(
                    {
                        "person_id": person_id,
                        "source_position_id": row["source_position_id"],
                        "page_number": row["page_number"],
                        "name_raw": row["name_raw"],
                        "field": "comments",
                        "before": before,
                        "after": COMMENT_TEXT,
                    }
                )

    write_csv(STAGED, source_columns, staged_rows)
    write_csv(
        CORRECTIONS,
        ["person_id", "source_position_id", "page_number", "name_raw", "age_before", "age_approved"],
        corrections,
    )
    write_csv(
        DIFF,
        ["person_id", "source_position_id", "page_number", "name_raw", "field", "before", "after"],
        diffs,
    )
    write_csv(
        REMAINING_REVIEW,
        [column for column in review_columns if column != "age_new"],
        remaining_review_rows,
    )
    confirmed_review_rows = []
    for row in remaining_review_rows:
        confirmed = row.copy()
        confirmed["manual_decision"] = "confirmed — no issue"
        confirmed["manual_notes"] = "Owner confirmed review completed with no issues on 2026-07-13."
        confirmed_review_rows.append(confirmed)
    write_csv(
        CONFIRMED_REVIEW,
        [column for column in review_columns if column != "age_new"],
        confirmed_review_rows,
    )
    blank_columns, blank_rows = read_csv(BLANK_AGE_REVIEW)
    if len(blank_rows) != 147 or any(row.get("age", "").strip() for row in blank_rows):
        raise ValueError("Blank-age review input does not contain the expected 147 blank-age records")
    blank_decision_rows = []
    for row in blank_rows:
        confirmed = row.copy()
        confirmed["review_status"] = "confirmed"
        confirmed["manual_decision"] = "confirmed — source blank"
        confirmed["manual_notes"] = (
            "Owner verified the source and raw CSV files for all three districts on 2026-07-13; "
            "no discrepancies identified."
        )
        blank_decision_rows.append(confirmed)
    write_csv(BLANK_AGE_DECISIONS, blank_columns, blank_decision_rows)

    staged_columns, staged_check = read_csv(STAGED)
    changed_ids = {row["person_id"] for row in diffs}
    non_target_mismatches = []
    for source_row, staged_row in zip(source_rows, staged_check, strict=True):
        allowed = {"age"} if source_row["person_id"] in correction_by_id else set()
        if source_row["person_id"] == COMMENT_PERSON_ID:
            allowed.add("comments")
        for column in source_columns:
            if column not in allowed and source_row[column] != staged_row[column]:
                non_target_mismatches.append({"person_id": source_row["person_id"], "field": column})

    qa = {
        "item": 7,
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "review_input": str(review_path),
        "review_input_sha256": sha256(review_path),
        "staged_output": str(STAGED.relative_to(ROOT)).replace("\\", "/"),
        "source_record_count": len(source_rows),
        "staged_record_count": len(staged_check),
        "source_column_count": len(source_columns),
        "staged_column_count": len(staged_columns),
        "schema_unchanged": source_columns == staged_columns,
        "age_new_absent_from_staged_schema": "age_new" not in staged_columns,
        "age_correction_count": len(corrections),
        "comment_change_count": sum(row["field"] == "comments" for row in diffs),
        "changed_record_count": len(changed_ids),
        "field_change_count": len(diffs),
        "post_feedback_screened_record_count": len(remaining_review_rows),
        "post_feedback_owner_confirmed_no_issue_count": len(confirmed_review_rows),
        "remaining_age_0_18_review_count": 0,
        "blank_age_owner_confirmed_no_discrepancy_count": len(blank_decision_rows),
        "remaining_blank_age_review_count": 0,
        "item_7_review_complete": True,
        "person_id_order_unchanged": [row["person_id"] for row in source_rows]
        == [row["person_id"] for row in staged_check],
        "source_position_id_order_unchanged": [row["source_position_id"] for row in source_rows]
        == [row["source_position_id"] for row in staged_check],
        "non_target_mismatch_count": len(non_target_mismatches),
        "p002570_age": next(row["age"] for row in staged_check if row["person_id"] == COMMENT_PERSON_ID),
        "p002570_comments": next(row["comments"] for row in staged_check if row["person_id"] == COMMENT_PERSON_ID),
        "source_sha256": sha256(SOURCE),
        "staged_sha256": sha256(STAGED),
        "corrections_sha256": sha256(CORRECTIONS),
        "diff_sha256": sha256(DIFF),
    }
    if not all(
        [
            qa["source_record_count"] == qa["staged_record_count"],
            qa["schema_unchanged"],
            qa["age_new_absent_from_staged_schema"],
            qa["age_correction_count"] == 25,
            qa["comment_change_count"] == 1,
            qa["changed_record_count"] == 25,
            qa["field_change_count"] == 26,
            qa["post_feedback_screened_record_count"] == 50,
            qa["post_feedback_owner_confirmed_no_issue_count"] == 50,
            qa["remaining_age_0_18_review_count"] == 0,
            qa["blank_age_owner_confirmed_no_discrepancy_count"] == 147,
            qa["remaining_blank_age_review_count"] == 0,
            qa["item_7_review_complete"],
            qa["person_id_order_unchanged"],
            qa["source_position_id_order_unchanged"],
            qa["non_target_mismatch_count"] == 0,
            qa["p002570_age"] == "49",
            qa["p002570_comments"] == COMMENT_TEXT,
        ]
    ):
        raise ValueError(f"Staging QA failed: {json.dumps(qa, ensure_ascii=False, indent=2)}")

    QA_JSON.parent.mkdir(parents=True, exist_ok=True)
    QA_JSON.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
