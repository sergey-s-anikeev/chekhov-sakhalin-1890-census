import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/staging/occupation_item18_20260717/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_staged.csv"
REVIEW = ROOT / "data/review/allowance_status_item19_20260717"
QA = ROOT / "outputs/qa/allowance_status_item19_20260717"


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    REVIEW.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    status_counts = Counter(r["allowance_status"] for r in rows)
    summary = []
    for status in ("TRUE", "FALSE", ""):
        matches = [r for r in rows if r["allowance_status"] == status]
        summary.append({
            "allowance_status": status,
            "record_count": len(matches),
            "arrival_year_blank": sum(not r["arrival_year"] for r in matches),
            "arrival_year_before_1880": sum(bool(r["arrival_year"]) and int(r["arrival_year"]) < 1880 for r in matches),
            "arrival_year_1880_or_later": sum(bool(r["arrival_year"]) and int(r["arrival_year"]) >= 1880 for r in matches),
        })

    flagged_source = [
        r for r in rows
        if r["allowance_status"] == "TRUE" and r["arrival_year"] and int(r["arrival_year"]) < 1880
    ]
    fields = [
        "person_id", "source_position_id", "page_number", "district", "settlement",
        "allowance_status", "arrival_year", "age", "legal_status_norm", "family_status_norm",
        "marriage_status_norm", "occupation_norm", "comments", "notes_raw",
    ]
    flagged = [{field: r.get(field, "") for field in fields} for r in flagged_source]
    for row in flagged:
        row["review_decision"] = ""
        row["review_note"] = ""

    true_blank_source = [r for r in rows if r["allowance_status"] == "TRUE" and not r["arrival_year"]]
    true_blank = [{field: r.get(field, "") for field in fields} for r in true_blank_source]
    year_counts = Counter(r["arrival_year"] for r in flagged_source)
    by_year = [{"arrival_year": year, "flagged_record_count": year_counts[year]} for year in sorted(year_counts, key=int)]

    write_csv(REVIEW / "allowance_status_value_summary.csv", summary, list(summary[0]))
    write_csv(REVIEW / "allowance_true_arrival_before_1880.csv", flagged, list(flagged[0]))
    write_csv(REVIEW / "allowance_true_blank_arrival_year.csv", true_blank, fields)
    write_csv(REVIEW / "allowance_true_before_1880_by_year.csv", by_year, list(by_year[0]))

    qa = {
        "source": str(SOURCE.relative_to(ROOT)),
        "row_count": len(rows),
        "distinct_allowance_values_including_blank": len(status_counts),
        "allowance_status_counts": {"TRUE": status_counts["TRUE"], "FALSE": status_counts["FALSE"], "blank": status_counts[""]},
        "arrival_year_blank_records": sum(not r["arrival_year"] for r in rows),
        "arrival_year_numeric_records": sum(bool(r["arrival_year"]) and r["arrival_year"].isdigit() for r in rows),
        "arrival_year_nonnumeric_records": sum(bool(r["arrival_year"]) and not r["arrival_year"].isdigit() for r in rows),
        "allowance_true_arrival_before_1880": len(flagged),
        "allowance_true_blank_arrival_year": len(true_blank),
        "flagged_min_arrival_year": min(int(r["arrival_year"]) for r in flagged),
        "flagged_max_arrival_year": max(int(r["arrival_year"]) for r in flagged),
        "status": "review only; no staged or canonical data modified",
    }
    (QA / "allowance_status_item19_qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
