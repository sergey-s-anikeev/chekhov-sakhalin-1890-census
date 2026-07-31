# Final Validation Summary

This release contains the reviewed Russian master dataset for the 1890 Sakhalin census records extracted from Alexandrovsky, Tymovsky, and Korsakovsky districts. One row represents one named person record.

## Final record counts

- Total records: **7446**

- Александровский: **2884** records across **18** settlements/posts (`P000001`–`P002884`).
- Тымовский: **3242** records across **9** settlements/posts (`P002885`–`P006126`).
- Корсаковский: **1320** records across **24** settlements/posts (`P006127`–`P007446`).

## Validation result

Overall QA status: **passed**.

The final dataset passed checks for duplicate IDs, blank names, settlement-level sequence gaps, invalid age values, invalid arrival years, and invalid allowance-status values.

## ID handling

`person_id` was reassigned globally after merging all districts. `source_position_id` was preserved from the district files and remains the stable link back to district, settlement, household, and within-settlement order.

## Output files

The release includes the merged clean dataset, district-level clean files, final QA reports, record-count validation, methodology, data dictionary, and release notes.

## Canonical name-normalization release v2

The owner-approved `v2_20260711` release retains all 7,446 records and stable identifiers, adds `name_alias` as the twenty-fourth schema field, and incorporates the approved Item 1 and Item 2 changes. Sixty-six `name_raw` records differ from the prior release, 40 records contain `name_alias`, 2 `family_status` records were corrected, and 7 `comments` records were updated.

The combined v2 file is the exact ordered concatenation of the three matching v2 district files. It contains no blank `name_raw`, duplicate `person_id`, or duplicate `source_position_id` values. The release-specific QA report and hashes are stored in `outputs/qa/name_normalization_canonical_v2_20260711/`.

## Canonical normalization release v3

The owner-approved `v3_20260712` release retains all 7,446 records in the established district and person order and expands the schema from 24 to 31 columns. It consolidates the approved household structure, archival-code recovery, religion, military-status, literacy, capitalization, derived sex, family-status normalization, legal-status normalization, and illness normalization decisions.

The release removes `household_number` from the current schema and adds `household_id`, `household_type`, `household_details`, `legal_status_norm`, `sex`, `sex_evidence`, `family_status_norm`, and `illness_norm`. It applies 16 detailed `legal_status` corrections, 9 religion changes, 5,419 literacy changes, 5 `illness` transfers to `Богадельщик`, 8 comment changes, 41 archival-code changes, and 299 source-position changes. The combined file is the exact ordered concatenation of its three matching district files.

Release QA confirms 31 fields, unique and nonblank identifiers, expected district counts, 24 owner-verified blank household types, Sentence case for normalized categories, and no cross-field gender conflicts. QA evidence and SHA-256 hashes are stored in `outputs/qa/canonical_v3_20260712/`. Items still pending in the normalization tracker are not included as new approved derived fields in this release.

## Canonical quality-review release v4

The owner-authorized `v4_20260717` release retains all 7,446 records and established identifier order while expanding the schema from 31 to 36 columns. It consolidates the approved post-v3 work: age corrections and `age_months`, `origin_place_norm`, `occupation_norm`, `marriage_status_norm`, `living_alone_status`, reviewed comments, and later `name_alias` additions.

The combined v4 dataset is the exact ordered concatenation of 2,884 Alexandrovsky, 3,242 Tymovsky, and 1,320 Korsakovsky records. Compared with v3, 7,016 records and 16,865 cells change. The five added schema fields are `age_months`, `origin_place_norm`, `occupation_norm`, `marriage_status_norm`, and `living_alone_status`.

Release QA confirms 36 fields; unique, formatted, and order-preserved identifiers; integer-or-blank numeric fields; valid age and arrival-year ranges; complete and internally consistent month values for ages 0–2; approved allowance values; Sentence case normalized categories; synchronization of all ten Item 3 legal-status corrections with `legal_status_norm`; and zero cross-field gender conflicts. The release also reconciles 274 approved comment changes and 18 unique late alias changes without branch conflicts.

QA evidence, complete v3-to-v4 diffs, and SHA-256 hashes are stored in `outputs/qa/canonical_v4_20260717/`.

## Post-v4 review status

Item 24 comments review was completed on 2026-07-18. Its superseding v3 staged candidate retains 7,446 records and 36 columns and differs from canonical v4 in exactly 56 `comments` cells, with no schema, identifier, ordering, or other-field changes. These approved changes are incorporated into canonical v5.

Item 25 occupation-semantic evaluation was reviewed and deferred without data changes for future English translation and gender-specific normalization work.

## Canonical reviewed-name release v5

The owner-authorized `v5_20260731` release retains all 7,446 records and established identifier order while expanding the schema from 36 to 50 columns. It incorporates the 56 approved Item 24 comment corrections and the completed reviewed-name workflow, including manual name splitting, first-name and patronymic review, the last-name book discrepancy decisions, and subsequent owner household corrections.

Compared with v4, all records receive the new name-component audit structure. Existing v4 fields change only within the approved scope: 56 `comments`, 55 `name_raw`, and 39 `name_alias` values. The combined file remains the exact ordered concatenation of 2,884 Alexandrovsky, 3,242 Tymovsky, and 1,320 Korsakovsky records.

Release QA confirms 50 fields; unique, formatted, and order-preserved identifiers; valid integer formats and ranges; complete age/month consistency; exact district slicing and concatenation; no unapproved changes to existing v4 fields; all 7,446 names resolved as `observed`; component/provenance consistency; no family-inferred name sources; no unresolved patronymic proposals; and zero first-name spelling candidates. Complete v4-to-v5 cell and record diffs and SHA-256 hashes are stored in `outputs/qa/canonical_v5_20260731/`.
