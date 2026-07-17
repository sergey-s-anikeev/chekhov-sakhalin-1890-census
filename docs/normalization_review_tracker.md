# Consolidated Dataset Normalization Review Tracker

## Purpose

This document tracks the post-release review and normalization of `data/processed/clean_sakhalin_1890_ru.csv`.

The canonical datasets are immutable. Each item must be completed separately, using a reproducible review script and, where needed, an explicit correction or mapping table. Proposed results must be written to a versioned staging location. No proposed result becomes canonical without project-owner approval.

## Status Key

- `[ ]` Not started
- `[~]` In progress
- `[R]` Ready for owner review
- `[x]` Approved and completed
- `[B]` Blocked pending evidence or owner decision

## One-Item Execution Protocol

For each numbered item:

1. Define the review rule and proposed normalized field or controlled vocabulary.
2. Generate a read-only exception inventory identifying every affected record by `person_id` and `source_position_id`.
3. Review ambiguous cases and record proposed decisions without changing canonical data.
4. Obtain project-owner approval for substantive mappings or controlled-vocabulary changes.
5. Apply approved decisions through a reproducible script and explicit mapping/correction input.
6. Write the result to a new versioned staging file.
7. Produce a record-level diff, field-level counts, applicable QA results, and a SHA-256 hash.
8. Mark the item complete only after owner review and approval.

Only one numbered item should be active at a time.

## Execution Order

### 1. Verify `name_raw` — `[x]` Approved and completed

- [x] Confirm that only personal names remain in `name_raw`.
- [x] Flag leaked roles or descriptions such as `жена`, `сын`, and `незаконнорожденный сын`.
- [x] Review unusually long non-Russian names without treating word count alone as an error.
- [x] Preserve `name_raw`; place approved aliases, former surnames, baptismal names, or explanatory text in separate derived fields.
- [x] Produce the complete affected-record inventory before proposing corrections.

Deliverables: exception inventory, proposed correction table, approved mapping decisions, staged result, diff, and QA report.

Completion status: the project owner supplied decisions for all 43 review records on 2026-07-11: 28 approved and 15 modified. The approved decisions were applied to a versioned staged candidate with `name_alias` immediately after `name_raw`. The canonical datasets remain unchanged.

### 2. Review parenthetical and double surnames — `[x]` Approved and completed

- [x] Review all names containing parentheses.
- [x] Classify each expression as an alternative surname, former surname, baptismal name, religious note, empty artifact, or unresolved text.
- [x] Define derived fields `name_norm` and `name_note` after the inventory review; use the existing `name_alias` field for approved alternatives.
- [x] Do not remove parenthetical evidence from `name_raw`.

Deliverables: classified record inventory, proposed field definitions, staged result, diff, and QA report.

Completion status: the owner reviewed all 75 hyphenated records on 2026-07-11. No `name_raw` values contain parentheses. The approved staged candidate contains `name_norm` and `name_note`; 26 approved alternative values were placed in the existing `name_alias` field. No `surname_alternative` field was created. For approved women’s hyphenated surname forms, `name_norm` retains the maiden surname and `name_alias` stores the husband surname. Canonical data remains unchanged.

### 3. Create and verify derived `sex` — `[x]` Approved and staged

- [x] Add a proposed derived field named `sex`; it is not present in the historical source dataset.
- [x] Propose Russian Sentence case controlled values: `Мужской`, `Женский`, or blank.
- [x] Derive a candidate value only from explicit grammatical or reviewed name evidence in `legal_status`, approved `legal_status_norm`, `family_status`, and `name_raw`.
- [x] Prefer explicit gendered evidence in `legal_status` or `family_status`; use `name_raw` only through reviewed patronymic morphology or a future approved name reference.
- [x] Require manual review when fields conflict, the name is unfamiliar or non-Russian, only a surname is present, or evidence is insufficient.
- [x] Never infer `sex` from occupation, religion, origin, household position, or indirect demographic assumptions.
- [x] Record provenance in the companion field `sex_evidence`.
- [x] Keep blank when the available evidence does not support a defensible value.
- [x] Review and approve the 12 unresolved records before final staging approval.

Deliverables: derivation rules, conflict inventory, unresolved inventory, proposed `sex` values, staged result, diff, and QA report.

Completion status: all 7,446 records have an approved value: 4,921 `Мужской` and 2,525 `Женский`. The 12 owner decisions resolve 10 grammatical conflicts and 2 insufficient-evidence cases. In all 10 conflicts, `family_status` agreed with the approved sex; the staged candidate therefore corrects 10 `legal_status` values and changes no `family_status` values or other existing fields. Canonical files remain unchanged.

Canonical-version follow-up:

- [x] Apply the 10 owner-approved Item 3 `legal_status` corrections before deriving or regenerating `legal_status_norm` in the next consolidated canonical candidate.
- [x] Regenerate `legal_status_norm` for those 10 records from the corrected `legal_status`; do not carry forward the earlier Item 17 values based on the superseded status text.
- [x] Confirm that the resulting `sex`, `legal_status`, `legal_status_norm`, and unchanged `family_status` are grammatically consistent for all 10 records.
- [x] Include these synchronized changes in the canonical-candidate diff and QA report.

Canonical follow-up completion (2026-07-17): v4 QA confirms all 10 corrected `legal_status` values and their approved `legal_status_norm` dependencies are synchronized, with zero cross-field gender conflicts.

### 4. Verify archival codes in `notes_raw` — `[x]` Approved and completed

- [x] Validate the expected `РГБ № NNNN` structure and indexed variants.
- [x] Inventory all duplicate `notes_raw` values and identify affected records by `person_id`, `source_position_id`, and `page_number`.
- [x] Match suspected missing suffixes against owner-reviewed raw PDF page extracts.
- [x] Preserve confirmed true duplicates from the original source.
- [x] Recover confirmed suffixes and use the approved indexed format without a space or hyphen, for example `РГБ № 6152a`.
- [x] Keep archival identifiers as text and preserve all non-`notes_raw` fields unchanged.

Completion status: the owner reviewed the duplicate archive references against the original PDF and supplied raw page extracts for records with missing suffixes. The approved staged candidate contains 41 `notes_raw` changes: 37 suffix recoveries from page evidence, two owner-specified manual corrections, and two existing indexed values reformatted without hyphens. There are no unmatched or low-confidence cases and no unexpected duplicate values. Canonical data remains unchanged.

Deliverables: invalid-format inventory, source-verification decisions, staged result, diff, and QA report.

### 5. Revisit household and source-position identifier rules — `[x]` Approved and completed

- [x] Preserve `person_id` and row order.
- [x] Inventory numeric and textual `household_number` values.
- [x] Replace `household_number` in the staged candidate with `household_id`, `household_type`, and `household_details`.
- [x] Apply the owner-reviewed workbook mapping by exact source-value match.
- [x] Treat `household_id` as a text identifier, not an integer-only field, because approved ranges such as `80-81` and `292-293` must be preserved.
- [x] Use `Частное` for numeric and corrected numeric household identifiers.
- [x] Use `000` in `source_position_id` when no numeric household identifier is available.
- [x] For approved hyphenated identifiers, use the first zero-padded number in the third `source_position_id` segment.
- [x] Preserve genuinely blank source household values as blank across all three household fields.

