# Chekhov Sakhalin 1890 Census

Historical data project based on Anton Chekhov’s 1890 Sakhalin census records.

The repository provides a reproducible person-level dataset, Python processing code, MySQL analysis, and CSV results prepared for Tableau visualization of population, settlements, legal status, age, literacy, family status, and migration origins.

## Purpose

The project transforms indexed historical census records into a structured flat dataset where one row represents one named person.

Russian/Cyrillic source and normalized values remain authoritative. English documentation explains the workflow, schema, QA, provenance, and release history.

## Current Status

**Ten named dashboards are published, as reported by the owner: settlement concentration, sex composition and combined legal/social status for all recorded people, adult literacy at ages 16+, recorded arrival years and household sizes/lodgers, plus four children’s dashboards covering age and sex (0–15), recorded literacy (5–15), settlement distribution (0–15), and recorded origin by age (0–15).** A two-group origin view also has an owner-supplied Tableau share link. Fifteen screenshots are saved. Action-plan items 1–7 are complete; item 8 is next. Owner review and updated screenshots confirm the age/literacy summary-filter corrections; independent live settlement-filter verification remains open. See the [visualization action plan](docs/tableau_visualization_action_plan.md), [children's findings and review](docs/children_findings.md), and [origin-by-age analysis](docs/children_origin_age_profile.md).

The [full inventory audit](outputs/qa/tableau_preflight_20261019_full_inventory/README.md), run on 2026-10-19, reconciled the 48 CSVs present then: 42 current-query matches, four documented variants and two known legacy exclusions. Two children's origin-by-age exports were [registered separately on 2026-10-27](outputs/qa/children_origin_age_export_20261027/validation.json), bringing the current inventory to 50. Source hashes and all retained practice-file values are unchanged.

| Stage | Status | Result |
|---|---|---|
| Extraction, cleaning, and Russian canonical release | Complete | Reviewed `v5_20260731` release, integrated QA, and manifest registration |
| English analytical dataset | Approved; QA complete | 7,446 records and 23 columns in `sakhalin_1890_en_v1.csv` |
| MySQL import and validation | Complete | 7,446 loaded rows, zero skipped records or warnings, and all validation controls passed |
| SQL analysis and visualization exports | In progress | Demographic and extended analytical queries; 50 CSV snapshots in `tableau/data/`; selected new origin views still await exports |
| Tableau source validation and dashboards | In progress | Ten named dashboards published (owner report), plus one shared two-group origin view; fifteen screenshots saved; action-plan items 1–7 complete |
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

Household sizes and recorded lodgers completed on 2026-10-30: [published dashboard](https://public.tableau.com/views/Sakhalin1890Householdsizesandrecordedlodgers/Sakhalin1890Householdsizesandrecordedlodgers), [screenshot](tableau/screenshots/households_lodgers_20261030.png), and [scope/calculations](docs/households_lodgers_tableau.md). Size bars cover 2,796 household groups; one-/two-person groups account for 62.1%. The all-settlement lodger indicator is 11.4%; a District filter applies only to the settlement comparison. Item 6 is complete; item 8, the historical origin map, remains planned. Screenshot inspected locally; live interactions were not independently inspected.

Recorded arrival years completed on 2026-10-29: [published dashboard](https://public.tableau.com/views/Sakhalin1890Recordedarrivalyears/Sakhalin1890Recordedarrivalyears), [screenshot](tableau/screenshots/arrival_years_20261029.png), and [scope/evidence](docs/arrival_years_tableau.md). Bars and a decade heatmap show 4,826 records with an arrival year, including the largest group in 1884 (548; 11.4%). Coverage and retrospective-count caveats are displayed. Item 5 is complete; item 6, household size and lodgers, is next.

Adult literacy by sex completed on 2026-10-29: [published dashboard](https://public.tableau.com/views/Sakhalin1890Recordedadultliteracybysex/Sakhalin1890Recordedadultliteracybysex), [screenshot](tableau/screenshots/adult_literacy_by_sex_20261029.png), and [scope/denominator record](docs/adult_literacy_tableau.md). Counts and both percentage views cover 5,832 people aged 16+; 787 have no literacy recorded. Item 4 is complete; item 5, recorded arrival years, is next. The saved screenshot was inspected locally; live connections and tooltips were not inspected.

Combined legal and social status groups completed on 2026-10-28: [published pie dashboard](https://public.tableau.com/views/Sakhalin1890Combinedlegalandsocialstatusgroups/Sakhalin1890Combinedlegalandsocialstatusgroups), [screenshot](tableau/screenshots/legal_status_groups_20261028.png), and [group definitions/historical context](docs/legal_status_tableau.md). All 7,446 records are represented in five groups, including 117 Other (24 missing). The detailed bars were completed during authoring according to the owner. Item 3 is complete; item 4, adult literacy, is next.

Sex composition by district and recorded ages completed on 2026-10-28: [published dashboard](https://public.tableau.com/views/Sakhalin1890Sexcompositionbydistrictandrecordedages/Sakhalin1890Sexcompositionandrecordedages), [saved screenshot](tableau/screenshots/sex_composition_recorded_ages_20261028.png). The screenshot shows Female 2,525 and Male 4,921, the District filter and fixed all-district median/coverage notes. The URL and filter behavior are owner-reported; the screenshot was inspected locally. Items 2 and 3 are complete; item 4, adult literacy, is next.

Settlement concentration for all recorded people completed on 2026-10-28: [published dashboard](https://public.tableau.com/views/Sakhalin1890Settlementconcentration/Settlementconcentration), [saved screenshot](tableau/screenshots/settlement_concentration_20261028.png). It shows ranked settlement counts, a District filter and selected-population total, plus a fixed top-five note for all districts: 4,046 / 7,446 (54.3%). The owner supplied the URL and completed the filter setup; the screenshot was inspected locally. Independent live interactions and workbook connections were not inspected. [Action-plan item 1](docs/tableau_visualization_action_plan.md) is complete; item 2, sex composition and recorded ages, is next.

Settlement dashboard completed by the owner on 2026-10-14; [screenshot](tableau/screenshots/children_by_settlement_20261014.png) inspected and 51-row export verified. Published dashboard: [Sakhalin 1890 — Children by settlement](https://public.tableau.com/views/Sakhalin1890Childrenbysettlement/Sakhalin1890Childrenbysettlement). URL supplied by the owner on 2026-10-14; recorded in documentation on 2026-10-19.

**Children's block:** Decision 40 approves **Children aged 0–15**. Both child queries are corrected, and their replacement exports are registered in [the export inventory](tableau/data/README.md). Use [the standalone SQL](sql/05_children_0_15_queries.sql) to reproduce them. Expected total: 1,467 children (726 female, 741 male). Earlier child exports use different age ranges and remain historical. See [correction QA](outputs/qa/children_0_15_20261012/README.md). Both replacement CSVs match the corrected queries. Published dashboard: [Sakhalin 1890 — Children aged 0–15](https://public.tableau.com/views/Sakhalin1890Childrenaged015/Dashboard1). The owner supplied this link on 2026-10-13; the published view has not been independently inspected.

Start local practice with [`tableau/practice/sakhalin_1890_en_no_full_name_20261004.csv`](tableau/practice/sakhalin_1890_en_no_full_name_20261004.csv): all 7,446 people and 22 columns, omitting only full_name. It retains linkable identifiers and is not an anonymous public-release file. Use the [Tableau preparation guide](docs/tableau_preparation.md) for import types, denominators, household grouping, legacy-export selection, and aggregate-only public dashboard recommendations. The [preflight report](outputs/qa/tableau_preflight_20261004/README.md) records snapshot reconciliation and exact retained-value verification.

The [analytical export inventory](tableau/data/README.md) describes all **50 CSV snapshots**: the earlier 48 plus two children’s origin-by-age results registered on 2026-10-27. It records their row counts, analytical scope, percentage denominators, and known differences from current SQL. Some snapshots are earlier or manual query variants; selected child-origin and two extended queries do not yet have corresponding CSV exports.

Published literacy analysis: children’s recorded literacy by age and sex. Decision 42 focuses its visualization on ages 5–15 using a Tableau filter; the export retains ages 0–15. Use the [export and browser-authoring instructions](docs/children_literacy_tableau.md) and [read-only SQL](sql/06_children_literacy_queries.sql). Published literacy dashboard: [Recorded literacy among children aged 5–15](https://public.tableau.com/views/Recordedliteracyamongchildrenaged515/Dashboard1). The saved literacy CSV matches the SQL locally; owner review and updated screenshot checks are complete.

Published origin-by-age analysis: the [detailed dashboard](https://public.tableau.com/views/ChildrensrecordedoriginbyageSakhalin1890/Dashboard1) separates On Sakhalin, recorded origin elsewhere, In transit and origin not recorded. The [earlier two-group view](https://public.tableau.com/shared/ZMWP4CSS2) combines the latter three categories as all other origin records. Both links were supplied by the owner on 2026-10-27; the [detailed screenshot](tableau/screenshots/children_origin_by_age_full_20261027.png) and [two-group screenshot](tableau/screenshots/children_origin_by_age_20261027.png) were inspected locally, but the live Tableau pages and workbook connections were not independently checked. The detailed view flags age eight: 52 of 54 children have no recorded origin. See [analysis, CSV sources and interpretation](docs/children_origin_age_profile.md).

On 2026-10-27, the owner paused further review and CSV extracts. The remaining project steps are:

1. Follow the agreed [eight-item Tableau visualization action plan](docs/tableau_visualization_action_plan.md): the original six whole-population figures, the completed children's segment, and a planned historical Russian Empire origin map.
2. Select the main findings from the published dashboards and finish the project narrative.
3. If review resumes, verify the live District filter on the settlement dashboard and published workbook connections; see [the settlement guide](docs/children_settlements_tableau.md). Resume further SQL exports only if the owner requests them. A numerical comparison with Chekhov’s published figures is outside the current plan.

The [development tracker](docs/english_dataset_development_tracker.md) records ten named dashboards, the additional two-group origin view, the owner review and fifteen screenshots. Summary-filter corrections are verified in the updated screenshots. No packaged Tableau workbook is stored in this repository.

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
        └── <48 analytical CSV exports>
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

Further Tableau dashboards and the final visual presentation are the next deliverables.

## Data Availability

This repository includes the reviewed Russian processed datasets, the approved English analytical dataset, code, SQL scripts, 48 analytical CSV snapshots, documentation, QA outputs, and a 500-record sample.

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
