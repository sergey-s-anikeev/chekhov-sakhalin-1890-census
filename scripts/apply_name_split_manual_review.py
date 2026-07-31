#!/usr/bin/env python3
"""Apply owner-reviewed name normalization changes by person_id.

This stage changes only name_raw/name_alias. Accepted split components are
applied separately by the reviewed exception table when name_split.py runs.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("overrides", type=Path)
    parser.add_argument("--diff-output", type=Path, required=True)
    args = parser.parse_args()

    with args.overrides.open(encoding="utf-8-sig", newline="") as handle:
        override_rows = list(csv.DictReader(handle))
    overrides = {row["person_id"]: row for row in override_rows}
    if len(overrides) != len(override_rows) or not all(overrides):
        raise ValueError("manual overrides contain blank or duplicate person_id")

    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle); rows = list(reader); fields = list(reader.fieldnames or [])
    missing = {"person_id", "name_raw", "name_alias"} - set(fields)
    if missing:
        raise ValueError("missing input fields: " + ", ".join(sorted(missing)))

    found = set(); diffs = []
    for row in rows:
        pid = row["person_id"]
        if pid not in overrides:
            continue
        change = overrides[pid]; found.add(pid)
        if row["name_raw"].strip() != change["match_name_raw"].strip():
            raise ValueError(f"name_raw mismatch for {pid}: {row['name_raw']!r}")
        old_raw, old_alias = row["name_raw"], row["name_alias"]
        row["name_raw"] = change["new_name_raw"].strip()
        if change["new_name_alias"].strip():
            row["name_alias"] = change["new_name_alias"].strip()
        diffs.append({
            "person_id": pid, "old_name_raw": old_raw, "new_name_raw": row["name_raw"],
            "old_name_alias": old_alias, "new_name_alias": row["name_alias"],
            "first_name_reviewed": change["first_name"],
            "patronymic_name_reviewed": change["patronymic_name"],
            "last_name_reviewed": change["last_name"],
            "review_reason": change["review_reason"],
        })
    missing_ids = set(overrides) - found
    if missing_ids:
        raise ValueError("override IDs absent from input: " + ", ".join(sorted(missing_ids)))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    diff_fields = list(diffs[0]) if diffs else []
    args.diff_output.parent.mkdir(parents=True, exist_ok=True)
    with args.diff_output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=diff_fields); writer.writeheader(); writer.writerows(diffs)


if __name__ == "__main__":
    main()
