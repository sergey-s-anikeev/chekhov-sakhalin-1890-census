import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "processed" / "clean_sakhalin_1890_ru.csv"
OUT = ROOT / "data" / "staging" / "items_10_14_20260711"
QA = ROOT / "outputs" / "qa" / "items_10_14_20260711"


def read_rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


rows = read_rows(SOURCE)
fields = list(rows[0])

item10_rows = []
item14_rows = []
item10_candidate = []
item14_candidate = []

for row in rows:
    staged10 = dict(row)
    for field in ("legal_status", "comments"):
        staged10[field] = re.sub(
            r"запасный",
            lambda match: "Запасной" if match.group(0)[0].isupper() else "запасной",
            staged10[field],
            flags=re.IGNORECASE,
        )
    if staged10 != row:
        item10_rows.append(staged10)
        item10_candidate.append({
            "person_id": row["person_id"],
            "source_position_id": row["source_position_id"],
            "field": "legal_status/comments",
            "before_legal_status": row["legal_status"],
            "after_legal_status": staged10["legal_status"],
            "before_comments": row["comments"],
            "after_comments": staged10["comments"],
        })

    staged14 = dict(row)
    if re.fullmatch(r"грамотен\s+неграмотен|неграмотен\s+грамотен", staged14["literacy"].strip(), flags=re.IGNORECASE):
        staged14["literacy"] = ""
    if staged14 != row:
        item14_rows.append(staged14)
        item14_candidate.append({
            "person_id": row["person_id"],
            "source_position_id": row["source_position_id"],
            "field": "literacy",
            "before": row["literacy"],
            "after": staged14["literacy"],
        })

def write_csv(path, data, header):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        writer.writerows(data)

OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)

item10_full = [dict(row) for row in rows]
item14_full = [dict(row) for row in rows]
for change in item10_candidate:
    for row in item10_full:
        if row["person_id"] == change["person_id"]:
            row["legal_status"] = change["after_legal_status"]
            row["comments"] = change["after_comments"]
for change in item14_candidate:
    for row in item14_full:
        if row["person_id"] == change["person_id"]:
            row["literacy"] = change["after"]

write_csv(OUT / "clean_sakhalin_1890_ru_item10_legal_status_v1.csv", item10_full, fields)
write_csv(OUT / "clean_sakhalin_1890_ru_item14_literacy_v1.csv", item14_full, fields)
write_csv(QA / "item10_legal_status_diff.csv", item10_candidate, list(item10_candidate[0]) if item10_candidate else ["person_id"])
write_csv(QA / "item14_literacy_diff.csv", item14_candidate, list(item14_candidate[0]) if item14_candidate else ["person_id"])

qa = {
    "source_rows": len(rows),
    "item10_changed_records": len(item10_candidate),
    "item10_legal_status_changes": sum(x["before_legal_status"] != x["after_legal_status"] for x in item10_candidate),
    "item10_comments_changes": sum(x["before_comments"] != x["after_comments"] for x in item10_candidate),
    "item14_changed_records": len(item14_candidate),
    "item14_contradictory_values_blank": sum(x["before"] != "" and x["after"] == "" for x in item14_candidate),
    "item10_only_target_fields_changed": all(
        all(before[k] == after[k] for k in fields if k not in {"legal_status", "comments"})
        for before, after in zip(rows, item10_full)
    ),
    "item14_only_literacy_changed": all(
        all(before[k] == after[k] for k in fields if k != "literacy")
        for before, after in zip(rows, item14_full)
    ),
    "item10_remaining_zapasny_values": sum(
        bool(re.search(r"запасный", row["legal_status"] + " " + row["comments"], flags=re.IGNORECASE))
        for row in item10_full
    ),
    "item14_remaining_contradictory_values": sum(
        bool(re.fullmatch(r"грамотен\s+неграмотен|неграмотен\s+грамотен", row["literacy"].strip(), flags=re.IGNORECASE))
        for row in item14_full
    ),
}
with (QA / "items_10_14_qa.json").open("w", encoding="utf-8") as handle:
    json.dump(qa, handle, ensure_ascii=False, indent=2)
    handle.write("\n")

with (QA / "items_10_14_artifact_manifest.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["path", "sha256"])
    writer.writeheader()
    for path in [OUT / "clean_sakhalin_1890_ru_item10_legal_status_v1.csv", OUT / "clean_sakhalin_1890_ru_item14_literacy_v1.csv", QA / "item10_legal_status_diff.csv", QA / "item14_literacy_diff.csv"]:
        writer.writerow({"path": str(path.relative_to(ROOT)), "sha256": sha256(path)})

print(json.dumps(qa, ensure_ascii=False))
