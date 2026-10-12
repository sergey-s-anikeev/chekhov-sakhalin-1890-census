# Chekhov Sakhalin 1890 Census

Historical data project based on Anton Chekhov’s 1890 Sakhalin census records.

The repository provides a reproducible person-level dataset, Python processing code, MySQL analysis, and CSV results prepared for Tableau visualization of population, settlements, legal status, age, literacy, family status, and migration origins.

## Purpose

The project transforms indexed historical census records into a structured flat dataset where one row represents one named person.

Russian/Cyrillic source and normalized values remain authoritative. English documentation explains the workflow, schema, QA, provenance, and release history.

## Current Status

**SQL analysis and Tableau source preparation are complete. Tableau import validation and dashboard construction remain pending.** The historical SQL snapshots run through 2026-09-08; the names-free practice source was prepared on 2026-10-04 and rechecked with exact import benchmarks on 2026-10-12. See the [latest preparation report](outputs/qa/tableau_preflight_20261012/README.md).

| Stage | Status | Result |
|---|---|---|
| Extraction, cleaning, and Russian canonical release | Complete | Reviewed `v5_20260731` release, integrated QA, and manifest registration |
| English analytical dataset | Approved; QA complete | 7,446 records and 23 columns in `sakhalin_1890_en_v1.csv` |
| MySQL import and validation | Complete | 7,446 loaded rows, zero skipped records or warnings, and all validation controls passed |
| SQL analysis and visualization exports | Complete | Demographic and extended analytical queries; 44 dated CSV snapshots in `tableau/data/` |
| Tableau source validation and dashboard | Pending | Import checks, charts, filters, and reconciliation to SQL totals |
| Final findings and portfolio presentation | Pending | Analytical summary, dashboard screenshots, and final project narrative |

The Russian canonical release `v5_20260731` retains the validated v4 analytical data, incorporates the approved Item 24 comment corrections, and adds the fully reviewed name-component and provenance structure.

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

## English Dataset and SQL Analysis

The approved [English analytical dataset](data/analytical/sakhalin_1890_en_v1.csv) is a separate 23-column analytical layer built from Russian canonical v5 plus documented, owner-approved staged corrections. Personal names are transliterated, and categories and places use approved English mappings. Field-level QA confirmed exact row-order reconciliation, unique identifiers, zero unmapped populated values, zero Cyrillic cells, and zero transformation mismatches.

The MySQL workflow is documented in [the import guide](docs/mysql_english_dataset_import.md):

1. [Create the analytical table](sql/01_create_english_dataset.sql).
2. [Load the English CSV](sql/02_load_english_dataset.sql), converting empty nullable fields to SQL `NULL` and allowance values to `1`, `0`, or `NULL`.
3. [Validate the loaded dataset](sql/03_validate_english_dataset.sql).
4. [Run analytical queries](sql/04_analysis_queries.sql) and export the required results.

Analysis covers population by district and settlement, age and sex, legal status, literacy, occupations, migration origins and arrival years, household sizes and lodgers, allowance, illness, and field completeness. Extended queries examine adult literacy by age band, allowance by legal status and arrival cohort, origin concentration and diversity, household status composition, recorded Sakhalin marriages, literacy by occupation, and origins in the Kingdom of Poland under historical boundaries.

## Visualization Exports and Next Steps

Start local practice with [`tableau/practice/sakhalin_1890_en_no_full_name_20261004.csv`](tableau/practice/sakhalin_1890_en_no_full_name_20261004.csv): all 7,446 people and 22 columns, omitting only full_name. It retains linkable identifiers and is not an anonymous public-release file. Use the [Tableau preparation guide](docs/tableau_preparation.md) for import types, denominators, household grouping, legacy-export selection, and aggregate-only public dashboard recommendations. The [preflight report](outputs/qa/tableau_preflight_20261004/README.md) records snapshot reconciliation and exact retained-value verification.

The [analytical export inventory](tableau/data/README.md) describes all **44 CSV snapshots**, exported on 2026-08-22, 2026-08-28, 2026-09-01, 2026-09-07, and 2026-09-08. It records each file's row count, analytical scope, percentage denominators, and known differences from the current SQL. Some snapshots are earlier or manual query variants; two extended queries do not yet have corresponding CSV exports.

