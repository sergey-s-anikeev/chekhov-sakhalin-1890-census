# Household Structure Normalization Proposal

Date: 2026-07-11

## Summary

This staged proposal applies the owner-reviewed decisions from `household_structure.xlsx`, separates household identifiers from categories and details, and corrects recognized household numbers.

No canonical processed CSV is overwritten by this stage.

## Proposed fields

| Field | Meaning |
|:--|:--|
| `household_id` | Text identifier preserving the original numeric household number or the owner-approved `household_number_normalized` value for selected source designations. Numeric households remain numeric-looking, but the field is stored as text because approved ranges such as `292-293` and `80-81` are allowed. Blank when no normalized number applies. |
| `household_type` | Owner-reviewed household category. Numeric and corrected numeric household rows use `Частное`. |
| `household_details` | Owner-reviewed household detail. Blank where no additional detail applies. |

The previous `household_number` field is replaced in the staged output by these three fields.

## `source_position_id` rule

The staged `source_position_id` format is:

```text
<district_code>-<settlement_order>-<household_segment>-<person_order_in_settlement>
```

The household segment is:

- zero-padded 3-digit `household_id` for numeric households;
- the zero-padded first number for a hyphenated household range (`292-293` becomes `292`; `80-81` becomes `080`);
- `000` when `household_id` is blank.

Examples:

```text
1-02-292-1259
1-02-080-0443
2-27-000-0364
```

The `000` segment means the reviewed household designation has no usable numeric household number. The designation should be read from `household_type` and `household_details`.

## Staged outputs

The reproducible staging script is:

```text
scripts/stage_household_structure_from_owner_workbook.py
```

It uses and produces:

```text
data/review/household_structure_owner_mapping_20260711.csv
data/staging/household_structure_20260711_v2/clean_sakhalin_1890_ru_household_structure_v2.csv
data/staging/household_structure_20260711_v2/household_structure_v2_diff.csv
data/staging/household_structure_20260711_v2/household_structure_v2_qa_summary.csv
data/staging/household_structure_20260711_v2/household_type_summary.csv
```

## Current QA result

The owner-reviewed staged run contains:

- 7,446 input records and 7,446 output records.
- 106 owner mapping decisions covering 269 records, with all expected counts matching.
- 39 records whose `household_id` is corrected from `household_number_normalized`.
- 9 records with approved hyphenated household IDs.
- 24 records with blank source household values.
- 0 blank or duplicate proposed `source_position_id` values.

## Review note

The category and detail values in v2 come from the owner workbook by exact `source_household_number` match. Blank source households remain blank in all three household fields and use `000` in `source_position_id`.
