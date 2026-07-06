# QA Plan

## Purpose

This document describes quality-assurance checks for the Chekhov Sakhalin 1890 Census dataset.

The goal is to ensure that extracted records are traceable, structurally valid, and ready for SQL analysis and visualization.

## QA Stages

The QA process is divided into four stages:

1. Source extraction QA
2. Raw split-record QA
3. Final CSV structural QA
4. Analytical-readiness QA

## 1. Source Extraction QA

Check whether extracted text preserves the source structure well enough for record-level parsing.

Review:

- printed book page numbers;
- settlement headings;
- repeated running headers;
- field numbers;
- person-record boundaries;
- footnote artifacts;
- broken or merged text.

Expected outcome:

- page text can be linked to printed book page numbers;
- running headers and repeated headings are removed before person-level conversion;
- ambiguous pages are flagged for manual review.

## 2. Raw Split-Record QA

The raw split-record CSV should preserve source-derived values before final normalization.

Check:

- one row represents one person;
- required raw fields are present;
- source page number is present;
- settlement name is present;
- household number is present where available;
- source field values have not shifted into the wrong columns;
- unclear values are preserved rather than guessed.

## 3. Final CSV Hard Checks

The final CSV must pass the following checks:

1. `person_id` is present and unique.
2. `source_position_id` is present and unique.
3. Every `settlement` maps to one valid `district`, `district_code`, and `settlement_order`.
4. Required final CSV fields are present.
5. `page_number` is numeric where present.
6. `age` is numeric where present.
7. `arrival_year` is numeric where present.
8. `literacy` uses controlled values.
9. `marriage_status` uses controlled values.
10. `allowance_status` uses `TRUE` / `FALSE` values.
11. No `<...>` angle-bracket markup remains in cleaned fields.
12. No `[...]` square-bracket markup remains in cleaned fields.
13. Trailing bare footnote digits do not remain in normalized text fields except `comments` and `notes_raw`.
14. `notes_raw` follows the expected archive-number pattern where present.

## 4. Soft Checks for Manual Review

The following values are not automatically treated as errors, but must be reviewed:

1. Unknown `legal_status` values.
2. Unknown `family_status` values.
3. Unknown `religion` values.
4. Unknown `origin_place` values.
5. Religion values that look like years or numeric values.
6. Origin-place values that look like occupations.
7. New historical spellings or administrative units.
8. Any field value that appears displaced from another source field.
9. Non-numeric household numbers used in `source_position_id`.
10. Records with missing page numbers or uncertain settlement assignment.

## Manual Review Output

The QA process should produce a list of records requiring review with:

- `person_id`;
- `source_position_id`;
- `page_number`;
- `settlement`;
- `name_raw`;
- field name;
- suspicious value;
- reason for review;
- proposed correction, if any;
- reviewer decision.

## Sample QA Goal

Before full-scale extraction, the 300–500 record sample should be checked for:

- extraction completeness;
- field consistency;
- category coverage;
- unknown values;
- likely source anomalies;
- manual-correction workload.

```
500 record sample results:
Unknown origin places: 0
Unknown legal statuses: 0
Unknown family statuses: 0
Unknown religions: 0
Unresolved source anomalies: 0
Confirmed source anomalies preserved as printed: 1
```
## QA Success Criteria for MVP

The MVP sample is considered ready for analysis when:

- all records have `person_id` and `source_position_id`;
- all records have page-number traceability;
- all settlements map to the locality lookup;
- hard validation errors are resolved;
- unresolved soft-check values are documented;
- controlled vocabularies are updated where appropriate;
- the final sample can be loaded into SQL without structural errors.
