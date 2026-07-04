# Data Dictionary

## Project

Chekhov Sakhalin 1890 Census Data Analysis

## Dataset Description

This dataset is being built from indexed person-level records based on Anton Chekhov’s 1890 Sakhalin census.

The final database is designed as a flat person-level CSV where **one row represents one person**. The expected combined database size is approximately **7,445 records**.

The source is a readable/searchable PDF with an existing text layer. OCR is not the primary extraction method. Printed book page numbers must be preserved for verification and traceability.

## Unit of Analysis

Individual person record.

## Dataset Status

Current status: extraction and normalization testing.

The field structure is stable enough for sample extraction, but controlled vocabularies may expand as more records are processed.

---

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
| `marriage_status` | string | Marriage status | `женат на родине` | Controlled values listed below |
| `allowance_status` | string | Allowance status | `TRUE` / `FALSE` | Converted from `Да` / `Нет` |
| `illness` | string | Illness field, source field `13.` | `Больная` | Cleaned text field |
| `comments` | string | Source field `14.` and age notes for infants | `7 месяцев` | Footnote digits are preserved if meaningful |
| `notes_raw` | string | Archival reference | `РГБ № 6810` | Normalized but not stripped of trailing digits |

---

## ID Rules

### `person_id`

Format:

```text
P + global sequential person number, zero-padded to 6 digits
```

Examples:

```text
P000001
P000125
P007445
```

`person_id` is the stable primary ID. It must not depend on settlement, household number, page number, or district.

### `source_position_id`

Format:

```text
D-SS-HHH-PPPP
```

Where:

| Component | Meaning |
|---|---|
| `D` | District code |
| `SS` | Settlement order |
| `HHH` | Household number, zero-padded to 3 digits when numeric |
| `PPPP` | Person order within locality, zero-padded to 4 digits |

Example:

```text
3-48-002-0005
```

If `household_number` is nonnumeric, it should be preserved in `source_position_id` in a safe text form rather than guessed.

---

## Controlled Fields

The following fields are normalized against controlled vocabularies:

- `settlement`
- `legal_status`
- `family_status`
- `religion`
- `origin_place`
- `literacy`
- `marriage_status`
- `allowance_status`

Unknown or unexpected values are preserved and reported for manual review rather than silently corrected.

---

## Controlled Values

### `literacy`

Allowed values:

```text
неграмотен
грамотен
образован
```

### `marriage_status`

Allowed values:

```text
женат на родине
женат на Сахалине
вдов
холост
```

If crossed-out text leaves only `на Сахалине`, normalize to:

```text
женат на Сахалине
```

### `allowance_status`

Source field `12.` is normalized as:

| Source value | Normalized value |
|---|---|
| `Да` | `TRUE` |
| `Нет` | `FALSE` |

### `religion`

Religion is normalized as a confession label / вероисповедание, not as an adjective describing a person.

Canonical values:

```text
Армяно-григорианское
Иудейское
Католическое
Лютеранское
Магометанское
Мусульманское
Православное
Раскольник
Римско-католическое
Старообрядец
```

Examples:

```text
6. Православного → Православное
6. Католического → Католическое
6. Лютеранского → Лютеранское
6. Магометанского → Магометанское
6. Мусульманского → Мусульманское
6. Иудейского → Иудейское
6. Армяно-григорианского → Армяно-григорианское
6. Римско-католического → Римско-католическое
6. Раскольн[ик] → Раскольник
6. Старообрядца → Старообрядец
```

Year-like or numeric values in the religion field should not be auto-corrected. They should be preserved and flagged for manual review as probable source anomalies.

---

## Source Markup Rules

### Angle brackets

Angle brackets `<...>` represent crossed-out text. Crossed-out text should not be converted into data.

Examples:

```text
11. <Холост> на Сахалине → женат на Сахалине
4. <Мечислав> Бронислав Лисавецкий → Бронислав Лисавецкий
12. <Да> нет → FALSE
12. Да <нет> → TRUE
```

### Square brackets

Square brackets `[...]` contain restored word parts. The restored letters are preserved and the brackets are removed.

Examples:

