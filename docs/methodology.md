# Methodology

## Project Goal

This project converts indexed historical records from Anton Chekhov's 1890 Sakhalin census into a structured person-level dataset suitable for demographic, settlement-level, and migration-origin analysis.

The master dataset is a flat CSV where one row represents one named person record.

## Source and Extraction Approach

The source material consists of searchable PDF district sections with a readable text layer. OCR was not used as the primary extraction method.

The extraction workflow:

```text
PDF text layer
↓
extract page text with PyMuPDF
↓
preserve printed book page number
↓
detect settlement/post headings
↓
split text into person-level records
↓
map numbered source fields into the fixed raw schema
↓
normalize and review district files
↓
merge reviewed district files
↓
run final validation and QA
```

Printed book page numbers are preserved in `page_number`. PDF viewer page numbers are not used unless they match the printed pagination.

If a person record begins on one printed page and continues onto the next, `page_number` records the printed page on which the record begins.

## Processing Layers

The project uses three data layers:

1. Raw/interim extraction files that preserve source-like parsed fields.
2. Clean Russian district files reviewed at district level.
3. Final merged Russian master file with global person identifiers.

Russian/Cyrillic source values remain the authoritative data layer. Translation, transliteration, and analytical grouping are intentionally deferred to later analytical layers.

Personal names are transliterated rather than translated. Analytical categories such as legal status, religion, literacy, family status, and origin place can later be translated through controlled reference tables.

## Raw-to-Final Conversion

The workflow separates extraction from normalization.

### 1. Raw split-record data

Raw records preserve source-derived values after record detection and source-field parsing.

Expected raw fields:

```text
settlement
page_number
household_number
legal_status
name_raw
family_status
age
religion
origin_place
arrival_year
occupation
literacy
marriage_status
allowance_status
illness
comments
notes_raw
```

Optional debug fields may include:

```text
source_record_number
source_block_raw
```

### 2. Clean district data

Each district is normalized, QA-checked, and manually reviewed. District-level review resolves critical extraction errors, controlled-vocabulary variants, field shifts, and explanatory details that belong in `comments`.

### 3. Final merged data

The reviewed Alexandrovsky, Tymovsky, and Korsakovsky district files are standardized and merged into the final Russian master dataset.

The final merged record count is **7,446**.

`person_id` is reassigned globally from `P000001` to `P007446`. `source_position_id` remains the stable source-navigation identifier.

The `v3_20260712` canonical release uses a 31-column schema. It replaces `household_number` with owner-reviewed `household_id`, `household_type`, and `household_details`, and adds the approved derived fields `legal_status_norm`, `sex`, `sex_evidence`, `family_status_norm`, and `illness_norm`. Detailed source-derived fields remain present alongside analytical fields.

## Source Field Mapping

```text
2  -> household_number
3  -> legal_status
4  -> name_raw + family_status
5  -> age
6  -> religion
7  -> origin_place
8  -> arrival_year
9  -> occupation
10 -> literacy
11 -> marriage_status
12 -> allowance_status
13 -> illness
14 -> comments
РГБ / РГАЛИ № -> notes_raw
```

## Locality Metadata

Settlement and post names are normalized and mapped through the `SETTLEMENTS` lookup table.

The lookup derives:

- `district_code`;
- `district`;
- `settlement_order`;
- settlement type;
- source starting-page reference.

If a locality is not found in the lookup table, processing stops for manual review rather than guessing.

## Normalization Principles

The workflow follows these principles:

1. Preserve source meaning.
2. Remove source markup only according to documented rules.
3. Normalize repeated historical categories through controlled dictionaries.
4. Preserve reviewed district-level values as canonical for this release.
5. Preserve unexpected values and report them for manual review.
6. Avoid silent correction of ambiguous source anomalies.
7. Keep printed page numbers for traceability.
8. Keep uncertain or explanatory details in `comments` rather than discarding them.
9. Keep archive references in `notes_raw`.
10. Keep `source_position_id` stable for source navigation.

## General Text Cleanup

General cleanup includes:

- removing PDF text-layer artifacts and invisible separators;
- joining ordinary Cyrillic words broken across line endings by PDF extraction;
- removing numbered source-field prefixes from converted values;
- removing crossed-out text in angle brackets;
- restoring square-bracketed word parts;
- normalizing whitespace;
- removing trailing bare footnote digits from selected normalized text fields.

Trailing bare footnote digits are not removed from `comments` or `notes_raw`.

## Source Markup Rules

Angle brackets `<...>` represent crossed-out text and are removed from normalized values.

Examples:

```text
11. <Холост> на Сахалине → женат на Сахалине
4. <Мечислав> Бронислав Лисавецкий → Бронислав Лисавецкий
12. <Да> нет → FALSE
12. Да <нет> → TRUE
```

Square brackets `[...]` contain restored word parts. The restored letters are retained and the brackets are removed.

Examples:

```text
Пензенск[ой] → Пензенской
Правосл[авного] → Православного
Сс[ыльно]каторжная → Ссыльнокаторжная
```

