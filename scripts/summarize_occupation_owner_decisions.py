import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/review/occupation_review_20260716/owner_all_values_inspection.ndjson"


def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = data["preview"]
    header = rows[0]
    decisions = []
    for raw in rows[1:]:
        values = ["" if value is None else str(value) for value in raw]
        row = dict(zip(header, values))
        if row["owner_decision"].strip() or row["owner_note"].strip():
            decisions.append(row)
    summary = {
        "decision_rows": len(decisions),
        "affected_records": sum(int(r["record_count"]) for r in decisions),
        "decisions": [
            {
                "occupation": r["occupation"],
                "record_count": int(r["record_count"]),
                "proposed": r["occupation_norm_proposed"],
                "owner_decision": r["owner_decision"],
                "owner_note": r["owner_note"],
            }
            for r in decisions
        ],
    }
    out = ROOT / "data/review/occupation_review_20260716/owner_decision_summary.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
