# Script Update Summary

Updated after final Alexandrovsky manual review and completion of all three districts.

## Files updated

- `scripts/create_raw_records_from_pages_v3.py`
- `scripts/sakhalin_conversion_helpers_v12.py`
- `scripts/finalize_reviewed_clean_csv.py`
- `scripts/merge_clean_districts.py`

`scripts/sakhalin_conversion_helpers_v12.py` is the canonical helper module for this working core. The package also contained `scripts/sakhalin_conversion_helpers_v11.py`, but it was intentionally excluded because it is byte-for-byte identical to v12 and the newer scripts import v12.

## Main changes

1. Accepted all reviewed district-level values from Alexandrovsky, Tymovsky, and Korsakovsky as canonical for district clean-file QA.
2. Added high-confidence reusable normalization variants from Alexandrovsky manual review.
3. Added row-level post-processing hooks:
   - move trailing role leakage from `name_raw` to `family_status`;
   - split explanatory suffixes in `marriage_status` to `comments`;
   - split descriptive occupation suffixes to `comments`.
4. Added CSV delimiter auto-detection for comma and semicolon files.
5. Added support for UTF-8 files with or without BOM.
6. Added project-standard clean CSV export: comma-delimited, UTF-8, schema-ordered.
7. Restored `settlement_order` to two-digit text during standardization.
8. Added sorting by `district_code`, `settlement_order`, `person_order_in_settlement`.
9. Patched parser record-start detection for embedded records after archival references on the same line, e.g. `РГБ № 2009. 18. 2. ...`.
10. Added merger utility for all three district clean files with optional global `person_id` reassignment.

## Reviewed canonical value counts

| Field | Accepted unique values |
|---|---:|
| legal_status | 99 |
| family_status | 189 |
| religion | 13 |
| origin_place | 106 |
| marriage_status | 22 |
| literacy | 4 |
| allowance_status | 2 |

## Recommended usage

Standardize a reviewed Excel-exported CSV:

```bash
python scripts/finalize_reviewed_clean_csv.py   --input data/processed/clean_alexandrovsky_ru_reviewed.csv   --output data/processed/clean_alexandrovsky_ru.csv   --qa-json outputs/qa/qa_alexandrovsky_final_review.json
```

Merge final districts:

```bash
python scripts/merge_clean_districts.py   --inputs     data/processed/clean_alexandrovsky_ru.csv     data/processed/clean_tymovsky_ru.csv     data/processed/clean_korsakovsky_ru.csv   --output data/processed/clean_sakhalin_1890_ru.csv   --qa-json outputs/qa/qa_sakhalin_1890_report.json
```

## Scope note

The updated helper accepts reviewed district-level values as canonical. It does **not** force final cross-district grouping decisions. Broader analytical grouping should be performed later on the consolidated dataset.
