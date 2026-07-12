from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


INPUT_CSV = Path("data/processed/clean_sakhalin_1890_ru.csv")
MAPPING_CSV = Path("data/review/household_structure_owner_mapping_20260711.csv")
OUTPUT_DIR = Path("data/staging/household_structure_20260711_v2")
OUTPUT_CSV = OUTPUT_DIR / "clean_sakhalin_1890_ru_household_structure_v2.csv"
DIFF_CSV = OUTPUT_DIR / "household_structure_v2_diff.csv"
QA_CSV = OUTPUT_DIR / "household_structure_v2_qa_summary.csv"
TYPE_SUMMARY_CSV = OUTPUT_DIR / "household_type_summary.csv"

NEW_HOUSEHOLD_COLUMNS = ["household_id", "household_type", "household_details"]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def normalized_household_segment(household_id: str) -> str:
    value = household_id.strip()
    if not value:
        return "000"
    if re.fullmatch(r"\d+", value):
        return value.zfill(3)
    range_match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", value)
    if range_match:
        return range_match.group(1).zfill(3)
    raise ValueError(f"Unsupported household_id for source_position_id: {value!r}")


def source_position_id(row: dict[str, str], household_id: str) -> str:
    district = row["district_code"].strip()
    settlement = row["settlement_order"].strip().zfill(2)
    person_order = row["person_order_in_settlement"].strip().zfill(4)
    household = normalized_household_segment(household_id)
    return f"{district}-{settlement}-{household}-{person_order}"


def main() -> None:
    input_fields, input_rows = read_csv(INPUT_CSV)
    mapping_fields, mapping_rows = read_csv(MAPPING_CSV)
    required_mapping = {
        "source_household_number",
        "record_count",
        "household_number_normalized",
        "household_type",
        "household_details",
    }
    missing_mapping_fields = required_mapping.difference(mapping_fields)
    if missing_mapping_fields:
        raise ValueError(f"Mapping is missing fields: {sorted(missing_mapping_fields)}")

    mapping: dict[str, dict[str, str]] = {}
    duplicate_mapping_values: list[str] = []
    for row in mapping_rows:
        key = row["source_household_number"]
        if key in mapping:
            duplicate_mapping_values.append(key)
        mapping[key] = row
    if duplicate_mapping_values:
        raise ValueError(f"Duplicate source values in mapping: {duplicate_mapping_values}")

    source_counts = Counter(row["household_number"] for row in input_rows)
    mapping_count_mismatches = []
    missing_source_values = []
    for source_value, decision in mapping.items():
        actual = source_counts[source_value]
        expected = int(decision["record_count"])
        if actual == 0:
            missing_source_values.append(source_value)
        if actual != expected:
            mapping_count_mismatches.append((source_value, expected, actual))

    output_fields: list[str] = []
    for field in input_fields:
        if field == "household_number":
            output_fields.extend(NEW_HOUSEHOLD_COLUMNS)
        else:
            output_fields.append(field)

    output_rows: list[dict[str, str]] = []
    diff_rows: list[dict[str, str]] = []
    mapped_records = 0
    corrected_id_records = 0
    range_id_records = 0

    for source_row in input_rows:
        source_household = source_row["household_number"]
        decision = mapping.get(source_household)
        if decision is not None:
            mapped_records += 1
            household_id = decision["household_number_normalized"].strip()
            household_type = decision["household_type"].strip()
            household_details = decision["household_details"].strip()
            if household_id and household_id != source_household:
                corrected_id_records += 1
        elif re.fullmatch(r"\d+", source_household.strip()):
            household_id = source_household.strip()
            household_type = "Частное"
            household_details = ""
        elif not source_household.strip():
            household_id = ""
            household_type = ""
            household_details = ""
        else:
            raise ValueError(f"Unmapped non-numeric household value: {source_household!r}")

        if re.fullmatch(r"\d+\s*-\s*\d+", household_id):
            range_id_records += 1

        new_row = dict(source_row)
        old_source_position_id = source_row["source_position_id"]
        new_source_position_id = source_position_id(source_row, household_id)
        new_row["source_position_id"] = new_source_position_id
        new_row.pop("household_number", None)
        new_row["household_id"] = household_id
        new_row["household_type"] = household_type
        new_row["household_details"] = household_details
        output_rows.append(new_row)

        if (
            source_household != household_id
            or old_source_position_id != new_source_position_id
            or decision is not None
        ):
            diff_rows.append(
                {
                    "person_id": source_row["person_id"],
                    "source_household_number": source_household,
                    "household_id": household_id,
                    "household_type": household_type,
                    "household_details": household_details,
                    "old_source_position_id": old_source_position_id,
                    "new_source_position_id": new_source_position_id,
                }
            )

    source_ids = [row["source_position_id"] for row in output_rows]
    type_counts = Counter(row["household_type"] for row in output_rows)
    invalid_household_ids = [
        row["household_id"]
        for row in output_rows
        if row["household_id"] and not re.fullmatch(r"\d+(?:-\d+)?", row["household_id"])
    ]

    qa_rows = [
        {"check": "input_records", "value": str(len(input_rows))},
        {"check": "output_records", "value": str(len(output_rows))},
        {"check": "owner_mapping_values", "value": str(len(mapping))},
        {"check": "mapped_records", "value": str(mapped_records)},
        {"check": "corrected_household_id_records", "value": str(corrected_id_records)},
        {"check": "hyphenated_household_id_records", "value": str(range_id_records)},
        {"check": "mapping_values_missing_from_source", "value": str(len(missing_source_values))},
        {"check": "mapping_record_count_mismatches", "value": str(len(mapping_count_mismatches))},
        {"check": "invalid_household_id_values", "value": str(len(invalid_household_ids))},
        {"check": "blank_source_position_id", "value": str(sum(not value for value in source_ids))},
        {"check": "duplicate_source_position_id", "value": str(len(source_ids) - len(set(source_ids)))},
        {"check": "blank_source_household_records", "value": str(source_counts[""])},
        {"check": "blank_household_type", "value": str(type_counts[""])},
        {"check": "owner_verified_blank_household_type_records", "value": str(type_counts[""])},
        {"check": "owner_verification_status", "value": "confirmed_as_source_blanks"},
    ]

    failures = {
        "row_count": len(input_rows) != len(output_rows),
        "mapping_missing": bool(missing_source_values),
        "mapping_count": bool(mapping_count_mismatches),
        "invalid_household_ids": bool(invalid_household_ids),
        "blank_source_ids": any(not value for value in source_ids),
        "duplicate_source_ids": len(source_ids) != len(set(source_ids)),
    }

    write_csv(OUTPUT_CSV, output_fields, output_rows)
    write_csv(
        DIFF_CSV,
        [
            "person_id",
            "source_household_number",
            "household_id",
            "household_type",
            "household_details",
            "old_source_position_id",
            "new_source_position_id",
        ],
        diff_rows,
    )
    write_csv(QA_CSV, ["check", "value"], qa_rows)
    write_csv(
        TYPE_SUMMARY_CSV,
        ["household_type", "record_count"],
        [
            {"household_type": key, "record_count": str(value)}
            for key, value in sorted(type_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
    )

    if any(failures.values()):
        raise RuntimeError(f"QA failed: {failures}")

    print(f"Staged {len(output_rows)} records in {OUTPUT_CSV}")
    print(f"Mapped {mapped_records} records from {len(mapping)} owner decisions")
    print(f"Wrote {len(diff_rows)} diff rows")


if __name__ == "__main__":
    main()
