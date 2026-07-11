# Chekhov Sakhalin 1890 Census

Historical data project based on Anton Chekhov’s 1890 Sakhalin census records.

The repository provides a reproducible person-level dataset and supporting code for demographic, settlement-level, legal-status, age, literacy, family-status, and migration-origin analysis using Python, SQL, and Tableau.

## Purpose

The project transforms indexed historical census records into a structured flat dataset where one row represents one named person.

Russian/Cyrillic source and normalized values remain authoritative. English documentation explains the workflow, schema, QA, provenance, and release history.

## Current Status

The project has completed district-level extraction, normalization, manual review, final merge, and project-level QA.

The current validated release contains:

- Alexandrovsky District: **2,884** records
- Tymovsky District: **3,242** records
- Korsakovsky District: **1,320** records
- Combined Sakhalin dataset: **7,446** records

The combined dataset is the exact row-wise concatenation of the three reviewed district datasets in this order:

1. Alexandrovsky
2. Tymovsky
3. Korsakovsky

`person_id` is assigned globally from `P000001` to `P007446`.

`source_position_id` remains the stable source-navigation identifier.

## GitHub Repository Workflow

This repository is connected to the project’s GitHub remote for version control and collaboration. The `main` branch represents the approved project state and tracks the configured `origin` remote.

GitHub workflow rules:

- Review local changes before committing or pushing them.
- Keep source files and approved canonical datasets immutable.
- Create new versioned files or release packages for proposed data results; never overwrite a canonical file in place.
- Attach a SHA-256 hash, QA results, and a record-level diff to every proposed replacement.
- Update `docs/canonical_manifest.csv` only after the project owner approves the new canonical version.
- Keep raw PDFs, ZIP packages, and sensitive material excluded through `.gitignore` and the documented publication policy.
- Confirm repository visibility, copyright, access, and ethical-release constraints before publishing new historical or person-level material.

The GitHub repository is a version-control mirror, not a substitute for owner approval or the project’s provenance and QA records.

## Canonical Datasets

Current versioned canonical release, approved 2026-07-11:

- `data/processed/clean_alexandrovsky_ru_v2_20260711.csv`
- `data/processed/clean_tymovsky_ru_v2_20260711.csv`
- `data/processed/clean_korsakovsky_ru_v2_20260711.csv`
- `data/processed/clean_sakhalin_1890_ru_v2_20260711.csv`

The prior unversioned canonical files remain unchanged as historical release artifacts.

The `district` field retains the approved Russian values:

```text
Александровский
Тымовский
Корсаковский
```

These values must not be translated or altered in the canonical Russian datasets.

## Main Scripts

- `scripts/create_raw_records_from_pages_v3.py` — extracts structured raw person records from searchable PDF page text.
- `scripts/finalize_reviewed_clean_csv.py` — standardizes an owner-reviewed district CSV and produces QA metadata.
- `scripts/merge_clean_districts.py` — merges the three canonical district datasets and can reassign global `person_id` values.
- `scripts/sakhalin_conversion_helpers_v12.py` — canonical parsing, normalization, controlled-vocabulary, transformation, and QA helpers.
- `scripts/apply_manual_anomaly_decisions.py` — applies documented manual anomaly decisions.
- `scripts/run_sample_pipeline.py` — runs the sample extraction and QA workflow.
- `scripts/extract_pdf_text.py` — extracts text from source PDF files.

## Project Documentation

- [Statement of Work](docs/SOW.md)
- [Source Note](docs/source_note.md)
- [Data Dictionary](docs/data_dictionary.md)
- [Methodology](docs/methodology.md)
- [Limitations](docs/limitations.md)
- [QA Plan](docs/qa_plan.md)
- [Final Validation Summary](docs/final_validation_summary.md)
- [Release Notes](docs/release_notes.md)
- [Decision Log](docs/decision_log.md)
- [Canonical Manifest](docs/canonical_manifest.csv)
- [Project Rules](PROJECT_RULES.md)

## QA Outputs

Project-level QA outputs include:

- `outputs/qa/qa_sakhalin_1890_report.md`
- `outputs/qa/qa_sakhalin_1890_report.json`
- `outputs/qa/settlement_sequence_validation.csv`
- `outputs/qa/district_record_count_summary.csv`
- `outputs/qa/updated_scripts_validation_summary.json`
- `outputs/qa/workspace_integrity_report.md`
- `outputs/qa/workspace_integrity_report.json`