The next steps are:

1. Select the main analytical findings and the charts needed to explain them.
2. Import the relevant CSVs into Tableau and verify field types, dimensions, missing values, aggregations, and totals against the saved results and SQL.
3. Build the charts and dashboard, then validate filters and percentage denominators.
4. Add dashboard screenshots, the final analytical findings, limitations, and a portfolio-ready project description.

Tableau source validation remains pending in the [development tracker](docs/english_dataset_development_tracker.md). No Tableau workbook or packaged dashboard is currently present in this repository.

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

Current versioned canonical release, approved 2026-07-31:

- `data/processed/clean_alexandrovsky_ru_v5_20260731.csv`
- `data/processed/clean_tymovsky_ru_v5_20260731.csv`
- `data/processed/clean_korsakovsky_ru_v5_20260731.csv`
- `data/processed/clean_sakhalin_1890_ru_v5_20260731.csv`

The v5 release contains 50 columns. It preserves the 36-column v4 structure and adds reviewed name components, component provenance, parsing status and confidence, parsing rules, detected order, naming model, manual-review reason, and proposal-audit fields. The v4, v3, v2, and prior unversioned canonical files remain unchanged as historical release artifacts.

The canonical v4 schema includes `age_months` for infant and young-child analysis. Explicit source precision takes precedence: for example, 1 year 7 months is stored as `age = 1`, `age_months = 19`. When the source gives only the completed whole-year age, month values are analytically derived as `12` for `age = 1` and `24` for `age = 2`.

The approved Item 24 stage contributes exactly 56 `comments` changes to v5. The reviewed name stage contributes the resolved name components and owner-approved corrections. All 7,446 records have `parse_status = observed` and no unresolved name proposals.

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
- [English Dataset Development Tracker](docs/english_dataset_development_tracker.md)
- [MySQL Import and Validation Guide](docs/mysql_english_dataset_import.md)
- [English Dataset Field Lineage](docs/english_dataset_field_lineage.md)
- [Analytical Export Inventory](tableau/data/README.md)
- [Tableau Preparation and Publication](docs/tableau_preparation.md)
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
│   ├── analytical/
│   │   └── sakhalin_1890_en_v1.csv
│   └── processed/
│       ├── clean_alexandrovsky_ru_v5_20260731.csv
│       ├── clean_tymovsky_ru_v5_20260731.csv
│       ├── clean_korsakovsky_ru_v5_20260731.csv
│       └── clean_sakhalin_1890_ru_v5_20260731.csv
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
│   ├── 01_create_english_dataset.sql
│   ├── 02_load_english_dataset.sql
│   ├── 03_validate_english_dataset.sql
│   └── 04_analysis_queries.sql
└── tableau/
    └── data/
        ├── README.md
        └── <44 dated analytical CSV exports>
```

## Processing Layers

The project distinguishes five information layers:

- **Source data** preserves documentary evidence and extraction context and must remain immutable.
- **Processed data** contains reviewed, normalized person-level records approved for the current release.
- **Analytical data** contains the approved English person-level dataset, its MySQL representation, and derived CSV query snapshots for visualization.
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
data/processed/clean_alexandrovsky_ru_v5_20260731.csv
data/processed/clean_tymovsky_ru_v5_20260731.csv
data/processed/clean_korsakovsky_ru_v5_20260731.csv
```

Run scripts only after reviewing their command-line arguments and the applicable project rules.

Direct outputs to a new staging directory, recalculate SHA-256 hashes, compare the merged output with the ordered district concatenation, run QA, and review the resulting diff before replacing any canonical artifact.

## Language and Analytical Layers

The canonical data layer remains Russian.

The completed English and SQL analytical layers provide:

- transliterated personal names;
- English translations of controlled categories;
- SQL-ready analytical tables;
- CSV snapshots prepared for Tableau visualization;
- aggregate demographic and migration-origin outputs.

Personal names are transliterated, not translated.

Tableau dashboards and the final visual presentation are the next deliverables.

## Data Availability

This repository includes the reviewed Russian processed datasets, the approved English analytical dataset, code, SQL scripts, 44 analytical CSV snapshots, documentation, QA outputs, and a 500-record sample.

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
