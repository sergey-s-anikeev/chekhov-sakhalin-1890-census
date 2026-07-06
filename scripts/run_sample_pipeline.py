from __future__ import annotations

import argparse
import json
from pathlib import Path

from sakhalin_conversion_helpers_v11 import (
    transform_records_csv,
    validate_output_csv,
)


def write_qa_report(report: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# QA Report",
        "",
        f"Row count: {report.get('row_count', 0)}",
        "",
        "## Unknown origin places",
        "",
    ]

    for value in report.get("unknown_origin_places", []):
        lines.append(f"- {value}")

    lines.extend([
        "",
        "## Unknown legal statuses",
        "",
    ])

    for value in report.get("unknown_legal_statuses", []):
        lines.append(f"- {value}")

    lines.extend([
        "",
        "## Unknown family statuses",
        "",
    ])

    for value in report.get("unknown_family_statuses", []):
        lines.append(f"- {value}")

    lines.extend([
        "",
        "## Unknown religions",
        "",
    ])

    for value in report.get("unknown_religions", []):
        lines.append(f"- {value}")

    lines.extend([
        "",
        "## Source anomalies",
        "",
    ])

    for item in report.get("source_anomalies", []):
        lines.append(
            f"- `{item.get('person_id')}` / `{item.get('source_position_id')}` "
            f"/ page `{item.get('page_number')}` / field `{item.get('field')}`: "
            f"{item.get('value')} — {item.get('reason')}"
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run sample transformation and QA for the Chekhov Sakhalin census project."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to raw split-record CSV."
    )

    parser.add_argument(
        "--output",
        default="data/processed/clean_sample_500.csv",
        help="Path to final normalized CSV."
    )

    parser.add_argument(
        "--qa-md",
        default="outputs/qa/sample_500_qa_report.md",
        help="Path to Markdown QA report."
    )

    parser.add_argument(
        "--qa-json",
        default="outputs/qa/sample_500_qa_report.json",
        help="Path to JSON QA report."
    )

    parser.add_argument(
        "--default-settlement",
        default=None,
        help="Optional default settlement name if the input CSV contains one locality only."
    )

    parser.add_argument(
        "--global-person-start",
        type=int,
        default=1,
        help="Starting global person number for generated person_id."
    )

    args = parser.parse_args()

    input_csv = Path(args.input)
    output_csv = Path(args.output)
    qa_md = Path(args.qa_md)
    qa_json = Path(args.qa_json)

    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    qa_json.parent.mkdir(parents=True, exist_ok=True)

    transform_records_csv(
        input_csv,
        output_csv,
        default_settlement=args.default_settlement,
        global_person_start=args.global_person_start,
    )

    report = validate_output_csv(output_csv)

    qa_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    write_qa_report(report, qa_md)

    print(f"Clean CSV written to: {output_csv}")
    print(f"QA Markdown report written to: {qa_md}")
    print(f"QA JSON report written to: {qa_json}")


if __name__ == "__main__":
    main()
