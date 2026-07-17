"""Apply the approved P003286 age correction and record all review decisions."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/staging/infant_age_item8_20260713_v2/clean_sakhalin_1890_ru_v3_20260712_items7_8_staged_v2.csv"
REVIEW = ROOT / "data/review/age_over18_child_status_item7_20260715/age_over18_child_status_review.csv"
OWNER_WORKBOOK = ROOT / "data/review/age_over18_child_status_item7_20260715/age_over18_child_status_review.xlsx"
OWNER_DIR = ROOT / "data/review/age_over18_child_status_item7_20260715/owner_response"
STAGING_DIR = ROOT / "data/staging/items7_8_age_followup_20260715"
QA_DIR = ROOT / "outputs/qa/items7_8_age_followup_20260715"
STAGED = STAGING_DIR / "clean_sakhalin_1890_ru_v3_20260712_items7_8_staged_v3.csv"
DECISIONS = OWNER_DIR / "age_over18_owner_decisions.csv"
DIFF = QA_DIR / "age_over18_item7_applied_diff.csv"
QA_JSON = QA_DIR / "age_over18_item7_staging_qa.json"

CORRECTED_PERSON_ID = "P003286"
AGE_BEFORE = "54"
AGE_AFTER = "5"


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
    review_columns, review_rows = read_csv(REVIEW)
    if len(review_rows) != 49:
        raise ValueError(f"Expected 49 review records, found {len(review_rows)}")
    if len({row["person_id"] for row in review_rows}) != len(review_rows):
        raise ValueError("Duplicate person_id in review inventory")

    source_by_id = {row["person_id"]: row for row in source_rows}
    target = source_by_id[CORRECTED_PERSON_ID]
    if target["age"] != AGE_BEFORE:
        raise ValueError(f"Unexpected source age for {CORRECTED_PERSON_ID}: {target['age']}")
    if target["age_months"]:
        raise ValueError(f"Expected blank age_months for {CORRECTED_PERSON_ID}")

    decisions = []
    for review_row in review_rows:
        person_id = review_row["person_id"]
        decision = review_row.copy()
        if person_id == CORRECTED_PERSON_ID:
            decision["manual_decision"] = AGE_AFTER
            decision["manual_notes"] = "Owner confirmed age 5; source footnote error."
            decision_status = "age corrected"
        else:
            decision["manual_decision"] = "confirmed — no issue"
            decision["manual_notes"] = "Owner reviewed; no issue identified."
            decision_status = "confirmed — no issue"
        decision["decision_status"] = decision_status
        decisions.append(decision)

    decision_columns = review_columns + (["decision_status"] if "decision_status" not in review_columns else [])
    write_csv(DECISIONS, decision_columns, decisions)

    staged_rows = [row.copy() for row in source_rows]
    diff_rows = []
    for row in staged_rows:
        if row["person_id"] == CORRECTED_PERSON_ID:
            row["age"] = AGE_AFTER
            diff_rows.append(
                {
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "page_number": row["page_number"],
                    "field": "age",
                    "before": AGE_BEFORE,
                    "after": AGE_AFTER,
                    "reason": "Owner-confirmed source footnote error",
                }
            )

    write_csv(STAGED, source_columns, staged_rows)
    write_csv(
        DIFF,
        ["person_id", "source_position_id", "page_number", "field", "before", "after", "reason"],
        diff_rows,
    )

    check_columns, check_rows = read_csv(STAGED)
    check_by_id = {row["person_id"]: row for row in check_rows}
    non_target_changes = []
    for source_row, staged_row in zip(source_rows, check_rows, strict=True):
        for column in source_columns:
            allowed = source_row["person_id"] == CORRECTED_PERSON_ID and column == "age"
            if not allowed and source_row[column] != staged_row[column]:
                non_target_changes.append({"person_id": source_row["person_id"], "field": column})

    corrected = check_by_id[CORRECTED_PERSON_ID]
    qa = {
        "item": 7,
        "status": "owner feedback applied; additional review complete",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "staged": str(STAGED.relative_to(ROOT)).replace("\\", "/"),
        "owner_workbook": str(OWNER_WORKBOOK.relative_to(ROOT)).replace("\\", "/"),
        "owner_workbook_sha256": sha256(OWNER_WORKBOOK),
        "source_record_count": len(source_rows),
        "staged_record_count": len(check_rows),
        "schema_unchanged": source_columns == check_columns,
        "owner_review_record_count": len(decisions),
        "owner_confirmed_no_issue_count": sum(row["person_id"] != CORRECTED_PERSON_ID for row in decisions),
        "age_correction_count": len(diff_rows),
        "corrected_person_id": CORRECTED_PERSON_ID,
        "corrected_age_before": AGE_BEFORE,
        "corrected_age_after": corrected["age"],
        "corrected_age_months": corrected["age_months"],
        "corrected_legal_status_norm": corrected["legal_status_norm"],
        "corrected_family_status_norm": corrected["family_status_norm"],
        "corrected_origin_place": corrected["origin_place"],
        "person_id_order_unchanged": [row["person_id"] for row in source_rows]
        == [row["person_id"] for row in check_rows],
        "source_position_id_order_unchanged": [row["source_position_id"] for row in source_rows]
        == [row["source_position_id"] for row in check_rows],
        "non_target_change_count": len(non_target_changes),
        "source_sha256": sha256(SOURCE),
        "decisions_sha256": sha256(DECISIONS),
        "staged_sha256": sha256(STAGED),
        "diff_sha256": sha256(DIFF),
    }
    if not all(
        [
            qa["source_record_count"] == qa["staged_record_count"] == 7446,
            qa["schema_unchanged"],
            qa["owner_review_record_count"] == 49,
            qa["owner_confirmed_no_issue_count"] == 48,
            qa["age_correction_count"] == 1,
            qa["corrected_age_after"] == AGE_AFTER,
            qa["corrected_age_months"] == "",
            qa["corrected_legal_status_norm"] == "Дочь поселенца",
            qa["corrected_family_status_norm"] == "Дочь",
            qa["corrected_origin_place"] == "На Сахалине",
            qa["person_id_order_unchanged"],
            qa["source_position_id_order_unchanged"],
            qa["non_target_change_count"] == 0,
        ]
    ):
        raise ValueError(json.dumps(qa, ensure_ascii=False, indent=2))

    QA_DIR.mkdir(parents=True, exist_ok=True)
    QA_JSON.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