Additional sample and anomaly-review outputs are retained in `outputs/qa/`.

## Repository Structure

```text
chekhov-sakhalin-1890-census/
├── README.md
├── PROJECT_RULES.md
├── data/
│   └── processed/
│       ├── clean_alexandrovsky_ru.csv
│       ├── clean_tymovsky_ru.csv
│       ├── clean_korsakovsky_ru.csv
│       ├── clean_sakhalin_1890_ru.csv
│       └── clean_sample_500.csv
├── docs/
│   ├── SOW.md
│   ├── source_note.md
│   ├── data_dictionary.md
│   ├── methodology.md
│   ├── limitations.md
│   ├── qa_plan.md
│   ├── final_validation_summary.md
│   ├── release_notes.md
│   ├── script_update_summary.md
│   ├── decision_log.md
│   ├── canonical_manifest.csv
│   ├── language_translation_strategy.md
│   ├── change_notes/
│   └── reference/
├── notebooks/
├── outputs/
│   └── qa/
├── scripts/
├── sql/
└── tableau/
```

## Processing Layers

The project distinguishes four information layers:

- **Source data** preserves documentary evidence and extraction context and must remain immutable.
- **Processed data** contains reviewed, normalized person-level records approved for the current release.
- **QA outputs** record structural checks, counts, identifier validation, and sequence validation for specific artifacts.
- **Documentation** records methodology, field definitions, decisions, provenance, and release history.

## Safe Working Procedure

1. Read `PROJECT_RULES.md`, `docs/decision_log.md`, and the relevant methodology before proposing a change.
2. Identify affected records through stable identifiers.
3. Work from copies or reproducible source inputs.
4. Do not manually edit canonical processed CSV files.
5. Implement substantive data changes through a versioned script or explicit correction table.
6. Write derived outputs to a new reviewable location.
7. Compare the result with the prior canonical artifact and provide a record-level diff.
8. Run the applicable QA checks and document the results.
9. Request owner approval before replacing or designating a new canonical artifact.

### Versioning rule

Canonical files are immutable release artifacts. A new processing result must be written as a new versioned file or release package; the existing canonical file is never overwritten in place. After review, update `docs/canonical_manifest.csv` with the new path, SHA-256, source package, approval date, and status. Only the project owner may approve which version becomes canonical. Older canonical versions remain available as historical records unless the owner explicitly authorizes their removal.

All substantive normalization decisions require explicit approval from the project owner. Ambiguous historical evidence must be sent for manual review.

> **Warning:** Manual editing of processed CSV files breaks reproducibility and may damage identifiers, ordering, quoting, encoding, or historical values.

## Reproducing Derived Outputs

Use an isolated working directory and copies of the canonical inputs.

The documented merge inputs are:

```text
data/processed/clean_alexandrovsky_ru.csv
data/processed/clean_tymovsky_ru.csv
data/processed/clean_korsakovsky_ru.csv
```

Run scripts only after reviewing their command-line arguments and the applicable project rules.

Direct outputs to a new staging directory, recalculate SHA-256 hashes, compare the merged output with the ordered district concatenation, run QA, and review the resulting diff before replacing any canonical artifact.

## Language and Analytical Layers

The canonical data layer remains Russian.

Later analytical layers may add:

- transliterated personal names;
- English translations of controlled categories;
- SQL-ready analytical tables;
- Tableau extracts and dashboards;
- aggregate demographic and migration-origin outputs.

Personal names are transliterated, not translated.

## Data Availability

This repository includes the reviewed processed datasets, code, documentation, QA outputs, and a 500-record sample.

The original source PDFs and full raw extracted text are not included here unless copyright, access, provenance, and ethical considerations permit publication.

## Data Publication Note

The repository is intended for reproducible historical data analysis and portfolio demonstration.

Published artifacts may include:

- reviewed person-level processed datasets;
- scripts and transformation logic;
- QA reports;
- documentation;
- aggregate analytical outputs;
- SQL queries;
- Tableau workbooks or dashboard screenshots;
- small samples where appropriate.

Any publication of source scans, raw extraction layers, or additional person-level material should follow the documented provenance, copyright, access, and ethical review process.
