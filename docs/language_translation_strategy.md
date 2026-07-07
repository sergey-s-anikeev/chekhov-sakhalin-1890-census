# Language and Translation Strategy

## Overview

The project preserves Russian/Cyrillic source values as the authoritative data layer. Translation and transliteration are applied only after cleaning and QA have been completed.

This approach preserves historical accuracy while providing an English analytical dataset suitable for SQL analysis, Tableau dashboards, and an international portfolio.

---

# Recommended Data Pipeline

```text
PDF source
↓
raw_extracted_records.csv               # Russian, close to source
↓
clean_ru.csv                            # cleaned Russian canonical database
↓
clean_bilingual.csv                     # Russian + English analytical columns
↓
SQL / Tableau / portfolio outputs
```

---

# Stage 1 — Raw Extraction

Keep all values as close to the source as possible.

Example:

- Правосл[авного]
- Сс[ыльно]каторжный
- Тверск[ой]
- РГБ № 6810

No translation is performed at this stage.

---

# Stage 2 — Clean Russian Canonical Database

This is the project's master dataset.

Example:

- religion = Православное
- legal_status = Ссыльнокаторжный
- origin_place = Тверская губерния
- family_status = Хозяин

Output:

```text
data/processed/full_clean_ru.csv
```

This dataset should remain the authoritative source for future historical work and the planned online database.

---

# Stage 3 — Bilingual Analytical Dataset

After district-level QA has been completed, create additional English columns.

Do **not** replace Russian values.

Instead, create bilingual fields such as:

```text
legal_status_ru
legal_status_en

family_status_ru
family_status_en

religion_ru
religion_en

origin_place_ru
origin_place_en

settlement_ru
settlement_en

occupation_ru
occupation_en

name_raw_ru
name_translit
```

Output:

```text
data/processed/full_clean_bilingual.csv
```

This becomes the main dataset used for SQL analysis, Tableau dashboards, and portfolio presentation.

---

# Translation vs Transliteration

## Translate analytical categories

Translate:

- legal_status
- family_status
- religion
- occupation
- literacy
- marriage_status
- allowance_status
- district
- settlement_type

Examples:

| Russian | English |
|----------|----------|
| Ссыльнокаторжный | Penal Convict |
| Поселенец | Exile Settler |
| Православное | Orthodox |
| Неграмотен | Illiterate |

---

## Transliterate personal names

Personal names should never be translated.

Example:

| Russian | Transliteration |
|----------|----------------|
| Иван Вардзинский | Ivan Vardzinsky |
| Анна Андреева Рудзит | Anna Andreeva Rudzit |

Store both:

```text
name_raw_ru
name_translit
```

---

## Administrative Units

Keep both Russian and English versions.

Example:

| Russian | English |
|----------|----------|
| Тверская губерния | Tver Governorate |
| Курляндская губерния | Courland Governorate |
| Подольская губерния | Podolia Governorate |
| Кубанская область | Kuban Oblast |

---

# Reference Tables

Translation should not be performed row-by-row.

Instead, maintain lookup/reference tables.

Examples:

```text
reference/legal_status_reference.csv
reference/religion_reference.csv
reference/origin_place_reference.csv
reference/family_status_reference.csv
reference/occupation_reference.csv
```

These reference tables are used to generate the bilingual analytical dataset.

---

# Recommended Workflow

For each district:

```text
1. Extract records
2. Clean in Russian
3. Run QA
4. Resolve anomalies
5. Freeze Russian master dataset
6. Apply lookup tables
7. Export bilingual dataset
```

After all districts:

```text
clean_alexandrovsky_ru.csv
clean_tymovsky_ru.csv
clean_korsakovsky_ru.csv
↓
full_clean_ru.csv
↓
full_clean_bilingual.csv
```

---

# SQL and Tableau

Modern SQL databases and Tableau fully support UTF-8, so Cyrillic is not a technical problem.

For international users, dashboards should primarily display English analytical fields while preserving Russian originals for traceability.

Example tooltip:

```text
Original: Ссыльнокаторжный
English: Penal Convict
Source page: 420
Archive note: РГБ № 6982
```

---

# Three-Layer Data Model

## Layer 1

```text
raw_extracted_records.csv
```

Source-like Russian data.

## Layer 2

```text
full_clean_ru.csv
```

Authoritative cleaned Russian database.

## Layer 3

```text
full_clean_bilingual.csv
```

English analytical dataset for SQL, Tableau, and GitHub portfolio.

---

# Recommendation

Always perform:

**Extract → Clean → QA → Freeze Russian Master → Translate via Lookup Tables**

Never translate before QA.

This preserves historical fidelity, simplifies quality control, and produces a professional bilingual dataset suitable for both academic work and an international data analytics portfolio.
