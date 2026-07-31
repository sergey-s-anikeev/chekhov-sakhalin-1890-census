#!/usr/bin/env python3
"""Validate the completed Muslim-name workbook and create parser exceptions."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import openpyxl

ALLOWED = {
    "Approve current",
    "Use full string as last",
    "First name only",
    "Correct split",
}


def clean(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def component(value) -> str:
    value = clean(value)
    return "" if value.upper() == "NULL" else value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("exceptions_output", type=Path)
    parser.add_argument("--audit-output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    args = parser.parse_args()

    book = openpyxl.load_workbook(args.workbook, read_only=True, data_only=True)
    sheet = book["All Muslim Names"]
    rows = list(sheet.iter_rows(values_only=True))
    headers = [clean(value).lstrip("\ufeff") for value in rows[0]]
    records = [dict(zip(headers, row)) for row in rows[1:] if clean(row[4])]

    errors = []
    seen = set()
    exceptions = []
    audit = []
    decisions = Counter()
    result_classes = Counter()
    changed = 0
    for row_number, row in enumerate(records, start=2):
        person_id = clean(row["person_id"])
        decision = clean(row["review_decision"])
        name_raw = clean(row["name_raw"])
        current_first = clean(row["current_first_name"])
        current_patronymic = clean(row["current_patronymic_name"])
        current_last = clean(row["current_last_name"])
        corrected_first = component(row["corrected_first_name"])
        corrected_last = component(row["corrected_last_name"])
        if person_id in seen:
            errors.append(f"row {row_number}: duplicate person_id {person_id}")
        seen.add(person_id)
        if decision not in ALLOWED:
            errors.append(f"row {row_number} {person_id}: unsupported/blank decision {decision!r}")
            continue

        if decision == "Approve current":
            first_name, last_name = current_first, current_last
            if current_patronymic:
                errors.append(f"row {row_number} {person_id}: Muslim patronymic is populated")
            if corrected_first != current_first or corrected_last != current_last:
                errors.append(
                    f"row {row_number} {person_id}: Approve current conflicts with corrected columns"
                )
        elif decision == "Use full string as last":
            first_name, last_name = "", name_raw
        elif decision == "First name only":
            first_name, last_name = corrected_first, ""
            if not first_name:
                errors.append(f"row {row_number} {person_id}: First name only requires corrected_first_name")
        else:
            first_name, last_name = corrected_first, corrected_last
            if not first_name:
                errors.append(f"row {row_number} {person_id}: Correct split requires corrected_first_name")

        if first_name and last_name:
            parse_rule = "reviewed_muslim_first_last"
            result_class = "first_last"
        elif first_name:
            parse_rule = "reviewed_muslim_first_only"
            result_class = "first_only"
        elif last_name:
            parse_rule = "reviewed_muslim_unsplit_as_last"
            result_class = "full_string_last"
            if last_name != name_raw:
                errors.append(f"row {row_number} {person_id}: last-only result must equal complete name_raw")
        else:
            errors.append(f"row {row_number} {person_id}: decision produced no accepted name component")
            continue

        is_changed = (first_name, "", last_name) != (
            current_first, current_patronymic, current_last
        )
        changed += int(is_changed)
        decisions[decision] += 1
        result_classes[result_class] += 1
        review_reason = (
            "Owner-approved complete Muslim-name re-review: "
            + decision
            + (f"; {clean(row['review_notes'])}" if clean(row["review_notes"]) else "")
        )
        exceptions.append({
            "person_id": person_id,
            "match_name_raw": name_raw,
            "match_name_alias": "",
            "first_name": first_name,
            "patronymic_name": "",
            "last_name": last_name,
            "parse_rule": parse_rule,
            "review_reason": review_reason,
        })
        audit.append({
            "person_id": person_id,
            "name_raw": name_raw,
            "review_decision": decision,
            "old_first_name": current_first,
            "old_patronymic_name": current_patronymic,
            "old_last_name": current_last,
            "new_first_name": first_name,
            "new_patronymic_name": "",
            "new_last_name": last_name,
            "changed": "Yes" if is_changed else "No",
            "review_notes": clean(row["review_notes"]),
        })

    if len(records) != 197:
        errors.append(f"expected 197 records, found {len(records)}")
    if errors:
        raise ValueError("\n".join(errors))

    args.exceptions_output.parent.mkdir(parents=True, exist_ok=True)
    with args.exceptions_output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(exceptions[0]))
        writer.writeheader()
        writer.writerows(exceptions)
    args.audit_output.parent.mkdir(parents=True, exist_ok=True)
    with args.audit_output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(audit[0]))
        writer.writeheader()
        writer.writerows(audit)
    summary = {
        "records": len(records),
        "review_decisions": dict(sorted(decisions.items())),
        "result_classes": dict(sorted(result_classes.items())),
        "changed_records": changed,
        "unchanged_records": len(records) - changed,
        "validation_errors": 0,
    }
    args.summary_output.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
