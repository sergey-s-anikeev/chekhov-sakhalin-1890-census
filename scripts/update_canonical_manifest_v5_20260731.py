#!/usr/bin/env python3
"""Register canonical v5 and retain earlier canonical releases historically."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/canonical_manifest.csv"
SOURCE = "owner_approved_reviewed_name_release_20260731"
APPROVED_DATE = "2026-07-31"
DATASETS = [
    ("data/processed/clean_alexandrovsky_ru_v5_20260731.csv", "Current canonical processed dataset for Alexandrovsky District"),
    ("data/processed/clean_tymovsky_ru_v5_20260731.csv", "Current canonical processed dataset for Tymovsky District"),
    ("data/processed/clean_korsakovsky_ru_v5_20260731.csv", "Current canonical processed dataset for Korsakovsky District"),
    ("data/processed/clean_sakhalin_1890_ru_v5_20260731.csv", "Current canonical combined processed dataset"),
]
SUPPORT = [
    (
        "scripts/build_canonical_v5_20260731.py",
        "Canonical v5 consolidation script",
        "Combines approved Item 24 comments with the final reviewed-name stage and writes district and combined v5 files.",
    ),
    (
        "outputs/qa/canonical_v5_20260731/canonical_v5_qa_report.json",
        "Canonical v5 machine-readable QA report",
        "All integrated hard release checks passed.",
    ),
    (
        "outputs/qa/canonical_v5_20260731/canonical_v5_hashes.csv",
        "Canonical v5 release hash table",
        "SHA-256 hashes for all four v5 processed datasets.",
    ),
]
DOCS = {
    "README.md",
    "docs/data_dictionary.md",
    "docs/final_validation_summary.md",
    "docs/methodology.md",
    "docs/normalization_review_tracker.md",
    "docs/release_notes.md",
}


def digest(relative: str) -> str:
    result = hashlib.sha256()
    with (ROOT / relative).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def main() -> None:
    with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        existing = list(reader)

    v5_paths = {path for path, _ in DATASETS} | {path for path, _, _ in SUPPORT}
    retained = []
    for row in existing:
        path = row["canonical_path"]
        if path in v5_paths:
            continue
        if "_v4_20260717.csv" in path:
            row["role"] = row["role"].replace("Current canonical", "Historical canonical")
            if "retained historically after v5 approval" not in row["notes"]:
                row["notes"] = row["notes"].rstrip(".") + "; retained historically after v5 approval."
        if path in DOCS:
            row["sha256"] = digest(path)
            row["source_zip"] = SOURCE
            row["source_internal_path"] = path
            row["approved_date"] = APPROVED_DATE
            if "updated for canonical v5" not in row["notes"]:
                row["notes"] = row["notes"].rstrip(".") + "; updated for canonical v5."
        retained.append(row)

    new_rows = []
    for path, role in DATASETS:
        combined = "sakhalin_1890" in path
        notes = (
            "Exact ordered concatenation of the three v5 district datasets; 50 columns; approved Item 24 and reviewed-name workflow consolidated."
            if combined
            else "Versioned 50-column reviewed-name release; v4 retained historically."
        )
        new_rows.append({
            "canonical_path": path,
            "source_zip": SOURCE,
            "source_internal_path": path,
            "sha256": digest(path),
            "role": role,
            "status": "approved",
            "approved_date": APPROVED_DATE,
            "notes": notes,
        })
    for path, role, notes in SUPPORT:
        new_rows.append({
            "canonical_path": path,
            "source_zip": SOURCE,
            "source_internal_path": path,
            "sha256": digest(path),
            "role": role,
            "status": "approved",
            "approved_date": APPROVED_DATE,
            "notes": notes,
        })

    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(new_rows + retained)


if __name__ == "__main__":
    main()