Completion status: the owner workbook supplied 106 mapping decisions covering 269 records. The staged v2 candidate contains 7,446 records, 39 corrected `household_id` values, and 9 hyphenated household IDs, with no blank or duplicate `source_position_id` values. On 2026-07-11, the project owner verified that the 24 blank `household_type` records correspond to blank source household values and should remain blank. Canonical data remains unchanged.

Deliverables: textual-marker inventory, proposed identifier specification, approved vocabulary, staged result, diff, and QA report.

### 6. Verify field data types and number formats — `[x]` Approved and completed

- [x] Keep identifiers, `district_code`, `settlement_order`, archival codes, and textual household markers as text.
- [x] Verify integer-or-blank storage for `person_order_in_settlement`, `page_number`, `age`, and `arrival_year`.
- [x] Preserve leading zeros in identifier components.
- [x] Define integer-or-blank types for approved `age_months` values.
- [x] Confirm that CSV serialization does not change identifier values or ordering.

Completion status (2026-07-17): canonical v4 QA found zero integer-format or identifier-format exceptions, preserved all identifier order and leading-zero formats, and confirmed the approved 36-column schema and 7,446 records.

Deliverables: type specification, exception inventory, staged result, structural diff, and QA report.

### 7. Verify `age` — `[x]` Approved and staged

- [x] Review all blank, zero, and suspicious age values.
- [x] Cross-check against explicit relationship evidence in `family_status`, including `Дочь`, `Сын`, `Внук`, and `Внучка`.
- [x] Use relationship evidence only to flag records; never infer an age from the relationship.
- [x] Verify that explicit age information has not shifted into another field.

Deliverables: age exception inventory, manual decisions, staged result, diff, and QA report.

Current review status: a read-only Item 7 package was generated from canonical `v3_20260712`. It contains all 1,606 records aged 0–18, a 274-record flagged subset, and all 147 blank-age records. Every review row includes `page_number`, `person_id`, and `source_position_id` for manual verification. Flags identify every zero age, adult or service household roles, blank normalized statuses, and standalone adult legal statuses; they are review prompts only and do not infer or change ages. Canonical data remains unchanged.

Owner review update, 2026-07-13: all 202 age-zero records were reviewed and confirmed without anomalies. Of these, 199 now require no further Item 7 review; three retain a separate blank-`family_status_norm` flag. Together with the 72 nonzero flagged records, 75 records remain under review. The 147 blank-age records also remain under review.

Partial owner-feedback staging update, 2026-07-13: the owner supplied 25 corrected ages in `age_new`. Those values were applied directly to the existing `age` column in a new 31-column staged candidate; no `age_new` column was added. The same staged candidate adds `Владеет участком № 33` to blank `comments` for `P002570`. QA confirms 7,446 records, unchanged schema and identifier order, 25 age changes, one comment change, and zero non-target changes. Fifty age/status records and all 147 blank-age records remain under review; canonical data remains unchanged.

Owner review update, 2026-07-13: the owner confirmed that all remaining 50 age/status screening cases were reviewed and have no issues. No age 0–18 consistency cases remain unresolved. Item 7 remains in progress only for the 147 blank-age records. The staged 25 age corrections and one comment addition remain unchanged; canonical data remains unchanged.

Completion status: the owner manually verified all 147 blank-age records against the source and raw CSV files for all three districts and identified no discrepancies. Together with the completed age-zero and age/status reviews, no Item 7 cases remain unresolved. The approved staged candidate applies 25 age corrections directly to `age`, adds the approved comment for `P002570`, retains all 7,446 records and the unchanged 31-column schema, and has zero non-target changes. Canonical data remains unchanged.

Additional verification, 2026-07-15: a read-only screen of the latest approved staged sequence identified 49 records with `age` greater than 18 and either an explicit child relationship in `family_status_norm` or `legal_status_norm`, or the owner-requested origin flag `origin_place = На Сахалине`. Forty-seven are flagged through `family_status_norm`, seven through `legal_status_norm`, and four through `На Сахалине`, with overlap; the origin rule adds one record not already present in the child-status set. Five records are age 35 or older. Every review row includes `page_number`, `person_id`, `source_position_id`, the raw and normalized status fields, and `origin_place`. These are review prompts rather than confirmed discrepancies; no dataset changes were made.

Additional owner-review completion, 2026-07-15: the owner reviewed all 49 records and confirmed one age error. `P003286` was corrected from age 54 to age 5 based on the source footnote; the other 48 records were confirmed with no issue. A new versioned staged candidate carries forward the approved Item 8 result and changes only `P003286.age`. At that stage its `age_months` remained blank because no explicit precise infant-age phrase was recorded; Item 23 later revised the whole-year rule only for ages 1 and 2, so this age-5 record remains outside the month-completion rule. `legal_status_norm = Дочь поселенца`, `family_status_norm = Дочь`, and `origin_place = На Сахалине` agree with the corrected age. Canonical data remains unchanged.

### 8. Structure infant ages — `[x]` Approved and staged

- [x] Identify explicit infant-age phrases in `comments`.
- [x] Add only one new derived field, `age_months`, immediately after `age`.
- [x] Define `age_months` as completed months stored as an integer.
- [x] Record an explicit age below one completed month as `0`; treat an explicit four weeks as one completed month.
- [x] Initially leave `age_months` blank when no explicit infant-age information is recorded; superseded for whole-year ages 1 and 2 by Item 23.
- [x] Keep the existing `age` meaning as completed years.
- [x] Extract components only from explicit age phrases.
- [x] Preserve exact week/day wording and all unrelated text in unchanged `comments`.
- [x] Do not create `age_text_raw`, `age_weeks`, `age_days`, or another source-text field.
- [x] Generate and validate a new staged candidate implementing the approved one-column rule.

Deliverables: parsed-age inventory, parsing rules, unresolved cases, staged result, diff, and QA report.

Current assessment, 2026-07-13: a read-only extraction proposal identified 307 explicit precise-age phrases at the start of `comments`: 185 month-only, 103 years-plus-months, 15 weeks, two days, and two years-only. These cover 202 records with `age` 0, 103 with `age` 1, and two with `age` 2. All parsed phrases agree with the existing completed-years value in `age`, and every record has a page locator.

Approved owner decision, 2026-07-13: create only `age_months` immediately after `age`. Store completed months as an integer; use `0` for an explicitly recorded age below one completed month, except that four weeks maps to `1`; initially leave blank when no explicit infant-age information exists. Preserve exact week/day wording in unchanged `comments`. Do not create `age_text_raw` or separate week/day fields. The blank-month rule for exact whole-year ages 1 and 2 was revised by Item 23 on 2026-07-17.

Superseded staging note: the earlier 33-column candidate containing both `age_months` and `age_text_raw` does not implement the approved schema and must not be approved or promoted. It remains only as historical review evidence pending a replacement staged candidate. Canonical files remain unchanged.

Completion status: the approved replacement candidate is staged separately as v2 with 7,446 records and 32 columns. It adds only `age_months` immediately after unchanged `age` and populates it for all 307 explicit precise-age records. For 290 month or year/month expressions, the leading age phrase was removed from `comments` while all residual comment content was preserved. For all 15 week and two day expressions, exact `comments` text was preserved; ages below four weeks or expressed in days map to `0`, and four weeks maps to `1`. QA confirms unchanged identifiers and row order, zero remaining month/year age phrases in affected comments, zero non-target changes, and no `age_text_raw`, week, or day columns. Canonical files remain unchanged.