```text
Пензенск[ой] → Пензенской
Правосл[авного] → Православного
Сс[ыльно]каторжная → Ссыльнокаторжная
Бессарабск[ой] обл[асти] → Бессарабской области
```

---

## Source Field Prefix Rules

Remove source field numbers from converted values.

Examples:

```text
6. Православного → Православное
7. Ставропольской → Ставропольская губерния
10. Грамотен → грамотен
```

---

## Footnote Digit Rules

Trailing bare footnote digits are removed from normalized text fields except `comments` and `notes_raw`.

Cleanup applies to:

- `legal_status`
- `name_raw`
- `family_status`
- `religion`
- `origin_place`
- `occupation`
- `literacy`
- `marriage_status`
- `illness`

Examples:

```text
Вера Суменко2 → Вера Суменко
Дочь поселенца1 → Дочь поселенца
На Сахалине6 → На Сахалине
Больная1 → Больная
```

Do not remove ordinal name markers:

```text
Марья Алексеева Попова 2-я
Андрей Иванов 1-й
```

Do not apply trailing digit cleanup to:

```text
notes_raw: РГБ № 6810
comments: 7 месяцев
comments: 1 год 5 месяцев
```

---

## Age Rules

`age` is a natural number of full years.

If months are present, preserve the full age phrase in `comments`.

| Source | `age` | `comments` |
|---|---:|---|
| `48` | `48` | empty |
| `7 м[есяцев]` | `0` | `7 месяцев` |
| `1 г[од] 5 м[есяцев]` | `1` | `1 год 5 месяцев` |

---

## Origin Place Rules

`origin_place` is normalized against the 1890 administrative-unit reference library.

Canonical values for governorates and oblasts should use full official administrative-unit names, for example:

```text
Тверская губерния
Ставропольская губерния
Кубанская область
Терская область
Область Войска Донского
```

Cleaning order:

1. Remove source field prefix, e.g. `7.`
2. Remove crossed-out text in `<angle brackets>`.
3. Restore `[square-bracketed]` word parts.
4. Remove trailing bare footnote digits.
5. Normalize administrative abbreviations: `обл.` → `область`, `губ.` → `губерния`.
6. Map source variants to canonical 1890 administrative units.
7. Preserve meaningful non-administrative source values such as `На Сахалине`, `По пути`, `Прусскоподданный`, `Прусскоподданная`, and `из Чибисани`.
8. If unresolved, preserve the cleaned value and report it for manual review.

Examples:

```text
7. Ставропольской → Ставропольская губерния
7. Тверск[ой] → Тверская губерния
7. Бессарабск[ой] обл[асти] → Бессарабская губерния
7. Кубанск[ой] → Кубанская область
7. Терской об[ласти] → Терская область
7. Донской → Область Войска Донского
7. Петербургск[ой] → Санкт-Петербургская губерния
7. Каменец-Под[ольской] → Подольская губерния
7. Петраковск[ой] → Петроковская губерния
7. Астроханск[ой] → Астраханская губерния
7. Курляд[ской] → Курляндская губерния
7. Финляндск[ой] → Великое княжество Финляндское
На Сахалине6 → На Сахалине
```

If `origin_place` contains a value that looks like an occupation, do not auto-correct it. Preserve the printed source value and flag it for manual review as a probable source anomaly.

---

## Notes Field Rules

`notes_raw` preserves archival references.

Normalize archive numbers as follows:

```text
РГ Б № 6810 → РГБ № 6810
РГБ 6844 → РГБ № 6844
```

Do not remove trailing digits from `notes_raw`.

---

## QA Notes

The final CSV should pass the following checks:

1. `person_id` is unique.
2. `source_position_id` is unique.
3. Every `settlement` maps to one valid `district`, `district_code`, and `settlement_order`.
4. `page_number`, `age`, and `arrival_year` are numeric where present.
5. `literacy`, `marriage_status`, and `allowance_status` use controlled values.
6. No `<...>` angle-bracket markup remains.
7. No `[...]` square-bracket markup remains.
8. Trailing bare footnote digits do not remain in normalized text fields except `comments` and `notes_raw`.
9. `notes_raw` follows the format `РГБ № NNNN` where present.
10. Unknown values in controlled fields are reported for manual review.
