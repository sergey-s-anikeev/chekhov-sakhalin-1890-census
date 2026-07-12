from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


INPUT = Path("data/processed/clean_sakhalin_1890_ru_v2_20260711.csv")
OUT = Path("data/review/legal_status_item17_20260712")
INVENTORY = OUT / "legal_status_distinct_value_inventory.csv"
EXAMPLES = OUT / "legal_status_representative_records.csv"
SUMMARY = OUT / "legal_status_profile_summary.csv"


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    counts = Counter(row["legal_status"].strip() for row in rows)
    examples: dict[str, list[dict[str, str]]] = defaultdict(list)
    districts: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        value = row["legal_status"].strip()
        districts[value].add(row["district"])
        if len(examples[value]) < 3:
            examples[value].append(row)

    inventory = []
    representative_rows = []
    for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        sample = examples[value][0]
        inventory.append(
            {
                "legal_status": value,
                "record_count": str(count),
                "district_count": str(len(districts[value])),
                "districts": "; ".join(sorted(districts[value])),
                "example_person_id": sample["person_id"],
                "example_source_position_id": sample["source_position_id"],
                "example_name_raw": sample["name_raw"],
                "review_notes": "",
            }
        )
        for sample_number, row in enumerate(examples[value], start=1):
            representative_rows.append(
                {
                    "legal_status": value,
                    "record_count": str(count),
                    "sample_number": str(sample_number),
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "district": row["district"],
                    "settlement": row["settlement"],
                    "page_number": row["page_number"],
                    "name_raw": row["name_raw"],
                    "family_status": row["family_status"],
                    "comments": row["comments"],
                }
            )

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(INVENTORY, inventory, list(inventory[0]))
    write_csv(EXAMPLES, representative_rows, list(representative_rows[0]))
    summary = [
        {"metric": "input_records", "value": str(len(rows))},
        {"metric": "distinct_values_including_blank", "value": str(len(counts))},
        {"metric": "distinct_nonblank_values", "value": str(sum(bool(value) for value in counts))},
        {"metric": "blank_records", "value": str(counts[""])},
        {"metric": "nonblank_records", "value": str(len(rows) - counts[""])},
        {"metric": "representative_records", "value": str(len(representative_rows))},
    ]
    write_csv(SUMMARY, summary, ["metric", "value"])


if __name__ == "__main__":
    main()
