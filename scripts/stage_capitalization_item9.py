from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


INPUT = Path("data/processed/clean_sakhalin_1890_ru_v2_20260711.csv")
REVIEW = Path("data/review/capitalization_item9_20260712")
STAGING = Path("data/staging/capitalization_item9_20260712")
QA = Path("outputs/qa/capitalization_item9_20260712")

MAPPING = {
    "": "",
    "грамотен": "Грамотен",
    "неграмотен": "Неграмотен",
    "образован": "Образован",
    "грамотен неграмотен": "",
}


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    fields = list(rows[0])
    counts = Counter(row["literacy"].strip() for row in rows)
    unknown = sorted(set(counts) - set(MAPPING))
    if unknown:
        raise ValueError(f"Unmapped literacy values: {unknown}")

    inventory = [
        {
            "literacy_before": value,
            "record_count": str(count),
            "literacy_after": MAPPING[value],
            "owner_decision": "approve",
            "decision_basis": "Sentence case" if value != "грамотен неграмотен" else "Previously approved Item 14 contradiction resolution",
        }
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_csv(REVIEW / "literacy_sentence_case_mapping.csv", inventory, list(inventory[0]))

    staged_rows = []
    diff_rows = []
    for row in rows:
        staged = dict(row)
        staged["literacy"] = MAPPING[row["literacy"].strip()]
        staged_rows.append(staged)
        if row["literacy"] != staged["literacy"]:
            diff_rows.append(
                {
                    "person_id": row["person_id"],
                    "source_position_id": row["source_position_id"],
                    "literacy_before": row["literacy"],
                    "literacy_after": staged["literacy"],
                }
            )

    write_csv(STAGING / "clean_sakhalin_1890_ru_capitalization_item9_v1.csv", staged_rows, fields)
    write_csv(QA / "capitalization_item9_diff.csv", diff_rows, list(diff_rows[0]))
    non_target_changes = sum(
        any(before[field] != after[field] for field in fields if field != "literacy")
        for before, after in zip(rows, staged_rows)
    )
    allowed = {"", "Грамотен", "Неграмотен", "Образован"}
    qa = [
        {"check": "input_records", "value": str(len(rows)), "pass": str(len(rows) == 7446).upper()},
        {"check": "staged_records", "value": str(len(staged_rows)), "pass": str(len(staged_rows) == len(rows)).upper()},
        {"check": "changed_records", "value": str(len(diff_rows)), "pass": str(len(diff_rows) == 5419).upper()},
        {"check": "non_target_field_changes", "value": str(non_target_changes), "pass": str(non_target_changes == 0).upper()},
        {"check": "unexpected_literacy_values", "value": str(len({row["literacy"] for row in staged_rows} - allowed)), "pass": str(not ({row["literacy"] for row in staged_rows} - allowed)).upper()},
        {"check": "contradictory_literacy_values", "value": str(sum("грамотен неграмотен" in row["literacy"].lower() for row in staged_rows)), "pass": str(not any("грамотен неграмотен" in row["literacy"].lower() for row in staged_rows)).upper()},
    ]
    write_csv(QA / "capitalization_item9_qa_summary.csv", qa, ["check", "value", "pass"])


if __name__ == "__main__":
    main()
