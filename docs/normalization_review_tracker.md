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

- [ ] Apply the 10 owner-approved Item 3 `legal_status` corrections before deriving or regenerating `legal_status_norm` in the next consolidated canonical candidate.
- [ ] Regenerate `legal_status_norm` for those 10 records from the corrected `legal_status`; do not carry forward the earlier Item 17 values based on the superseded status text.
- [ ] Confirm that the resulting `sex`, `legal_status`, `legal_status_norm`, and unchanged `family_status` are grammatically consistent for all 10 records.
- [ ] Include these synchronized changes in the canonical-candidate diff and QA report.

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

### 6. Verify field data types and number formats

- [ ] Keep identifiers, `district_code`, `settlement_order`, archival codes, and textual household markers as text.
- [ ] Verify integer-or-blank storage for `person_order_in_settlement`, `page_number`, `age`, and `arrival_year`.
- [ ] Preserve leading zeros in identifier components.
- [ ] Define integer-or-blank types for any approved infant-age component fields.
- [ ] Confirm that staged CSV serialization does not change identifier values or ordering.

Deliverables: type specification, exception inventory, staged result, structural diff, and QA report.

### 7. Verify `age`

- [ ] Review all blank, zero, and suspicious age values.
- [ ] Cross-check against explicit relationship evidence in `family_status`, including `Дочь`, `Сын`, `Внук`, and `Внучка`.
- [ ] Use relationship evidence only to flag records; never infer an age from the relationship.
- [ ] Verify that explicit age information has not shifted into another field.

Deliverables: age exception inventory, manual decisions, staged result, diff, and QA report.

### 8. Structure infant ages

- [ ] Identify explicit infant-age phrases in `comments`.
- [ ] Define derived fields `age_years`, `age_months`, `age_weeks`, `age_days`, and `age_text_raw`.
- [ ] Keep the existing `age` meaning as completed years.
- [ ] Extract components only from explicit age phrases.
- [ ] Preserve unrelated comment text and retain the source-derived age phrase.

Deliverables: parsed-age inventory, parsing rules, unresolved cases, staged result, diff, and QA report.

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

- [ ] For every new or revised normalized categorical field, verify that each nonblank Russian category uses Sentence case before owner approval and staging.
- [ ] Include capitalization exceptions in the affected-value inventory and mapping table.
- [ ] Preserve proper nouns, abbreviations, identifiers, free text, and source-preserving fields without blanket capitalization.
- [ ] Add a QA check confirming that no approved normalized category begins with an unintended lowercase letter.

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

### 12. Normalize `origin_place`

- [ ] Review transit expressions including `По пути`, `В пути следования`, and `На пути`.
- [ ] Decide whether they map to a shared analytical category such as `В пути` while preserving the original value.
- [ ] Separate foreign-state or subjecthood information from Russian administrative origin where the source explicitly supports it.
- [ ] Review foreign powers and exceptional non-administrative values individually.
- [ ] Do not infer a country from ethnicity, religion, or personal name.

Deliverables: exceptional-value inventory, approved vocabulary and mappings, staged result, diff, and QA report.

### 13. Normalize `religion` — `[x]` Approved and completed

- [ ] Review the proposed analytical mapping `Римско-католическое` to `Католическое`.
- [ ] Review the proposed analytical consolidation of `Магометанское` and `Мусульманское`, preferably under `Мусульманское`.
- [ ] Preserve source-faithful values and implement approved changes in a derived normalized field first.
- [ ] Update controlled-vocabulary documentation only after owner approval.

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

### 16. Normalize `marriage_status` and spouse location

- [ ] Preserve the complete current `marriage_status` value.
- [ ] Define a broader `marriage_status_norm` field with an approved Russian vocabulary.
- [x] Add the approved derived field `living_alone_status` using `Одинок` when `marriage_status` explicitly contains `одинок`, `одинока`, or `одинокий`; otherwise leave it blank.
- [x] Treat blank `living_alone_status` as "not explicitly recorded," not as false; do not create a `FALSE` value from absence of evidence.
- [x] Preserve the source wording and gendered variants in the unchanged `marriage_status`; use the Sentence case analytical value `Одинок` in the derived field.
- [ ] Define `spouse_location_norm` for explicit locations such as `На Сахалине`, `На родине`, `Кара`, `Сибирь`, `Владивосток`, `Николаевск`, `Другое`, or blank.
- [ ] Review `женат в другом месте` and named-location variants individually.
- [ ] Preserve contradictory or compound statements for manual review.

Current approved decision: `living_alone_status` will contain `Одинок` for the 442 canonical records with an explicit `одинок-` form and blank for the remaining records. This field has been approved conceptually but has not yet been staged.

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

## Final Integrated Validation

This section begins only after Items 1-17 have been approved individually.

The `v3_20260712` canonical release is an approved interim consolidation of all completed items through 2026-07-12. It does not close this final-validation section because Items 6–8, 12, and 16 remain pending.

- [ ] Generate one versioned consolidated candidate from the approved scripts and mappings.
- [ ] Confirm 7,446 records and the approved 23 canonical columns plus only the approved new derived fields.
- [ ] Confirm district order, row order, `person_id`, and `source_position_id` are unchanged.
- [ ] Run all hard QA checks and produce all soft-review inventories.
- [ ] Confirm every approved nonblank normalized Russian categorical value uses Sentence case, except documented proper-name, abbreviation, identifier, or source-preservation exceptions.
- [ ] Apply the 10 approved Item 3 `legal_status` corrections before regenerating `legal_status_norm`; verify all 10 corresponding normalized values change consistently.
- [ ] Run a cross-field QA check for gender consistency among `sex`, `legal_status`, `legal_status_norm`, and `family_status`, with every exception explicitly reviewed.
- [ ] Produce a complete record-level and schema-level diff against the current canonical dataset.
- [ ] Calculate SHA-256 hashes for the candidate and supporting correction inputs.
- [ ] Submit the candidate package for project-owner review.
- [ ] Do not replace a canonical file or update `docs/canonical_manifest.csv` before explicit approval.

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
