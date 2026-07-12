import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "processed" / "clean_sakhalin_1890_ru.csv"
INVENTORY = ROOT / "data" / "review" / "notes_raw_duplicates_item4_20260711" / "notes_raw_duplicate_inventory.csv"
RAW_DIR = ROOT / "data" / "review" / "notes_raw_duplicates_item4_20260711" / "raw_page_extracts"
TRUE_DUPLICATES = ROOT / "data" / "review" / "notes_raw_duplicates_item4_20260711" / "owner_confirmed_true_duplicates.txt"
OUT_DIR = ROOT / "data" / "staging" / "notes_raw_suffix_recovery_20260711"
QA_DIR = ROOT / "outputs" / "qa" / "notes_raw_suffix_recovery_20260711"

MANUAL = {
    "P001792": "РГБ № 4300а",
    "P007384": "РГБ № 6152a",
}

ARCHIVE_RE = re.compile(r"\b(РГБ|РГАЛИ)\s*№?\s*(\d+)(?:\s*[-–—]?\s*([А-Яа-яA-Za-z]))?\b", re.I)
FILE_PAGE_RE = re.compile(r"book_page_(\d+)\.txt$", re.I)


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize(value):
    value = unicodedata.normalize("NFKC", value or "").lower().replace("ё", "е")
    return " ".join(re.findall(r"[а-яa-z]+", value))


def archive_base(value):
    match = ARCHIVE_RE.search(value or "")
    return f"{match.group(1).upper()} № {match.group(2)}" if match else ""


def source_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


rows = read_csv(SOURCE)
inventory = read_csv(INVENTORY)
by_person = {row["person_id"]: row for row in rows}
inventory_by_base_page = {}
for row in inventory:
    key = (archive_base(row["notes_raw"]), str(int(row["page_number"])))
    inventory_by_base_page.setdefault(key, []).append(row)

all_by_base_page = {}
for row in rows:
    base = archive_base(row["notes_raw"])
    if base and row.get("page_number", "").strip():
        key = (base, str(int(row["page_number"])))
        all_by_base_page.setdefault(key, []).append(row)

true_duplicate_values = {
    archive_base(line.strip())
    for line in TRUE_DUPLICATES.read_text(encoding="utf-8-sig").splitlines()
    if archive_base(line.strip())
}

evidence = []
for path in sorted(RAW_DIR.glob("*.txt")):
    page_match = FILE_PAGE_RE.search(path.name)
    if not page_match:
        continue
    page = str(int(page_match.group(1)))
    text = path.read_text(encoding="utf-8-sig")
    matches = list(ARCHIVE_RE.finditer(text))
    previous_end = 0
    for match in matches:
        suffix = match.group(3)
        context = text[previous_end:match.start()]
        previous_end = match.end()
        if not suffix:
            continue
        base = f"{match.group(1).upper()} № {match.group(2)}"
        proposed = f"{base}{suffix.lower()}"
        candidates = inventory_by_base_page.get((base, page), [])
        exact_existing = [
            row for row in rows
            if re.sub(r"\s*[-–—]\s*", "", row["notes_raw"]).lower() == proposed.lower()
        ]
        if len(exact_existing) == 1:
            candidates = exact_existing
        scored = []
        for candidate in candidates:
            score = SequenceMatcher(None, normalize(candidate["name_raw"]), normalize(context)).ratio()
            # Direct name containment is stronger than whole-context similarity.
            name_norm = normalize(candidate["name_raw"])
            context_norm = normalize(context)
            if name_norm and name_norm in context_norm:
                score = 1.0
            scored.append((score, candidate))
        scored.sort(key=lambda item: item[0], reverse=True)
        selected = scored[0][1] if scored else None
        score = scored[0][0] if scored else 0.0
        evidence.append({
            "source_file": path.name,
            "page_number": page,
            "source_reference": match.group(0),
            "proposed_notes_raw": proposed,
            "matched_person_id": selected["person_id"] if selected else "",
            "matched_name_raw": selected["name_raw"] if selected else "",
            "match_score": f"{score:.3f}",
            "candidate_count": str(len(candidates)),
            "context": " ".join(context.split())[-500:],
        })

proposals = {}
for item in evidence:
    person_id = item["matched_person_id"]
    if not person_id:
        continue
    score = float(item["match_score"])
    if item["candidate_count"] == "1" or score >= 0.85:
        proposals[person_id] = {
            "new_notes_raw": item["proposed_notes_raw"],
            "decision_source": "uploaded_raw_page",
            "evidence_file": item["source_file"],
            "match_score": item["match_score"],
        }

for person_id, value in MANUAL.items():
    proposals[person_id] = {
        "new_notes_raw": value,
        "decision_source": "owner_manual_override",
        "evidence_file": "",
        "match_score": "1.000",
    }

# Apply the owner-approved no-space/no-hyphen format to suffixes already present.
for row in rows:
    match = ARCHIVE_RE.fullmatch(row.get("notes_raw", "").strip())
    if not match or not match.group(3):
        continue
    normalized_value = f"{match.group(1).upper()} № {match.group(2)}{match.group(3).lower()}"
    if normalized_value != row["notes_raw"]:
        proposals[row["person_id"]] = {
            "new_notes_raw": normalized_value,
            "decision_source": "owner_format_normalization",
            "evidence_file": "",
            "match_score": "1.000",
        }

