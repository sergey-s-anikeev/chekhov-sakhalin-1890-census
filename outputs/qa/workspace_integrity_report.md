# Workspace Integrity Report

Generated: `2026-07-10T15:56:56+06:00`

Overall status: **passed**

This report validates the clean working core assembled from the two owner-approved priority packages. Project data-processing scripts were not executed.

## Passed checks

- Every approved canonical file was hashed and reconciled with its extracted source and the package-validation inventory; the only hash divergence is the authorized documentation revision to script_update_summary.md.
- All canonical datasets and Python scripts are byte-for-byte identical to the authoritative package copies and validation hashes.
- All four canonical Python scripts pass AST syntax validation without execution.
- The combined CSV is the exact row-wise concatenation of Alexandrovsky, Tymovsky, and Korsakovsky district CSVs in the owner-approved order.
- District codes and Russian district values match the owner-approved mappings.
- The packaged v11 and v12 helper modules are byte-for-byte identical; only v12 is included in the clean core.
- Canonical Markdown headings, explanatory prose, QA narratives, and human-readable JSON status fields are in English; Russian occurrences are preserved dataset or historical values.
- No Russian dataset value was translated or modified; dataset hashes are unchanged from the authoritative package.
- All 716 files in the pre-existing audited project baseline retain their recorded SHA-256 hashes.

## Warnings

- `scripts/create_raw_records_from_pages_v3.py` imports `fitz` (PyMuPDF), which is not available in the current validation runtime. The script was not executed; this dependency must be provisioned before a future approved extraction run.
- script_update_summary.md has a new canonical hash because it was deliberately revised to document the owner-approved v12 selection and v11 exclusion; its source-package hash remains recorded.
- Canonical documentation contains Cyrillic only where it quotes approved district names, historical values, normalized values, settlement names, or archive references. These occurrences were intentionally preserved.

## Unresolved issues

- None.

## Owner decisions required

- No additional owner decision is required to assemble the approved clean core.
- Before any future extraction run, the owner must approve an isolated runtime setup that provides the `fitz` module through PyMuPDF.
- Future substantive normalization changes still require an owner-approved plan, record list, diff, and QA results.
- Any future replacement of a canonical file requires explicit owner approval and a manifest update.

## Canonical file hash reconciliation

| Canonical path | Source hash match | Validation hash match | Status |
|---|---:|---:|---|
| `data/processed/clean_alexandrovsky_ru.csv` | yes | yes | passed |
| `data/processed/clean_tymovsky_ru.csv` | yes | yes | passed |
| `data/processed/clean_korsakovsky_ru.csv` | yes | yes | passed |
| `data/processed/clean_sakhalin_1890_ru.csv` | yes | yes | passed |
| `scripts/create_raw_records_from_pages_v3.py` | yes | yes | passed |
| `scripts/finalize_reviewed_clean_csv.py` | yes | yes | passed |
| `scripts/merge_clean_districts.py` | yes | yes | passed |
| `scripts/sakhalin_conversion_helpers_v12.py` | yes | yes | passed |
| `docs/data_dictionary.md` | yes | yes | passed |
| `docs/final_validation_summary.md` | yes | yes | passed |
| `docs/methodology.md` | yes | yes | passed |
| `docs/release_notes.md` | yes | yes | passed |
| `docs/script_update_summary.md` | no | no | passed_with_authorized_revision |
| `outputs/qa/district_record_count_summary.csv` | yes | yes | passed |
| `outputs/qa/qa_sakhalin_1890_report.json` | yes | yes | passed |
| `outputs/qa/qa_sakhalin_1890_report.md` | yes | yes | passed |
| `outputs/qa/settlement_sequence_validation.csv` | yes | yes | passed |
| `outputs/qa/updated_scripts_validation_summary.json` | yes | yes | passed |

## Python static validation

| Script | Syntax | Imports resolved |
|---|---:|---:|
| `scripts/create_raw_records_from_pages_v3.py` | passed | no |
| `scripts/finalize_reviewed_clean_csv.py` | passed | yes |
| `scripts/merge_clean_districts.py` | passed | yes |
| `scripts/sakhalin_conversion_helpers_v12.py` | passed | yes |

## Combined dataset validation

- Combined rows: **7446**.
- Sum of district rows: **7446**.
- Exact concatenation in approved order: **yes**.
- Approved order: Alexandrovsky, Tymovsky, Korsakovsky.

## Preservation and language validation

- Canonical datasets and scripts retain the authoritative package hashes.
- English is used for canonical explanatory documentation and human-readable QA narratives.
- Russian district names, historical values, normalized values, settlement names, and archive references were preserved and were not treated as documentation-language defects.

## Historical project boundary

- Audited baseline files checked: **716**.
- All baseline hashes unchanged: **yes**.
- No Git repository was created.
- No project data-processing script was executed.
