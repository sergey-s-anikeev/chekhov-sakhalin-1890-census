# Parser Improvements After Full-District Validation

## Children's origin-by-age Tableau views — 2026-10-27

Recorded the owner-supplied [detailed four-category dashboard](https://public.tableau.com/views/ChildrensrecordedoriginbyageSakhalin1890/Dashboard1) and [two-group share link](https://public.tableau.com/shared/ZMWP4CSS2). Saved screenshots of both views were visually inspected. The detailed dashboard retains On Sakhalin, recorded origin elsewhere, In transit and origin not recorded as separate segments and displays the age-eight missing-origin caveat. Updated the README, origin analysis and tracker to four named children's dashboards, an additional shared view and nine screenshots. Live Tableau pages and data-source connections were not independently inspected. No existing dataset or CSV values changed.

## Children's origin-by-age CSV registration — 2026-10-27

Registered two owner-supplied, 17-row children’s origin-by-age results from `sql/10_children_origin_age_profile.sql`. Every header and value matches the locally validated query results; hashes are saved in `outputs/qa/children_origin_age_export_20261027/validation.json`. The current Tableau inventory is 50 CSV files. The results of `sql/09_arrival_children_origin_queries.sql` and the new settlement-literacy query remain unexported. No canonical or previously registered CSV was changed.

## Children's documentation and full inventory reconciliation — 2026-10-19

Updated current status to three dashboards and seven screenshots, recorded the previously supplied settlement URL, and kept live filter verification separate. Expanded the general export audit to include the literacy and settlement SQL, preserving earlier QA reports. All 48 CSVs reconcile: 42 current matches, four documented historical variants and two known legacy exclusions; no retained source-value differences. Added settlement findings comparing counts and shares with explicit denominators and missing-age limitations. Earlier establishment remains a hypothesis for later comparison with historical sources. No canonical data or exported CSVs changed.

## Settlement dashboard and saved export — 2026-10-14

Recorded owner completion and the final screenshot. Registered the settlement CSV after exact comparison with validated SQL results: 51 rows, 7,446 people, 1,467 children. Inventory now 48 CSVs. Screenshot layout reviewed; public URL and independent live filter checks pending. Source data unchanged.

## Settlement geography preparation — 2026-10-14

Owner selected settlement-level analysis instead of a district-only dashboard. Added a read-only query, reproducible validation and Tableau guide. Local checks reconcile 51 district/settlement groups to 7,446 people and 1,467 children, retaining seven zero-child groups and reporting missing-age coverage. Settlement establishment is an untested explanatory hypothesis. CSV export remains pending; the 47-file inventory and all source records are unchanged.

## Children's findings and corrected screenshot acceptance — 2026-10-14

Verified updated single-sex screenshots: literacy totals 274 female / 262 male; age totals 726 female / 741 male. Closed displayed summary-filter checks and reconciled current documentation. The findings section records 136 Literate, 178 Illiterate and 222 Not recorded among ages 5–15, with missingness and school-attendance limitations. README now describes literacy as published and explains all 47 CSVs, including the literacy export. Historical review entries below retain their original status; the corrections in this entry supersede those open summary issues.

## Dashboard review, findings and district query — 2026-10-14

Recorded owner review completion and six screenshots. Local image inspection found that the literacy summary remains 536 in both single-sex views; expected values are 274 and 262. The age summary table also remains unfiltered. These acceptance items stay open. Added `docs/children_findings.md` and a read-only district comparison query, locally validated against 7,446 people and 1,467 children. District export is pending; inventory remains 47 CSV files. No source data or existing exports changed.

## Literacy dashboard publication and export registration — 2026-10-13

Owner supplied the second dashboard URL: [Recorded literacy among children aged 5–15](https://public.tableau.com/views/Recordedliteracyamongchildrenaged515/Dashboard1). Registered `children_literacy_age_sex_20261013.csv`: 75 rows matching SQL exactly, 1,467 children in the full export and 536 aged 5–15. Inventory is now 47 CSVs. SHA-256 and local reconciliation evidence: `outputs/qa/children_literacy_export_20261013/validation.json`. Published layout, sources, filters and percentage behavior remain unverified because web retrieval could not inspect the dashboard. Existing source data and historical exports remain unchanged.

## Revised literacy chart age filter — 2026-10-13

Decision 42 supersedes Decision 41: use ages 5–15 to include one recorded literate child at age five and one at age six. The owner reports setting the chart filter. Updated current guidance and benchmarks: 536 children (274 female; 262 male), including 136 Literate, 178 Illiterate and 222 Not recorded. Educated remains zero. The 0–15 SQL/export and source data remain unchanged; propagation to all related sheets still requires verification.

## Initial literacy chart age filter — 2026-10-13 (superseded by Decision 42)

Decision 41 records the owner-approved ages 7–15 focus for the literacy visualization. The 0–15 definition and SQL/export scope remain unchanged. Updated the authoring instructions and checklist to apply the filter to related sheets, retain missing literacy and verify 346 children (176 female; 170 male). Source tallies: Literate 134, Educated 0, Illiterate 150, Not recorded 62. Tableau application remains pending.

## First Tableau dashboard and next literacy source — 2026-10-13

Recorded the owner-supplied public link: [Sakhalin 1890 — Children aged 0–15](https://public.tableau.com/views/Sakhalin1890Childrenaged015/Dashboard1). Construction/publication is owner-reported; independently checking the published view remains pending. Added the children’s literacy SQL, export/browser instructions and local validation. The query returns 75 groups covering 1,467 children: Literate 136, Educated 0, Illiterate 211, Not recorded 1,120. Each age/sex total reconciles to the first dashboard’s registered CSV. No canonical data or existing CSVs changed. The next MySQL export has not been created; the inventory remains 46 files. See `docs/children_literacy_tableau.md` and `outputs/qa/children_literacy_20261013/`.

## Approved children's scope and SQL correction — 2026-10-12

Decision 40 defines the children's block as Children aged 0–15. Corrected both child queries in `sql/04_analysis_queries.sql`, and added `sql/05_children_0_15_queries.sql` with the two replacement queries and a validation result. Child-age totals change from 1,545 to 1,467; child-sex totals from 1,510 to 1,467. Female: 726; Male: 741. Local validation passed, and the affected IDs are recorded in `outputs/qa/children_0_15_20261012/`. Existing 16+ analyses retain their filters, with clearer descriptive comments. Original CSVs and person records remain unchanged. Follow-up registration: both supplied replacement CSVs with suffix `10122026` are present and match the corrected queries. The export register now contains 46 CSVs. Verification evidence is in `outputs/qa/tableau_preflight_20261012_csv_register/`; MySQL execution logs were not inspected and Tableau checks remain pending.

## Tableau pre-import follow-up — 2026-10-12

Refreshed source and snapshot reconciliation in a separate dated QA package, preserving the 2026-10-04 evidence. All 59 preparation assertions passed. Added exact import benchmarks, explicit starter-source selection, and numerical examples of subtotal, percentage-denominator, and age-scope errors. Reconfirmed the 22-column practice file has zero retained-cell differences from English v1. The 44 snapshot results remain 40 current matches, two documented variants, and two legacy files excluded from starter use. No person values, canonical releases, or historical exports changed. Tableau application tests and external publication verification remain pending.

## Tableau preparation and documentation reconciliation — 2026-10-04

Added a separate 7,446-row, 22-column local practice derivative of English v1, omitting only full_name. All retained values and row order reconcile exactly. The approved source hash is unchanged. Preparation guidance defines dimensions, missing values, denominators, household grouping, age scopes, historical snapshot selection, and public aggregate recommendations. Preflight evidence is in `outputs/qa/tableau_preflight_20261004/`.

Reconciled the development checklist with existing English approval and MySQL QA evidence, documented the English dictionary and excluded canonical fields, and replaced obsolete sample-stage limitations. Tableau application checks and external publication verification remain pending. Original releases and historical exports remain unchanged.

## Approved English analytical release v1 — 2026-08-09

Decision 38 approved `data/analytical/sakhalin_1890_en_v1.csv`: 7,446 rows and 23 fields, with approved transliteration and category/geographic mappings. SHA-256: `1b77d6330855763c54c32f21d247dc44471a69590db4fc00925c4e22eb8ac508`. Field reconciliation found zero mismatches; the MySQL import loaded all records without warnings and passed documented controls. Russian canonical v5 remains authoritative. See `outputs/qa/english_dataset_quality_review_20260809/english_dataset_quality_report_20260809.json` and `docs/mysql_english_dataset_import.md`.

## Canonical reviewed-name release v5 — 2026-07-31

Release `v5_20260731` promotes the completed post-v4 review sequence into a new immutable canonical version. It retains 7,446 records and established identifier order, expands the schema from 36 to 50 columns, and preserves all prior analytical fields.

The release incorporates exactly 56 approved Item 24 `comments` corrections, 55 reviewed `name_raw` changes, and 39 `name_alias` changes relative to v4. It adds `first_name`, `patronymic_name`, `last_name`, component-level provenance, parsing status and confidence, parsing rule, detected source order, naming model, manual-review reason, and two blank proposal-audit fields.

All 7,446 name records are resolved with `parse_status = observed`. Integrated QA passed record and schema counts, identifier stability and formatting, district counts and exact concatenation, numeric formats and ranges, age/month consistency, controlled-value capitalization, approved-change boundaries, component/provenance consistency, zero unresolved name proposals, zero first-name spelling candidates, complete v4-to-v5 diffs, and SHA-256 hashing. Evidence is stored in `outputs/qa/canonical_v5_20260731/`.

The v4, v3, v2, and original canonical datasets remain unchanged as historical release artifacts.

## Canonical quality-review release v4 — 2026-07-17

Release `v4_20260717` promotes the approved post-v3 quality-review sequence into a new immutable canonical version. It retains 7,446 records, expands the schema from 31 to 36 columns, and adds `age_months`, `origin_place_norm`, `occupation_norm`, `marriage_status_norm`, and `living_alone_status`.

The release includes approved age and raw-recognition corrections, whole-year month derivation for ages 1 and 2, origin and occupation normalization, marriage-status structure, reviewed comment cleanup and owner feedback, and 18 unique late alias additions. All four v3 files remain unchanged as historical canonical artifacts.

Integrated QA passed record counts, schema, district ordering and concatenation, identifier uniqueness and formatting, numeric formats and ranges, age/month consistency, controlled values, Sentence case, Item 3 legal-status dependency synchronization, gender consistency, complete diffs, and SHA-256 hashing. Evidence is stored in `outputs/qa/canonical_v4_20260717/`.

Historical post-v4 status (2026-07-18, superseded by the v5 release above): Item 24 comments review was complete in a staged candidate with 56 comment-only changes. Item 25 occupation-semantic grouping was evaluated and deferred without changes. At that date no v5 release had been authorized and v4 remained canonical.

---

The initial parser and normalization pipeline were developed and validated on a 500-record MVP sample. Running the pipeline on complete district-level data exposed several edge cases that were not present in the sample. The parser, normalization helper, controlled dictionaries, QA workflow, and final CSV utilities were subsequently improved through full validation on all three Sakhalin Census districts: Alexandrovsky, Tymovsky, and Korsakovsky.

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
| **v2.1** | Alexandrovsky District extraction support and parser fixes |
| **v2.2** | Alexandrovsky sequence-gap recovery and missing-record insertion |
| **v2.3** | Final Alexandrovsky manual-review integration |
| **v2.4** | Final three-district script update, CSV finalization, and merge support |

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

## 15. Alexandrovsky District extraction support

### Issue

Processing Alexandrovsky District exposed additional parser edge cases:

- printed book pages begin with two-digit page numbers, for example page `27`;
- ordinary Cyrillic words are sometimes broken by line breaks and hyphens;
- long record blocks contain archival references followed immediately by the next source record.

Examples:

```text
Негра-
мотен
→
Неграмотен

Саха-
лине
→
Сахалине
```

and:

```text
РГБ № 2009. 18. 2. 4. 2. 3. Ж[енщина] св[ободного] состояния...
```

### Solution

The parser was updated to:

- detect two-digit printed page numbers;
- join ordinary Cyrillic hyphenated line breaks;
- detect embedded record starts after archival references;
- preserve full source text for traceability while splitting person records correctly.

---

## 16. Alexandrovsky sequence-gap recovery

### Issue

Initial Alexandrovsky extraction produced complete-looking rows but record-sequence QA found gaps in five settlements/posts.

The missing source records were present in the extracted text but had been swallowed into preceding parsed blocks.

### Solution

The missing records were recovered, inserted into the clean file, and numbering was regenerated.

Recovered records:

```text
Александровское: 18, 23
Пост Александровский: 549, 1151
Ново-Михайловское: 163
Красный Яр: 49, 50
Пост Дуэ: 200, 255
```

### Result

After recovery:

```text
Rows: 2884
Inserted missing records: 9
Settlements with sequence gaps: 0
Record sequence QA: passed
```

---

## 17. Alexandrovsky critical review and final manual review

### Issue

Alexandrovsky manual review identified critical data issues and broader review decisions:

- blank `age` values where source field `5` was present;
- age values inflated by footnote digits;
- `arrival_year` source typos or extraction artefacts;
- names contaminated by household roles or explanatory text;
- household-role values stored in `name_raw` instead of `family_status`;
- locality-level notes better stored in `comments`.

### Solution

Critical corrections were applied first, then the final reviewed Alexandrovsky CSV was accepted as the district-level canonical file.

Manual-review decisions reflected in the final file:

- `name_raw` contains the person name only;
- household/family role details are stored in `family_status`;
- explanatory source details are stored in `comments`;
- critical `age`, `arrival_year`, and `name_raw` issues are resolved;
- remaining reviewed values are accepted as Alexandrovsky district-level canonical values for now.

### Result

Final Alexandrovsky validation:

```text
Rows: 2884
Duplicate person_id: 0
Duplicate source_position_id: 0
Blank name_raw: 0
Record sequence gaps: 0
Age non-numeric: 0
Age > 100: 0
Arrival year bad format: 0
Arrival year outside 1860–1891: 0
```

---

## 18. Excel and CSV finalization support

### Issue

Manual review in Excel can change technical CSV properties without changing substantive data.

Observed examples:

```text
Delimiter: comma → semicolon
Encoding: UTF-8 → UTF-8 with BOM
settlement_order: 01 → 1
```

These are export artefacts but can affect reproducibility and downstream processing.

### Solution

Finalization utilities were added to standardize reviewed CSV files.

The finalizer now supports:

- comma or semicolon delimiter detection;
- UTF-8 and UTF-8-BOM input;
- restoration of two-digit `settlement_order` values;
- sorting by source order;
- export as project-standard comma-delimited UTF-8 CSV.

Recommended Excel workflow for future manual edits:

```text
Data → From Text/CSV
File origin: UTF-8
Delimiter: choose actual delimiter
Transform Data
Set all columns to Text
Then edit/save
```

Key columns should always be treated as text:

```text
person_id
source_position_id
district_code
settlement_order
person_order_in_settlement
page_number
household_number
age
arrival_year
notes_raw
```

---

## 19. Final script update and merge support

### Issue

After all three districts were manually reviewed, the scripts needed to support both district-level reproducibility and a consolidated all-district dataset.

### Solution

The final script update added:

- reviewed Alexandrovsky, Tymovsky, and Korsakovsky values as accepted district-level canonical values;
- CSV finalization for manually reviewed files;
- post-processing helpers for `name_raw` role leakage into `family_status`;
- post-processing helpers for `marriage_status` explanations into `comments`;
- post-processing helpers for occupation explanatory suffixes into `comments`;
- merge utility for the three final district clean files.

Current final scripts include:

```text
sakhalin_conversion_helpers_v12.py
create_raw_records_from_pages_v3.py
finalize_reviewed_clean_csv.py
merge_clean_districts.py
```

The merge workflow keeps `source_position_id` stable and can assign final global `person_id` values across all districts.

---

## 20. Three-district record-count validation

### Issue

After all districts were processed, the project required an all-district row-count validation based on settlement/post person-order sequences.

### Solution

Record counts were validated using this rule:

```text
records_with_name = max(person_order_in_settlement)
and
no missing person_order_in_settlement numbers
and
no duplicate person_order_in_settlement numbers
and
no blank name_raw rows
```

### Result

All 51 settlements/posts passed sequence validation.

| District | Records | Settlements/posts | Sequence validation |
| -------- | ------: | ----------------: | ------------------- |
| Александровский | 2884 | 18 | passed |
| Тымовский | 3242 | 9 | passed |
| Корсаковский | 1320 | 24 | passed |
| **Total** | **7446** | **51** | **passed** |

---

## Current Status

The pipeline now supports full-district extraction, normalization, QA, manual review, final CSV standardization, and reproducible correction workflows for all three districts.

Current validated outputs:

```text
Alexandrovsky District:
- rows: 2884
- record-sequence QA: passed
- blank name_raw: 0
- duplicate source_position_id: 0
- age range QA: passed
- arrival_year range QA: passed

Tymovsky District:
- rows: 3242
- manual-review issues: 0
- unknown controlled-vocabulary values: 0
- record-sequence QA: passed
- age range QA: passed
- arrival_year range QA: passed

Korsakovsky District:
- rows: 1320
- manual-review issues: 0
- source anomalies: 0
- record-sequence QA: passed
```

All three districts combined:

```text
Total records: 7446
Total settlements/posts: 51
Settlement/post sequence validation: passed
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
- reviewed CSV finalization;
- final district validation;
- three-district merge support;
- consolidated record-count validation.


---

## v2.5 Final three-district merge

### Issue

After district-level review, the final release required a project-level merge with consistent identifiers, CSV formatting, and validation across all three districts.

### Solution

The finalization step standardizes the reviewed district files, restores two-digit `settlement_order`, sorts records by source order, preserves `source_position_id`, and assigns global `person_id` values across the merged dataset.

### Result

```text
Total records: 7446
Alexandrovsky District: 2884
Tymovsky District: 3242
Korsakovsky District: 1320
Settlement/post sequence validation: passed
Final QA status: passed
```

The final release includes the merged Russian master file, district-level clean files, QA reports, settlement-sequence validation, district record counts, methodology, data dictionary, and final validation summary.

---

## v2.6 Owner-approved name normalization release

### Date

2026-07-11

### Scope

This versioned canonical release incorporates the approved Item 1 and Item 2 name reviews without overwriting the prior canonical artifacts.

### Changes

- Updated `name_raw` in 66 records: 37 Item 1 corrections and 29 approved Item 2 normalized names.
- Added `name_alias` immediately after `name_raw`; 40 records contain approved alias values.
- Applied 2 approved `family_status` corrections.
- Applied 7 approved `comments` updates.
- Excluded the review-only `name_norm`, `name_note`, `surname_alternative`, and `surname_alternative_proposed` fields from the canonical schema.
- Created versioned combined and district files with a common 24-column schema.

### Validation

- Records: 7,446.
- District counts: 2,884 Alexandrovsky; 3,242 Tymovsky; 1,320 Korsakovsky.
- Blank `name_raw`: 0.
- Duplicate `person_id`: 0.
- Duplicate `source_position_id`: 0.
- Stable identifier and district ordering: unchanged.
- Combined file equals the exact ordered concatenation of the three versioned district files.

QA evidence is stored in `outputs/qa/name_normalization_canonical_v2_20260711/`.

---

## v3.0 Approved normalization consolidation

### Date

2026-07-12

### Scope

This versioned canonical release consolidates all normalization items approved through 2026-07-12 while preserving v2 and the unversioned canonical releases as historical artifacts. Pending tracker items are not represented as completed fields.

### Schema

- Expanded the common schema from 24 to 31 columns.
- Replaced `household_number` with `household_id`, `household_type`, and `household_details`.
- Added `legal_status_norm`, `sex`, `sex_evidence`, `family_status_norm`, and `illness_norm`.
- Preserved detailed `legal_status`, `family_status`, and `illness` alongside their approved analytical fields.

### Integrated approved changes

- Applied the owner-reviewed household structure and 299 resulting source-position updates.
- Applied 41 approved `notes_raw` changes.
- Applied 16 detailed `legal_status` corrections and regenerated `legal_status_norm` afterward.
- Added approved `sex` values for all records: 4,921 `Мужской` and 2,525 `Женский`.
- Added approved `family_status_norm` and `illness_norm` mappings.
- Applied 9 religion changes, 5,419 Sentence case literacy changes, 5 `Богадельщик` transfers to `illness`, and 8 comment changes.

### Validation

- Records: 7,446; fields: 31.
- District counts: 2,884 Alexandrovsky; 3,242 Tymovsky; 1,320 Korsakovsky.
- Unique, nonblank `person_id` and `source_position_id`: passed.
- Person order and ordered district concatenation: passed.
- Owner-verified blank `household_type` count: 24.
- Sentence case normalized-category check: passed.
- Cross-field gender consistency check: passed with zero unresolved conflicts.
- Combined file equals the exact ordered concatenation of the three v3 district files.

QA evidence and SHA-256 hashes are stored in `outputs/qa/canonical_v3_20260712/`.
