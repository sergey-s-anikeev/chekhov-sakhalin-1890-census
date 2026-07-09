# Parser Improvements After Full-District Validation

The initial parser and normalization pipeline were developed and validated on a 500-record MVP sample. Running the pipeline on complete district-level data exposed several edge cases that were not present in the sample. The parser, normalization helper, controlled dictionaries, and QA workflow were subsequently improved through full validation on the Korsakovsky and Tymovsky districts.

| Version  | Description |
| -------- | ----------- |
| **v1.0** | Initial MVP parser for a 500-record sample |
| **v1.1** | Improved normalization rules |
| **v1.2** | Support for inline record starts |
| **v1.3** | Record-splitting prevention |
| **v1.4** | Arrival year extraction fix |
| **v1.5** | RGALI support and category-code recovery |
| **v1.6** | Full Korsakovsky District validation and manual-review workflow |
| **v1.7** | Tymovsky District parser/layout support |
| **v1.8** | Controlled-vocabulary expansion for Tymovsky values |
| **v1.9** | Critical manual-review corrections and reproducible correction scripts |
| **v2.0** | Numeric range QA and symbol-tolerant normalization |

---

## 1. Support for inline record starts

### Issue

Some census records begin on a single line:

```text
104. 2. 41. 3. ...
1153. 2. 256. 3. ...
```

instead of:

```text
104.
2. 41. 3. ...
```

The original parser failed to detect these records correctly.

### Solution

The record-start detection was generalized to support both layouts.

---

## 2. Prevent record splitting

### Issue

Some field lines begin with numeric field identifiers, for example:

```text
5. 2.
6. Правосл[авного].
```

The parser occasionally interpreted these as the beginning of a new person record, resulting in:

- duplicated records;
- empty records;
- missing `name_raw`;
- incorrect settlement population counts.

Example:

- Settlement **Сиянцы** contains **71** residents in the source.
- The parser initially produced **72** records.

### Solution

Record-start detection was tightened.

A new record is now accepted only if it satisfies the complete record-start pattern instead of relying on leading numbers alone.

Additional validation verifies that every parsed record contains a populated `name_raw` field.

---

## 3. Preserve complete settlements in MVP samples

### Issue

The initial 500-record sample ended in the middle of **Пост Корсаковский**, resulting in incomplete settlement data.

### Solution

The extraction workflow now continues until the current settlement has been completely processed.

This produces a minimum sample of approximately 500 records without truncating settlements.

---

## 4. Arrival year extraction

### Issue

The majority of `arrival_year` values were missing after normalization despite being present in the extracted text.

The normalization routine incorrectly treated valid years as formatting artefacts.

### Solution

Year normalization was rewritten.

Valid four-digit years are now preserved while only genuine OCR artefacts and footnotes are removed.

---

## 5. Archive reference normalization

### Issue

Two archive reference formats occur in the source:

```text
РГ Б № 4568
РГ АЛИ № 146
```

Only the first format was originally recognized.

### Solution

Normalization now supports both archive identifiers.

Examples:

```text
РГ Б № 4568
→
РГБ № 4568

РГ АЛИ № 146
→
РГАЛИ № 146
```

The normalizer also preserves archive-number suffixes, for example:

```text
РГБ № 5774-а
```

---

## 6. Category-code recovery

### Issue

Some census records contain typographical errors in printed category numbers, for example:

```text
5. Анна Андреева...
```

instead of:

```text
4. Анна Андреева...
```

This caused incorrect field assignment.

### Solution

Recovery logic was added for known category-code inconsistencies.

The parser now reconstructs the intended field structure while preserving the original text for traceability.

---

## 7. Full Korsakovsky District validation

### Issue

Running the pipeline on the full Korsakovsky District exposed issues that were not visible in the MVP sample, including:

- incomplete settlement handling;
- false record starts;
- missing or malformed `arrival_year` values;
- previously unseen legal-status, family-status, religion, and origin-place variants;
- source-specific archive-reference formats.

### Solution

A full-district QA workflow was added. It includes:

- row-count and record-sequence checks;
- missing `name_raw` validation;
- controlled-vocabulary validation;
- manual-review export;
- manual-review application scripts;
- applied-change logs;
- remaining-issue reports.

### Result

After manual review, the Korsakovsky District output reached approved status:

```text
Rows: 1320
Unknown legal_status values: 0
Unknown family_status values: 0
Unknown religion values: 0
Unknown origin_place values: 0
Remaining source anomalies: 0
Remaining manual-review issues: 0
```

---

## 8. Tymovsky District parser/layout support

### Issue

Processing Tymovsky District exposed additional source layouts, including:

```text
1. <settlement correction>. 2. <household>. 3. ...
```

and mixed Latin/Cyrillic characters in field content, for example:

```text
Cc[ыльно]каторжный
```

These layouts could interfere with field detection and dictionary matching.

### Solution

The parser and helper were extended to support:

- records where field `1.` appears before field `2.`;
- mixed Latin/Cyrillic cleanup in selected controlled fields;
- additional Tymovsky heading and settlement patterns;
- continued record-sequence validation across the full district.