### 9. Normalize capitalization — `[x]` Approved and staged

- [x] Define Sentence case for normalized categorical fields separately from proper names and free text.
- [x] Preserve proper-name capitalization in `name_raw` after verification.
- [x] Confirm initial-uppercase forms for approved `legal_status_norm`, `family_status_norm`, and `religion` values.
- [x] Normalize `literacy` to `Грамотен`, `Неграмотен`, `Образован`, or blank.
- [x] Preserve `comments` and all other source-preserving or free-text fields without blanket capitalization.
- [x] Do not apply blanket title-casing.

Deliverables: capitalization specification, affected-value inventory, approved mappings, staged result, diff, and QA report.

Completion status: the Sentence case specification is documented in `docs/capitalization_specification.md`. A 7,446-record candidate stages the approved literacy capitalization and the previously approved contradictory-value resolution. It changes 5,419 `literacy` records, changes no other field, and leaves canonical files unchanged.

#### Required capitalization step for subsequent normalization items

- [x] For every new or revised normalized categorical field, verify that each nonblank Russian category uses Sentence case before owner approval and staging.
- [x] Include capitalization exceptions in the affected-value inventory and mapping table.
- [x] Preserve proper nouns, abbreviations, identifiers, free text, and source-preserving fields without blanket capitalization.
- [x] Add a QA check confirming that no approved normalized category begins with an unintended lowercase letter.

Final completion (2026-07-17): canonical v4 QA checked all approved normalized categorical fields and found zero unintended lowercase initial categories; source-preserving and free-text fields were excluded from blanket capitalization.

This checkpoint applies to pending normalized fields such as `sex`, `origin_place` or `origin_place_norm`, `illness_norm`, `marriage_status_norm`, and `spouse_location_norm`, as well as any later categorical fields.

### 10. Correct military reserve-status grammar — `[x]` Approved and completed

- [x] Review `legal_status` values containing `рядовой`, `унтер-офицер`, and reserve-status wording.
- [x] Normalize `Запасный рядовой` to `Запасной рядовой` in the staged candidate.
- [x] Normalize `Запасный унтер-офицер` to `Запасной унтер-офицер` in the staged candidate.
- [x] Preserve the source-faithful canonical value pending final integrated approval.

Deliverables: affected-record inventory, approved mappings, staged result, diff, and QA report.

Completion status: six `legal_status` records were corrected from `запасный` to `запасной`; no matching values were present in `comments`. Canonical data remains unchanged.

### 11. Create `family_status_norm` — `[x]` Approved and staged

- [x] Preliminary decision: keep the existing detailed `family_status` unchanged as the source-preserving field.
- [x] Preliminary decision: add a compact Russian analytical field named `family_status_norm`, normally containing one or two words.
- [x] Preliminary decision: prefer full historical terminology over abbreviations; retain forms such as `Незаконнорожденный сын` and `Незаконнорожденная дочь` in full.
- [x] Profile and review every distinct `family_status` value before approving the controlled vocabulary or mapping rules.
- [x] Approve the complete source-to-normalized mapping table after owner review.
- [x] Preserve source details that are not selected for `family_status_norm` only in the unchanged `family_status`; do not reconstruct relationships between household members.
- [x] Stage the approved field addition separately with diff and QA evidence; keep canonical files unchanged.

Deliverables: distinct-value inventory, proposed controlled vocabulary, mapping table, staged result, diff, and QA report.

Completion status: all 190 distinct values including blank were reviewed and approved. A 25-column candidate was staged with `family_status_norm` immediately after the unchanged `family_status`. The staged result contains all 7,446 records, has no unmapped nonblank values or non-target changes, and does not modify canonical files.

### 12. Normalize `origin_place` — `[x]` Approved and staged

Approved result (2026-07-15): retained `origin_place` unchanged and added `origin_place_norm` immediately after it in the latest 7,446-record staged candidate. Applied all 109 owner-reviewed mappings, including five transit variants (113 records) normalized to `В пути`; zero unmapped records and zero non-target changes. Canonical data remains unchanged.

- [x] Review transit expressions including `По пути`, `В пути следования`, and `На пути`.
- [x] Decide whether they map to a shared analytical category such as `В пути` while preserving the original value.
- [x] Separate foreign-state or subjecthood information from Russian administrative origin where the source explicitly supports it.
- [x] Review foreign powers and exceptional non-administrative values individually.
- [x] Do not infer a country from ethnicity, religion, or personal name.

Deliverables: exceptional-value inventory, approved vocabulary and mappings, staged result, diff, and QA report.

### 13. Normalize `religion` — `[x]` Approved and completed

- [x] Review the proposed analytical mapping `Римско-католическое` to `Католическое`.
- [x] Review the proposed consolidation of `Магометанское` and `Мусульманское`; the owner selected `Магометанское` rather than the initial proposal.
- [x] Apply the owner-approved direct source-field corrections while retaining the review mapping and diff as provenance.
- [x] Document the approved controlled values after owner approval.

Deliverables: affected-record inventory, approved controlled vocabulary, mapping table, staged result, diff, and QA report.

Completion status: the owner approved replacing 6 `Римско-католическое` values with `Католическое`, 2 `Мусульманское` values with `Магометанское`, and 1 `Православное (выкрест)` value with `Православное`, moving `выкрест` to `comments`. The staged v2 candidate changes only `religion` and `comments`; canonical data remains unchanged.

### 14. Resolve contradictory `literacy` — `[x]` Approved and completed

- [x] Review the record containing `грамотен неграмотен` against the source evidence.
- [x] Apply the owner decision to use blank when several categories are selected.
- [x] Confirm all other `literacy` values against the approved vocabulary.

Deliverables: record-level decision, staged result, diff, and QA report.

Completion status: the one contradictory `literacy` value `грамотен неграмотен` was changed to blank per owner decision. No contradictory literacy values remain. Canonical data remains unchanged.

### 15. Normalize `illness` — `[x]` Approved and staged

- [x] Profile every nonblank `illness` value, incorporating the five approved Item 17 `Богадельщик` transfers.
- [x] Review and approve every proposed source-to-normalized mapping.
- [x] Preserve `illness` and add the approved analytical field `illness_norm` in a separate staged candidate.
- [x] Prefer concise, gender-neutral Russian condition nouns, for example `Слепой` / `Слепая` to `Слепота`.
- [x] Use semicolon-separated categories for explicitly compound conditions while preserving the complete original `illness`.
- [x] Apply Sentence case to every proposed normalized category.
- [x] Do not infer a diagnosis beyond the explicit historical wording.

Deliverables: complete illness inventory, proposed controlled vocabulary, mapping table, staged result, diff, and QA report.

Completion status: all 30 distinct nonblank values plus blank are approved. The owner preserved six historical expressions unchanged in `illness_norm` and normalized `Слаб` to `Слабосилен`; all other proposals were confirmed. The staged candidate contains 53 nonblank `illness_norm` values, preserves every original `illness`, uses Sentence case, and has zero non-target changes. Canonical files remain unchanged.

### 16. Normalize `marriage_status` and spouse location — `[x]` Approved and staged

