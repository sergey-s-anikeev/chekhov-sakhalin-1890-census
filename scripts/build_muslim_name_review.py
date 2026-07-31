#!/usr/bin/env python3
"""Build a complete owner-review queue for all Muslim-name records."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--hyphen-output", type=Path)
    args = parser.parse_args()

    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    review_rows = []
    for row in rows:
        if row.get("naming_model") != "muslim":
            continue
        tokens = row["name_raw"].split()
        hyphenated_two_token = len(tokens) == 2 and any("-" in token for token in tokens)
        first = row.get("first_name", "")
        patronymic = row.get("patronymic_name", "")
        last = row.get("last_name", "")
        if first and last and not patronymic:
            current_class = "first_last"
        elif first and not patronymic and not last:
            current_class = "first_only"
        elif last and not first and not patronymic:
            current_class = "full_string_last" if last == row["name_raw"] else "last_only"
        else:
            current_class = "needs_review"
        review_rows.append({
            "review_decision": "",
            "corrected_first_name": first,
            "corrected_last_name": last,
            "review_notes": "",
            "person_id": row["person_id"],
            "name_raw": row["name_raw"],
            "current_first_name": first,
            "current_patronymic_name": patronymic,
            "current_last_name": last,
            "current_class": current_class,
            "hyphenated_two_token": "Yes" if hyphenated_two_token else "No",
            "previously_owner_reviewed": (
                "Yes" if row.get("parse_rule", "").startswith("reviewed_muslim_") else "No"
            ),
            "current_parse_rule": row.get("parse_rule", ""),
            "sex": row.get("sex", ""),
            "religion": row.get("religion", ""),
            "family_status": row.get("family_status", ""),
            "family_status_norm": row.get("family_status_norm", ""),
            "district": row.get("district", ""),
            "settlement": row.get("settlement", ""),
            "household_id": row.get("household_id", ""),
            "source_position_id": row.get("source_position_id", ""),
            "page_number": row.get("page_number", ""),
            "comments": row.get("comments", ""),
            "notes_raw": row.get("notes_raw", ""),
        })

    review_rows.sort(key=lambda row: (
        0 if row["hyphenated_two_token"] == "Yes" else 1,
        0 if row["previously_owner_reviewed"] == "No" else 1,
        row["person_id"],
    ))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(review_rows[0]) if review_rows else []
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(review_rows)
    if args.hyphen_output:
        args.hyphen_output.parent.mkdir(parents=True, exist_ok=True)
        with args.hyphen_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(
                row for row in review_rows if row["hyphenated_two_token"] == "Yes"
            )


if __name__ == "__main__":
    main()
