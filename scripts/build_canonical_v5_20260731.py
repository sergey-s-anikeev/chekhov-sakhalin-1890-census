#!/usr/bin/env python3
"""Build and validate canonical Sakhalin release v5_20260731."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V4 = ROOT / "data/processed/clean_sakhalin_1890_ru_v4_20260717.csv"
NAMES = ROOT / (
    "data/staging/name_split_todor_marin_family_20260731/"
    "clean_sakhalin_1890_ru_v4_20260717_names_todor_marin_family_staged.csv"
)
COMMENTS = ROOT / (
    "data/staging/comments_initial_capitalization_item24_20260718_v3/"
    "clean_sakhalin_1890_ru_v4_20260717_item24_comments_staged_v3.csv"
)
OUT = ROOT / "data/processed"
QA = ROOT / "outputs/qa/canonical_v5_20260731"
COMBINED = OUT / "clean_sakhalin_1890_ru_v5_20260731.csv"
DISTRICT_OUTPUTS = {
    "Александровский": OUT / "clean_alexandrovsky_ru_v5_20260731.csv",
    "Тымовский": OUT / "clean_tymovsky_ru_v5_20260731.csv",
    "Корсаковский": OUT / "clean_korsakovsky_ru_v5_20260731.csv",
}
EXPECTED_DISTRICT_COUNTS = {
    "Александровский": 2884,
    "Тымовский": 3242,
    "Корсаковский": 1320,
}
INTEGER_FIELDS = {
    "person_order_in_settlement", "page_number", "age", "age_months", "arrival_year"
}
NORMALIZED_CATEGORY_FIELDS = {
    "legal_status_norm", "sex", "family_status_norm", "religion", "literacy",
    "illness_norm", "origin_place_norm", "occupation_norm", "marriage_status_norm",
    "living_alone_status",
}
NAME_FIELDS = [
    "first_name", "patronymic_name", "last_name",
    "first_name_source", "patronymic_source", "last_name_source",
    "parse_status", "parse_confidence", "parse_rule", "name_order_detected",
    "naming_model", "manual_review_reason", "patronymic_name_proposed", "proposal_rule",
]
ALLOWED_EXISTING_FIELD_CHANGES = {"comments", "name_raw", "name_alias"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def first_alpha_is_lower(value: str) -> bool:
    first = next((char for char in value if char.isalpha()), "")
    return bool(first and first.islower())


def main() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    v4_fields, v4 = read_csv(V4)
    name_fields, names = read_csv(NAMES)
    comment_fields, comments = read_csv(COMMENTS)
    v4_ids = [row["person_id"] for row in v4]
    name_ids = [row["person_id"] for row in names]
    comment_ids = [row["person_id"] for row in comments]
    if not (v4_ids == name_ids == comment_ids):
        raise ValueError("approved inputs do not preserve the canonical person_id order")
    if comment_fields != v4_fields:
        raise ValueError("Item 24 staged schema does not match canonical v4")
    if name_fields != v4_fields + NAME_FIELDS:
        raise ValueError("reviewed name stage does not have the expected 50-column schema")

    v4_by_id = {row["person_id"]: row for row in v4}
    comments_by_id = {row["person_id"]: row for row in comments}

    item24_diffs = []
    item24_unexpected = []
    for row in comments:
        before = v4_by_id[row["person_id"]]
        for field in v4_fields:
            if before[field] != row[field]:
                target = item24_diffs if field == "comments" else item24_unexpected
                target.append({
                    "person_id": row["person_id"], "field": field,
                    "old_value": before[field], "new_value": row[field],
                })
    if len(item24_diffs) != 56 or item24_unexpected:
        raise ValueError(
            f"Item 24 validation failed: comment_changes={len(item24_diffs)}, "
            f"unexpected_changes={len(item24_unexpected)}"
        )

    output = []
    for source in names:
        row = dict(source)
        row["comments"] = comments_by_id[row["person_id"]]["comments"]
        output.append(row)

    write_csv(COMBINED, output, name_fields)
    district_rows = {
        district: [row for row in output if row["district"] == district]
        for district in DISTRICT_OUTPUTS
    }
    for district, path in DISTRICT_OUTPUTS.items():
        write_csv(path, district_rows[district], name_fields)

    cell_diffs = []
    record_diffs = []
    field_counts = Counter()
    unexpected_v4_changes = []
    for after in output:
        before = v4_by_id[after["person_id"]]
        changed_fields = []
        for field in name_fields:
            old_value = before.get(field, "")
            new_value = after[field]
            if old_value == new_value:
                continue
            changed_fields.append(field)
            field_counts[field] += 1
            cell_diffs.append({
                "person_id": after["person_id"], "field": field,
                "old_value": old_value, "new_value": new_value,
            })
            if field in v4_fields and field not in ALLOWED_EXISTING_FIELD_CHANGES:
                unexpected_v4_changes.append({
                    "person_id": after["person_id"], "field": field,
                    "old_value": old_value, "new_value": new_value,
                })
        if changed_fields:
            record_diffs.append({
                "person_id": after["person_id"],
                "changed_field_count": str(len(changed_fields)),
                "changed_fields": "; ".join(changed_fields),
            })
    write_csv(
        QA / "canonical_v5_cell_diff_vs_v4.csv", cell_diffs,
        ["person_id", "field", "old_value", "new_value"],
    )
    write_csv(
        QA / "canonical_v5_record_diff_vs_v4.csv", record_diffs,
        ["person_id", "changed_field_count", "changed_fields"],
    )
    write_csv(
        QA / "canonical_v5_field_change_summary_vs_v4.csv",
        [{"field": field, "changed_records": str(count)} for field, count in sorted(field_counts.items())],
        ["field", "changed_records"],
    )
    write_csv(
        QA / "canonical_v5_schema_diff_vs_v4.csv",
        [{"change": "added", "field": field} for field in NAME_FIELDS],
        ["change", "field"],
    )
    write_csv(
        QA / "canonical_v5_unexpected_v4_field_changes.csv", unexpected_v4_changes,
        ["person_id", "field", "old_value", "new_value"],
    )
    write_csv(
        QA / "canonical_v5_item24_comment_diff.csv", item24_diffs,
        ["person_id", "field", "old_value", "new_value"],
    )

    integer_exceptions = [
        {"person_id": row["person_id"], "field": field, "value": row[field]}
        for row in output for field in INTEGER_FIELDS
        if row[field] and not re.fullmatch(r"\d+", row[field])
    ]
    write_csv(
        QA / "canonical_v5_integer_format_exceptions.csv", integer_exceptions,
        ["person_id", "field", "value"],
    )
    identifier_exceptions = []
    for index, row in enumerate(output, 1):
        if row["person_id"] != f"P{index:06d}":
            identifier_exceptions.append({
                "person_id": row["person_id"], "field": "person_id",
                "value": row["person_id"], "issue": "global sequence",
            })
        if not re.fullmatch(r"\d{2}", row["settlement_order"]):
            identifier_exceptions.append({
                "person_id": row["person_id"], "field": "settlement_order",
                "value": row["settlement_order"], "issue": "not two digits",
            })
        if not re.fullmatch(r"\d+-\d{2}-[^-]+-\d{4}", row["source_position_id"]):
            identifier_exceptions.append({
                "person_id": row["person_id"], "field": "source_position_id",
                "value": row["source_position_id"], "issue": "format",
            })
    write_csv(
        QA / "canonical_v5_identifier_format_exceptions.csv", identifier_exceptions,
        ["person_id", "field", "value", "issue"],
    )
    lowercase_exceptions = [
        {"person_id": row["person_id"], "field": field, "value": part.strip()}
        for row in output for field in NORMALIZED_CATEGORY_FIELDS
        for part in row[field].split(";")
        if part.strip() and first_alpha_is_lower(part.strip())
    ]
    write_csv(
        QA / "canonical_v5_lowercase_category_exceptions.csv", lowercase_exceptions,
        ["person_id", "field", "value"],
    )

    component_exceptions = []
    for row in output:
        for component, source_field in (
            ("first_name", "first_name_source"),
            ("patronymic_name", "patronymic_source"),
            ("last_name", "last_name_source"),
        ):
            if bool(row[component]) != bool(row[source_field]):
                component_exceptions.append({
                    "person_id": row["person_id"], "check": "component_source_mismatch",
                    "field": component, "value": row[component], "detail": row[source_field],
                })
        if row["parse_status"] != "observed":
            component_exceptions.append({
                "person_id": row["person_id"], "check": "parse_status_not_observed",
                "field": "parse_status", "value": row["parse_status"], "detail": "",
            })
        if any(row[field].startswith("inferred_") for field in (
            "first_name_source", "patronymic_source", "last_name_source"
        )):
            component_exceptions.append({
                "person_id": row["person_id"], "check": "forbidden_family_inference",
                "field": "name_source", "value": "", "detail": "",
            })
        if row["patronymic_name_proposed"] or row["proposal_rule"]:
            component_exceptions.append({
                "person_id": row["person_id"], "check": "unresolved_name_proposal",
                "field": "patronymic_name_proposed", "value": row["patronymic_name_proposed"],
                "detail": row["proposal_rule"],
            })
    write_csv(
        QA / "canonical_v5_name_component_exceptions.csv", component_exceptions,
        ["person_id", "check", "field", "value", "detail"],
    )

    district_counts = Counter(row["district"] for row in output)
    ordered_concat = [row for district in DISTRICT_OUTPUTS for row in district_rows[district]]
    age_month_consistency = all(
        not row["age_months"] or int(row["age"]) == int(row["age_months"]) // 12
        for row in output
    )
    checks = {
        "record_count_7446": len(output) == 7446,
        "field_count_50": len(name_fields) == 50,
        "schema_is_v4_plus_14_name_fields": name_fields == v4_fields + NAME_FIELDS,
        "person_ids_unique": len(set(v4_ids)) == len(output),
        "name_raw_nonblank": all(row["name_raw"] for row in output),
        "source_position_ids_nonblank_unique": all(row["source_position_id"] for row in output)
        and len({row["source_position_id"] for row in output}) == len(output),
        "identifier_order_preserved": v4_ids == [row["person_id"] for row in output],
        "district_counts_match": dict(district_counts) == EXPECTED_DISTRICT_COUNTS,
        "ordered_district_concatenation": ordered_concat == output,
        "written_district_slices_match": all(
            read_csv(path)[1] == district_rows[district]
            for district, path in DISTRICT_OUTPUTS.items()
        ),
        "combined_matches_written_file": read_csv(COMBINED)[1] == output,
        "item24_comment_changes_56": len(item24_diffs) == 56,
        "item24_changes_comments_only": not item24_unexpected,
        "existing_v4_fields_restricted_to_approved_changes": not unexpected_v4_changes,
        "integer_or_blank_formats_valid": not integer_exceptions,
        "identifier_formats_valid": not identifier_exceptions,
        "arrival_year_range_valid": all(
            not row["arrival_year"] or 1865 <= int(row["arrival_year"]) <= 1890 for row in output
        ),
        "age_range_valid": all(not row["age"] or 0 <= int(row["age"]) <= 120 for row in output),
        "age_months_range_valid": all(
            not row["age_months"] or 0 <= int(row["age_months"]) <= 35 for row in output
        ),
        "age_and_age_months_consistent": age_month_consistency,
        "no_blank_age_months_for_age_0_1_2": all(
            row["age_months"] for row in output if row["age"] in {"0", "1", "2"}
        ),
        "allowance_values_valid": {row["allowance_status"] for row in output} <= {"", "TRUE", "FALSE"},
        "no_lowercase_normalized_categories": not lowercase_exceptions,
        "all_name_components_resolved_with_provenance": not component_exceptions,
    }
    report = {
        "release": "v5_20260731",
        "base_canonical": str(V4.relative_to(ROOT)).replace("\\", "/"),
        "reviewed_name_stage": str(NAMES.relative_to(ROOT)).replace("\\", "/"),
        "approved_comments_stage": str(COMMENTS.relative_to(ROOT)).replace("\\", "/"),
        "record_count": len(output),
        "field_count": len(name_fields),
        "fields": name_fields,
        "district_counts": dict(district_counts),
        "changed_records_vs_v4": len(record_diffs),
        "changed_cells_vs_v4": len(cell_diffs),
        "field_change_counts_vs_v4": dict(sorted(field_counts.items())),
        "checks": checks,
    }
    report_path = QA / "canonical_v5_qa_report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_csv(
        QA / "canonical_v5_hashes.csv",
        [
            {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path)}
            for path in [*DISTRICT_OUTPUTS.values(), COMBINED]
        ],
        ["path", "sha256"],
    )
    if not all(checks.values()):
        raise SystemExit(
            "QA failed: " + ", ".join(name for name, passed in checks.items() if not passed)
        )
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
