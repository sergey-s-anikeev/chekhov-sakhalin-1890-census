from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/canonical_manifest.csv"
SOURCE = "owner_approved_quality_review_items_20260717"

V4_DATASETS = [
    ("data/processed/clean_alexandrovsky_ru_v4_20260717.csv", "Current canonical processed dataset for Alexandrovsky District"),
    ("data/processed/clean_tymovsky_ru_v4_20260717.csv", "Current canonical processed dataset for Tymovsky District"),
    ("data/processed/clean_korsakovsky_ru_v4_20260717.csv", "Current canonical processed dataset for Korsakovsky District"),
    ("data/processed/clean_sakhalin_1890_ru_v4_20260717.csv", "Current canonical combined processed dataset"),
]
V4_SUPPORT = [
    ("scripts/build_canonical_v4_20260717.py", "Canonical v4 consolidation script", "Reconciles approved staged branches and writes district and combined v4 files."),
    ("outputs/qa/canonical_v4_20260717/canonical_v4_qa_report.json", "Canonical v4 machine-readable QA report", "All integrated hard checks passed."),
    ("outputs/qa/canonical_v4_20260717/canonical_v4_hashes.csv", "Canonical v4 release hash table", "SHA-256 hashes for all four v4 processed datasets."),
]
DOC_PATHS = {
    "docs/data_dictionary.md",
    "docs/final_validation_summary.md",
    "docs/methodology.md",
    "docs/release_notes.md",
}


def digest(relative: str) -> str:
    h = hashlib.sha256()
    with (ROOT / relative).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        assert fields is not None
        existing = list(reader)

    skip = {path for path, _ in V4_DATASETS} | {path for path, _, _ in V4_SUPPORT}
    retained = []
    for row in existing:
        path = row["canonical_path"]
        if path in skip:
            continue
        if "_v3_20260712.csv" in path:
            row["role"] = row["role"].replace("Current canonical", "Historical canonical")
            row["notes"] = row["notes"].replace("currently approved", "historically approved")
            if "retained historically" not in row["notes"].lower():
                row["notes"] = row["notes"].rstrip(".") + "; retained historically after v4 approval."
        if path in DOC_PATHS:
            row["sha256"] = digest(path)
            row["source_zip"] = SOURCE
            row["source_internal_path"] = path
            row["approved_date"] = "2026-07-17"
            row["notes"] = row["notes"].rstrip(".") + "; updated for canonical v4."
        retained.append(row)

    new_rows = []
    for path, role in V4_DATASETS:
        district = "combined" if "sakhalin_1890" in path else "district"
        notes = (
            "Exact ordered concatenation of the three v4 district datasets; 36 columns; approved Items 1-23 consolidated."
            if district == "combined"
            else "Versioned 36-column quality-review consolidation; v3 retained historically."
        )
        new_rows.append(
            {"canonical_path": path, "source_zip": SOURCE, "source_internal_path": path,
             "sha256": digest(path), "role": role, "status": "approved", "approved_date": "2026-07-17", "notes": notes}
        )
    for path, role, notes in V4_SUPPORT:
        new_rows.append(
            {"canonical_path": path, "source_zip": SOURCE, "source_internal_path": path,
             "sha256": digest(path), "role": role, "status": "approved", "approved_date": "2026-07-17", "notes": notes}
        )

    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(new_rows + retained)


if __name__ == "__main__":
    main()
