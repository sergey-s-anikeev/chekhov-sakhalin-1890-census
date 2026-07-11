from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


INPUT_CSV = Path("data/processed/clean_sakhalin_1890_ru.csv")
OUTPUT_DIR = Path("data/staging/household_structure_20260711")
OUTPUT_CSV = OUTPUT_DIR / "clean_sakhalin_1890_ru_household_structure_v1.csv"
INVENTORY_CSV = OUTPUT_DIR / "household_structure_affected_inventory.csv"
VALUE_SUMMARY_CSV = OUTPUT_DIR / "household_structure_value_summary.csv"
DIFF_CSV = OUTPUT_DIR / "household_structure_diff.csv"
QA_CSV = OUTPUT_DIR / "household_structure_qa_summary.csv"

HOUSEHOLD_COLUMNS = [
    "household_id",
    "household_type",
    "household_detail",
]


def is_numeric_household(value: str) -> bool:
    return bool(re.fullmatch(r"\d+", value.strip()))


def classify_household_type(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value.strip()).replace("ё", "е")
    lowered = normalized.lower()

    if not normalized:
        return ""
    if lowered.startswith("казарма") or lowered.startswith("каз."):
        return "Казарма"
    if lowered == "тюрьма":
        return "Тюрьма"
    if lowered == "школа":
        return "Школа"
    if lowered == "мечеть":
        return "Мечеть"
    if lowered == "баня":
        return "Баня"
    if lowered == "старый лазарет":
        return "Лазарет"
    if lowered == "кирпичный завод":
        return "Кирпичный завод"
    if lowered in {"катерная мастерская", "столярная мастерская"}:
        return "Мастерская"
    if lowered == "телеграф":
        return "Телеграф"
    if "метеорологическая" in lowered and "станция" in lowered:
        return "Метеорологическая станция"
    if lowered == "смольная яма":
        return "Смольная яма"
    if lowered == "штольня":
        return "Штольня"
    if lowered == "кабельный дом":
        return "Кабельный дом"
    if lowered == "собственный дом":
        return "Собственный дом"
    if lowered.startswith("у перевоза"):
        return "У перевоза"
    if lowered.startswith("дом ") or lowered.startswith("дом-"):
        return "Дом"
    return "Другое"


def household_segment(household_id: str) -> str:
    if household_id:
        return str(int(household_id)).zfill(3)
    return "000"


def rewritten_source_position_id(row: dict[str, str], household_id: str) -> str:
    return (
        f"{row['district_code']}-"
        f"{row['settlement_order']}-"
        f"{household_segment(household_id)}-"
        f"{str(int(row['person_order_in_settlement'])).zfill(4)}"
    )


def output_fieldnames(input_fieldnames: list[str]) -> list[str]:
    fieldnames = []
    for field in input_fieldnames:
        if field == "household_number":
            fieldnames.extend(HOUSEHOLD_COLUMNS)
        else:
            fieldnames.append(field)
    return fieldnames


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with INPUT_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        input_rows = list(reader)
        input_fieldnames = reader.fieldnames or []

    output_rows: list[dict[str, str]] = []
    inventory_rows: list[dict[str, str]] = []
    diff_rows: list[dict[str, str]] = []
    nonnumeric_values: Counter[str] = Counter()

    for row in input_rows:
        source_household = (row.get("household_number") or "").strip()
        household_id = source_household if is_numeric_household(source_household) else ""
        household_type = "Стандарт" if household_id else classify_household_type(source_household)
        household_detail = "" if household_id else source_household
        new_source_position_id = rewritten_source_position_id(row, household_id)

        out = dict(row)
        out["source_position_id"] = new_source_position_id
        out["household_id"] = household_id
        out["household_type"] = household_type
        out["household_detail"] = household_detail
        out.pop("household_number", None)
        output_rows.append(out)

        if source_household and not household_id:
            nonnumeric_values[source_household] += 1
            inventory_rows.append({
                "person_id": row["person_id"],
                "old_source_position_id": row["source_position_id"],
                "new_source_position_id": new_source_position_id,
                "district": row["district"],
                "settlement": row["settlement"],
                "person_order_in_settlement": row["person_order_in_settlement"],
                "source_household_number": source_household,
                "household_id": household_id,
                "household_type": household_type,
                "household_detail": household_detail,
            })

        if row["source_position_id"] != new_source_position_id or "household_number" in row:
            diff_rows.append({
                "person_id": row["person_id"],
                "old_source_position_id": row["source_position_id"],
                "new_source_position_id": new_source_position_id,
                "old_household_number": source_household,
                "new_household_id": household_id,
                "new_household_type": household_type,
                "new_household_detail": household_detail,
            })

    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames(input_fieldnames))
        writer.writeheader()
        writer.writerows(output_rows)

    inventory_fields = [
        "person_id",
        "old_source_position_id",
        "new_source_position_id",
        "district",
        "settlement",
        "person_order_in_settlement",
        "source_household_number",
        "household_id",
        "household_type",
        "household_detail",
    ]
    with INVENTORY_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=inventory_fields)
        writer.writeheader()
        writer.writerows(inventory_rows)

    with VALUE_SUMMARY_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["source_household_number", "record_count", "household_type"])
        writer.writeheader()
        for value, count in sorted(nonnumeric_values.items(), key=lambda item: (-item[1], item[0])):
            writer.writerow({
                "source_household_number": value,
                "record_count": count,
                "household_type": classify_household_type(value),
            })

    with DIFF_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "person_id",
            "old_source_position_id",
            "new_source_position_id",
            "old_household_number",
            "new_household_id",
            "new_household_type",
            "new_household_detail",
        ])
        writer.writeheader()
        writer.writerows(diff_rows)

    qa_rows = [
        ("input_records", len(input_rows)),
        ("output_records", len(output_rows)),
        ("nonnumeric_textual_household_records", len(inventory_rows)),
        ("nonnumeric_household_distinct_values", len(nonnumeric_values)),
        ("blank_source_household_records", sum(not (r.get("household_number") or "").strip() for r in input_rows)),
        ("blank_new_source_position_id", sum(not r["source_position_id"] for r in output_rows)),
        ("duplicate_new_source_position_id", len(output_rows) - len({r["source_position_id"] for r in output_rows})),
        ("blank_household_type", sum(not r["household_type"] for r in output_rows)),
        ("blank_household_detail_for_textual_nonnumeric", sum(
            not r["household_detail"]
            for r in output_rows
            if not r["household_id"] and r["household_type"]
        )),
    ]
    with QA_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["check", "value"])
        writer.writerows(qa_rows)

    print(f"Wrote {OUTPUT_CSV}")
    print(f"Wrote {INVENTORY_CSV}")
    print(f"Wrote {VALUE_SUMMARY_CSV}")
    print(f"Wrote {DIFF_CSV}")
    print(f"Wrote {QA_CSV}")


if __name__ == "__main__":
    main()
