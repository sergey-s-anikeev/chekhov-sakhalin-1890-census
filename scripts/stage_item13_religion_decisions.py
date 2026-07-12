import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "processed" / "clean_sakhalin_1890_ru.csv"
OUT = ROOT / "data" / "staging" / "item13_religion_20260711"
QA = ROOT / "outputs" / "qa" / "item13_religion_20260711"
MAPPING = {
    "Римско-католическое": "Католическое",
    "Мусульманское": "Магометанское",
    "Православное (выкрест)": "Православное",
}


def read_rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


rows = read_rows(SOURCE)
fields = list(rows[0])
staged = []
diff = []
for row in rows:
    updated = dict(row)
    if row["religion"] in MAPPING:
        updated["religion"] = MAPPING[row["religion"]]
        if row["religion"] == "Православное (выкрест)":
            updated["comments"] = "выкрест" if not row["comments"].strip() else f"{row['comments']}; выкрест"
        diff.append({
            "person_id": row["person_id"],
            "source_position_id": row["source_position_id"],
            "name_raw": row["name_raw"],
            "religion_before": row["religion"],
            "religion_after": updated["religion"],
            "comments_before": row["comments"],
            "comments_after": updated["comments"],
        })
    staged.append(updated)

OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)

candidate = OUT / "clean_sakhalin_1890_ru_item13_religion_v2.csv"
diff_path = QA / "item13_religion_v2_diff.csv"
with candidate.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    writer.writerows(staged)
with diff_path.open("w", encoding="utf-8-sig", newline="") as handle:
    diff_fields = ["person_id", "source_position_id", "name_raw", "religion_before", "religion_after", "comments_before", "comments_after"]
    writer = csv.DictWriter(handle, fieldnames=diff_fields)
    writer.writeheader()
    writer.writerows(diff)

qa = {
    "source_rows": len(rows),
    "staged_rows": len(staged),
    "changed_records": len(diff),
    "rimskо_katolicheskoe_changes": sum(x["religion_before"] == "Римско-католическое" for x in diff),
    "musulmanskoe_changes": sum(x["religion_before"] == "Мусульманское" for x in diff),
    "vy_krest_changes": sum(x["religion_before"] == "Православное (выкрест)" for x in diff),
    "comments_vy_krest_changes": sum(x["religion_before"] == "Православное (выкрест)" and "выкрест" in x["comments_after"] for x in diff),
    "only_religion_or_comments_changed": all(
        all(before[field] == after[field] for field in fields if field not in {"religion", "comments"})
        for before, after in zip(rows, staged)
    ),
    "remaining_rimsko_katolicheskoe": sum(row["religion"] == "Римско-католическое" for row in staged),
    "remaining_musulmanskoe": sum(row["religion"] == "Мусульманское" for row in staged),
    "remaining_pravoslavnoe_vy_krest": sum(row["religion"] == "Православное (выкрест)" for row in staged),
    "person_ids_preserved": [row["person_id"] for row in rows] == [row["person_id"] for row in staged],
}
with (QA / "item13_religion_qa.json").open("w", encoding="utf-8") as handle:
    json.dump(qa, handle, ensure_ascii=False, indent=2)
    handle.write("\n")
with (QA / "item13_religion_artifact_manifest.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["path", "sha256"])
    writer.writeheader()
    for path in [candidate, diff_path]:
        writer.writerow({"path": str(path.relative_to(ROOT)), "sha256": sha256(path)})

print(json.dumps(qa, ensure_ascii=True))
