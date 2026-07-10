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
