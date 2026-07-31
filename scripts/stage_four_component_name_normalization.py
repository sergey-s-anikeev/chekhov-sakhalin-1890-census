#!/usr/bin/env python3
"""Apply reviewed four-component names, one manual fix, and ordinal formatting."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path


BARE_ORDINAL_RE = re.compile(r"(?<![\w-])(\d+)([йяе])(?!\w)", re.IGNORECASE)
MANUAL_FIXES = {"P000064": ("Василий 2 Герасимов", "Василий Герасимов")}


def clean_cell(value):
    value = "" if value is None else str(value).strip()
    return "" if value.casefold() == "null" else value


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("review_json", type=Path)
    parser.add_argument("stage_dir", type=Path)
    parser.add_argument("qa_dir", type=Path)
    args = parser.parse_args()

    rows, fields = read_csv(args.base)
    original = {row["person_id"]: dict(row) for row in rows}
    if len(original) != len(rows):
        parser.error("person_id is not unique in base data")

    matrix = json.loads(args.review_json.read_text(encoding="utf-8"))
    headers = matrix[0]
    decisions = [dict(zip(headers, values + [None] * (len(headers) - len(values))))
                 for values in matrix[1:]]
    if len(decisions) != 65:
        parser.error(f"expected 65 reviewed rows, found {len(decisions)}")

    decision_counts = Counter(clean_cell(row["owner_decision"]) for row in decisions)
    if "Pending" in decision_counts or "" in decision_counts:
        parser.error("review workbook contains pending or blank decisions")

    change_basis = {}
    for review in decisions:
        pid = clean_cell(review["person_id"])
        if pid not in original:
            parser.error(f"review person_id not found: {pid}")
        if original[pid]["name_raw"] != clean_cell(review["current_name_raw"]):
            parser.error(f"name_raw mismatch for {pid}")
        decision = clean_cell(review["owner_decision"])
        if decision == "Approve proposal":
            new_name = clean_cell(review["proposed_name_raw"])
            new_alias = clean_cell(review["proposed_name_alias"])
            if not new_name:
                parser.error(f"approved proposal lacks proposed_name_raw: {pid}")
            original[pid]["name_raw"] = new_name
            original[pid]["name_alias"] = new_alias
            change_basis[pid] = "owner_approved_four_component_proposal"
        elif decision == "Modify":
            new_name = clean_cell(review["owner_name_raw"])
            if not new_name:
                parser.error(f"modified decision lacks owner_name_raw: {pid}")
            original[pid]["name_raw"] = new_name
            original[pid]["name_alias"] = clean_cell(review["owner_name_alias"])
            change_basis[pid] = "owner_modified_four_component_decision"
        elif decision in {"Keep unchanged", "Manual review"}:
            pass
        else:
            parser.error(f"unsupported owner decision for {pid}: {decision}")

    # Explicit record correction supplied after workbook review.
    for pid, (expected, replacement) in MANUAL_FIXES.items():
        if original[pid]["name_raw"] != expected:
            parser.error(f"manual-fix source mismatch for {pid}")
        original[pid]["name_raw"] = replacement
        change_basis[pid] = "owner_explicit_manual_name_raw_fix"

    # Canonicalize every remaining bare ordinal suffix, including records that
    # were outside the four-component review inventory.
    for pid, row in original.items():
        normalized = BARE_ORDINAL_RE.sub(r"\1-\2", row["name_raw"])
        if normalized != row["name_raw"]:
            row["name_raw"] = normalized
            prior = change_basis.get(pid)
            change_basis[pid] = ((prior + "; ") if prior else "") + "global_ordinal_format_normalization"

    staged = [original[row["person_id"]] for row in rows]
    combined_name = "clean_sakhalin_1890_ru_v4_20260717_name_raw_staged.csv"
    write_csv(args.stage_dir / combined_name, staged, fields)
    district_files = {
        "Александровский": "clean_alexandrovsky_ru_v4_20260717_name_raw_staged.csv",
        "Тымовский": "clean_tymovsky_ru_v4_20260717_name_raw_staged.csv",
        "Корсаковский": "clean_korsakovsky_ru_v4_20260717_name_raw_staged.csv",
    }
    for district, filename in district_files.items():
        write_csv(args.stage_dir / filename, [row for row in staged if row["district"] == district], fields)

    diff = []
    allowed = {"name_raw", "name_alias"}
    for before_row, after_row in zip(rows, staged, strict=True):
        changed = [field for field in fields if before_row[field] != after_row[field]]
        if set(changed) - allowed:
            parser.error(f"unexpected changed fields for {before_row['person_id']}: {changed}")
        if changed:
            diff.append({
                "person_id": before_row["person_id"],
                "source_position_id": before_row["source_position_id"],
                "district": before_row["district"],
                "name_raw_before": before_row["name_raw"],
                "name_raw_after": after_row["name_raw"],
                "name_alias_before": before_row["name_alias"],
                "name_alias_after": after_row["name_alias"],
                "changed_fields": "; ".join(changed),
                "change_basis": change_basis.get(before_row["person_id"], ""),
            })
    write_csv(args.qa_dir / "name_raw_normalization_diff.csv", diff, list(diff[0]))

    remaining_bare = [row for row in staged if BARE_ORDINAL_RE.search(row["name_raw"])]
    qa = {
        "base": str(args.base),
        "record_count_before": len(rows),
        "record_count_after": len(staged),
        "schema_unchanged": fields == list(staged[0]),
        "person_id_order_unchanged": [r["person_id"] for r in rows] == [r["person_id"] for r in staged],
        "owner_decision_counts": dict(decision_counts),
        "changed_record_count": len(diff),
        "name_raw_changed": sum(r["name_raw_before"] != r["name_raw_after"] for r in diff),
        "name_alias_changed": sum(r["name_alias_before"] != r["name_alias_after"] for r in diff),
        "remaining_bare_ordinal_count": len(remaining_bare),
        "p000064_correct": original["P000064"]["name_raw"] == "Василий Герасимов",
        "p001550_unchanged_for_pipeline_handling": original["P001550"]["name_raw"] == "Август Вильгельм Генрих Меллартек",
        "p001550_pipeline_interpretation": {
            "first_name": "Август Вильгельм Генрих", "patronymic_name": "", "last_name": "Меллартек"
        },
        "hard_checks_passed": (
            len(rows) == len(staged)
            and fields == list(staged[0])
            and not remaining_bare
            and original["P000064"]["name_raw"] == "Василий Герасимов"
        ),
    }
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    (args.qa_dir / "name_raw_normalization_qa.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if not qa["hard_checks_passed"]:
        raise SystemExit("hard QA checks failed")


if __name__ == "__main__":
    main()
