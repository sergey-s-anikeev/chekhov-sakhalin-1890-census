"""Restage Item 8 using the approved one-column completed-month rule."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/staging/age_item7_20260713/clean_sakhalin_1890_ru_v3_20260712_age_item7_staged.csv"
PROPOSAL = ROOT / "data/review/infant_age_item8_20260713/infant_age_extraction_proposal.csv"
REVIEW_DIR = ROOT / "data/review/infant_age_item8_20260713_v2"
STAGING_DIR = ROOT / "data/staging/infant_age_item8_20260713_v2"
QA_DIR = ROOT / "outputs/qa/infant_age_item8_20260713_v2"
STAGED = STAGING_DIR / "clean_sakhalin_1890_ru_v3_20260712_items7_8_staged_v2.csv"
MAPPING = REVIEW_DIR / "age_months_approved_mapping.csv"
DIFF = QA_DIR / "infant_age_item8_v2_diff.csv"
QA_JSON = QA_DIR / "infant_age_item8_v2_qa.json"


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
    if len(proposal_rows) != 307 or any(row["review_required"] == "YES" for row in proposal_rows):
        raise ValueError("Expected 307 fully parsed proposal rows")
    proposal_by_id = {row["person_id"]: row for row in proposal_rows}
    if len(proposal_by_id) != 307:
        raise ValueError("Duplicate person_id in proposal")

    staged_columns = []
    for column in source_columns:
        staged_columns.append(column)
        if column == "age":
            staged_columns.append("age_months")

    staged_rows = []
    mapping_rows = []
    diff_rows = []
    for source_row in source_rows:
        row = source_row.copy()
        proposal = proposal_by_id.get(row["person_id"])
        row["age_months"] = ""
        if proposal:
            parse_type = proposal["parse_type"]
            if parse_type in {"months", "years_and_months", "years_only"}:
                age_months = proposal["age_months_proposed"]
                comments_after = proposal["comments_residual_preview"].strip()
                action = "remove leading year/month age phrase from comments"
            elif parse_type == "weeks":
                weeks = int(proposal["age_weeks_proposed"])
                age_months = "1" if weeks == 4 else "0"
                comments_after = source_row["comments"]
                action = "preserve exact week wording in comments"
            elif parse_type == "days":
                age_months = "0"
                comments_after = source_row["comments"]
                action = "preserve exact day wording in comments"
            else:
                raise ValueError(f"Unexpected parse type: {parse_type}")

            row["age_months"] = age_months
            row["comments"] = comments_after
            mapping_rows.append(
                {
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "page_number": row["page_number"],
                    "age": row["age"],
                    "parse_type": parse_type,
                    "age_phrase": proposal["age_text_raw_proposed"],
                    "age_months": age_months,
                    "comments_before": source_row["comments"],
                    "comments_after": comments_after,
                    "action": action,
                }
            )
            diff_rows.append(
                {
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "page_number": row["page_number"],
                    "field": "age_months",
                    "before": "",
                    "after": age_months,
                }
            )
            if comments_after != source_row["comments"]:
                diff_rows.append(
                    {
                        "person_id": row["person_id"],
                        "source_position_id": row["source_position_id"],
                        "page_number": row["page_number"],
                        "field": "comments",
                        "before": source_row["comments"],
                        "after": comments_after,
                    }
                )
        staged_rows.append(row)

    write_csv(STAGED, staged_columns, staged_rows)
    write_csv(
        MAPPING,
        [
            "person_id", "source_position_id", "page_number", "age", "parse_type", "age_phrase",
            "age_months", "comments_before", "comments_after", "action",
        ],
        mapping_rows,
    )
    write_csv(
        DIFF,
        ["person_id", "source_position_id", "page_number", "field", "before", "after"],
        diff_rows,
    )

    check_columns, check_rows = read_csv(STAGED)
    source_by_id = {row["person_id"]: row for row in source_rows}
    mapping_by_id = {row["person_id"]: row for row in mapping_rows}
    non_target_changes = []
    for row in check_rows:
        source_row = source_by_id[row["person_id"]]
        for column in source_columns:
            if column != "comments" and row[column] != source_row[column]:
                non_target_changes.append({"person_id": row["person_id"], "field": column})
            if column == "comments" and row["person_id"] not in mapping_by_id and row[column] != source_row[column]:
                non_target_changes.append({"person_id": row["person_id"], "field": column})

    week_day_ids = {
        row["person_id"] for row in mapping_rows if row["parse_type"] in {"weeks", "days"}
    }
    month_year_ids = {
        row["person_id"]
        for row in mapping_rows
        if row["parse_type"] in {"months", "years_and_months", "years_only"}
    }
    comments_changed_ids = {
        row["person_id"] for row in diff_rows if row["field"] == "comments"
    }
    month_values = [int(row["age_months"]) for row in mapping_rows]

    qa = {
        "item": 8,
        "status": "approved rule staged",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "staged": str(STAGED.relative_to(ROOT)).replace("\\", "/"),
        "source_record_count": len(source_rows),
        "staged_record_count": len(check_rows),
        "source_column_count": len(source_columns),
        "staged_column_count": len(check_columns),
        "staged_columns_added": [column for column in check_columns if column not in source_columns],
        "age_months_immediately_after_age": check_columns[check_columns.index("age") + 1] == "age_months",
        "age_months_populated_count": len(mapping_rows),
        "age_months_zero_count": sum(value == 0 for value in month_values),
        "age_months_one_count": sum(value == 1 for value in month_values),
        "week_day_record_count": len(week_day_ids),
        "week_day_comments_preserved_count": sum(
            row["comments"] == source_by_id[row["person_id"]]["comments"]
            for row in check_rows
            if row["person_id"] in week_day_ids
        ),
        "month_year_record_count": len(month_year_ids),
        "month_year_comments_changed_count": len(comments_changed_ids & month_year_ids),
        "month_year_age_phrase_still_present_count": sum(
            mapping_by_id[row["person_id"]]["age_phrase"] in row["comments"]
            for row in check_rows
            if row["person_id"] in month_year_ids and row["comments"]
        ),
        "age_unchanged": all(
            row["age"] == source_by_id[row["person_id"]]["age"] for row in check_rows
        ),
        "person_id_order_unchanged": [row["person_id"] for row in source_rows]
        == [row["person_id"] for row in check_rows],
        "source_position_id_order_unchanged": [row["source_position_id"] for row in source_rows]
        == [row["source_position_id"] for row in check_rows],
        "non_target_change_count": len(non_target_changes),
        "diff_row_count": len(diff_rows),
        "source_sha256": sha256(SOURCE),
        "mapping_sha256": sha256(MAPPING),
        "staged_sha256": sha256(STAGED),
        "diff_sha256": sha256(DIFF),
    }
    if not all(
        [
            qa["source_record_count"] == qa["staged_record_count"] == 7446,
            qa["staged_column_count"] == qa["source_column_count"] + 1,
            qa["staged_columns_added"] == ["age_months"],
            qa["age_months_immediately_after_age"],
            qa["age_months_populated_count"] == 307,
            qa["week_day_record_count"] == 17,
            qa["week_day_comments_preserved_count"] == 17,
            qa["month_year_record_count"] == 290,
            qa["month_year_comments_changed_count"] == 290,
            qa["month_year_age_phrase_still_present_count"] == 0,
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
