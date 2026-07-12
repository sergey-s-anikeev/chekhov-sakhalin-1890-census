import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "data" / "staging" / "item13_religion_20260711" / "clean_sakhalin_1890_ru_item13_religion_v2.csv"
output = ROOT / "outputs" / "qa" / "item11_family_status_20260711" / "family_status_grouped_values.csv"
output.parent.mkdir(parents=True, exist_ok=True)
with source.open("r", encoding="utf-8-sig", newline="") as handle:
    counts = Counter(row["family_status"] for row in csv.DictReader(handle))
with output.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["family_status", "count"])
    writer.writeheader()
    for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        writer.writerow({"family_status": value, "count": count})
print(f"distinct_values={len(counts)}")
print(f"output={output}")