Approved result (2026-07-16): preserved `marriage_status` and staged only `marriage_status_norm` and `living_alone_status`. The owner decided not to create `spouse_location_norm`; exact other-region locations remain in `comments`. All 23 source values are mapped, `living_alone_status = Одинок` is populated for 442 records, and no cases remain unresolved. Canonical data remains unchanged.

- [x] Preserve the complete current `marriage_status` value.
- [x] Define a broader `marriage_status_norm` field with an approved Russian vocabulary.
- [x] Add the approved derived field `living_alone_status` using `Одинок` when `marriage_status` explicitly contains `одинок`, `одинока`, or `одинокий`; otherwise leave it blank.
- [x] Treat blank `living_alone_status` as "not explicitly recorded," not as false; do not create a `FALSE` value from absence of evidence.
- [x] Preserve the source wording and gendered variants in the unchanged `marriage_status`; use the Sentence case analytical value `Одинок` in the derived field.
- [x] Do not create `spouse_location_norm`; preserve explicit other-region locations in `comments`.
- [x] Review `женат в другом месте` and named-location variants individually.
- [x] Resolve contradictory or compound statements using owner-approved mappings.

Current approved decision: `living_alone_status` contains `Одинок` for the 442 records with an explicit `одинок-` form and blank for the remaining records. No spouse-location field is created.

Deliverables: distinct-value inventory, approved category, living-alone, and location vocabularies, mapping table, staged result, diff, and QA report.

### 17. Normalize `legal_status` — `[x]` Approved and staged

- [x] Profile every distinct `legal_status` value and its record count from the current canonical dataset.
- [x] Separate the respondent's own legal or social status from occupation, military rank, geographic, and other removable details while retaining approved gendered and child/parent forms.
- [x] Preserve the existing detailed `legal_status` unchanged.
- [x] Add the approved Russian analytical vocabulary in a derived `legal_status_norm` field.
- [x] Review compound, gendered, dependent-child, free-status, exile, penal, military, and exceptional forms individually or in transparent groups.
- [x] Approve every distinct source-to-normalized mapping before staging the new field.
- [x] Create a separate versioned staged candidate with a complete mapping table, record-level diff, and QA report; keep canonical files unchanged pending explicit release approval.

Deliverables: distinct-value inventory, proposed controlled vocabulary, complete approved mapping table, staged result, diff, and QA report.

Completion status: the owner approved all 100 distinct mappings including blank and supplied 12 corrections in `legal_status_review_owner.xlsx`. The staged 25-column candidate retains all 7,446 records, preserves detailed `legal_status`, adds `legal_status_norm` immediately after it, moves `Богадельщик` to blank `illness` fields in 5 records, and has zero non-target changes. Canonical files remain unchanged.

### 18. Normalize `occupation` — `[x]` Approved and staged

- [x] Profile all exact `occupation` values and record counts from the latest staged candidate.
- [x] Separate blank, explicit no-occupation, and family-dependency statements.
- [x] Group related trades and identify capitalization, spelling, and close-synonym variants.
- [x] Identify double occupations and propose semicolon-delimited analytical values.
- [x] Approve the controlled vocabulary and every source-to-normalized mapping.
- [x] Stage an `occupation_norm` field only after owner approval.

Approved result (2026-07-17): all 171 exact values are approved, comprising 21 explicit owner decisions and 150 confirmed proposals. The staged candidate preserves `occupation`, adds `occupation_norm` immediately after it, and transfers descriptive residue to `comments` for 12 records without overwriting existing text. All 7,446 records are mapped with zero non-target changes; canonical data remains unchanged.

Deliverables: grouped inventory, no-occupation inventory, double-occupation review, approved mapping, staged result, diff, and QA report.

### 19. Review `allowance_status` consistency — `[x]` Approved and completed

- [x] Profile all exact `allowance_status` values and counts from the latest staged candidate.
- [x] Confirm that the field contains only `TRUE`, `FALSE`, or blank.
- [x] Flag `allowance_status = TRUE` when `arrival_year < 1880`.
- [x] Keep `TRUE` records with blank `arrival_year` separate because the date rule cannot be evaluated.
- [x] Review the 96 flagged records against the source using person IDs and page locators.
- [x] Apply owner-confirmed corrections, if any, in a new staged candidate; no corrections were required.

Completion status (2026-07-17): the owner reviewed the allowance-status consistency package and found no issues. All 96 `TRUE` records with arrival years before 1880 were accepted as recorded, and the 760 `TRUE` records with blank arrival years produced no identified discrepancy. No corrections or new staged candidate were required; canonical data remains unchanged.

Deliverables: value summary, flagged record inventory with page numbers, blank-arrival context inventory, owner decisions, staged result if required, diff, and QA report.

### 20. Clean number-only values from `comments` — `[x]` Approved and staged

- [x] Use the latest staged candidate as the input.
- [x] Inventory every nonblank `comments` value whose trimmed content consists only of digits.
- [x] Blank only those pure numeric values, which are recorder numbers from the census cards.
- [x] Preserve every mixed text-and-number string exactly.
- [x] Preserve row count, schema, identifier order, and all non-`comments` fields.

Approved result (2026-07-17): the owner approved removal of pure recorder numbers while requiring preservation of strings that contain both text and numbers. The staged candidate blanks 1,865 digit-only `comments` values and preserves all 389 mixed text-and-number comments exactly. QA confirms 7,446 records, 36 columns, unchanged identifier order, zero remaining pure numeric comments, and no changes outside `comments`. Canonical data remains unchanged.

Owner-feedback update (2026-07-17): the owner reviewed all 389 mixed text-and-number records in `owner_review_comments.xlsx`, supplying 225 retained or cleaned `comments_norm` values, 164 blank decisions, and five `name_alias` values. The feedback was applied to the existing `comments` and `name_alias` fields without adding a `comments_norm` column. Nineteen address strings were standardized to ordinal forms such as `1-я Кирпичная` and `3-я Сизовская улица начало`. The resulting candidate changes 274 comments and five aliases; all reviewed source values match, and no fields outside `comments` and `name_alias` change. Canonical data remains unchanged.

Address-feedback refinement (2026-07-17): the owner edited the address-normalization diff and approved grammatical ordinal forms for three genitive address expressions: `2-ой Мало-Российской улицы конец`, `3-ей Сизовской улицы конец`, and `4-ой Набережной улицы конец`. All 19 address mappings were reapplied as explicit approved inputs and the staged candidate and QA hashes were regenerated. Canonical data remains unchanged.

Deliverables: affected-record inventory, preserved mixed-string inventory, reproducible staging script, staged result, diff, and QA report.

### 21. Review `arrival_year` substantive consistency — `[x]` Approved and staged

- [x] Profile range, format, post-census values, and implied arrival age from the latest staged candidate.
- [x] Review the four records with negative implied arrival ages.
- [x] Apply the owner-confirmed `P005199` age correction from `2` to `25`.
- [x] Retain `P003355`, `P004849`, and `P005024` unchanged per owner review.
- [x] Check all populated `arrival_year` values against exact and case-insensitive `origin_place = На Сахалине`.
- [x] Document `P003355` as the sole reviewed exception to the usual non-co-presence rule.
- [x] Preserve row count, schema, identifier order, and all fields other than the approved `age` cell.

