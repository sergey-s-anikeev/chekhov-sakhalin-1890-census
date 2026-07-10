from __future__ import annotations

import argparse
import csv
from pathlib import Path

from sakhalin_conversion_helpers_v12 import FINAL_FIELD_ORDER, read_csv_dicts_auto, write_project_csv, source_order_key, validate_output_csv


def merge_districts(inputs: list[str | Path], output: str | Path, *, reassign_global_ids: bool = True) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in inputs:
        file_rows, _fieldnames, _delimiter = read_csv_dicts_auto(path)
        for row in file_rows:
            rows.append({f: row.get(f, "") for f in FINAL_FIELD_ORDER})

    rows.sort(key=source_order_key)
    if reassign_global_ids:
        for i, row in enumerate(rows, start=1):
            row["person_id"] = f"P{i:06d}"

    write_project_csv(output, rows, FINAL_FIELD_ORDER)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge reviewed district clean CSVs into one project clean CSV.")
    parser.add_argument("--inputs", nargs="+", required=True, help="District clean CSV files")
    parser.add_argument("--output", required=True, help="Merged output CSV")
    parser.add_argument("--keep-district-person-ids", action="store_true", help="Do not reassign global person_id")
    parser.add_argument("--qa-json", default="", help="Optional path to write validation report JSON")
    args = parser.parse_args()

    rows = merge_districts(args.inputs, args.output, reassign_global_ids=not args.keep_district_person_ids)
    report = validate_output_csv(args.output)
    if args.qa_json:
        import json
        out = Path(args.qa_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rows written: {len(rows)}")
    print(f"Source anomalies: {len(report.get('source_anomalies', []))}")


if __name__ == "__main__":
    main()