mapping = []
for person_id, proposal in sorted(proposals.items()):
    source_row = by_person[person_id]
    old_value = source_row["notes_raw"]
    new_value = proposal["new_notes_raw"]
    if old_value == new_value:
        continue
    mapping.append({
        "person_id": person_id,
        "source_position_id": source_row["source_position_id"],
        "page_number": source_row["page_number"],
        "name_raw": source_row["name_raw"],
        "notes_raw_before": old_value,
        "notes_raw_after": new_value,
        "decision_source": proposal["decision_source"],
        "evidence_file": proposal["evidence_file"],
        "match_score": proposal["match_score"],
    })

mapping_by_person = {row["person_id"]: row for row in mapping}
staged_rows = []
for row in rows:
    staged = dict(row)
    if row["person_id"] in mapping_by_person:
        staged["notes_raw"] = mapping_by_person[row["person_id"]]["notes_raw_after"]
    staged_rows.append(staged)

OUT_DIR.mkdir(parents=True, exist_ok=True)
QA_DIR.mkdir(parents=True, exist_ok=True)

mapping_fields = [
    "person_id", "source_position_id", "page_number", "name_raw",
    "notes_raw_before", "notes_raw_after", "decision_source",
    "evidence_file", "match_score",
]
with (OUT_DIR / "notes_raw_suffix_mapping.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=mapping_fields)
    writer.writeheader()
    writer.writerows(mapping)

with (OUT_DIR / "clean_sakhalin_1890_ru_notes_raw_item4_v1.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(staged_rows)

evidence_fields = [
    "source_file", "page_number", "source_reference", "proposed_notes_raw",
    "matched_person_id", "matched_name_raw", "match_score", "candidate_count", "context",
]
with (QA_DIR / "notes_raw_suffix_match_evidence.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=evidence_fields)
    writer.writeheader()
    writer.writerows(evidence)

remaining_counts = Counter(row["notes_raw"] for row in staged_rows if row["notes_raw"].strip())
remaining_duplicates = {value: count for value, count in remaining_counts.items() if count > 1}
unexpected_remaining = {
    value: count for value, count in remaining_duplicates.items()
    if archive_base(value) not in true_duplicate_values
}

qa = {
    "source_file": str(SOURCE.relative_to(ROOT)),
    "source_sha256": source_sha256(SOURCE),
    "source_rows": len(rows),
    "staged_rows": len(staged_rows),
    "changed_records": len(mapping),
    "uploaded_suffix_recoveries": sum(row["decision_source"] == "uploaded_raw_page" for row in mapping),
    "manual_overrides": sum(row["decision_source"] == "owner_manual_override" for row in mapping),
    "format_normalizations": sum(row["decision_source"] == "owner_format_normalization" for row in mapping),
    "manual_override_values": {pid: by_person[pid]["notes_raw"] + " -> " + value for pid, value in MANUAL.items()},
    "true_duplicate_base_values": len(true_duplicate_values),
    "remaining_duplicate_values": len(remaining_duplicates),
    "unexpected_remaining_duplicate_values": unexpected_remaining,
    "all_person_ids_preserved": [row["person_id"] for row in rows] == [row["person_id"] for row in staged_rows],
    "all_source_position_ids_preserved": [row["source_position_id"] for row in rows] == [row["source_position_id"] for row in staged_rows],
    "only_notes_raw_changed": all(
        all(before[field] == after[field] for field in before if field != "notes_raw")
        for before, after in zip(rows, staged_rows)
    ),
    "unmatched_suffix_evidence": [item for item in evidence if not item["matched_person_id"]],
    "low_confidence_suffix_evidence": [item for item in evidence if item["matched_person_id"] and float(item["match_score"]) < 0.85 and item["candidate_count"] != "1"],
}
with (QA_DIR / "notes_raw_suffix_recovery_qa.json").open("w", encoding="utf-8", newline="") as handle:
    json.dump(qa, handle, ensure_ascii=False, indent=2)
    handle.write("\n")

manifest_paths = [
    OUT_DIR / "clean_sakhalin_1890_ru_notes_raw_item4_v1.csv",
    OUT_DIR / "notes_raw_suffix_mapping.csv",
    TRUE_DUPLICATES,
    INVENTORY,
]
with (QA_DIR / "notes_raw_suffix_artifact_manifest.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["path", "sha256"])
    writer.writeheader()
    for path in manifest_paths:
        writer.writerow({"path": str(path.relative_to(ROOT)), "sha256": source_sha256(path)})

print(json.dumps({
    "changed_records": len(mapping),
    "uploaded_suffix_recoveries": qa["uploaded_suffix_recoveries"],
    "manual_overrides": qa["manual_overrides"],
    "format_normalizations": qa["format_normalizations"],
    "unmatched_suffix_evidence": len(qa["unmatched_suffix_evidence"]),
    "low_confidence_suffix_evidence": len(qa["low_confidence_suffix_evidence"]),
    "unexpected_remaining_duplicate_values": len(unexpected_remaining),
}, ensure_ascii=False))