Approved result (2026-07-17): all 4,826 populated arrival years are four-digit values from 1865 through 1890, with no post-census values. The owner confirmed no issue for three initially flagged records. `P005199` was a recognition and cleanup error, so `age` was corrected from `2` to `25`; its `arrival_year` and `origin_place` remain unchanged. The cross-field check found only `P003355` with both `origin_place = На Сахалине` and a populated arrival year; the owner accepted that record as recorded. QA confirms 7,446 records, 36 columns, one changed cell, unchanged identifier order, and no non-target changes. Canonical data remains unchanged.

Deliverables: anomaly inventory, owner decisions, reproducible staging script, staged result, applied diff, and QA report.

### 22. Audit raw age recognition after symbol cleanup — `[x]` Approved and staged with three linkage exclusions

- [x] Link the supplied raw district files to the latest staged candidate.
- [x] Inventory non-plain raw age expressions, including angle-bracket deletions, uncertainty marks, fractions, and unit wording.
- [x] Verify all embedded struck-content patterns such as `2<0>5` against staged `age`.
- [x] Compare clear fractional-year and year/month expressions against `age` and `age_months`.
- [x] Review the 18 proposed precise-age corrections or completions.
- [x] Apply the 15 owner-approved changes in a new staged candidate.
- [x] Exclude `P004306`, `P005959`, and `P006718` because their structured names conflict with `source_block_raw` names.

Review result (2026-07-17): linked 7,446 staged people to the supplied raw district files and excluded one blank raw extraction row. All 19 embedded struck-content age patterns now resolve correctly, including corrected `P005199 = 25`; no clear-integer mismatch remains. Eighteen precise-age records require owner review: two likely `age` errors, two existing `age_months` discrepancies, and fourteen blank `age_months` values with explicit raw evidence. Canonical and staged data remain unchanged by this audit.

Approved result (2026-07-17): the owner validated semantic age values for 15 records and excluded three records with mismatched structured and source-block names. The new staged candidate applies 17 cell changes across 15 people: two `age` corrections and 15 `age_months` updates. `P004306`, `P005959`, and `P006718` remain exactly unchanged and are isolated for raw-extraction linkage review. QA confirms 7,446 records, 36 columns, unchanged identifier order, and no non-target changes. Canonical data remains unchanged.

Linkage resolution (2026-07-17): the owner confirmed the six-person comparison. The three apparent mismatches pair distinct people whose archival references differ by the `а` suffix: `РГБ № 5594/5594а`, `5528/5528а`, and `5549/5549а`. The latest staged ages and month values for all six people are correct. No further correction is required for these cases.

Deliverables: complete non-plain-age inventory, focused 18-row review file, unmatched-raw inventory, reproducible audit script, and QA summary.

### 23. Populate `age_months` for whole-year ages 1 and 2 — `[x]` Approved and staged

- [x] Fill blank `age_months` with `12` where `age = 1`.
- [x] Fill blank `age_months` with `24` where `age = 2`.
- [x] Preserve all existing precise `age_months` values derived from explicit source wording.
- [x] Do not change `age`, another age group, or any unrelated field.
- [x] Mark newly populated values as derived from completed whole-year age in the review inventory.

Approved result (2026-07-17): the owner revised the earlier explicit-evidence-only convention to improve statistical coverage. The new staged candidate derives 105 values of `12` for records aged 1 and 211 values of `24` for records aged 2, filling 316 previously blank `age_months` cells. All 118 pre-existing precise values for these age groups remain unchanged. QA confirms 7,446 records, 36 columns, unchanged identifier order, no remaining blank `age_months` among ages 1 and 2, and no changes outside `age_months`. Canonical data remains unchanged.

Interpretation rule: `age_months` may now contain either an exact value supported by precise source wording or a whole-year conversion derived from `age`. When `age = 1` or `2` and a more precise source-based value already exists, the precise value takes precedence over 12 or 24.

Deliverables: affected-record inventory, reproducible staging script, staged candidate, diff, and QA report.

## Final Integrated Validation

This section begins only after Items 1-23 have been approved individually.

The `v4_20260717` canonical release completes the integrated validation and consolidation of approved Items 1–23. Earlier v3, v2, and unversioned canonical releases remain unchanged as historical artifacts.

- [x] Generate one versioned consolidated candidate from the approved scripts and mappings.
- [x] Confirm 7,446 records and the approved schema: the 31-column canonical v3 base plus only the approved staged fields, yielding the 36-column v4 release.
- [x] Confirm district order, row order, `person_id`, and `source_position_id` are unchanged.
- [x] Run all hard QA checks and produce all soft-review inventories.
- [x] Confirm every approved nonblank normalized Russian categorical value uses Sentence case, except documented proper-name, abbreviation, identifier, or source-preservation exceptions.
- [x] Apply the 10 approved Item 3 `legal_status` corrections before regenerating `legal_status_norm`; verify all 10 corresponding normalized values change consistently.
- [x] Run a cross-field QA check for gender consistency among `sex`, `legal_status`, `legal_status_norm`, and `family_status`, with every exception explicitly reviewed.
- [x] Produce a complete record-level and schema-level diff against canonical v3.
- [x] Calculate SHA-256 hashes for all four v4 datasets.
- [x] Submit the candidate package for project-owner review; the owner authorized the new canonical version on 2026-07-17.
- [x] Update `docs/canonical_manifest.csv` only after explicit approval.

## Progress Log

