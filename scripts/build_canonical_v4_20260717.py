from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "data/processed/clean_sakhalin_1890_ru_v3_20260712.csv"
LATEST = ROOT / "data/staging/age_months_whole_year_item23_20260717/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_items21_22_23_staged.csv"
COMMENTS_BASE = ROOT / "data/staging/comments_numeric_cleanup_20260717/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_staged.csv"
COMMENTS_REVIEWED = ROOT / "data/staging/comments_owner_feedback_20260717/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_reviewed_staged.csv"
ALIASES_REVIEWED = ROOT / "data/staging/name_alias_add_20260717/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_comments_item21_alias_staged.csv"
SEX_STAGE = ROOT / "data/staging/sex_item3_20260712/clean_sakhalin_1890_ru_sex_item3_v1.csv"
LEGAL_MAPPING = ROOT / "data/review/legal_status_item17_20260712/legal_status_norm_approved_mapping.csv"

OUT = ROOT / "data/processed"
QA_DIR = ROOT / "outputs/qa/canonical_v4_20260717"
COMBINED = OUT / "clean_sakhalin_1890_ru_v4_20260717.csv"
DISTRICT_OUTPUTS = {
    "Александровский": OUT / "clean_alexandrovsky_ru_v4_20260717.csv",
    "Тымовский": OUT / "clean_tymovsky_ru_v4_20260717.csv",
    "Корсаковский": OUT / "clean_korsakovsky_ru_v4_20260717.csv",
}
EXPECTED_DISTRICT_COUNTS = {"Александровский": 2884, "Тымовский": 3242, "Корсаковский": 1320}

