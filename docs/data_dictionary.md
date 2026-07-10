# Data Dictionary

## Project

Chekhov Sakhalin 1890 Census Data Analysis

## Dataset

Clean Russian master dataset for the reviewed 1890 Sakhalin census extraction.

One row represents one named person record.

Final merged record count: **7,446**.

The final release combines the Alexandrovsky, Tymovsky, and Korsakovsky district datasets in source order. Printed book page numbers are preserved for verification and traceability.

## Unit of Analysis

Individual person record.

---

## Final Field Structure

| Field | Type | Description | Example |
|:--|:--|:--|:--|
| `person_id` | string | Global sequential person ID assigned after merging all districts. | `P000001` |
| `source_position_id` | string | Stable source-navigation ID built from district, settlement order, household number, and person order within settlement/post. | `3-48-002-0005` |
| `district_code` | string | District code from the settlement lookup. | `1` |
| `district` | string | District name. | `Александровский` |
| `settlement_order` | string | Two-digit settlement/post order in the source structure. | `01` |
| `settlement` | string | Normalized settlement/post name. | `Пост Дуэ` |
| `person_order_in_settlement` | integer | Sequential source person number within settlement/post. | `274` |
| `page_number` | integer | Printed book page where the record begins. | `203` |
| `household_number` | string | Source household/dwelling number or textual household marker from field `2.` | `Казарма Ж 1` |
| `legal_status` | string | Legal/social status from field `3.`, normalized after district review. | `Ссыльнокаторжный` |
| `name_raw` | string | Person name from field `4.` after cleanup of markup and role leakage. | `Андрей Васильев Васильев` |
| `family_status` | string | Household/family role parsed from field `4.` | `Хозяин` |
| `age` | integer | Age in full years where possible; infants may be coded as `0` with exact age retained in `comments`. | `35` |
| `religion` | string | Confession/religion from field `6.` | `Православное` |
| `origin_place` | string | Place of origin from field `7.`, normalized and reviewed at district level. | `Смоленская губерния` |
| `arrival_year` | integer | Year of arrival from field `8.` when present. | `1885` |
| `occupation` | string | Occupation or activity from field `9.` | `Каменный уголь` |
| `literacy` | string | Literacy category from field `10.` | `грамотен` |
| `marriage_status` | string | Marriage status from field `11.`, with explanatory details moved to `comments` where reviewed. | `женат на родине` |
| `allowance_status` | string | Allowance status from field `12.`, normalized from `Да/Нет` to `TRUE/FALSE`. | `TRUE` |
| `illness` | string | Illness or condition from field `13.` | `Хронический катар желудка и кишок` |
| `comments` | string | Source field `14.` and other reviewed explanatory notes. | `6 месяцев` |
| `notes_raw` | string | Archive reference, normalized but preserved. | `РГБ № 2010` |

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
P007446
```

`person_id` is global in the final merged file and in the final district slices included in this release.

### `source_position_id`

Format:

```text
D-SS-HHH-PPPP
```

Where:

| Component | Meaning |
|:--|:--|
| `D` | District code |
| `SS` | Settlement order |
| `HHH` | Household number, zero-padded to 3 digits when numeric |
| `PPPP` | Person order within settlement/post, zero-padded to 4 digits |

Example:

```text
3-48-002-0005
```

If `household_number` is nonnumeric, it is preserved in `source_position_id` in a safe text form rather than guessed.

`source_position_id` is stable and source-derived.

---

## Controlled Fields

The following fields are normalized against controlled vocabularies or reviewed canonical forms:

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

Canonical values include:

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
|:--|:--|
| `Да` | `TRUE` |
| `Нет` | `FALSE` |

Allowed final values are:

```text
TRUE
FALSE
blank
```

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

Year-like or numeric values in the religion field are not auto-corrected. They are preserved and flagged for manual review as probable source anomalies.

---

## Source Markup Rules

### Angle brackets

Angle brackets `<...>` represent crossed-out text. Crossed-out text is not converted into data.

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

Source field numbers are removed from converted values.

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

Ordinal name markers are retained:

```text
Марья Алексеева Попова 2-я
Андрей Иванов 1-й
```

Trailing digit cleanup is not applied to:

```text
notes_raw: РГБ № 6810
comments: 7 месяцев
comments: 1 год 5 месяцев
```

---

## Age Rules

`age` is stored as a natural number of full years.

If months are present, the full age phrase is preserved in `comments`.

| Source | `age` | `comments` |
|:--|--:|:--|
| `48` | `48` | blank |
| `7 м[есяцев]` | `0` | `7 месяцев` |
| `1 г[од] 5 м[есяцев]` | `1` | `1 год 5 месяцев` |

---

## Origin Place Rules

`origin_place` is normalized against the reviewed 1890 administrative reference list where possible.

Canonical governorate and oblast names use full official administrative-unit forms, for example:

```text
Тверская губерния
Ставропольская губерния
Кубанская область
Терская область
Область Войска Донского
```

Cleaning order:

1. Remove the source field prefix, for example `7.`
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

Values that look like an occupation but occur in `origin_place` are not silently corrected. They are preserved and flagged for manual review as probable source anomalies.

---

## Notes Field Rules

`notes_raw` preserves archival references.

Normalize archive numbers as follows:

```text
РГ Б № 6810 → РГБ № 6810
РГБ 6844 → РГБ № 6844
```

Trailing digits are not removed from `notes_raw`.

---

## QA Constraints

The final CSV must satisfy the following checks:

1. `name_raw` is populated.
2. `person_id` is unique.
3. `source_position_id` is unique.
4. Every `settlement` maps to one valid `district`, `district_code`, and `settlement_order`.
5. `page_number`, `age`, and `arrival_year` are numeric where present.
6. `age`, when present, is numeric and no greater than `100`.
7. `arrival_year`, when present, is a four-digit year between `1860` and `1891`.
8. `literacy`, `marriage_status`, and `allowance_status` use controlled values.
9. `allowance_status` is `TRUE`, `FALSE`, or blank.
10. No `<...>` angle-bracket markup remains.
11. No `[...]` square-bracket markup remains.
12. Trailing bare footnote digits do not remain in normalized text fields except `comments` and `notes_raw`.
13. `notes_raw` follows the format `РГБ № NNNN` where present.
14. `person_order_in_settlement` forms a complete sequence within each settlement/post.
15. Unknown values in controlled fields are reported for manual review.