## Record Detection and Source Anomalies

The parser detects both standalone and inline source record numbers and validates the field sequence that follows each candidate record start.

The extraction logic accounts for source and text-layer anomalies including:

- records beginning with an additional field `1.`;
- missing or misprinted field labels `2.`, `3.`, `4.`, `7.`, or `8.`;
- shifted labels in legal status, name, age, religion, origin place, literacy, marriage status, and allowance status;
- embedded record starts after archival references;
- wrapped age lines that could otherwise be misread as new records;
- household numbers and other numeric values that resemble source field labels.

Repairs are applied only where the source pattern is sufficiently explicit. Ambiguous cases are preserved for manual review.

## Field Normalization

### Settlement

Ordinary settlements remove the prefix `Селение`.

Special locality types are preserved, including:

```text
Пост Александровский
Арковский кордон
Арковский станок
Пост Дуэ
Пост Корсаковский
Тарайское Зимовье
```

### Legal Status

`legal_status` is normalized against a controlled vocabulary.

Known variants, abbreviations, and extraction artifacts are mapped to canonical values. Unknown values are preserved and reported for review.

### Family Status

`family_status` is normalized against a controlled vocabulary.

Restored bracketed forms, spelling variants, and common abbreviations are mapped to canonical values. Unknown values are preserved and reported for review.

### Religion

`religion` is normalized as a confession label / вероисповедание.

Canonical values use neuter Russian forms where appropriate. The noun values `Раскольник` and `Старообрядец` remain nouns.

Year-like or numeric values in the religion field are preserved and flagged as probable source anomalies.

### Origin Place

`origin_place` is normalized against the reviewed 1890 administrative-unit reference library.

The reference library covers:

- governorates of the Russian Empire;
- Polish governorates;
- Finnish governorates;
- oblasts;
- special administrative units;
- selected non-administrative source values such as `На Сахалине` and `По пути`.

Unknown values are preserved and reported for manual review.

Occupation-like values found in `origin_place` are not silently corrected. They are preserved and flagged as probable source anomalies.

### Age

`age` is stored as completed years. `age_months` stores total completed months for infant and young-child analysis in the latest staged schema.

When the source records a precise expression, that evidence controls both fields: for example, `1 год 7 месяцев` becomes `age = 1`, `age_months = 19`, and `5 месяцев` becomes `age = 0`, `age_months = 5`. Explicit ages below one month map to `0` completed months, except four weeks maps to one completed month under the approved convention.

For statistical completeness, when the source gives only the completed whole-year age, blank month values are derived as follows:

```text
age = 1  → age_months = 12
age = 2  → age_months = 24
```

Existing precise month values always take precedence over these derived whole-year conversions. The Item 23 review inventory records which values were derived. These rules are incorporated into canonical release `v4_20260717`.

### Allowance Status

Source values from field `12.` are normalized as:

```text
Да  → TRUE
Нет → FALSE
```

### Notes

Archive references are normalized into a consistent form while preserving the reference number, for example:

```text
РГ Б № 6810 → РГБ № 6810
РГБ 6844 → РГБ № 6844
```

## Manual Review

Each district was processed, QA-checked, and manually reviewed.

Manual review focused on:

- critical extraction errors;
- record-sequence gaps;
- age and arrival-year validation;
- name and family-status parsing;
- controlled-vocabulary expansion;
- source field-number shifts;
- probable source typos;
- movement of explanatory details into `comments`;
- preservation of uncertain values where automatic correction was not justified.

Confirmed source typos were either preserved as printed or normalized through documented rules, depending on the field and level of certainty.

## Python Workflow

The validated workflow includes scripts for:

- PDF text extraction;
- person-record detection;
- source-field parsing;
- district-level cleaning;
- manual anomaly decision application;
- final district validation;
- merging reviewed districts;
- generation of QA reports and validation summaries.

The extraction parser uses PyMuPDF (`fitz`) to read the PDF text layer.

## Final Merge

After district-level review, the three final district files were standardized and merged in this order:

1. Alexandrovsky
2. Tymovsky
3. Korsakovsky

The merged dataset contains **7,446 person records**.

The district-level files included in the release are slices of the same validated project-level dataset and use the same final schema.

## Final Quality Assurance

The final QA validates:

- row counts by district and settlement/post;
- exact combined row count of 7,446;
- no duplicate `person_id`;
- no duplicate `source_position_id`;
- no blank `name_raw`;
- no settlement/post person-sequence gaps;
- valid settlement-to-district mapping;
- consistent 23-field schema;
- two-digit `settlement_order`;
- numeric `page_number`, `age`, and `arrival_year` where present;
- `age` not greater than 100 where present;
- `arrival_year` between 1860 and 1891 where present;
- `allowance_status` limited to `TRUE`, `FALSE`, or blank;
- controlled values for literacy, marriage status, and allowance status;
- no residual `<...>` or `[...]` markup;
- no trailing bare footnote digits in normalized text fields except `comments` and `notes_raw`;
- valid normalized archive-reference format;
- reporting of unresolved controlled-field values and probable source anomalies.
