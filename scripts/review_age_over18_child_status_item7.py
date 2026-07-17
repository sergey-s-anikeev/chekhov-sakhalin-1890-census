"""Create a read-only Item 7 review for adult ages with child-status evidence."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/staging/infant_age_item8_20260713_v2/clean_sakhalin_1890_ru_v3_20260712_items7_8_staged_v2.csv"
REVIEW_DIR = ROOT / "data/review/age_over18_child_status_item7_20260715"
QA_DIR = ROOT / "outputs/qa/age_over18_child_status_item7_20260715"

CHILD_FAMILY_STATUSES = {
    "Сын",
    "Дочь",
    "Незаконнорожденный сын",
    "Незаконнорожденная дочь",
    "Приемный сын",
    "Приемная дочь",
    "Внук",
    "Внучка",
    "Пасынок",
    "Падчерица",
}
import re

CHILD_LEGAL_RE = re.compile(r"^(?:Сын|Дочь)\b", re.IGNORECASE)
FLAGGED_ORIGIN_PLACE = "На Сахалине"

OUTPUT_COLUMNS = [
    "review_priority",
    "review_reasons",
    "manual_decision",
    "manual_notes",
    "person_id",
    "source_position_id",
    "page_number",
    "district",
    "settlement",
    "household_id",
    "name_raw",
    "sex",
    "age",
    "legal_status",
    "legal_status_norm",
    "family_status",
    "family_status_norm",
    "origin_place",
    "origin_place_flag",
    "comments",
    "notes_raw",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as handle:
        source_rows = list(csv.DictReader(handle))

    review_rows = []
    origin_flagged_ids = []
    for row in source_rows:
        age_text = row["age"].strip()
        if not age_text.isdigit() or int(age_text) <= 18:
            continue
        reasons = []
        if row["family_status_norm"].strip() in CHILD_FAMILY_STATUSES:
            reasons.append("CHILD_RELATIONSHIP_IN_FAMILY_STATUS_NORM")
        if CHILD_LEGAL_RE.search(row["legal_status_norm"].strip()):
            reasons.append("CHILD_RELATIONSHIP_IN_LEGAL_STATUS_NORM")
        origin_marker = row["origin_place"].strip().casefold() == FLAGGED_ORIGIN_PLACE.casefold()
        if origin_marker:
            reasons.append("ORIGIN_PLACE_NA_SAKHALINE_OVER_18")
            origin_flagged_ids.append(row["person_id"])
        if not reasons:
            continue

        output = {column: row.get(column, "") for column in OUTPUT_COLUMNS}
        output.update(
            review_priority="high" if int(age_text) >= 30 else "standard",
            review_reasons="; ".join(reasons),
            manual_decision="",
            manual_notes="",
            origin_place_flag="YES — На Сахалине and age >18" if origin_marker else "NO",
        )
        review_rows.append(output)

    review_rows.sort(
        key=lambda row: (
            0 if row["review_priority"] == "high" else 1,
            -int(row["age"]),
            int(row["page_number"]),
            row["person_id"],
        )
    )
    inventory_path = REVIEW_DIR / "age_over18_child_status_review.csv"
    write_csv(inventory_path, review_rows, OUTPUT_COLUMNS)

    reason_counts = Counter(
        reason for row in review_rows for reason in row["review_reasons"].split("; ") if reason
    )
    age_counts = Counter(row["age"] for row in review_rows)
    write_csv(
        REVIEW_DIR / "age_over18_child_status_age_summary.csv",
        [
            {"age": age, "record_count": str(count)}
            for age, count in sorted(age_counts.items(), key=lambda item: int(item[0]))
        ],
        ["age", "record_count"],
    )

    qa = {
        "item": 7,
        "mode": "read-only additional verification; no dataset changes",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(SOURCE),
        "source_record_count": len(source_rows),
        "age_over_18_record_count": sum(
            row["age"].strip().isdigit() and int(row["age"]) > 18 for row in source_rows
        ),
        "review_record_count": len(review_rows),
        "reason_counts": dict(sorted(reason_counts.items())),
        "age_counts": dict(sorted(age_counts.items(), key=lambda item: int(item[0]))),
        "age_30_or_more_count": sum(int(row["age"]) >= 30 for row in review_rows),
        "origin_place_na_sakhaline_over18_count": len(origin_flagged_ids),
        "origin_place_only_added_count": sum(
            row["review_reasons"] == "ORIGIN_PLACE_NA_SAKHALINE_OVER_18" for row in review_rows
        ),
        "origin_place_and_child_status_overlap_count": sum(
            "ORIGIN_PLACE_NA_SAKHALINE_OVER_18" in row["review_reasons"]
            and row["review_reasons"] != "ORIGIN_PLACE_NA_SAKHALINE_OVER_18"
            for row in review_rows
        ),
        "page_number_present_for_all_review_rows": all(row["page_number"] for row in review_rows),
        "unique_person_ids_in_review": len({row["person_id"] for row in review_rows}) == len(review_rows),
        "canonical_or_staged_dataset_modified": False,
        "inventory_sha256": sha256(inventory_path),
    }
    QA_DIR.mkdir(parents=True, exist_ok=True)
    (QA_DIR / "age_over18_child_status_qa.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary = f"""# Item 7 additional age verification

This read-only review identifies {len(review_rows)} records with integer `age` greater than 18 and either an explicit child relationship in `family_status_norm` or `legal_status_norm`, or `origin_place` equal to `На Сахалине`.

`origin_place = На Сахалине` is an explicit user-requested review flag. It does not by itself establish an age discrepancy.

These are review prompts, not confirmed errors. Adult sons, daughters, grandchildren, or stepchildren may be historically valid household relationships. Use `page_number` and the raw status fields to verify the source before proposing any correction.
"""
    (QA_DIR / "age_over18_child_status_summary.md").write_text(summary, encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
