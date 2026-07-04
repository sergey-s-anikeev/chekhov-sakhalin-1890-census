# Data Dictionary

## Project

Chekhov Sakhalin 1890 Census Data Analysis

## Dataset Description

This dataset is being built from indexed person-level records based on Anton Chekhov’s 1890 Sakhalin census.

The final database is designed as a flat person-level CSV where one row represents one person. The expected combined database size is approximately 7,445 records.

The source is a readable/searchable PDF with an existing text layer. OCR is not the primary extraction method. Printed book page numbers must be preserved for verification.

## Unit of Analysis

Individual person record.

## Final Field Structure

| Field name | Type | Description | Example | Notes |
|---|---:|---|---|---|
| `person_id` | string | Stable global person ID | `P000001` | Generated sequentially across the whole database |
| `source_position_id` | string | Source-navigation ID | `3-48-002-0005` | Built from district, settlement, household, and person order |
| `district_code` | string | District code | `1`, `2`, `3` | Derived from settlement lookup |
| `district` | string | District name | `Корсаковский` | Derived from settlement lookup |
| `settlement_order` | string | Locality order in the book structure | `48` | Derived from settlement lookup |
| `settlement` | string | Normalized locality name | `Сиянцы` | Standardized from source |
| `person_order_in_settlement` | integer | Sequential person number within locality | `1` | Generated during transformation |
| `page_number` | integer | Printed book page where the record begins | `479` | Must preserve printed page number, not PDF viewer page |
| `household_number` | string | Source household number, field `2.` | `1` | Used in `source_position_id` |
| `legal_status` | string | Legal/social status, source field `3.` | `Поселенец` | Normalized against controlled vocabulary |
| `name_raw` | string | Person name from source field `4.` | `Семен Осипов Агапов` | Preserves source spelling after markup cleanup |
| `family_status` | string | Family/household role from source field `4.` | `Хозяин` | Normalized against controlled vocabulary |
| `age` | integer | Age in full years | `48` | Infants/months handled through `comments` |
| `religion` | string | Confession label / вероисповедание | `Православное` | Normalized to canonical confession label |
| `origin_place` | string | Place of origin | `Костромская губерния` | Normalized to 1890 administrative unit where possible |
| `arrival_year` | integer | Year of arrival | `1882` | Natural 4-digit year where present |
| `occupation` | string | Occupation, source field `9.` | `Плотник` | Cleaned text field |
| `literacy` | string | Literacy category | `грамотен` | Controlled values: `неграмотен`, `грамотен`, `образован` |
| `marriage_status` | string | Marriage status | `женат на родине` | Controlled values |
| `allowance_status` | string | Allowance status | `TRUE` / `FALSE` | Converted from `Да` / `Нет` |
| `illness` | string | Illness field, source field `13.` | `Больная` | Cleaned text field |
| `comments` | string | Source field `14.` and age notes for infants | `7 месяцев` | Footnote digits are preserved if meaningful |
| `notes_raw` | string | Archival reference | `РГБ № 6810` | Normalized but not stripped of trailing digits |

## ID Rules

### `person_id`

Format:

```text
P + global sequential person number, zero-padded to 6 digits
