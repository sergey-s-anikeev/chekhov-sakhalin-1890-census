#!/usr/bin/env python3
"""Select a deterministic, diverse review sample from current parsed output.

The sampler supports the observed-only name splitter. It can exclude records
from an earlier review, limit Muslim records, and favors rare parse structures
while maintaining broad demographic and geographic coverage.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import Counter
from pathlib import Path


DERIVED = {
    "first_name", "patronymic_name", "last_name", "first_name_source",
    "patronymic_source", "last_name_source", "parse_status",
    "parse_confidence", "parse_rule", "name_order_detected", "naming_model",
    "manual_review_reason", "patronymic_name_proposed", "proposal_rule",
}


def read_rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def identity(row):
    return row.get("person_id") or row.get("source_position_id") or row.get("name_raw", "")


def token_bucket(name):
    count = len((name or "").split())
    return str(count) if count <= 4 else "5+"


def tags(row):
    raw = row.get("name_raw", "")
    return {
        "status=" + (row.get("parse_status") or "blank"),
        "rule=" + (row.get("parse_rule") or "blank"),
        "order=" + (row.get("name_order_detected") or "blank"),
        "model=" + (row.get("naming_model") or "blank"),
        "tokens=" + token_bucket(raw),
        "sex=" + (row.get("sex") or "blank"),
        "religion=" + (row.get("religion") or "blank"),
        "district=" + (row.get("district") or "blank"),
        "alias=" + str(bool(row.get("name_alias"))),
        "ordinal=" + str(any(part[:1].isdigit() and "-" in part for part in raw.split())),
        "proposal=" + str(bool(row.get("patronymic_name_proposed"))),
    }


def stable_tie(row, seed):
    return hashlib.sha256((seed + "|" + identity(row)).encode("utf-8")).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parsed_input", type=Path)
    parser.add_argument("sample_output", type=Path)
    parser.add_argument("--source-output", type=Path)
    parser.add_argument("--exclude", type=Path, action="append", default=[])
    parser.add_argument("--size", type=int, default=200)
    parser.add_argument("--max-muslim", type=int, default=5)
    parser.add_argument("--seed", default="name-review-v2-20260720")
    args = parser.parse_args()

    rows, fields = read_rows(args.parsed_input)
    excluded = set()
    for path in args.exclude:
        old_rows, _ = read_rows(path)
        excluded.update(identity(row) for row in old_rows)
    candidates = [row for row in rows if identity(row) not in excluded]
    if len(candidates) < args.size:
        parser.error(f"only {len(candidates)} eligible rows for sample of {args.size}")

    # Reserve scarce diagnostic cases first, but keep Muslim names intentionally
    # small. Remaining records are selected by maximum diversity gain.
    selected = []
    selected_ids = set()
    counts = Counter()

    def add(row):
        key = identity(row)
        if key in selected_ids:
            return
        selected.append(row); selected_ids.add(key)
        counts.update(tags(row))

    muslim = [r for r in candidates if r.get("naming_model") == "muslim"]
    muslim.sort(key=lambda r: stable_tie(r, args.seed))
    # Include at most one representative of each Muslim parsing rule.
    seen_rules = set()
    for row in muslim:
        rule = row.get("parse_rule")
        if rule not in seen_rules and len(seen_rules) < args.max_muslim:
            add(row); seen_rules.add(rule)

    # Always retain rare review-sensitive cases from non-Muslim records.
    priority_rules = (
        "second_given_name_manual_review", "complex_token_count_manual",
        "single_unknown_as_last", "reviewed_compound_first_name",
        "reviewed_alias_as_primary", "reviewed_infant_name_exception",
        "reviewed_single_token_surname", "reviewed_descriptor_as_last",
    )
    for rule in priority_rules:
        pool = [r for r in candidates if r.get("parse_rule") == rule and r.get("naming_model") != "muslim"]
        pool.sort(key=lambda r: stable_tie(r, args.seed))
        for row in pool[: min(8, len(pool))]:
            add(row)

    remaining = [
        r for r in candidates
        if identity(r) not in selected_ids
        and (r.get("naming_model") != "muslim"
             or sum(x.get("naming_model") == "muslim" for x in selected) < args.max_muslim)
    ]
    while remaining and len(selected) < args.size:
        def rank(row):
            row_tags = tags(row)
            diversity = sum(1.0 / (1 + counts[tag]) for tag in row_tags)
            diagnostic = 2.0 * bool(row.get("manual_review_reason"))
            diagnostic += 1.5 * bool(row.get("name_alias"))
            diagnostic += 1.5 * bool(row.get("patronymic_name_proposed"))
            diagnostic += 1.0 * any(part[:1].isdigit() and "-" in part for part in row.get("name_raw", "").split())
            return (-diversity - diagnostic, stable_tie(row, args.seed))
        best = min(remaining, key=rank)
        remaining.remove(best)
        add(best)
        if sum(x.get("naming_model") == "muslim" for x in selected) >= args.max_muslim:
            remaining = [r for r in remaining if r.get("naming_model") != "muslim"]

    selected = selected[:args.size]
    selected.sort(key=lambda r: int((r.get("person_id") or "P0")[1:]))
    priority = [
        "person_id", "source_position_id", "name_raw", "name_alias",
        "first_name", "patronymic_name", "last_name",
        "first_name_source", "patronymic_source", "last_name_source",
        "parse_status", "parse_confidence", "parse_rule", "name_order_detected",
        "naming_model", "manual_review_reason", "patronymic_name_proposed",
        "proposal_rule", "sex", "religion", "family_status", "family_status_norm",
        "district", "settlement", "household_id",
    ]
    review_fields = (["sample_no", "review_decision", "corrected_first_name",
                      "corrected_patronymic_name", "corrected_last_name", "review_notes"]
                     + [f for f in priority if f in fields]
                     + [f for f in fields if f not in priority]
                     + ["sample_ordinal_case"])
    args.sample_output.parent.mkdir(parents=True, exist_ok=True)
    with args.sample_output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=review_fields); writer.writeheader()
        for number, row in enumerate(selected, 1):
            ordinal = any(part[:1].isdigit() and "-" in part for part in row.get("name_raw", "").split())
            writer.writerow({"sample_no": number, "review_decision": "Pending",
                             **row, "sample_ordinal_case": "Yes" if ordinal else "No"})

    if args.source_output:
        source_fields = [f for f in fields if f not in DERIVED]
        with args.source_output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=source_fields); writer.writeheader()
            for row in selected:
                writer.writerow({f: row.get(f, "") for f in source_fields})


if __name__ == "__main__":
    main()
