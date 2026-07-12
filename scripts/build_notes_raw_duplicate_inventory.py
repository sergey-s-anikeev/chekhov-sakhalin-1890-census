import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "data" / "processed" / "clean_sakhalin_1890_ru.csv"
out_dir = ROOT / "data" / "review" / "notes_raw_duplicates_item4_20260711"
out_dir.mkdir(parents=True, exist_ok=True)
output = out_dir / "notes_raw_duplicate_inventory.csv"

with source.open("r", encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))

counts = Counter(
    row["notes_raw"]
    for row in rows
    if row.get("notes_raw", "").strip()
)
duplicate_values = {value for value, count in counts.items() if count > 1}

fields = [
    "notes_raw",
    "notes_raw_occurrence_count",
    "person_id",
    "source_position_id",
    "district_code",
    "district",
    "settlement_order",
    "settlement",
    "page_number",
    "household_number",
    "person_order_in_settlement",
    "name_raw",
]

selected = []
for row in rows:
    value = row.get("notes_raw", "")
    if value in duplicate_values:
        selected.append({
            "notes_raw": value,
            "notes_raw_occurrence_count": counts[value],
            **{field: row.get(field, "") for field in fields[2:]},
        })

selected.sort(key=lambda row: (row["notes_raw"], row["person_id"]))
with output.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(selected)

print(f"source_rows={len(rows)}")
print(f"duplicate_values={len(duplicate_values)}")
print(f"duplicate_rows={len(selected)}")
print(f"output={output}")