| Date | Item | Status | Summary | Evidence / Output |
|:--|:--|:--|:--|:--|
| 2026-07-10 | Tracker creation | Completed | Created the ordered one-item normalization review tracker; no dataset changes. | `docs/normalization_review_tracker.md` |
| 2026-07-10 | Item 1: `name_raw` verification | Ready for owner review | Reviewed all 7,446 records; identified 43 exception records and prepared 43 decision rows. Canonical data unchanged. | `data/review/name_raw_item1_20260710/`; `outputs/qa/name_raw_item1_20260710/` |
| 2026-07-11 | Item 1: owner decisions applied | Approved and completed | Validated 28 approvals and 15 modifications; generated a 7,446-record staged candidate with 37 changed records and 14 populated `name_alias` values. Canonical data unchanged. | `data/staging/name_raw_item1_20260711/`; `outputs/qa/name_raw_item1_20260711_approved/` |
| 2026-07-11 | Item 2: parenthetical and double surname review | Ready for owner review | No parenthetical `name_raw` values; inventoried all 75 hyphenated names. Proposed derived fields and conservative classifications are staged; 39 records require owner review. Canonical data unchanged. | `data/review/name_double_surnames_item2_20260711/`; `data/staging/name_double_surnames_item2_20260711/`; `outputs/qa/name_double_surnames_item2_20260711/` |
| 2026-07-11 | Item 2: owner decisions applied | Approved and completed | Applied 29 owner-approved corrections: 29 `name_norm` changes and 26 `name_alias` values. The women’s maiden-surname–husband-surname split rationale is documented; no surname-alternative column was created. Canonical data unchanged. | `data/review/name_double_surnames_item2_20260711/owner_response/`; `data/staging/name_double_surnames_item2_20260711_approved/`; `outputs/qa/name_double_surnames_item2_20260711_approved/` |
| 2026-07-11 | Item 5: household structure | Approved and completed | Applied 106 owner mapping decisions to 269 records. The owner verified that all 24 blank `household_type` values are intentional source blanks, not classification errors. Canonical data unchanged. | `data/review/household_structure_owner_mapping_20260711.csv`; `data/staging/household_structure_20260711_v2/` |
| 2026-07-11 | Item 4: archival codes in `notes_raw` | Approved and completed | Recovered 37 missing suffixes from owner-reviewed raw pages, applied two manual corrections, and normalized two existing indexed values to the approved no-hyphen format. The 7,446-record staged candidate has no unresolved matches or unexpected duplicate values. Canonical data unchanged. | `data/review/notes_raw_duplicates_item4_20260711/`; `data/staging/notes_raw_suffix_recovery_20260711/`; `outputs/qa/notes_raw_suffix_recovery_20260711/` |
| 2026-07-11 | Item 10: military reserve-status grammar | Approved and completed | Corrected six `legal_status` values from `запасный` to `запасной`; no matching `comments` values were present. Canonical data unchanged. | `data/staging/items_10_14_20260711/`; `outputs/qa/items_10_14_20260711/` |
| 2026-07-11 | Item 14: contradictory `literacy` | Approved and completed | Changed the one value `грамотен неграмотен` to blank per owner decision. Canonical data unchanged. | `data/staging/items_10_14_20260711/`; `outputs/qa/items_10_14_20260711/` |
| 2026-07-11 | Item 13: religion | Approved and completed | Replaced 6 `Римско-католическое` values with `Католическое`, 2 `Мусульманское` values with `Магометанское`, and 1 `Православное (выкрест)` value with `Православное`, moving `выкрест` to `comments`. Canonical data unchanged. | `data/staging/item13_religion_20260711/`; `outputs/qa/item13_religion_20260711/` |
| 2026-07-12 | Item 17: `legal_status` current-value profile | Ready for owner review | Profiled all 7,446 canonical v2 records: 99 distinct nonblank values, 24 blank records, and 195 representative records. No normalization mappings proposed and no dataset changes made. | `data/review/legal_status_item17_20260712/` |
| 2026-07-12 | Item 17: `legal_status_norm` mapping proposal | Ready for owner review | Proposed mappings for all 100 distinct values including blank. Applied the requested `Свободного состояния` category, proposed moving the subsequently corrected category `Богадельщик` to `illness` for 5 records, and removed district or settlement qualifiers from normalized values. Eleven distinct values covering 12 records are flagged for focused review. No dataset changes made. | `data/review/legal_status_item17_20260712/legal_status_norm_mapping_proposal.csv` |
| 2026-07-12 | Item 17: gender-preserving mapping revision | Ready for owner review | Revised the complete proposal to retain Russian gender distinctions for penal, peasant, settler, and child/parent forms. Normalized `Поселенка` to `Поселка`, including the inflected `Сын поселенки` to `Сын поселки`. Six distinct values covering 6 records remain flagged for focused review. No dataset changes made. | `data/review/legal_status_item17_20260712/legal_status_norm_mapping_proposal.csv` |
| 2026-07-12 | Item 17: owner decisions applied | Approved and staged | Reconciled 12 owner corrections and 88 confirmed mappings. Staged all 7,446 records with `legal_status_norm`; preserved `legal_status`; added the corrected category `Богадельщик` to 5 previously blank `illness` values; zero unmapped values or non-target changes. Canonical data unchanged. | `data/review/legal_status_item17_20260712/owner_response/`; `data/staging/legal_status_norm_item17_20260712/`; `outputs/qa/legal_status_norm_item17_20260712/` |
| 2026-07-12 | Item 9: Sentence case | Approved and staged | Approved Sentence case for normalized categorical fields, including `literacy`. Staged `Грамотен`, `Неграмотен`, `Образован`, or blank for all 7,446 records; 5,419 literacy values changed and no other fields changed. Canonical data unchanged. | `docs/capitalization_specification.md`; `data/review/capitalization_item9_20260712/`; `data/staging/capitalization_item9_20260712/`; `outputs/qa/capitalization_item9_20260712/` |
| 2026-07-12 | Item 3: derived `sex` proposal | Ready for owner review | Proposed `Мужской` for 4,919 records and `Женский` for 2,515 records using explicit grammatical evidence and reviewed patronymic morphology. Twelve records remain blank: 10 status conflicts and 2 with insufficient explicit evidence. Canonical data unchanged. | `data/review/sex_item3_20260712/`; `data/staging/sex_item3_20260712/`; `outputs/qa/sex_item3_20260712/` |
| 2026-07-12 | Item 3: owner decisions applied | Approved and staged | Applied all 12 owner-approved sex decisions. Final counts are 4,921 `Мужской` and 2,525 `Женский`, with no blanks. Corrected 10 conflicting `legal_status` values; all corresponding `family_status` values already agreed and remain unchanged. Canonical data unchanged. | `data/review/sex_item3_20260712/sex_owner_review_cases.csv`; `data/staging/sex_item3_20260712/`; `outputs/qa/sex_item3_20260712/` |
| 2026-07-12 | Item 15: `illness_norm` proposal | Ready for owner review | Profiled 53 nonblank records and 30 distinct nonblank values after incorporating five approved `Богадельщик` transfers. Proposed Sentence case, gender-neutral, and compound mappings; 10 values covering 12 records require focused review. No normalized field staged and canonical data unchanged. | `data/review/illness_item15_20260712/` |
| 2026-07-12 | Item 15: owner decisions applied | Approved and staged | Approved all 31 mappings including blank. Preserved six owner-selected historical expressions in `illness_norm`, normalized `Слаб` to `Слабосилен`, and confirmed all other proposals. Staged 53 nonblank normalized values with original `illness` unchanged and zero non-target changes. Canonical data unchanged. | `data/review/illness_item15_20260712/illness_norm_approved_mapping.csv`; `data/staging/illness_item15_20260712/`; `outputs/qa/illness_item15_20260712/` |
| 2026-07-12 | Canonical normalization release v3 | Approved and completed | Created and designated the 31-column `v3_20260712` combined and district datasets as current canonical files. Integrated all approved items in dependency order; retained 7,446 records, exact district concatenation, unique identifiers, Sentence case categories, and zero gender conflicts. Prior canonical releases remain unchanged. | `data/processed/*_v3_20260712.csv`; `scripts/build_canonical_v3_20260712.py`; `outputs/qa/canonical_v3_20260712/` |
| 2026-07-13 | Item 7: `age` child-consistency screening | In progress | Extracted all 1,606 records aged 0–18 and all 147 blank-age records from canonical v3. Flagged 274 child records for manual review using zero-age, normalized family-status, and normalized legal-status screening rules. Every review record includes its source-book page locator; no dataset changes made. | `data/review/age_item7_20260713/`; `outputs/qa/age_item7_20260713/`; `scripts/review_age_item7.py` |
| 2026-07-13 | Item 7: age-zero owner review | Confirmed; other cases under review | The owner reviewed all 202 age-zero records and found no anomalies. Three of those records retain a separate blank-family-status flag; 75 age 0–18 records and all 147 blank-age records remain under review. No dataset changes made. | `data/review/age_item7_20260713/owner_response/age_zero_review_decisions.csv`; `data/review/age_item7_20260713/age_0_18_remaining_under_review.csv` |
| 2026-07-13 | Item 7: partial age feedback applied | Approved decisions staged; remaining cases under review | Applied 25 owner-supplied `age_new` decisions directly to `age` without adding a column. Added `Владеет участком № 33` to `comments` for `P002570`. The staged candidate retains 7,446 records and 31 columns with zero non-target changes; 50 age/status records and 147 blank-age records remain under review. Canonical data unchanged. | `data/staging/age_item7_20260713/`; `data/review/age_item7_20260713/owner_response/age_corrections_approved.csv`; `outputs/qa/age_item7_20260713/age_item7_applied_diff.csv`; `outputs/qa/age_item7_20260713/age_item7_staging_qa.json` |
| 2026-07-13 | Item 7: remaining age/status review | Confirmed; no issues | The owner confirmed all remaining 50 age/status screening cases have been reviewed and contain no issues. No age 0–18 consistency cases remain unresolved. Only the 147 blank-age records remain under review; no dataset changes made. | `data/review/age_item7_20260713/owner_response/remaining_50_review_decisions.csv`; `data/review/age_item7_20260713/blank_age_review.csv` |
| 2026-07-13 | Item 7: blank-age owner review | Approved and completed | The owner verified all 147 blank-age records against the source and raw CSV files for all three districts and found no discrepancies. All Item 7 review cases are resolved. The staged candidate retains the 25 approved age corrections and one approved comment addition; canonical data unchanged. | `data/review/age_item7_20260713/owner_response/blank_age_review_decisions.csv`; `data/staging/age_item7_20260713/`; `outputs/qa/age_item7_20260713/age_item7_staging_qa.json` |
| 2026-07-15 | Item 7: age over 18 with child-status evidence | Ready for owner review | Screened the latest staged sequence and identified 48 records over age 18 with explicit child relationships in normalized family or legal status. Included origin as context; no origin value contains an explicit child/dependency marker. All records have page locators. No dataset changes made. | `data/review/age_over18_child_status_item7_20260715/`; `outputs/qa/age_over18_child_status_item7_20260715/`; `scripts/review_age_over18_child_status_item7.py` |
| 2026-07-15 | Item 7: `На Сахалине` origin expansion | Ready for owner review | Expanded the over-18 screen to flag `origin_place = На Сахалине`. Four records meet the origin rule; three overlap the child-status set and one is newly added, producing 49 unique review records. All records retain page locators; no dataset changes made. | `data/review/age_over18_child_status_item7_20260715/age_over18_child_status_review.csv`; `data/review/age_over18_child_status_item7_20260715/age_over18_child_status_review_v2.xlsx`; `outputs/qa/age_over18_child_status_item7_20260715/age_over18_child_status_qa.json` |
| 2026-07-15 | Item 7: over-18 owner decisions applied | Approved and staged | The owner confirmed one age error among 49 reviewed records: corrected `P003286` from 54 to 5 based on a source footnote. The other 48 records were confirmed with no issue. The new 7,446-record, 32-column staged candidate carries forward Item 8 and changes only this age value, with zero non-target changes. Canonical data unchanged. | `data/review/age_over18_child_status_item7_20260715/owner_response/age_over18_owner_decisions.csv`; `data/staging/items7_8_age_followup_20260715/`; `outputs/qa/items7_8_age_followup_20260715/`; `scripts/apply_age_over18_item7_feedback.py` |
| 2026-07-13 | Item 8: precise infant/young-child age assessment | In progress | Identified and parsed 307 leading precise-age phrases from `comments` with zero consistency exceptions. Proposed total completed months as the main numeric measure and exact source text retention; week/day values remain in exact text without unsupported conversion. Comments remain unchanged; no dataset changes made. | `data/review/infant_age_item8_20260713/`; `outputs/qa/infant_age_item8_20260713/`; `scripts/profile_infant_age_item8.py` |
| 2026-07-13 | Item 8: minimal precise-age schema staged | Ready for owner review | Staged `age_months` for 290 records and exact `age_text_raw` for 307 records immediately after unchanged `age`. Week/day expressions remain exact text with blank months; `comments` is unchanged. The candidate retains 7,446 records, adds two columns, and has zero consistency or non-target exceptions. | `data/staging/infant_age_item8_20260713/`; `outputs/qa/infant_age_item8_20260713/infant_age_item8_diff.csv`; `outputs/qa/infant_age_item8_20260713/infant_age_item8_staging_qa.json`; `scripts/stage_infant_age_item8.py` |
| 2026-07-13 | Item 8: owner field and unit decision | Approved rule; restaging pending | Approved one new field only: integer completed-month `age_months` immediately after `age`. Explicit ages below one month map to `0`, four weeks maps to `1`, and absence of explicit infant-age information remains blank. Exact week/day wording stays in `comments`; no source-text or separate week/day fields will be created. The earlier two-field stage is superseded. | `docs/normalization_review_tracker.md` |
| 2026-07-13 | Item 8: approved one-column restage | Approved and staged | Created a new v2 staged candidate with only `age_months` added after unchanged `age`. Populated 307 values; removed 290 leading month/year phrases from `comments` while preserving residual text; preserved all 17 week/day comments exactly, with sub-four-week/day values mapped to `0` and four weeks to `1`. The 7,446-record candidate has 32 columns and zero non-target changes. Canonical data unchanged. | `data/staging/infant_age_item8_20260713_v2/`; `data/review/infant_age_item8_20260713_v2/age_months_approved_mapping.csv`; `outputs/qa/infant_age_item8_20260713_v2/`; `scripts/stage_infant_age_item8_v2.py` |
| 2026-07-15 | Item 12: `origin_place` profile and mapping proposal | Ready for owner review | Profiled all 7,446 records and 109 exact values including blank. Proposed one shared analytical value `В пути` for five transit variants covering 113 records; separated 12 foreign-subjecthood records, 3 foreign-state records, 31 higher-level imperial-territory records, and exceptional non-administrative values. Review files include page locators. No dataset changes made. | `data/review/origin_place_item12_20260715/`; `outputs/qa/origin_place_item12_20260715/`; `scripts/profile_origin_place_item12.py` |
| 2026-07-15 | Item 12: owner mappings applied | Approved and staged | Applied all 109 owner-reviewed mappings in a new `origin_place_norm` column immediately after preserved `origin_place`. Incorporated three owner revisions, normalized 128 records relative to their source spelling/value, retained 838 blanks, and found zero unmapped or non-target changes. Canonical data unchanged. | `data/review/origin_place_item12_20260715/owner_response/`; `data/staging/origin_place_item12_20260715/`; `outputs/qa/origin_place_item12_20260715/`; `scripts/stage_origin_place_item12.py` |
| 2026-07-15 | Item 16: marriage status and spouse-location proposal | Ready for owner review | Profiled 7,446 records and 23 exact values. Proposed `marriage_status_norm`, the approved `living_alone_status = Одинок` for 442 explicit records, and `spouse_location_norm`. Ten distinct values covering 49 records require focused review, including contradictions and named locations. Five `женат в другом месте` records receive record-level proposals from explicit comments: `Сибирь` (2), `Амур` (1), and `Кара` (2). No dataset changes made. | `data/review/marriage_status_item16_20260715/`; `outputs/qa/marriage_status_item16_20260715/`; `scripts/profile_marriage_status_item16.py` |
| 2026-07-16 | Item 16: approved married-category structure staged | Partially approved and staged | Staged `marriage_status_norm`, `living_alone_status`, and `spouse_location_norm` after preserved `marriage_status`. Applied `Женат на родине` (2,679), `Женат на Сахалине` (383), and `Женат в другом регионе` (13). Standardized or appended exact-location wording in `comments` for 12 records while preserving existing content. Ten contradictory records remain unresolved, including two dual-location cases. Canonical data unchanged. | `data/staging/marriage_status_item16_20260716/`; `data/review/marriage_status_item16_20260715/owner_response/`; `outputs/qa/marriage_status_item16_20260716/`; `scripts/stage_marriage_status_item16_partial.py` |
| 2026-07-16 | Item 16: final owner decisions staged | Approved and staged | Superseded the partial stage and created a 35-column candidate containing only `marriage_status_norm` and `living_alone_status`; `spouse_location_norm` was not created. Applied `Девица → Холост`, retained two `Женат на родине и на Сахалине` cases, mapped five cases to `Женат на Сахалине; Вдов`, and resolved the three married/single compounds. All 7,446 records are mapped with zero unresolved or non-target changes. Canonical data unchanged. | `data/staging/marriage_status_item16_20260716_v2/`; `data/review/marriage_status_item16_20260715/owner_response/marriage_status_item16_approved_mapping.csv`; `outputs/qa/marriage_status_item16_20260716_v2/`; `scripts/stage_marriage_status_item16_final.py` |
| 2026-07-16 | Item 18: `occupation` profile and grouped proposal | Ready for owner review | Profiled all 7,446 records and 171 exact values. Separated 5,972 blanks, 31 explicit no-occupation records, 43 family-dependency statements, 11 double occupations, and related trade families. Proposed semicolon-delimited analytical values for double occupations and page-linked review rows. No dataset changes made. | `data/review/occupation_review_20260716/`; `outputs/qa/occupation_review_20260716/`; `scripts/profile_occupation_review.py` |
| 2026-07-17 | Item 18: owner decisions applied | Approved and staged | Applied 21 explicit owner decisions and 150 confirmed proposals across all 171 exact occupation values. Added `occupation_norm` after preserved `occupation`, populated 1,474 normalized values, retained 5,972 blanks, and transferred descriptive occupation text to `comments` for 12 records. QA found 88 source-to-normalized differences, zero unmapped records, and zero non-target changes. Canonical data unchanged. | `data/staging/occupation_item18_20260717/`; `data/review/occupation_review_20260716/owner_response/`; `outputs/qa/occupation_item18_20260717/`; `scripts/stage_occupation_item18.py` |
| 2026-07-17 | Item 19: allowance-status consistency review | Ready for owner review | Profiled all 7,446 records: 2,550 `TRUE`, 4,328 `FALSE`, and 568 blank values. Flagged 96 `TRUE` records with `arrival_year < 1880`, all with person IDs and page locators. Listed 760 additional `TRUE` records with blank arrival years separately because the date rule cannot be evaluated. No dataset changes made. | `data/review/allowance_status_item19_20260717/`; `outputs/qa/allowance_status_item19_20260717/`; `scripts/review_allowance_status_item19.py` |
| 2026-07-17 | Item 19: owner review completed | Approved and completed | The owner reviewed the full allowance-status check and found no issues. All 96 `TRUE` records with arrival years before 1880 were accepted as recorded; no discrepancy was identified among the separately listed 760 `TRUE` records with blank arrival years. No corrections or dataset changes were required. | `data/review/allowance_status_item19_20260717/owner_response/allowance_review_completion.md` |
| 2026-07-17 | Item 1 follow-up: additional `name_alias` values | Approved and staged | Applied 14 owner-supplied alias additions from the 7,446-row workbook to the latest Item 21 staged candidate. All workbook `person_id` and `name_raw` values matched exactly; existing aliases were preserved, populated aliases increased from 40 to 54, and no fields outside `name_alias` changed. Canonical data unchanged. | `data/review/alias_name_add_20260717/owner_response/`; `data/staging/name_alias_add_20260717/`; `outputs/qa/name_alias_add_20260717/`; `scripts/stage_name_alias_additions_20260717.py` |
| 2026-07-17 | Item 20: number-only `comments` cleanup | Approved and staged | Starting from the latest Item 18 staged candidate, blanked 1,865 comments containing digits only and preserved all 389 mixed text-and-number comments exactly. Only `comments` changed; all 7,446 rows, 36 columns, identifiers, and row order are preserved. Canonical data unchanged. | `data/staging/comments_numeric_cleanup_20260717/`; `data/review/comments_numeric_cleanup_20260717/`; `outputs/qa/comments_numeric_cleanup_20260717/`; `scripts/stage_comments_numeric_cleanup.py` |
| 2026-07-17 | Item 20: mixed-comment owner feedback | Approved and staged | Applied all 389 owner-reviewed decisions from `comments_norm` to `comments`, including 164 blank decisions, and updated five `name_alias` values. Standardized 19 address strings to ordinal forms. QA confirms 274 comment changes, five alias changes, exact source matching, and no changes outside the two approved fields. Canonical data unchanged. | `data/review/comments_numeric_cleanup_20260717/owner_review_comments.xlsx`; `data/staging/comments_owner_feedback_20260717/`; `outputs/qa/comments_owner_feedback_20260717/`; `scripts/stage_comments_owner_feedback.py` |
| 2026-07-17 | Item 20: address-mapping refinement | Approved and staged | Applied the owner-edited 19-row address mapping, including the approved genitive forms `2-ой`, `3-ей`, and `4-ой`. Rebuilt the candidate and QA with 274 comment changes, five alias changes, and no changes outside `comments` and `name_alias`. Canonical data unchanged. | `outputs/qa/comments_owner_feedback_20260717/address_normalization_diff.csv`; `data/staging/comments_owner_feedback_20260717/`; `outputs/qa/comments_owner_feedback_20260717/comments_owner_feedback_qa.json` |
| 2026-07-17 | Item 21: `arrival_year` substantive consistency | Approved and staged | Profiled all arrival years, applied the owner-confirmed `P005199` age correction from 2 to 25, retained the other three reviewed records unchanged, and found only one populated `arrival_year` paired with `origin_place = На Сахалине`: owner-accepted `P003355`. The new staged candidate changes one `age` cell only; canonical data unchanged. | `data/review/arrival_year_20260717/`; `data/staging/arrival_year_item21_20260717/`; `outputs/qa/arrival_year_item21_20260717/`; `scripts/stage_arrival_year_item21.py` |
| 2026-07-17 | Item 22: raw age-recognition audit | Approved and staged with three exclusions | Applied owner-validated semantic age values to 15 records: two `age` corrections and 15 `age_months` updates. Excluded `P004306`, `P005959`, and `P006718` because their structured names conflict with their attached source-block names; those records remain unchanged for separate linkage review. Canonical data unchanged. | `data/review/raw_age_recognition_item22_20260717/`; `data/staging/raw_age_recognition_item22_20260717/`; `outputs/qa/raw_age_recognition_item22_20260717/`; `scripts/stage_raw_age_recognition_item22.py` |
| 2026-07-17 | Item 23: whole-year `age_months` completion | Approved and staged | Revised the rule to derive `age_months = 12` for 105 blank records aged 1 and `24` for 211 blank records aged 2. Preserved all 118 explicit precise-month values and changed no other field. Canonical data unchanged. | `data/review/age_months_whole_year_item23_20260717/`; `data/staging/age_months_whole_year_item23_20260717/`; `outputs/qa/age_months_whole_year_item23_20260717/`; `scripts/stage_age_months_whole_year_item23.py` |
