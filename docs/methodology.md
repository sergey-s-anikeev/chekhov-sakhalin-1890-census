# Methodology

## Project Goal

The goal of this project is to transform indexed historical census records from Anton Chekhov's 1890 Sakhalin census into a structured person-level dataset suitable for demographic, settlement-level, and migration-origin analysis.

The workflow converts a searchable PDF source into a normalized flat CSV where one row equals one person.

## Current Phase

Current phase: PDF text extraction testing and conversion workflow design.

The project has already defined:

- final CSV schema;
- locality metadata lookup;
- stable person ID logic;
- source-position ID logic;
- controlled vocabularies;
- text-cleaning rules;
- Python helper functions for transformation and quality assurance.

## Source Extraction Approach

The source PDF has a readable text layer. Therefore, OCR is not the primary extraction method.

The planned workflow is:

```text
PDF text layer
↓
extract page text with pdfplumber
↓
preserve printed book page number
↓
remove running headers and repeated locality/district headings
↓
split text into person-level records
↓
convert raw split records into final CSV schema
↓
run validation and QA
```
Workflow now includes manual anomaly review after automated QA and confirmed source typos are either: preserved as printed or mapped through documented normalization rules depending on the field and certainty.

Printed book page numbers are preserved in `page_number`. PDF viewer page numbers are not used unless they match printed pagination.

If a person record starts on one printed page and continues onto the next page, the `page_number` should be the printed page where the record begins.

## Language and Translation Strategy

The project preserves Russian/Cyrillic source values as the authoritative data layer. Translation and transliteration are applied only after cleaning and QA are completed.

The workflow uses three layers:

1. Raw extracted data — source-like Russian text.
2. Clean Russian canonical data — normalized Russian values used as the master database.
3. Bilingual analytical data — Russian values plus English translations/transliterations for SQL, Tableau, and portfolio presentation.

Personal names are transliterated, not translated. Analytical categories such as legal status, religion, literacy, family status, and origin place are translated through controlled reference tables.

## Raw-to-Final Conversion

The extraction workflow separates the process into two stages.

### 1. Raw split-record CSV

This file contains source-derived fields after initial record splitting.

Expected raw input fields include:

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

### 2. Final normalized CSV

The helper script transforms the raw split-record CSV into the final flat schema.

The final schema includes generated IDs, district metadata, settlement metadata, normalized fields, and cleaned source-derived values.

## Locality Metadata

Settlement names are normalized and mapped through the `SETTLEMENTS` lookup table.

The lookup derives:

- `district_code`;
- `district`;
- `settlement_order`;
- settlement type;
- starting page reference.

If a settlement is not found in the lookup table, the workflow should stop for manual review rather than guessing.

## Cleaning Principles

The cleaning workflow follows these principles:

1. Preserve source meaning.
2. Remove source markup only according to documented rules.
3. Normalize repeated historical categories through controlled vocabularies.
4. Preserve unexpected values and report them for manual review.
5. Avoid silent correction of ambiguous source anomalies.
6. Keep printed page numbers for traceability.
7. Keep `comments` and `notes_raw` separate from normalized analytical fields.

## General Text Cleanup Rules

General cleanup includes:

- removing PDF artifacts and invisible separators;
- removing source field prefixes such as `3.`, `6.`, `7.`;
- removing crossed-out text in angle brackets;
- restoring square-bracketed word parts;
- normalizing whitespace;
- removing trailing bare footnote digits from selected text fields.

Trailing bare footnote digits are not removed from `comments` and `notes_raw`.

## Source Markup Rules

Angle brackets `<...>` represent crossed-out text and are removed from converted values.

Examples:

```text
11. <Холост> на Сахалине → женат на Сахалине
4. <Мечислав> Бронислав Лисавецкий → Бронислав Лисавецкий
12. <Да> нет → FALSE
12. Да <нет> → TRUE
```

Square brackets `[...]` contain restored word parts. The restored letters are kept and the brackets are removed.

Examples:

```text
Пензенск[ой] → Пензенской
Правосл[авного] → Православного
Сс[ыльно]каторжная → Ссыльнокаторжная
```

## Field Normalization

### Settlement

Ordinary settlements remove the prefix `Селение`.

Special locality types are preserved, for example:

```text
Пост Александровский
Арковский кордон
Арковский станок
Пост Дуэ
Пост Корсаковский
Тарайское Зимовье
```

### Legal Status

`legal_status` is normalized against an expandable controlled vocabulary.

Known variants, abbreviations, and extraction artifacts are mapped to canonical values. Unknown values are preserved and reported for review.

### Family Status

`family_status` is normalized against an expandable controlled vocabulary.

Variants such as restored bracketed forms, spelling variants, and common abbreviations are mapped to canonical values. Unknown values are preserved and reported for review.

### Religion

`religion` is normalized as a confession label / вероисповедание.

Canonical values use neuter Russian forms where appropriate. The noun values `Раскольник` and `Старообрядец` are preserved as nouns.

Year-like or numeric values in the religion field are preserved and flagged as probable source anomalies.

### Origin Place

`origin_place` is normalized against an 1890 administrative-unit reference library.

The reference library includes:

- main governorates of the Russian Empire;
- Polish governorates;
- Finnish governorates;
- oblasts;
- special administrative units;
- selected non-administrative source values such as `На Сахалине` and `По пути`.

Unknown values are preserved and reported for manual review.

If `origin_place` contains an occupation-like value, it is not automatically corrected. It is preserved and flagged as a probable source anomaly.

## Python Helper Script

The current helper script supports:

- PDF artifact cleanup;
- source markup normalization;
- field prefix removal;
- trailing footnote cleanup;
- settlement normalization;
- household number normalization;
- generation of `person_id`;
- generation of `source_position_id`;
- normalization of legal status, family status, religion, origin place, age, allowance status, and notes;
- transformation of raw split-record CSV into final CSV;
- validation of final output.

The main planned workflow functions are:

```python
extract_pdf_text_pages()
transform_records_csv()
validate_output_csv()
```

## Quality Assurance

The QA workflow checks:

- `person_id` uniqueness;
- `source_position_id` uniqueness;
- valid settlement-to-district mapping;
- valid natural-number fields for page number, age, and arrival year;
- controlled values for literacy, marriage status, and allowance status;
- absence of leftover `<...>` or `[...]` markup;
- absence of trailing bare footnote digits in normalized text fields;
- valid `notes_raw` archive-number format;
- unknown legal status, family status, religion, and origin-place values;
- possible source anomalies such as religion values that look like years or origin values that look like occupations.

## Current Next Step

The next methodological step is to create a 300–500 record sample and run the full conversion and QA workflow on that sample.

The sample should produce:

- raw split-record CSV;
- final normalized CSV;
- QA report;
- list of unknown or ambiguous values for manual review;
- updated controlled vocabularies where necessary.

