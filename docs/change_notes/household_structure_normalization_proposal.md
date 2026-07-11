# Household Structure Normalization Proposal

Date: 2026-07-11

## Summary

This staged proposal separates numeric household identifiers from textual household descriptions while preserving the original source household designation.

No canonical processed CSV is overwritten by this stage.

## Proposed fields

| Field | Meaning |
|:--|:--|
| `household_id` | Numeric household number from source field `2.`. Blank when the source value is textual or missing. |
| `household_type` | Normalized category for textual household designations, such as `Казарма`, `Тюрьма`, `Дом`, `Школа`, or `Другое`. Numeric household rows use `Стандарт`. |
| `household_detail` | Complete original textual household designation exactly as recorded. Blank for numeric household rows and blank source values. |

The previous `household_number` field is replaced in the staged output by these three fields.

## `source_position_id` rule

The staged `source_position_id` format is:

```text
<district_code>-<settlement_order>-<household_segment>-<person_order_in_settlement>
```

The household segment is:

- zero-padded 3-digit `household_id` for numeric households;
- `000` when `household_id` is blank.

Examples:

```text
2-27-012-0086
2-27-000-0364
1-18-000-0274
2-27-000-0412
```

The `000` segment means the original source did not provide a usable numeric household number. The original designation should be read from `household_type` and `household_detail`.

## Staged outputs

The reproducible staging script is:

```text
scripts/stage_household_structure_normalization.py
```

It produces:

```text
data/staging/household_structure_20260711/clean_sakhalin_1890_ru_household_structure_v1.csv
data/staging/household_structure_20260711/household_structure_affected_inventory.csv
data/staging/household_structure_20260711/household_structure_value_summary.csv
data/staging/household_structure_20260711/household_structure_diff.csv
data/staging/household_structure_20260711/household_structure_qa_summary.csv
```

## Current QA result

The first staged run contains:

- 7,446 input records.
- 7,446 output records.
- 269 records with textual non-numeric household designations.
- 106 distinct textual non-numeric household values.
- 24 records with blank source household values.
- 0 blank proposed `source_position_id` values.
- 0 duplicate proposed `source_position_id` values.

## Review note

The category mapping is intentionally conservative. Values that are descriptive, editorial, range-like, or personal names are mapped to `Другое` unless they match an explicit institutional/building pattern.
