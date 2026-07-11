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
