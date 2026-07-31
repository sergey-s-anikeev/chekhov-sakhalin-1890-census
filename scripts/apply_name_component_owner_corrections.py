#!/usr/bin/env python3
"""Apply explicit owner-reviewed name-component corrections to a staged CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


COMPONENTS = ["first_name", "patronymic_name", "last_name"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("corrections", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--diff-output", type=Path, required=True)
    parser.add_argument("--qa-output", type=Path, required=True)
    args = parser.parse_args()

    fields, rows = read_csv(args.source)
    correction_fields, corrections = read_csv(args.corrections)
    required_correction_fields = {
        "person_id", "match_name_raw", "match_name_alias", "new_name_alias",
        "review_reason",
        *[f"match_{field}" for field in COMPONENTS],
        *[f"new_{field}" for field in COMPONENTS],
    }
    if required_correction_fields - set(correction_fields):
        raise ValueError("correction table is missing required fields")
    required_source_fields = {
        "person_id", "source_position_id", "name_raw", "name_alias",
        "first_name_source", "patronymic_source", "last_name_source",
        "parse_status", "parse_confidence", "parse_rule",
        "name_order_detected", "manual_review_reason", *COMPONENTS,
    }
    if required_source_fields - set(fields):
        raise ValueError("source is missing required fields")

    correction_by_id = {row["person_id"]: row for row in corrections}
    if len(correction_by_id) != len(corrections) or not all(correction_by_id):
        raise ValueError("correction table contains blank or duplicate person_id")

    found = set()
    changed_ids = set()
    confirmed_noop_ids = []
    diffs = []
    output_rows = []
    for before in rows:
        after = dict(before)
        person_id = before["person_id"]
        correction = correction_by_id.get(person_id)
        if correction is None:
            output_rows.append(after)
            continue
        found.add(person_id)
        if before["name_raw"] != correction["match_name_raw"]:
            raise ValueError(f"name_raw mismatch for {person_id}")
        if before["name_alias"] != correction["match_name_alias"]:
            raise ValueError(f"name_alias mismatch for {person_id}")
        for field in COMPONENTS:
            expected = correction[f"match_{field}"]
            if before[field] != expected:
                raise ValueError(
                    f"{field} mismatch for {person_id}: expected {expected!r}, found {before[field]!r}"
                )

        components_changed = False
        if before["name_alias"] != correction["new_name_alias"]:
            after["name_alias"] = correction["new_name_alias"]
        for field in COMPONENTS:
            new_value = correction[f"new_{field}"]
            if before[field] == new_value:
                continue
            after[field] = new_value
            source_field = {
                "first_name": "first_name_source",
                "patronymic_name": "patronymic_source",
                "last_name": "last_name_source",
            }[field]
            after[source_field] = "reviewed_exception" if new_value else ""
            components_changed = True
        if components_changed:
            after["parse_status"] = "observed"
            after["parse_confidence"] = "high"
            after["parse_rule"] = "reviewed_owner_name_component_update"
            after["name_order_detected"] = "reviewed_exception"
            after["manual_review_reason"] = correction["review_reason"]

        changed_fields = [field for field in fields if before[field] != after[field]]
        if changed_fields:
            changed_ids.add(person_id)
            for field in changed_fields:
                diffs.append({
                    "person_id": person_id,
                    "source_position_id": before["source_position_id"],
                    "field": field,
                    "before": before[field],
                    "after": after[field],
                    "review_reason": correction["review_reason"],
                })
        else:
            confirmed_noop_ids.append(person_id)
        output_rows.append(after)

    missing_ids = sorted(set(correction_by_id) - found)
    if missing_ids:
        raise ValueError("correction IDs absent from source: " + ", ".join(missing_ids))

    allowed = {
        "name_alias", *COMPONENTS,
        "first_name_source", "patronymic_source", "last_name_source",
        "parse_status", "parse_confidence", "parse_rule",
        "name_order_detected", "manual_review_reason",
    }
    unexpected = sorted({row["field"] for row in diffs} - allowed)
    if unexpected:
        raise ValueError("unexpected changed fields: " + ", ".join(unexpected))

    write_csv(args.output, output_rows, fields)
    write_csv(
        args.diff_output,
        diffs,
        ["person_id", "source_position_id", "field", "before", "after", "review_reason"],
    )
    qa = {
        "status": "passed",
        "source": str(args.source).replace("\\", "/"),
        "source_sha256": sha256(args.source),
        "corrections": str(args.corrections).replace("\\", "/"),
        "corrections_sha256": sha256(args.corrections),
        "staged_output": str(args.output).replace("\\", "/"),
        "staged_output_sha256": sha256(args.output),
        "records": len(output_rows),
        "columns": len(fields),
        "unique_person_ids": len({row["person_id"] for row in output_rows}),
        "correction_records": len(corrections),
        "changed_records": len(changed_ids),
        "confirmed_noop_records": len(confirmed_noop_ids),
        "confirmed_noop_person_ids": confirmed_noop_ids,
        "changed_cells": len(diffs),
        "unexpected_changed_fields": unexpected,
        "row_order_preserved": [row["person_id"] for row in rows]
        == [row["person_id"] for row in output_rows],
        "schema_preserved": True,
        "canonical_data_modified": False,
    }
    args.qa_output.parent.mkdir(parents=True, exist_ok=True)
    args.qa_output.write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(qa, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
