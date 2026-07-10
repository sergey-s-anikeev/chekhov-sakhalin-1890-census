# Decision Log

## Decision 1 — Authoritative package sources

- Date: 2026-07-10
- Decision: `final_sakhalin_1890_project_outputs.zip` and `final_scripts_update.zip` are the authoritative sources for the clean working core.
- Rationale: The project owner identified these packages as containing the latest validated datasets, scripts, documentation, and QA outputs.
- Affected files: Every canonical file listed in `canonical_manifest.csv`.
- Approval status: Approved by the project owner.

## Decision 2 — Canonical datasets

- Date: 2026-07-10
- Decision: Four CSV files are approved as canonical: the Alexandrovsky, Tymovsky, and Korsakovsky district datasets and the combined Sakhalin dataset.
- Rationale: Package validation confirmed a common 23-column schema, unique identifiers, expected row counts, and no full-row duplicates.
- Affected files: `data/processed/clean_alexandrovsky_ru.csv`, `data/processed/clean_tymovsky_ru.csv`, `data/processed/clean_korsakovsky_ru.csv`, `data/processed/clean_sakhalin_1890_ru.csv`.
- Approval status: Approved by the project owner.

## Decision 3 — District codes

- Date: 2026-07-10
- Decision: District code `1` identifies `Александровский`, code `2` identifies `Тымовский`, and code `3` identifies `Корсаковский`.
- Rationale: These mappings are present in the validated release and were explicitly approved by the project owner.
- Affected files: All four canonical processed datasets and their QA outputs.
- Approval status: Approved by the project owner.

## Decision 4 — Concatenation order

- Date: 2026-07-10
- Decision: The combined dataset must be the exact concatenation of Alexandrovsky, then Tymovsky, then Korsakovsky district records.
- Rationale: Validation confirmed that this order reproduces all 7,446 combined rows exactly, with no rows exclusive to either side.
- Affected files: The four canonical processed datasets and `scripts/merge_clean_districts.py`.
- Approval status: Approved by the project owner.

## Decision 5 — Canonical helper module

- Date: 2026-07-10
- Decision: `scripts/sakhalin_conversion_helpers_v12.py` is the canonical helper module.
- Rationale: v12 is the version imported by the newer scripts and is the latest named helper in the authoritative package.
- Affected files: `scripts/sakhalin_conversion_helpers_v12.py`, `scripts/create_raw_records_from_pages_v3.py`, and `scripts/finalize_reviewed_clean_csv.py`.
- Approval status: Approved by the project owner.

## Decision 6 — Exclusion of helper v11

- Date: 2026-07-10
- Decision: `scripts/sakhalin_conversion_helpers_v11.py` is not included in the clean working core.
- Rationale: v11 and v12 are byte-for-byte identical, while the newer scripts import v12. Including both would create an unnecessary duplicate and ambiguity.
- Affected files: `scripts/sakhalin_conversion_helpers_v11.py` and `scripts/sakhalin_conversion_helpers_v12.py`.
- Approval status: Approved by the project owner.

## Decision 7 — Historical project directory

- Date: 2026-07-10
- Decision: The old project directory remains unchanged as a historical archive.
- Rationale: It preserves provenance, prior iterations, manual-review packages, and audit evidence while the clean core is established separately.
- Affected files: All files outside `workspace_candidate/`.
- Approval status: Approved by the project owner.

## Decision 8 — Documentation language

- Date: 2026-07-10
- Decision: English is the canonical language for project documentation, reports, logs, comments, headings, descriptions, and status messages.
- Rationale: A single professional documentation language improves maintainability and review consistency.
- Affected files: Markdown, JSON narrative fields, QA narratives, logs, and future code comments.
- Approval status: Approved by the project owner.

## Decision 9 — Preservation of Russian values

- Date: 2026-07-10
- Decision: Russian historical values and normalized dataset values remain unchanged and must not be translated for documentation-language consistency.
- Rationale: These values carry source meaning, approved normalization decisions, and stable analytical categories.
- Affected files: All datasets and any documentation or QA output that quotes dataset values.
- Approval status: Approved by the project owner.