### Result

The Tymovsky extraction passed core structural checks:

```text
Rows: 3242
Missing name_raw: 0
Record-sequence QA: passed
```

---

## 9. Controlled-vocabulary expansion

### Issue

Tymovsky District contains a wider range of household roles, legal statuses, religions, origins, and marriage-status descriptions than the initial Korsakovsky-oriented dictionaries.

Examples include:

```text
Жена совладельца
Дочь совладельца
Сожительница совладельца
Запасный унтер-офицер
Административно сосланный
Православное (выкрест)
Молоканское
Раскольничество
Старообрядчество
В пути следования
Австрийский подданный
женат на родине. одинок
```

### Solution

The controlled dictionaries were expanded for:

- `family_status`;
- `origin_place`;
- `legal_status`;
- `religion`;
- `marriage_status`.

Variant mappings were added so that spelling, gender, case, and OCR variants normalize to canonical values.

Examples:

```text
Молоканин
→
Молоканское

Раскольник / Раскольница
→
Раскольничество

Старовер / Староверка
→
Старообрядчество

Румынского королевства
→
Румынское королевство

В Усть-Каре
→
Усть-Кара
```

---

## 10. Critical manual-review corrections

### Issue

A small number of records contained critical extraction or normalization issues, including:

- inline footnote digits attached to names;
- noisy `allowance_status` values;
- rare field shifts where age and religion were combined in field `5`;
- blank `age` values where source field `5` required review.

Examples:

```text
Иван Алексеев2 Самудоров3
→
Иван Алексеев Самудоров

нет. 14.?
→
FALSE

5. 44. Раскольн[ица].
→
age = 44
religion = Раскольничество
```

### Solution

Critical review corrections were implemented through reproducible correction scripts rather than ad hoc edits.

The workflow now produces:

- applied-change logs;
- remaining-review files;
- summary documentation;
- reproducible district-specific correction scripts.

---

## 11. Manual-review feedback workflow

### Issue

Some QA flags were not extraction errors but legitimate source values or values requiring field-specific decisions.

For example, some `origin_place` values were better preserved as non-administrative source categories, while some values needed to be moved to `comments`.

### Solution

A manual-review feedback workflow was added.

The workflow supports:

- adding reviewed values to controlled dictionaries;
- applying corrected values by `person_id`;
- appending reviewed content to `comments` where appropriate;
- preserving unresolved text-recognition issues for later clean-CSV correction;
- generating applied-change and remaining-review reports.

---

## 12. Numeric range QA

### Issue

Some numeric fields may absorb footnote digits or source typos.

Examples:

```text
56 + footnote 1 → 561
45 + footnote 1 → 451
1976 instead of 1876
```

### Solution

Numeric range validation was added to QA.

Rules:

```text
age:
- must be numeric when present;
- must not exceed 100.

arrival_year:
- must be a four-digit year when present;
- must be between 1860 and 1891.
```

### Result

The current Tymovsky output passes these checks:

```text
age non-numeric: 0
age > 100: 0
arrival_year bad format: 0
arrival_year outside 1860–1891: 0
```

---

## 13. Symbol-tolerant normalization

### Issue

Some source values contain special symbols that should not prevent normalization.

Examples:

```text
5. /39?/
холост (?)
/1887?/
```

These values should normalize to their substantive content.

### Solution

Normalization now ignores selected special symbols in controlled and numeric fields:

```text
/ , ? ( )
```

Examples:

```text
/39?/ → 39
холост (?) → холост
/1887?/ → 1887
```

The cleanup is not applied to `comments` or `notes_raw`, where punctuation and archive references may be meaningful.

Canonical dictionary values with meaningful parentheses are preserved, for example:

```text
Православное (выкрест)
Поселка (богадельщик)
```

---

## 14. Additional normalization improvements

Additional normalization rules were added after reviewing real source anomalies.

Examples include:

```text
Сс[ылно]каторжный
→
Ссыльнокаторжный

Правосл [авного]
→
Православное

Каменецк-Подольская
→
Подольская губерния

Курляндского
→
Курляндская губерния

Ломжинская
→
Ломжинская губерния
```

---

## Current Status

The pipeline currently supports full-district extraction, normalization, QA, manual review, and reproducible correction workflows for the processed districts.

Current validated outputs include:

```text
Korsakovsky District:
- rows: 1320
- manual-review issues: 0
- source anomalies: 0

Tymovsky District:
- rows: 3242
- manual-review issues: 0
- unknown controlled-vocabulary values: 0
- age range QA: passed
- arrival_year range QA: passed
```

---

## Result

The parser has evolved from a sample-oriented prototype into a reusable district-scale extraction pipeline capable of processing the complete 1890 Sakhalin Census while preserving historical fidelity and supporting reproducible QA.

The current workflow includes:

- district-level raw extraction;
- page-level text extraction;
- Russian clean master data generation;
- controlled-vocabulary normalization;
- record-sequence validation;
- numeric range validation;
- blank-age source verification;
- manual-review export;
- reproducible correction scripts;
- applied-change logs;
- final remaining-issue reports.
