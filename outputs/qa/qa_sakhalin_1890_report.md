# Sakhalin 1890 Final QA Report

Generated: `2026-07-10T04:55:24Z`

Overall status: **passed**

## Record counts

Total records: **7446**

|   district_code | district        |   records |   settlements_posts | sequence_validation_status   | first_person_id   | last_person_id   |
|----------------:|:----------------|----------:|--------------------:|:-----------------------------|:------------------|:-----------------|
|               1 | Александровский |      2884 |                  18 | passed                       | P000001           | P002884          |
|               2 | Тымовский       |      3242 |                   9 | passed                       | P002885           | P006126          |
|               3 | Корсаковский    |      1320 |                  24 | passed                       | P006127           | P007446          |


## Core QA checks

| Check                                     |   Count |
|:------------------------------------------|--------:|
| Blank `name_raw`                          |       0 |
| Duplicate `person_id`                     |       0 |
| Duplicate `source_position_id`            |       0 |
| Blank `source_position_id`                |       0 |
| Age non-numeric                           |       0 |
| Age > 100                                 |       0 |
| Arrival year bad format                   |       0 |
| Arrival year outside 1860–1891            |       0 |
| Invalid allowance_status                  |       0 |
| Settlement order not two digits           |       0 |
| Settlements/posts needing sequence review |       0 |


## Settlement/post sequence validation

Settlements/posts validated: **51**; passed: **51**; needs review: **0**.

Each settlement/post passed when person order numbers start at 1, have no gaps, have no duplicates, and `max(person_order_in_settlement)` equals the row count for that settlement/post.


## Notes

- The merged file assigns global `person_id` values from `P000001` to `P007446`.

- `source_position_id` values were preserved as the stable source-navigation IDs.

- District-level files in this final package are slices of the merged file and therefore also use global `person_id` values.

- Reviewed district-level values are treated as accepted canonical values for this release; broader normalization/grouping can be performed later for analytical layers.
