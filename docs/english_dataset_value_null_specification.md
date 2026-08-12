# English Dataset Value and NULL Specification

## Status

Approved by the project owner on 2026-08-02 for the 23-field compact English
analytical dataset derived from canonical `v5_20260731`.

## Missing-value rules

1. Export missing values as empty CSV fields.
2. Convert empty nullable fields to true SQL `NULL` during MySQL loading.
3. Do not use placeholder strings such as `NULL`, `N/A`, or `Not recorded`
   merely to represent a missing value.
4. Preserve meaningful numeric `0` and Boolean `FALSE` values.
5. Use `Unknown`, `Not recorded`, or `Not applicable` only when a reviewed
   canonical source value explicitly carries that meaning.
6. Inventory every distinct included categorical value during lookup-table
   development; do not assume that explicit unknown or applicability categories
   are absent.
7. Tableau may use reader-friendly display labels without modifying the stored
   source value.

## Boolean and numeric rules

- `allowance_status` is a nullable Boolean: CSV `TRUE`, CSV `FALSE`, or blank;
  MySQL `1`, `0`, or SQL `NULL`.
- `age = 0` and `age_months = 0` are valid recorded values and are not missing.
- Numeric fields contain unformatted integers without thousands separators.
- `arrival_year` is stored as a small integer rather than MySQL `YEAR`, because
  the canonical range includes years before 1901.

## Approved MySQL field specification

| Order | Field | MySQL type | Nullable |
|---:|:--|:--|:--:|
| 1 | `person_id` | `CHAR(7)` | No |
| 2 | `source_position_id` | `CHAR(13)` | No |
| 3 | `district` | `VARCHAR(32)` | No |
| 4 | `settlement` | `VARCHAR(64)` | No |
| 5 | `person_seq` | `SMALLINT UNSIGNED` | No |
| 6 | `household_id` | `VARCHAR(16)` | Yes |
| 7 | `household_type` | `VARCHAR(64)` | Yes |
| 8 | `legal_status` | `VARCHAR(100)` | Yes |
| 9 | `full_name` | `VARCHAR(128)` | No |
| 10 | `sex` | `VARCHAR(10)` | No |
| 11 | `family_status` | `VARCHAR(64)` | Yes |
| 12 | `age` | `TINYINT UNSIGNED` | Yes |
| 13 | `age_months` | `TINYINT UNSIGNED` | Yes |
| 14 | `religion` | `VARCHAR(64)` | Yes |
| 15 | `origin_place` | `VARCHAR(128)` | Yes |
| 16 | `arrival_year` | `SMALLINT UNSIGNED` | Yes |
| 17 | `occupation` | `VARCHAR(128)` | Yes |
| 18 | `literacy` | `VARCHAR(32)` | Yes |
| 19 | `marital_status` | `VARCHAR(64)` | Yes |
| 20 | `living_alone_status` | `VARCHAR(32)` | Yes |
| 21 | `allowance_status` | `BOOLEAN` | Yes |
| 22 | `illness` | `VARCHAR(128)` | Yes |
| 23 | `archive_code` | `VARCHAR(32)` | Yes |

`person_id` is the primary key. `source_position_id` must also remain unique.

## Capitalization and punctuation

- Column names use lowercase `snake_case`.
- Controlled English categories use sentence case.
- Proper geographic names and personal names use conventional English name
  capitalization.
- CSV Boolean values use uppercase `TRUE` and `FALSE`.
- Compound categories use a semicolon followed by one space: `; `.
- Commas are not used as list delimiters.
- Hyphens that belong to names, places, or translated terms are preserved.
- Compound components retain canonical order unless an approved translation
  rule requires a change.

## Field-specific interpretation

- `living_alone_status` remains nullable text. The explicit canonical value is
  translated as `Living alone`; a blank is not converted to Boolean `FALSE`.
- `allowance_status` is the only approved Boolean field in the compact schema.
- `household_id` remains text because it is an identifier, not a measure.
- `full_name` and `archive_code` remain text even when they contain numeric
  characters.

## Known edge cases requiring later lookup review

- Canonical occupation `Нет занятия` is an explicit value meaning `No
  occupation`; it must not become blank or SQL `NULL`.
- Canonical `name_raw` includes `Человек неизвестного звания`. Its treatment in
  `full_name` requires explicit review during personal-name transliteration; it
  must not be silently replaced with a generic missing-value label.
- All distinct values in every translated field must be reviewed for explicit
  `Unknown`, `Not recorded`, and `Not applicable` meanings during Items 4–6.