TEXT_FIELDS = {
    "person_id", "source_position_id", "district_code", "district", "settlement_order", "settlement",
    "household_id", "household_type", "household_details", "legal_status", "legal_status_norm",
    "name_raw", "name_alias", "sex", "sex_evidence", "family_status", "family_status_norm",
    "religion", "origin_place", "origin_place_norm", "occupation", "occupation_norm", "literacy",
    "marriage_status", "marriage_status_norm", "living_alone_status", "allowance_status", "illness",
    "illness_norm", "comments", "notes_raw",
}
INTEGER_OR_BLANK_FIELDS = {"person_order_in_settlement", "page_number", "age", "age_months", "arrival_year"}
NORMALIZED_CATEGORY_FIELDS = {
    "legal_status_norm", "sex", "family_status_norm", "religion", "literacy", "illness_norm",
    "origin_place_norm", "occupation_norm", "marriage_status_norm", "living_alone_status",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def indexed(path: Path) -> dict[str, dict[str, str]]:
    rows = read_rows(path)
    result = {row["person_id"]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"Duplicate person_id in {path}")
    return result


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
    QA_DIR.mkdir(parents=True, exist_ok=True)
    v3 = read_rows(V3)
    latest = read_rows(LATEST)
    fields = list(latest[0])
    comments_base = indexed(COMMENTS_BASE)
    comments_reviewed = indexed(COMMENTS_REVIEWED)
    aliases_reviewed = indexed(ALIASES_REVIEWED)
    sex_stage = indexed(SEX_STAGE)
    v2_by_id = indexed(ROOT / "data/processed/clean_sakhalin_1890_ru_v2_20260711.csv")

    expected_ids = [row["person_id"] for row in latest]
    expected_set = set(expected_ids)
    for label, source in (
        ("comments_base", comments_base), ("comments_reviewed", comments_reviewed),
        ("aliases_reviewed", aliases_reviewed), ("sex_stage", sex_stage),
    ):
        if set(source) != expected_set:
            raise ValueError(f"Person-id mismatch in {label}")

    comment_changes = {
        pid: row["comments"]
        for pid, row in comments_reviewed.items()
        if row["comments"] != comments_base[pid]["comments"]
    }
    comment_alias_changes = {
        pid: row["name_alias"]
        for pid, row in comments_reviewed.items()
        if row["name_alias"] != comments_base[pid]["name_alias"]
    }
    alias_changes = {
        pid: row["name_alias"]
        for pid, row in aliases_reviewed.items()
        if row["name_alias"] != comments_base[pid]["name_alias"]
    }
    alias_conflicts = {
        pid: (comment_alias_changes[pid], alias_changes[pid])
        for pid in set(comment_alias_changes) & set(alias_changes)
        if comment_alias_changes[pid] != alias_changes[pid]
    }
    if alias_conflicts:
        raise ValueError(f"Conflicting approved alias branches: {alias_conflicts}")
    merged_alias_changes = {**comment_alias_changes, **alias_changes}

    output = []
    for source in latest:
        row = dict(source)
        pid = row["person_id"]
        if pid in comment_changes:
            row["comments"] = comment_changes[pid]
        if pid in merged_alias_changes:
            row["name_alias"] = merged_alias_changes[pid]
        output.append(row)

    write_csv(COMBINED, output, fields)
    district_rows = {district: [row for row in output if row["district"] == district] for district in DISTRICT_OUTPUTS}
    for district, path in DISTRICT_OUTPUTS.items():
        write_csv(path, district_rows[district], fields)

    # Complete v3-to-v4 cell and record diffs.
    v3_by_id = {row["person_id"]: row for row in v3}
    cell_diffs = []
    record_summary = []
    field_counts = Counter()
    for after in output:
        before = v3_by_id[after["person_id"]]
        changed_fields = []
        for field in sorted(set(before) | set(after)):
            old, new = before.get(field, ""), after.get(field, "")
            if old != new:
                changed_fields.append(field)
                field_counts[field] += 1
                cell_diffs.append({"person_id": after["person_id"], "field": field, "old_value": old, "new_value": new})
        if changed_fields:
            record_summary.append(
                {"person_id": after["person_id"], "changed_field_count": str(len(changed_fields)), "changed_fields": "; ".join(changed_fields)}
            )
    write_csv(QA_DIR / "canonical_v4_cell_diff_vs_v3.csv", cell_diffs, ["person_id", "field", "old_value", "new_value"])
    write_csv(QA_DIR / "canonical_v4_record_diff_vs_v3.csv", record_summary, ["person_id", "changed_field_count", "changed_fields"])
    write_csv(
        QA_DIR / "canonical_v4_field_change_summary_vs_v3.csv",
        [{"field": field, "changed_records": str(count)} for field, count in sorted(field_counts.items())],
        ["field", "changed_records"],
    )
    v3_fields = list(v3[0])
    write_csv(
        QA_DIR / "canonical_v4_schema_diff_vs_v3.csv",
        ([{"change": "removed", "field": field} for field in v3_fields if field not in fields]
         + [{"change": "added", "field": field} for field in fields if field not in v3_fields]),
        ["change", "field"],
    )

    # Type and format checks.
    integer_exceptions = [
        {"person_id": row["person_id"], "field": field, "value": row[field]}
        for row in output for field in INTEGER_OR_BLANK_FIELDS
        if row[field] and not re.fullmatch(r"\d+", row[field])
    ]
    write_csv(QA_DIR / "canonical_v4_integer_format_exceptions.csv", integer_exceptions, ["person_id", "field", "value"])
    identifier_exceptions = []
    for index, row in enumerate(output, 1):
        if row["person_id"] != f"P{index:06d}":
            identifier_exceptions.append({"person_id": row["person_id"], "field": "person_id", "value": row["person_id"], "issue": "global sequence"})
        if not re.fullmatch(r"\d{2}", row["settlement_order"]):
            identifier_exceptions.append({"person_id": row["person_id"], "field": "settlement_order", "value": row["settlement_order"], "issue": "not two digits"})
        if not re.fullmatch(r"\d+-\d{2}-[^-]+-\d{4}", row["source_position_id"]):
            identifier_exceptions.append({"person_id": row["person_id"], "field": "source_position_id", "value": row["source_position_id"], "issue": "format"})
    write_csv(QA_DIR / "canonical_v4_identifier_format_exceptions.csv", identifier_exceptions, ["person_id", "field", "value", "issue"])

    lowercase = [
        {"person_id": row["person_id"], "field": field, "value": part.strip()}
        for row in output for field in NORMALIZED_CATEGORY_FIELDS for part in row[field].split(";")
        if part.strip() and first_alpha_is_lower(part.strip())
    ]
    write_csv(QA_DIR / "canonical_v4_lowercase_category_exceptions.csv", lowercase, ["person_id", "field", "value"])

    # Dependency synchronization for the 10 Item 3 legal-status corrections.
    legal_rows = read_rows(LEGAL_MAPPING)
    legal_map = {row["legal_status"]: row["owner_legal_status_norm"] for row in legal_rows}
    for value in list(legal_map.values()):
        if value:
            legal_map.setdefault(value, value)
    corrected_item3_ids = [pid for pid in expected_ids if sex_stage[pid]["legal_status"] != v2_by_id[pid]["legal_status"]]
    dependency_exceptions = []
    output_by_id = {row["person_id"]: row for row in output}
    for pid in corrected_item3_ids:
        row = output_by_id[pid]
        expected_legal = sex_stage[pid]["legal_status"]
        expected_norm = legal_map.get(expected_legal, "")
        if row["legal_status"] != expected_legal or row["legal_status_norm"] != expected_norm:
            dependency_exceptions.append(
                {"person_id": pid, "legal_status": row["legal_status"], "expected_legal_status": expected_legal,
                 "legal_status_norm": row["legal_status_norm"], "expected_legal_status_norm": expected_norm}
            )
    write_csv(
        QA_DIR / "canonical_v4_item3_dependency_exceptions.csv", dependency_exceptions,
        ["person_id", "legal_status", "expected_legal_status", "legal_status_norm", "expected_legal_status_norm"],
    )

    # Cross-field gender consistency.
    female_tokens = ("Женщина", "Жена", "Дочь", "Поселка", "Ссыльнокаторжная", "Крестьянка", "Солдатка")
    male_tokens = ("Сын", "Поселенец", "Ссыльнокаторжный", "Крестьянин", "Рядовой", "Офицер")
    gender_conflicts = []
    for row in output:
        evidence = " | ".join((row["legal_status"], row["legal_status_norm"], row["family_status"], row["family_status_norm"]))
        female = any(token.casefold() in evidence.casefold() for token in female_tokens)
        male = any(token.casefold() in evidence.casefold() for token in male_tokens)
        if female != male:
            implied = "Женский" if female else "Мужской"
            if row["sex"] != implied:
                gender_conflicts.append(
                    {"person_id": row["person_id"], "sex": row["sex"], "implied_sex": implied,
                     "legal_status": row["legal_status"], "legal_status_norm": row["legal_status_norm"],
                     "family_status": row["family_status"], "family_status_norm": row["family_status_norm"]}
                )
    write_csv(
        QA_DIR / "canonical_v4_gender_conflicts.csv", gender_conflicts,
        ["person_id", "sex", "implied_sex", "legal_status", "legal_status_norm", "family_status", "family_status_norm"],
    )

    district_counts = Counter(row["district"] for row in output)
    ordered_concat = [row for district in DISTRICT_OUTPUTS for row in district_rows[district]]
    allowance_values = {row["allowance_status"] for row in output}
    age_month_consistency = all(
        not row["age_months"] or int(row["age"]) == int(row["age_months"]) // 12
        for row in output
    )
    checks = {
        "record_count_7446": len(output) == 7446,
        "field_count_36": len(fields) == 36,
        "expected_schema_fields": set(fields) == TEXT_FIELDS | INTEGER_OR_BLANK_FIELDS,
        "person_ids_unique": len(set(expected_ids)) == len(output),
        "source_position_ids_nonblank_unique": all(row["source_position_id"] for row in output) and len({row["source_position_id"] for row in output}) == len(output),
        "identifier_order_preserved": expected_ids == [row["person_id"] for row in output],
        "district_counts_match": dict(district_counts) == EXPECTED_DISTRICT_COUNTS,
        "ordered_district_concatenation": ordered_concat == output,
        "written_district_slices_match": all(read_rows(path) == district_rows[district] for district, path in DISTRICT_OUTPUTS.items()),
        "combined_matches_written_file": read_rows(COMBINED) == output,
        "integer_or_blank_formats_valid": not integer_exceptions,
        "identifier_formats_valid": not identifier_exceptions,
        "arrival_year_range_valid": all(not row["arrival_year"] or 1865 <= int(row["arrival_year"]) <= 1890 for row in output),
        "age_range_valid": all(not row["age"] or 0 <= int(row["age"]) <= 120 for row in output),
        "age_months_range_valid": all(not row["age_months"] or 0 <= int(row["age_months"]) <= 35 for row in output),
        "age_and_age_months_consistent": age_month_consistency,
        "no_blank_age_months_for_age_0_1_2": all(row["age_months"] for row in output if row["age"] in {"0", "1", "2"}),
        "allowance_values_valid": allowance_values <= {"", "TRUE", "FALSE"},
        "no_lowercase_normalized_categories": not lowercase,
        "item3_corrected_record_count_10": len(corrected_item3_ids) == 10,
        "item3_dependencies_synchronized": not dependency_exceptions,
        "no_gender_conflicts": not gender_conflicts,
        "comment_feedback_count_274": len(comment_changes) == 274,
        "merged_late_alias_change_count_18": len(merged_alias_changes) == 18,
    }
    report = {
        "release": "v4_20260717",
        "base_canonical": str(V3.relative_to(ROOT)),
        "latest_staged_input": str(LATEST.relative_to(ROOT)),
        "record_count": len(output),
        "field_count": len(fields),
        "fields": fields,
        "district_counts": dict(district_counts),
        "changed_records_vs_v3": len(record_summary),
        "changed_cells_vs_v3": len(cell_diffs),
        "field_change_counts_vs_v3": dict(sorted(field_counts.items())),
        "approved_branch_merge": {
            "comment_changes": len(comment_changes),
            "comment_branch_alias_changes": len(comment_alias_changes),
            "additional_alias_changes": len(alias_changes),
            "unique_merged_alias_changes": len(merged_alias_changes),
            "alias_conflicts": alias_conflicts,
        },
        "checks": checks,
    }
    (QA_DIR / "canonical_v4_qa_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(
        QA_DIR / "canonical_v4_hashes.csv",
        [{"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path)} for path in [*DISTRICT_OUTPUTS.values(), COMBINED]],
        ["path", "sha256"],
    )
    if not all(checks.values()):
        raise SystemExit(f"QA failed: {[name for name, passed in checks.items() if not passed]}")


if __name__ == "__main__":
    main()
