from __future__ import annotations

import argparse
from pathlib import Path

from sakhalin_conversion_helpers_v12 import standardize_clean_csv, validate_output_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Standardize a reviewed clean CSV for project use.")
    parser.add_argument("--input", required=True, help="Reviewed clean CSV, comma or semicolon delimited")
    parser.add_argument("--output", required=True, help="Project-standard output CSV")
    parser.add_argument("--qa-json", default="", help="Optional path to write validation report JSON")
    args = parser.parse_args()

    rows = standardize_clean_csv(args.input, args.output)
    report = validate_output_csv(args.output)
    if args.qa_json:
        import json
        out = Path(args.qa_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rows written: {len(rows)}")
    print(f"Source anomalies: {len(report.get('source_anomalies', []))}")
    print(f"Unknown legal_status: {len(report.get('unknown_legal_statuses', []))}")
    print(f"Unknown family_status: {len(report.get('unknown_family_statuses', []))}")
    print(f"Unknown religion: {len(report.get('unknown_religions', []))}")
    print(f"Unknown origin_place: {len(report.get('unknown_origin_places', []))}")


if __name__ == "__main__":
    main()
