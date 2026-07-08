# Parser Improvements After Full-District Validation

The initial parser and normalization pipeline were developed and validated on a 500-record MVP sample. Running the pipeline on the complete Korsakovsky District exposed several edge cases that were not present in the sample. The parser and helper library were subsequently improved.

| Version  | Description                              |
| -------- | ---------------------------------------- |
| **v1.0** | Initial MVP parser (500-record sample)   |
| **v1.1** | Improved normalization rules             |
| **v1.2** | Support for inline record starts         |
| **v1.3** | Record-splitting prevention              |
| **v1.4** | Arrival year fix                         |
| **v1.5** | RGALI support and category-code recovery |


## 1. Support for inline record starts

### Issue

Some census records begin on a single line:

```
104. 2. 41. 3. ...
1153. 2. 256. 3. ...
```

instead of

```
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

```
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

```
РГ Б № 4568
РГ АЛИ № 146
```

Only the first format was originally recognized.

### Solution

Normalization now supports both archive identifiers.

Examples:

```
РГ Б № 4568
→
РГБ № 4568

РГ АЛИ № 146
→
РГАЛИ № 146
```

---

## 6. Category-code recovery

### Issue

Some census records contain typographical errors in printed category numbers, for example:

```
5. Анна Андреева...
```

instead of

```
4. Анна Андреева...
```

This caused incorrect field assignment.

### Solution

Recovery logic was added for known category-code inconsistencies.

The parser now reconstructs the intended field structure while preserving the original text for traceability.

---

## 7. Normalization improvements

Additional normalization rules were added after reviewing real source anomalies.

Examples include:

```
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
```

---

## Result

The parser has evolved from a sample-oriented prototype into a reusable district-scale extraction pipeline capable of processing the complete 1890 Sakhalin Census while preserving historical fidelity and supporting reproducible QA.
