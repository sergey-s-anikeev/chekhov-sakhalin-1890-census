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

### 3. Create and verify derived `sex`

- [ ] Add a proposed derived field named `sex`; it is not present in the historical source dataset.
- [ ] Use controlled values: `male`, `female`, or blank.
- [ ] Derive a candidate value only from explicit grammatical or name evidence in `legal_status`, `family_status`, and `name_raw`.
- [ ] Prefer explicit gendered evidence in `legal_status` or `family_status`; use `name_raw` only through a reviewed name rule or approved name reference.
- [ ] Require manual review when fields conflict, the name is unfamiliar or non-Russian, only a surname is present, or evidence is insufficient.
- [ ] Never infer `sex` from occupation, religion, origin, household position, or indirect demographic assumptions.
- [ ] Record provenance in a companion field such as `sex_evidence` and optionally a confidence/review field.
- [ ] Keep blank when the available evidence does not support a defensible value.

Deliverables: derivation rules, conflict inventory, unresolved inventory, proposed `sex` values, staged result, diff, and QA report.

### 4. Verify archival codes in `notes_raw`

- [ ] Validate the expected `РГБ № NNNN` structure.
- [ ] Investigate archival identifiers containing letters or missing components, including the reported Tymovsky records associated with `РГБ № 4521г`.
- [ ] Determine whether a suffix such as `г` is part of the identifier, a transcription artifact, or displaced text.
- [ ] Preserve the complete source-derived `notes_raw` value.
- [ ] Consider derived fields `archive_repository`, `archive_number`, and `archive_suffix`.
- [ ] Keep archival identifiers as text.

Deliverables: invalid-format inventory, source-verification decisions, staged result, diff, and QA report.

### 5. Revisit household and source-position identifier rules

- [ ] Preserve `person_id` and `source_position_id` unchanged.
- [ ] Inventory numeric and textual `household_number` values.
- [ ] Separate household grouping from institutional or work-location descriptions.
- [ ] Define proposed derived fields such as `household_group_id`, `household_number_norm`, `location_type`, and `location_name_or_number`.
- [ ] Review proposed controlled Russian `location_type` values: `Домохозяйство`, `Штольня`, `Казарма`, `Тюрьма`, `Другое`, or blank.
- [ ] Do not force textual household markers into numeric identifiers.

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

### 9. Normalize capitalization

- [ ] Define capitalization separately for proper names and categorical fields.
- [ ] Preserve proper-name capitalization in `name_raw` after verification.
- [ ] Review initial-uppercase forms for normalized `legal_status`, `family_status`, and `religion` values.
- [ ] Preserve lowercase controlled `literacy` values: `грамотен`, `неграмотен`, and `образован`.
- [ ] Do not apply blanket title-casing.

Deliverables: capitalization specification, affected-value inventory, approved mappings, staged result, diff, and QA report.

### 10. Correct military reserve-status grammar

- [ ] Review `legal_status` values containing `рядовой`, `унтер-офицер`, and reserve-status wording.
- [ ] Normalize `Запасный рядовой` to `Запасной рядовой` in an approved normalized field.
- [ ] Normalize `Запасный унтер-офицер` to `Запасной унтер-офицер` in an approved normalized field.
- [ ] Preserve the source-faithful value where required for auditability.

Deliverables: affected-record inventory, approved mappings, staged result, diff, and QA report.

### 11. Create `family_status_norm`

- [ ] Add a proposed one-word analytical field named `family_status_norm` while preserving detailed `family_status`.
- [ ] Profile all distinct source-derived values before fixing the vocabulary.
- [ ] Review candidate Russian categories: `Хозяин`, `Хозяйка`, `Жена`, `Муж`, `Сын`, `Дочь`, `Внук`, `Внучка`, `Сожитель`, `Сожительница`, `Жилец`, `Жилица`, `Совладелец`, `Работник`, `Прислуга`, `Родственник`, `Другое`, or blank.
- [ ] Preserve qualifiers such as `незаконнорожденная`, `приемная`, and relationship-to-householder details outside the one-word field.

Deliverables: distinct-value inventory, proposed controlled vocabulary, mapping table, staged result, diff, and QA report.

### 12. Normalize `origin_place`

- [ ] Review transit expressions including `По пути`, `В пути следования`, and `На пути`.
- [ ] Decide whether they map to a shared analytical category such as `В пути` while preserving the original value.
- [ ] Separate foreign-state or subjecthood information from Russian administrative origin where the source explicitly supports it.
- [ ] Review foreign powers and exceptional non-administrative values individually.
- [ ] Do not infer a country from ethnicity, religion, or personal name.

Deliverables: exceptional-value inventory, approved vocabulary and mappings, staged result, diff, and QA report.

### 13. Normalize `religion`

- [ ] Review the proposed analytical mapping `Римско-католическое` to `Католическое`.
- [ ] Review the proposed analytical consolidation of `Магометанское` and `Мусульманское`, preferably under `Мусульманское`.
- [ ] Preserve source-faithful values and implement approved changes in a derived normalized field first.
- [ ] Update controlled-vocabulary documentation only after owner approval.

Deliverables: affected-record inventory, approved controlled vocabulary, mapping table, staged result, diff, and QA report.

### 14. Resolve contradictory `literacy`

- [ ] Review the record containing `грамотен неграмотен` against the source evidence.
- [ ] Do not automatically convert the value to blank.
- [ ] Use blank only if the source is genuinely unresolved and the reviewer approves that representation.
- [ ] Confirm all other `literacy` values against the approved vocabulary.

Deliverables: record-level decision, staged result, diff, and QA report.

### 15. Normalize `illness`

- [ ] Review every nonblank `illness` value.
- [ ] Preserve `illness` and create an analytical field such as `illness_norm` only after vocabulary approval.
- [ ] Prefer concise, gender-neutral Russian condition nouns, for example `слеп` / `слепа` to `Слепота`.
- [ ] Do not infer a diagnosis beyond the explicit historical wording.

Deliverables: complete illness inventory, proposed controlled vocabulary, mapping table, staged result, diff, and QA report.

### 16. Normalize `marriage_status` and spouse location

- [ ] Preserve the complete current `marriage_status` value.
- [ ] Define a broader `marriage_status_norm` field with an approved Russian vocabulary.
- [ ] Define `spouse_location_norm` for explicit locations such as `На Сахалине`, `На родине`, `Кара`, `Сибирь`, `Владивосток`, `Николаевск`, `Другое`, or blank.
- [ ] Review `женат в другом месте` and named-location variants individually.
- [ ] Preserve contradictory or compound statements for manual review.

Deliverables: distinct-value inventory, approved category and location vocabularies, mapping table, staged result, diff, and QA report.

## Final Integrated Validation

This section begins only after Items 1-16 have been approved individually.

- [ ] Generate one versioned consolidated candidate from the approved scripts and mappings.
- [ ] Confirm 7,446 records and the approved 23 canonical columns plus only the approved new derived fields.
- [ ] Confirm district order, row order, `person_id`, and `source_position_id` are unchanged.
- [ ] Run all hard QA checks and produce all soft-review inventories.
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
