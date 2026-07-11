#!/usr/bin/env python3
"""Validate the Item 1 owner-response workbook and export an approved CSV input."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


REQUIRED_COLUMNS = [
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
PROTECTED_COLUMNS = [
    "person_id",
    "source_position_id",
    "current_name_raw",
    "current_family_status",
    "proposal_basis",
    "proposal_confidence",
]
ALLOWED_DECISIONS = {"approve", "reject", "modify", "defer"}
MAIN_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workbook",
        default=(
            "data/review/name_raw_item1_20260710/owner_response/"
            "name_raw_proposed_corrections_owner_response_20260711.xlsx"
        ),
    )
    parser.add_argument(
        "--proposal-input",
        default="data/review/name_raw_item1_20260710/name_raw_proposed_corrections.csv",
    )
    parser.add_argument(
        "--output",
        default=(
            "data/review/name_raw_item1_20260710/owner_response/"
            "name_raw_approved_decisions_20260711.csv"
        ),
    )
    parser.add_argument(
        "--metadata-output",
        default=(
            "data/review/name_raw_item1_20260710/owner_response/"
            "name_raw_owner_response_validation_20260711.json"
        ),
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def column_number(cell_reference: str) -> int:
    match = re.match(r"[A-Z]+", cell_reference)
    if not match:
        raise ValueError(f"Invalid cell reference: {cell_reference}")
    result = 0
    for letter in match.group(0):
        result = result * 26 + ord(letter) - 64
    return result


def workbook_rows(path: Path) -> tuple[str, list[list[str]]]:
    with zipfile.ZipFile(path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("m:si", MAIN_NS):
                shared_strings.append(
                    "".join(node.text or "" for node in item.iterfind(".//m:t", MAIN_NS))
                )

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relationship_targets = {
            relation.attrib["Id"]: relation.attrib["Target"]
            for relation in relationships
        }
        sheet = workbook.find("m:sheets/m:sheet", MAIN_NS)
        if sheet is None:
            raise ValueError("Workbook contains no worksheet.")
        sheet_name = sheet.attrib["name"]
        relationship_id = sheet.attrib[
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        ]
        target = relationship_targets[relationship_id].lstrip("/")
        sheet_path = target if target.startswith("xl/") else "xl/" + target
        sheet_root = ET.fromstring(archive.read(sheet_path))

        rows: list[list[str]] = []
        for row_node in sheet_root.findall(".//m:sheetData/m:row", MAIN_NS):
            values = [""] * len(REQUIRED_COLUMNS)
            for cell in row_node.findall("m:c", MAIN_NS):
                column_index = column_number(cell.attrib["r"]) - 1
                cell_type = cell.attrib.get("t")
                value_node = cell.find("m:v", MAIN_NS)
                inline_node = cell.find("m:is", MAIN_NS)
                value = ""
                if cell_type == "s" and value_node is not None:
                    value = shared_strings[int(value_node.text or "0")]
                elif cell_type == "inlineStr" and inline_node is not None:
                    value = "".join(
                        node.text or ""
                        for node in inline_node.iterfind(".//m:t", MAIN_NS)
                    )
                elif value_node is not None:
                    value = value_node.text or ""
                if column_index < len(values):
                    values[column_index] = value.strip()
            rows.append(values)
    return sheet_name, rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    workbook_path = Path(args.workbook)
    proposal_path = Path(args.proposal_input)
    output_path = Path(args.output)
    metadata_path = Path(args.metadata_output)

    sheet_name, raw_rows = workbook_rows(workbook_path)
    if len(raw_rows) < 3:
        raise SystemExit("Owner-response workbook does not contain decision rows.")

    header_index = next(
        (index for index, row in enumerate(raw_rows) if row == REQUIRED_COLUMNS), None
    )
    if header_index is None:
        raise SystemExit("Owner-response workbook does not contain the required header row.")
    records = [
        dict(zip(REQUIRED_COLUMNS, row, strict=True))
        for row in raw_rows[header_index + 1 :]
        if any(value for value in row)
    ]
    proposals = read_csv(proposal_path)
    proposal_by_id = {row["person_id"]: row for row in proposals}
    record_by_id = {row["person_id"]: row for row in records}

    if len(record_by_id) != len(records):
        raise SystemExit("Duplicate person_id found in owner-response workbook.")
    if set(record_by_id) != set(proposal_by_id):
        missing = sorted(set(proposal_by_id) - set(record_by_id))
        extra = sorted(set(record_by_id) - set(proposal_by_id))
        raise SystemExit(f"Owner-response ID mismatch; missing={missing}, extra={extra}")

    protected_changes: list[dict[str, str]] = []
    invalid_decisions: list[dict[str, str]] = []
    for record in records:
        expected = proposal_by_id[record["person_id"]]
        for column in PROTECTED_COLUMNS:
            if record[column] != expected[column]:
                protected_changes.append(
                    {
                        "person_id": record["person_id"],
                        "column": column,
                        "expected": expected[column],
                        "actual": record[column],
                    }
                )
        record["owner_decision"] = record["owner_decision"].casefold()
        if record["owner_decision"] not in ALLOWED_DECISIONS:
            invalid_decisions.append(
                {
                    "person_id": record["person_id"],
                    "owner_decision": record["owner_decision"],
                }
            )
        if record["owner_decision"] in {"approve", "modify"} and not record[
            "proposed_name_raw"
        ]:
            invalid_decisions.append(
                {
                    "person_id": record["person_id"],
                    "owner_decision": "approved/modified row has blank proposed_name_raw",
                }
            )

    if protected_changes:
        raise SystemExit(f"Protected workbook cells changed: {protected_changes}")
    if invalid_decisions:
        raise SystemExit(f"Invalid owner decisions: {invalid_decisions}")

    write_csv(output_path, records)
    metadata = {
        "status": "validated",
        "owner_response_workbook": str(workbook_path).replace("\\", "/"),
        "owner_response_workbook_sha256": sha256(workbook_path),
        "source_proposal_csv": str(proposal_path).replace("\\", "/"),
        "source_proposal_csv_sha256": sha256(proposal_path),
        "approved_decision_csv": str(output_path).replace("\\", "/"),
        "approved_decision_csv_sha256": sha256(output_path),
        "sheet_name": sheet_name,
        "record_count": len(records),
        "id_set_matches_proposal": set(record_by_id) == set(proposal_by_id),
        "protected_cells_unchanged": not protected_changes,
        "decision_counts": dict(
            sorted(Counter(row["owner_decision"] for row in records).items())
        ),
        "invalid_decision_count": len(invalid_decisions),
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
