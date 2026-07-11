#!/usr/bin/env python3
"""Apply approved Item 1 name decisions to a versioned staged candidate."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


CANONICAL_COLUMNS = [
    "person_id",
    "source_position_id",
    "district_code",
    "district",
    "settlement_order",
    "settlement",
    "person_order_in_settlement",
    "page_number",
    "household_number",
    "legal_status",
    "name_raw",
    "family_status",
    "age",
    "religion",
    "origin_place",
    "arrival_year",
    "occupation",
    "literacy",
    "marriage_status",
    "allowance_status",
    "illness",
    "comments",
    "notes_raw",
]
CANDIDATE_COLUMNS = CANONICAL_COLUMNS.copy()
CANDIDATE_COLUMNS.insert(CANDIDATE_COLUMNS.index("name_raw") + 1, "name_alias")
DECISION_COLUMNS = [
    "person_id",
    "source_position_id",
    "current_name_raw",
    "proposed_name_raw",
    "proposed_name_alias",
    "proposed_name_note",
    "current_family_status",
    "proposed_family_status",
    "proposed_destination_field",
    "proposed_destination_value",
    "proposal_basis",
    "proposal_confidence",
    "owner_decision",
    "reviewer_notes",
]
DIFF_COLUMNS = [
    "person_id",
    "source_position_id",
    "field",
    "canonical_value",
    "staged_value",
    "owner_decision",
    "reviewer_notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", default="data/processed/clean_sakhalin_1890_ru.csv"
    )
    parser.add_argument(
        "--decisions",
        default=(
            "data/review/name_raw_item1_20260710/owner_response/"
            "name_raw_approved_decisions_20260711.csv"
        ),
    )
    parser.add_argument(
        "--output",
        default=(
            "data/staging/name_raw_item1_20260711/"
            "clean_sakhalin_1890_ru_item1_name_v1.csv"
        ),
    )
    parser.add_argument(
        "--qa-dir", default="outputs/qa/name_raw_item1_20260711_approved"
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def append_comment(existing: str, extra: str) -> str:
    existing = existing.strip()
    extra = extra.strip()
    if not extra:
        return existing
    if extra.casefold() in existing.casefold():
        return existing
    if not existing:
        return extra
    return f"{existing}; {extra}"


def diff_row(
    source: dict[str, str],
    field: str,
    old: str,
    new: str,
    decision: dict[str, str],
) -> dict[str, str]:
    return {
        "person_id": source["person_id"],
        "source_position_id": source["source_position_id"],
        "field": field,
        "canonical_value": old,
        "staged_value": new,
        "owner_decision": decision["owner_decision"],
        "reviewer_notes": decision["reviewer_notes"],
    }


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    decision_path = Path(args.decisions)
    output_path = Path(args.output)
    qa_dir = Path(args.qa_dir)
    diff_path = qa_dir / "name_raw_item1_approved_diff.csv"
    qa_json_path = qa_dir / "qa_name_raw_item1_approved_report.json"
    qa_md_path = qa_dir / "qa_name_raw_item1_approved_report.md"
    manifest_path = qa_dir / "name_raw_item1_approved_artifact_manifest.csv"

    input_hash_before = sha256(input_path)
    input_headers, source_rows = read_csv(input_path)
    decision_headers, decisions = read_csv(decision_path)
    if input_headers != CANONICAL_COLUMNS:
        raise SystemExit(f"Unexpected canonical schema: {input_headers}")
    if decision_headers != DECISION_COLUMNS:
        raise SystemExit(f"Unexpected decision schema: {decision_headers}")

    source_by_id = {row["person_id"]: row for row in source_rows}
    if len(source_by_id) != len(source_rows):
        raise SystemExit("Canonical person_id values are not unique.")
    decision_by_id = {row["person_id"]: row for row in decisions}
    if len(decision_by_id) != len(decisions):
        raise SystemExit("Decision person_id values are not unique.")

    allowed_decisions = {"approve", "modify", "reject", "defer"}
    unsupported_destination_fields = sorted(
        {
            row["proposed_destination_field"]
            for row in decisions
            if row["proposed_destination_field"]
            and row["proposed_destination_field"] != "comments"
        }
    )
    if unsupported_destination_fields:
        raise SystemExit(
            f"Unsupported destination fields: {unsupported_destination_fields}"
        )

    for decision in decisions:
        person_id = decision["person_id"]
        if person_id not in source_by_id:
            raise SystemExit(f"Decision ID not found in canonical data: {person_id}")
        source = source_by_id[person_id]
        if source["source_position_id"] != decision["source_position_id"]:
            raise SystemExit(f"source_position_id mismatch for {person_id}")
        if source["name_raw"] != decision["current_name_raw"]:
            raise SystemExit(f"current_name_raw mismatch for {person_id}")
        if source["family_status"] != decision["current_family_status"]:
            raise SystemExit(f"current_family_status mismatch for {person_id}")
        normalized_decision = decision["owner_decision"].casefold()
        if normalized_decision not in allowed_decisions:
            raise SystemExit(f"Invalid owner_decision for {person_id}")
        decision["owner_decision"] = normalized_decision

    staged_rows: list[dict[str, str]] = []
    diff_rows: list[dict[str, str]] = []
    changed_record_ids: set[str] = set()
    applied_decision_ids: set[str] = set()

    for source in source_rows:
        staged = source.copy()
        staged["name_alias"] = ""
        decision = decision_by_id.get(source["person_id"])
        if decision and decision["owner_decision"] in {"approve", "modify"}:
            applied_decision_ids.add(source["person_id"])

            new_name = decision["proposed_name_raw"].strip()
            if not new_name:
                raise SystemExit(f"Approved blank proposed name: {source['person_id']}")
            if new_name != source["name_raw"]:
                staged["name_raw"] = new_name
                diff_rows.append(
                    diff_row(source, "name_raw", source["name_raw"], new_name, decision)
                )

            new_alias = decision["proposed_name_alias"].strip()
            if new_alias:
                staged["name_alias"] = new_alias
                diff_rows.append(
                    diff_row(source, "name_alias", "", new_alias, decision)
                )

            new_family_status = decision["proposed_family_status"].strip()
            if new_family_status != source["family_status"]:
                staged["family_status"] = new_family_status
                diff_rows.append(
                    diff_row(
                        source,
                        "family_status",
                        source["family_status"],
                        new_family_status,
                        decision,
                    )
                )

            destination_field = decision["proposed_destination_field"].strip()
            destination_value = decision["proposed_destination_value"].strip()
            if destination_field == "comments" and destination_value:
                new_comments = append_comment(source["comments"], destination_value)
                if new_comments != source["comments"]:
                    staged["comments"] = new_comments
                    diff_rows.append(
                        diff_row(
                            source,
                            "comments",
                            source["comments"],
                            new_comments,
                            decision,
                        )
                    )

        if decision and decision["owner_decision"] in {"reject", "defer"}:
            staged["name_alias"] = ""

        if any(
            staged.get(field, "") != source.get(field, "")
            for field in CANDIDATE_COLUMNS
        ):
            changed_record_ids.add(source["person_id"])
        staged_rows.append(staged)

    write_csv(output_path, CANDIDATE_COLUMNS, staged_rows)
    write_csv(diff_path, DIFF_COLUMNS, diff_rows)

    output_headers, output_rows = read_csv(output_path)
    input_hash_after = sha256(input_path)
    output_by_id = {row["person_id"]: row for row in output_rows}
    allowed_changed_fields = {"name_raw", "name_alias", "family_status", "comments"}
    actual_changed_fields: set[str] = set()
    for source, staged in zip(source_rows, output_rows, strict=True):
        for field in CANDIDATE_COLUMNS:
            if staged.get(field, "") != source.get(field, ""):
                actual_changed_fields.add(field)

    residual_role_leaks = [
        row["person_id"]
        for row in output_rows
        if re.search(
            r"\s(?:жена|незаконнорожденный\s+сын)$",
            row["name_raw"],
            flags=re.IGNORECASE,
        )
    ]
    residual_age_text = [
        row["person_id"]
        for row in output_rows
        if re.search(r"\b\d{1,3}\s+лет\b", row["name_raw"], flags=re.IGNORECASE)
    ]
    intentionally_preserved_descriptions = [
        row["person_id"]
        for row in output_rows
        if row["name_raw"] in {"Некрещеная", "Человек неизвестного звания"}
    ]
    decision_application_mismatches: list[dict[str, str]] = []
    for decision in decisions:
        staged = output_by_id[decision["person_id"]]
        if decision["owner_decision"] in {"approve", "modify"}:
            expected_values = {
                "name_raw": decision["proposed_name_raw"],
                "name_alias": decision["proposed_name_alias"],
                "family_status": decision["proposed_family_status"],
            }
            for field, expected_value in expected_values.items():
                if staged[field] != expected_value:
                    decision_application_mismatches.append(
                        {
                            "person_id": decision["person_id"],
                            "field": field,
                            "expected": expected_value,
                            "actual": staged[field],
                        }
                    )
            if (
                decision["proposed_destination_field"] == "comments"
                and decision["proposed_destination_value"]
                and decision["proposed_destination_value"].casefold()
                not in staged["comments"].casefold()
            ):
                decision_application_mismatches.append(
                    {
                        "person_id": decision["person_id"],
                        "field": "comments",
                        "expected": decision["proposed_destination_value"],
                        "actual": staged["comments"],
                    }
                )

    decision_counts = Counter(row["owner_decision"] for row in decisions)
    diff_counts = Counter(row["field"] for row in diff_rows)
    qa = {
        "item": "1. Verify name_raw",
        "status": "owner_approved_and_staged",
        "canonical_input": str(input_path).replace("\\", "/"),
        "canonical_sha256_before": input_hash_before,
        "canonical_sha256_after": input_hash_after,
        "canonical_unchanged": input_hash_before == input_hash_after,
        "decision_input": str(decision_path).replace("\\", "/"),
        "decision_input_sha256": sha256(decision_path),
        "decision_record_count": len(decisions),
        "decision_counts": dict(sorted(decision_counts.items())),
        "applied_decision_count": len(applied_decision_ids),
        "decision_application_mismatch_count": len(
            decision_application_mismatches
        ),
        "decision_application_mismatches": decision_application_mismatches,
        "staged_output": str(output_path).replace("\\", "/"),
        "staged_output_sha256": sha256(output_path),
        "staged_record_count": len(output_rows),
        "staged_schema": output_headers,
        "staged_schema_matches_expected": output_headers == CANDIDATE_COLUMNS,
        "name_alias_position_valid": output_headers.index("name_alias")
        == output_headers.index("name_raw") + 1,
        "person_id_unique": len(output_by_id) == len(output_rows),
        "source_position_id_unique": len(
            {row["source_position_id"] for row in output_rows}
        )
        == len(output_rows),
        "person_id_order_unchanged": [row["person_id"] for row in source_rows]
        == [row["person_id"] for row in output_rows],
        "source_position_id_order_unchanged": [
            row["source_position_id"] for row in source_rows
        ]
        == [row["source_position_id"] for row in output_rows],
        "district_order_unchanged": [row["district"] for row in source_rows]
        == [row["district"] for row in output_rows],
        "blank_name_raw_count": sum(not row["name_raw"].strip() for row in output_rows),
        "changed_record_count": len(changed_record_ids),
        "field_diff_count": len(diff_rows),
        "field_diff_counts": dict(sorted(diff_counts.items())),
        "populated_name_alias_count": sum(
            bool(row["name_alias"].strip()) for row in output_rows
        ),
        "actual_changed_fields": sorted(actual_changed_fields),
        "only_allowed_fields_changed": actual_changed_fields <= allowed_changed_fields,
        "residual_role_leak_ids": residual_role_leaks,
        "residual_age_text_ids": residual_age_text,
        "intentionally_preserved_description_ids": intentionally_preserved_descriptions,
        "angle_markup_count": sum(
            bool(re.search(r"<[^>]*>", value or ""))
            for row in output_rows
            for value in row.values()
        ),
        "square_markup_count": sum(
            bool(re.search(r"\[[^\]]*\]", value or ""))
            for row in output_rows
            for value in row.values()
        ),
        "notes": [
            "The staged candidate adds name_alias immediately after name_raw.",
            "Four source-derived descriptions remain in name_raw because no personal name is recoverable from the current evidence.",
            "The canonical datasets and canonical manifest were not modified.",
        ],
    }

    qa_dir.mkdir(parents=True, exist_ok=True)
    qa_json_path.write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    qa_md_lines = [
        "# Item 1 Final QA: Approved `name_raw` Decisions",
        "",
        "## Status",
        "",
        "Owner decisions have been applied to a versioned staged candidate. Canonical datasets remain unchanged.",
        "",
        "## Owner Decisions",
        "",
        f"- Decision records: **{qa['decision_record_count']}**",
        f"- Approved: **{decision_counts.get('approve', 0)}**",
        f"- Modified: **{decision_counts.get('modify', 0)}**",
        f"- Rejected: **{decision_counts.get('reject', 0)}**",
        f"- Deferred: **{decision_counts.get('defer', 0)}**",
        f"- Decision application mismatches: **{qa['decision_application_mismatch_count']}**",
        "",
        "## Applied Changes",
        "",
        f"- Changed records: **{qa['changed_record_count']}**",
        f"- Field-level differences: **{qa['field_diff_count']}**",
        f"- `name_raw` changes: **{diff_counts.get('name_raw', 0)}**",
        f"- Populated `name_alias` values: **{qa['populated_name_alias_count']}**",
        f"- `family_status` changes: **{diff_counts.get('family_status', 0)}**",
        f"- `comments` changes: **{diff_counts.get('comments', 0)}**",
        "",
        "## Structural QA",
        "",
        f"- Staged records: **{qa['staged_record_count']:,}**",
        f"- Expected 24-column schema: **{qa['staged_schema_matches_expected']}**",
        f"- `name_alias` immediately follows `name_raw`: **{qa['name_alias_position_valid']}**",
        f"- Unique `person_id`: **{qa['person_id_unique']}**",
        f"- Unique `source_position_id`: **{qa['source_position_id_unique']}**",
        f"- Identifier and row order unchanged: **{qa['person_id_order_unchanged'] and qa['source_position_id_order_unchanged']}**",
        f"- District ordering unchanged: **{qa['district_order_unchanged']}**",
        f"- Blank `name_raw`: **{qa['blank_name_raw_count']}**",
        f"- Only approved fields changed: **{qa['only_allowed_fields_changed']}**",
        f"- Residual role leakage: **{len(residual_role_leaks)}**",
        f"- Residual age text: **{len(residual_age_text)}**",
        f"- Angle-bracket markup: **{qa['angle_markup_count']}**",
        f"- Square-bracket markup: **{qa['square_markup_count']}**",
        "",
        "## Preserved Source Descriptions",
        "",
        "The following records remain unchanged because the reviewed field contains no recoverable personal name: "
        + ", ".join(f"`{person_id}`" for person_id in intentionally_preserved_descriptions)
        + ".",
        "",
        "## Canonical Safeguard",
        "",
        f"- Canonical SHA-256 unchanged: **{qa['canonical_unchanged']}**",
        "- No canonical dataset or canonical manifest entry was modified.",
    ]
    qa_md_path.write_text("\n".join(qa_md_lines) + "\n", encoding="utf-8")

    manifest_inputs = [
        (input_path, "canonical_input"),
        (decision_path, "approved_decision_input"),
        (Path(__file__), "application_script"),
        (output_path, "staged_candidate"),
        (diff_path, "record_level_diff"),
        (qa_json_path, "machine_readable_qa_report"),
        (qa_md_path, "human_readable_qa_report"),
    ]
    manifest_rows = []
    for artifact_path, role in manifest_inputs:
        try:
            display_path = artifact_path.resolve().relative_to(Path.cwd().resolve())
        except ValueError:
            display_path = artifact_path
        manifest_rows.append(
            {
                "path": str(display_path).replace("\\", "/"),
                "role": role,
                "sha256": sha256(artifact_path),
                "bytes": artifact_path.stat().st_size,
            }
        )
    write_csv(manifest_path, ["path", "role", "sha256", "bytes"], manifest_rows)

    print(json.dumps(qa, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
