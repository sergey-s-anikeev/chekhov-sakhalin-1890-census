# Decision Log

## Decision 1 — Authoritative package sources

- Date: 2026-07-10
- Decision: `final_sakhalin_1890_project_outputs.zip` and `final_scripts_update.zip` are the authoritative sources for the clean working core.
- Rationale: The project owner identified these packages as containing the latest validated datasets, scripts, documentation, and QA outputs.
- Affected files: Every canonical file listed in `canonical_manifest.csv`.
- Approval status: Approved by the project owner.

## Decision 2 — Canonical datasets

- Date: 2026-07-10
- Decision: Four CSV files are approved as canonical: the Alexandrovsky, Tymovsky, and Korsakovsky district datasets and the combined Sakhalin dataset.
- Rationale: Package validation confirmed a common 23-column schema, unique identifiers, expected row counts, and no full-row duplicates.
- Affected files: `data/processed/clean_alexandrovsky_ru.csv`, `data/processed/clean_tymovsky_ru.csv`, `data/processed/clean_korsakovsky_ru.csv`, `data/processed/clean_sakhalin_1890_ru.csv`.
- Approval status: Approved by the project owner.

## Decision 3 — District codes

- Date: 2026-07-10
- Decision: District code `1` identifies `Александровский`, code `2` identifies `Тымовский`, and code `3` identifies `Корсаковский`.
- Rationale: These mappings are present in the validated release and were explicitly approved by the project owner.
- Affected files: All four canonical processed datasets and their QA outputs.
- Approval status: Approved by the project owner.

## Decision 4 — Concatenation order

- Date: 2026-07-10
- Decision: The combined dataset must be the exact concatenation of Alexandrovsky, then Tymovsky, then Korsakovsky district records.
- Rationale: Validation confirmed that this order reproduces all 7,446 combined rows exactly, with no rows exclusive to either side.
- Affected files: The four canonical processed datasets and `scripts/merge_clean_districts.py`.
- Approval status: Approved by the project owner.

## Decision 5 — Canonical helper module

- Date: 2026-07-10
- Decision: `scripts/sakhalin_conversion_helpers_v12.py` is the canonical helper module.
- Rationale: v12 is the version imported by the newer scripts and is the latest named helper in the authoritative package.
- Affected files: `scripts/sakhalin_conversion_helpers_v12.py`, `scripts/create_raw_records_from_pages_v3.py`, and `scripts/finalize_reviewed_clean_csv.py`.
- Approval status: Approved by the project owner.

## Decision 6 — Exclusion of helper v11

- Date: 2026-07-10
- Decision: `scripts/sakhalin_conversion_helpers_v11.py` is not included in the clean working core.
- Rationale: v11 and v12 are byte-for-byte identical, while the newer scripts import v12. Including both would create an unnecessary duplicate and ambiguity.
- Affected files: `scripts/sakhalin_conversion_helpers_v11.py` and `scripts/sakhalin_conversion_helpers_v12.py`.
- Approval status: Approved by the project owner.

## Decision 7 — Historical project directory

- Date: 2026-07-10
- Decision: The old project directory remains unchanged as a historical archive.
- Rationale: It preserves provenance, prior iterations, manual-review packages, and audit evidence while the clean core is established separately.
- Affected files: All files outside `workspace_candidate/`.
- Approval status: Approved by the project owner.

## Decision 8 — Documentation language

- Date: 2026-07-10
- Decision: English is the canonical language for project documentation, reports, logs, comments, headings, descriptions, and status messages.
- Rationale: A single professional documentation language improves maintainability and review consistency.
- Affected files: Markdown, JSON narrative fields, QA narratives, logs, and future code comments.
- Approval status: Approved by the project owner.

## Decision 9 — Preservation of Russian values

- Date: 2026-07-10
- Decision: Russian historical values and normalized dataset values remain unchanged and must not be translated for documentation-language consistency.
- Rationale: These values carry source meaning, approved normalization decisions, and stable analytical categories.
- Affected files: All datasets and any documentation or QA output that quotes dataset values.
- Approval status: Approved by the project owner.

## Decision 10 — Item 1 `name_raw` normalization and `name_alias`

- Date: 2026-07-11
- Decision: Approve 28 proposed `name_raw` review actions and approve 15 owner-modified actions. Add the derived field `name_alias` immediately after `name_raw` in the versioned staged candidate. Move the seven explicitly approved explanatory values to `comments`, and apply the two approved `family_status` corrections.
- Rationale: The project owner reviewed all 43 identified name exceptions in `name_raw_proposed_corrections_owner_response_20260711.xlsx`. The response contains no rejected, deferred, missing, or invalid decisions.
- Affected files: `data/review/name_raw_item1_20260710/owner_response/name_raw_approved_decisions_20260711.csv`, `data/staging/name_raw_item1_20260711/clean_sakhalin_1890_ru_item1_name_v1.csv`, and `outputs/qa/name_raw_item1_20260711_approved/`.
- Safeguard: The four canonical processed datasets and `docs/canonical_manifest.csv` remain unchanged. The new result is a staged candidate, not a canonical replacement.
- Approval status: Approved by the project owner.

## Decision 11 - Item 2 parenthetical and double-surname review

- Date: 2026-07-11
- Decision: Apply the 29 owner-approved Item 2 corrections. Add derived `name_norm` and `name_note` fields. Place 26 approved alternative-surname or name values in the existing `name_alias` field; do not create `surname_alternative` or `surname_alternative_proposed` fields.
- Rationale: No parenthetical expressions occur in `name_raw`. For approved women’s hyphenated surname forms, the left component represents the maiden surname and the right component represents the husband surname. `name_norm` retains the maiden-surname form and `name_alias` stores the husband surname. Fixed complex surnames, compound given names, ordinal markers, and ethnic-name constructions remain source-faithful unless explicitly corrected by the owner.
- Affected files: `data/review/name_double_surnames_item2_20260711/owner_response/`, `data/staging/name_double_surnames_item2_20260711_approved/`, and `outputs/qa/name_double_surnames_item2_20260711_approved/`.
- Safeguard: `name_raw`, identifiers, row order, all canonical processed datasets, and `docs/canonical_manifest.csv` remain unchanged. The new result is a staged candidate, not a canonical replacement.
- Approval status: Approved by the project owner.

## Decision 12 - Canonical name-normalization release v2

- Date: 2026-07-11
- Decision: Designate the versioned Item 1 and Item 2 release as the new canonical clean dataset series. Update `name_raw` with all 29 approved Item 2 `name_norm` values, retain the 37 approved Item 1 `name_raw` changes, and add only `name_alias` to the prior 23-column schema.
- Rationale: The project owner explicitly approved the 24-column release design. `name_norm` is merged into `name_raw`; `name_note` remains review/QA evidence; no surname-alternative field is included.
- Affected files: `data/processed/*_v2_20260711.csv`, `outputs/qa/name_normalization_canonical_v2_20260711/`, `docs/data_dictionary.md`, `docs/release_notes.md`, and `docs/canonical_manifest.csv`.
- Safeguard: The prior canonical datasets remain unchanged as historical release artifacts. The new combined file must equal the ordered concatenation of its three matching district slices.
- Approval status: Approved by the project owner.

## Preliminary Decision 13 - Design of `family_status_norm`

- Date: 2026-07-12
- Decision: Keep the existing detailed `family_status` unchanged. Add a compact Russian analytical field named `family_status_norm`, normally containing one or two words. Prefer full historical terminology over abbreviations, including `Незаконнорожденный сын` and `Незаконнорожденная дочь`.
- Analytical scope: Distinguish explicitly recorded registered husband-wife and child statuses from explicitly recorded non-registered cohabitation and illegitimate-child statuses. Do not use this field to reconstruct relationships between household members.
- Review requirement: Review the mapping of every distinct `family_status` value before approving the controlled vocabulary, mapping table, or staged dataset.
- Safeguard: This preliminary decision does not modify canonical or staged data and does not approve any individual source-to-normalized mapping.
- Approval status: Preliminary design approved by the project owner; complete value mapping remains pending review.

## Decision 14 - Item 11 exceptional `family_status_norm` mappings

- Date: 2026-07-12
- Decision: Approve the 17 exceptional source-to-normalized mappings recorded in `data/review/family_status_norm_item11_20260712/family_status_owner_review_cases.csv`, covering 23 records. Owner modifications to the initial proposals are: `Муж. хозяин` to `Хозяин`; `На воспитании. Сын` to `Сын`; and both `Приемыш жильца` and `Приемыш незаконный внук` to `Приемный сын`.
- Rationale: The selected compact value represents the analytically preferred household or family status while the complete historical expression remains unchanged in `family_status`.
- Safeguard: This decision approves only the exceptional mapping rows. It does not approve all remaining proposed mappings and does not modify canonical or staged datasets.
- Approval status: Approved by the project owner.

## Decision 15 - Item 11 domestic-service and cousin mappings

- Date: 2026-07-12
- Decision: Preserve `Кухарка`, `Нянька`, and `Служанка` as distinct `family_status_norm` values rather than consolidating them under `Прислуга`. Map `Двоюродный брат` to the broader analytical category `Брат`.
- Rationale: The three domestic-service terms express distinct recorded household functions worth retaining analytically, while the cousin distinction is not required in the compact kinship vocabulary.
- Safeguard: The detailed `family_status` values remain unchanged. This decision updates only the approved mapping specification and does not modify canonical or staged datasets.
- Approval status: Approved by the project owner.

## Decision 16 - Complete Item 11 `family_status_norm` mapping

- Date: 2026-07-12
- Decision: Approve all remaining proposed `family_status_norm` mappings in the complete 190-value inventory, including blank, after the separately recorded owner modifications in Decisions 14 and 15. Add the approved derived field immediately after the unchanged `family_status` in a versioned staged candidate.
- Rationale: The compact Russian vocabulary supports analysis of recorded household and family status, including registered spouses, cohabitants, and explicitly recorded illegitimate children, without reconstructing relationships or discarding the detailed historical expression.
- Affected review files: `data/review/family_status_norm_item11_20260712/`.
- Staged and QA files: `data/staging/family_status_norm_item11_20260712/` and `outputs/qa/family_status_norm_item11_20260712/`.
- Safeguard: The canonical `v2_20260711` datasets and canonical manifest remain unchanged. Canonical release requires a separate explicit approval.
- Approval status: Complete mapping approved by the project owner; staged implementation authorized.

## Decision 17 - Complete Item 17 `legal_status_norm` mapping

- Date: 2026-07-12
- Decision: Approve all 100 distinct `legal_status` mappings including blank, incorporating the 12 owner corrections supplied in `legal_status_review_owner.xlsx`. Retain Russian gender distinctions, retain approved `Сын` and `Дочь` forms with parent variants, normalize `Поселенка` to `Поселка`, remove approved geographic qualifiers from `legal_status_norm`, and move `Богадельщик` to `illness` for the five affected records. The owner subsequently corrected the preliminary analytical label `Богаделец` to `Богадельщик`.
- Rationale: The approved Russian analytical field reduces inconsistent wording without prematurely applying the broader aggregation planned for the English version. The unchanged detailed `legal_status` preserves the reviewed historical expression.
- Affected review files: `data/review/legal_status_item17_20260712/`, including the retained owner workbook and approved mapping table.
- Staged and QA files: `data/staging/legal_status_norm_item17_20260712/` and `outputs/qa/legal_status_norm_item17_20260712/`.
- Safeguard: The canonical `v2_20260711` datasets and canonical manifest remain unchanged. Canonical release requires separate explicit approval.
- Approval status: Complete mapping approved by the project owner; staged implementation authorized.

## Decision 18 - Sentence case for normalized categorical fields

- Date: 2026-07-12
- Decision: Use Sentence case consistently for normalized Russian categorical fields, including `literacy`. Normalize the literacy vocabulary to `Грамотен`, `Неграмотен`, `Образован`, or blank.
- Scope: Apply the rule to controlled categorical fields and approved derived normalized fields. Preserve reviewed capitalization in proper names, free text, and source-preserving fields, including `comments`. Boolean codes and identifiers remain outside Sentence case.
- Rationale: Sentence case provides consistent Russian analytical categories while avoiding destructive blanket capitalization of historical text and proper names.
- Documentation: `docs/capitalization_specification.md` and `docs/data_dictionary.md`.
- Staged and QA files: `data/staging/capitalization_item9_20260712/` and `outputs/qa/capitalization_item9_20260712/`.
- Safeguard: The staged candidate changes only `literacy`; canonical datasets and the canonical manifest remain unchanged.
- Approval status: Approved by the project owner; staged implementation authorized.

## Decision 19 - Item 3 derived `sex` and conflict corrections

- Date: 2026-07-12
- Decision: Approve `sex` for all 7,446 records using the Russian Sentence case values `Мужской` and `Женский`. Approve the proposed values for all 12 initially unresolved records. Correct the conflicting `legal_status` value in 10 of those records; retain all corresponding `family_status` values because they already agree with the approved sex.
- Result: 4,921 records are `Мужской` and 2,525 are `Женский`, with no blanks. Ten `legal_status` values change and zero `family_status` values change in the staged candidate.
- Evidence: Explicit grammatical evidence in `legal_status`, approved `legal_status_norm`, and `family_status`; reviewed patronymic morphology; and owner-approved name evidence for unresolved cases. Provenance is retained in `sex_evidence`.
- Staged and QA files: `data/staging/sex_item3_20260712/` and `outputs/qa/sex_item3_20260712/`.
- Safeguard: Canonical datasets and the canonical manifest remain unchanged. Canonical release requires separate explicit approval.
- Approval status: Approved by the project owner; staged implementation authorized.

## Decision 20 - Complete Item 15 `illness_norm` mapping

- Date: 2026-07-12
- Decision: Approve all 31 `illness` mappings including blank. Preserve the full forms `Застарелый вывих в левом локтевом сочленении`, `Контужен`, `Левая рука не работает`, `Немой`, `Разбита параличом`, and `Слабосилен` in `illness_norm`. Normalize `Слаб` to `Слабосилен`. Confirm all other proposed mappings, including compound semicolon-separated categories and `Богадельщик`.
- Result: The staged candidate contains 53 nonblank `illness_norm` values. Original `illness` values remain unchanged, all normalized categories use Sentence case, and no non-target fields change.
- Review and mapping files: `data/review/illness_item15_20260712/`.
- Staged and QA files: `data/staging/illness_item15_20260712/` and `outputs/qa/illness_item15_20260712/`.
- Safeguard: The Item 15 stage depends on the approved Item 17 `Богадельщик` transfers. Canonical datasets and the canonical manifest remain unchanged.
- Approval status: Approved by the project owner; staged implementation authorized.

## Decision 21 - Canonical normalization release v3

- Date: 2026-07-12
- Decision: Designate the versioned `v3_20260712` combined and district datasets as the current canonical release. Consolidate every normalization item approved through this date into a common 31-column schema while leaving still-pending tracker items untouched.
- Schema: Replace `household_number` with `household_id`, `household_type`, and `household_details`; add `legal_status_norm`, `sex`, `sex_evidence`, `family_status_norm`, and `illness_norm`; retain the approved `name_alias` field and all other continuing v2 fields.
- Dependency order: Apply detailed corrections first, including the 10 Item 3 `legal_status` corrections, then regenerate dependent normalized fields. Apply Item 17 `Богадельщик` transfers before deriving `illness_norm`.
- Validation: 7,446 records, 31 fields, expected district counts, unique identifiers, exact district concatenation, Sentence case normalized categories, and zero cross-field gender conflicts.
- Files: `data/processed/*_v3_20260712.csv`, `scripts/build_canonical_v3_20260712.py`, and `outputs/qa/canonical_v3_20260712/`.
- Safeguard: Preserve v2 and unversioned canonical files as immutable historical release artifacts. Items 6–8, 12, and 16 remain pending and are not represented as completed derived fields.
- Approval status: Approved by the project owner as the new canonical release.

## Decision 22 — Compact English analytical dataset

- Date: 2026-08-01
- Decision: Create a compact English-only analytical dataset derived from canonical `v5_20260731` for MySQL analysis and Tableau visualization. This will be a separate analytical product and will not replace or modify the authoritative Russian canonical datasets.
- Language rule: Translate analytical categories and geographic values through explicit reviewed lookup tables. Transliterate personal names consistently; never translate personal names.
- Technical purpose: Use simple English column names, controlled English values, analysis-ready numeric fields, and SQL-compatible blank/NULL handling for straightforward MySQL and Tableau imports.
- Column scope: The final compact column set is intentionally **not yet approved**. The project owner will revisit and approve the included and excluded columns before any English dataset is generated.
- Deferred implementation: Do not create the English CSV, SQL table definition, loading script, or Tableau extract until the compact schema has been reviewed.
- Safeguard: Preserve canonical `v5_20260731`, all Russian values, review provenance, and source-traceability fields in the canonical layer. Any omitted columns remain available there for audit and historical research.
- Expected future outputs: A versioned file under `data/analytical/`, reviewed translation and transliteration lookup tables, MySQL schema and loading scripts, and QA evidence reconciling the English layer to all 7,446 canonical records.
- Approval status: English-only analytical-layer direction approved by the project owner; column selection and implementation remain pending.

## Decision 23 - Owner-approved manual name revisions

- Date: 2026-08-02
- Decision: Apply the following owner-approved corrections to canonical `v5_20260731` name components: set `P005330.first_name` to `Филипп` and clear `P005330.patronymic_name`; clear `P002763.patronymic_name` and `P002788.patronymic_name`; and store the complete string `Ахмет Оглы Аскар` as `P006902.last_name`, clearing its `first_name` and `patronymic_name`.
- Rationale: These are direct manual revisions to the parsed name components. The unchanged `name_raw` field remains the source transcription, while the component fields reflect the owner’s canonical interpretation.
- Affected files: `data/processed/clean_sakhalin_1890_ru_v5_20260731.csv` and the corresponding district files `clean_tymovsky_ru_v5_20260731.csv`, `clean_korsakovsky_ru_v5_20260731.csv`, and `clean_alexandrovsky_ru_v5_20260731.csv`.
- Provenance: The affected rows retain observed source fields where applicable; manually revised component metadata uses `manual_override` in `parse_rule` and clears the source field for cleared components.
- Approval status: Approved by the project owner and applied to the canonical v5 datasets.

## Decision 24 — Blank and NULL convention for the English analytical dataset

- Date: 2026-08-02
- Decision: Represent missing values as empty fields in the English analytical CSV.
- SQL rule: Convert empty nullable fields to true SQL `NULL` during MySQL loading; do not load placeholder text such as `"NULL"`, `"N/A"`, or `"Not recorded"` solely to represent missingness.
- Value safeguard: Preserve meaningful values such as numeric `0` and Boolean `FALSE`; they are not missing values.
- Age rule: Preserve `age = 0` as a valid recorded numeric value; only a blank age represents missingness.
- Boolean rule: Keep `allowance_status` as a three-state nullable Boolean. Export `TRUE` for yes, `FALSE` for no, and an empty CSV field for missing; load these into MySQL as `1`, `0`, and SQL `NULL`, respectively.
- Tableau rule: Reader-friendly labels may be applied in Tableau calculations or presentation layers without replacing the underlying missing value in the source dataset.
- Approval status: Approved by the project owner as the first rule under Item 3, English Value and NULL Specification. The remaining Item 3 conventions were subsequently approved in Decision 25.

## Decision 25 — Complete English value and SQL type specification

- Date: 2026-08-02
- Decision: Approve the complete field-level MySQL types, nullability, English capitalization, compound-value delimiters, and special-value handling in `docs/english_dataset_value_null_specification.md`.
- Unknown-value safeguard: Do not assume that explicit `Unknown`, `Not recorded`, or `Not applicable` concepts are absent. Inventory and review every distinct included categorical value during lookup-table development, and use these English labels only when the canonical source explicitly carries the corresponding meaning.
- Compound-value rule: Use semicolon plus one space (`; `) between multiple categories and preserve canonical component order unless an approved translation rule requires otherwise.
- Living-alone rule: Keep `living_alone_status` as nullable text; translate the explicit value as `Living alone` and do not reinterpret blanks as Boolean `FALSE`.
- Edge cases: Preserve `Нет занятия` as an explicit `No occupation` category. Review `Человек неизвестного звания` during personal-name handling rather than silently converting it to a missing-value label.
- Approval status: Approved by the project owner. Item 3 is complete.

## Decision 26 — Compact English personal-name transliteration standard

- Date: 2026-08-02
- Decision: Use a simplified ASCII implementation of BGN/PCGN Russian romanization to generate compact English `full_name` from canonical `name_raw`.
- Fidelity rule: Preserve canonical token order, historical spelling, hyphens, Latin initials, masking, and unusual punctuation. Do not modernize, correct, translate, or infer personal names. The authoritative Cyrillic value remains available through `person_id` in canonical v5.
- Character rule: Use ordinary Latin characters without diacritics or typographic prime marks; omit soft and hard signs while applying positional rules to surrounding letters; use `yo` for `ё` if it occurs in a future canonical version.
- Numbering rule: Convert ordinal disambiguators such as `1-й` and `2-я` to neutral parenthetical markers such as `(1)` and `(2)`, preserving their position.
- Exception: Translate the descriptive non-name value `Человек неизвестного звания` as `Person of unknown rank` through an explicit reviewed lookup.
- Implementation gate: Create the reproducible transliteration function, reviewed exception inventory, collision report, and QA evidence before Item 4 is complete.
- Specification: `docs/english_name_transliteration_specification.md`.
- Approval status: Rules approved by the project owner; implementation and quality review remain pending.

## Decision 27 — English name review approval and deferred Russian mixed-script audit

- Date: 2026-08-02
- English review decision: Approve all 44 priority transliteration records, comprising 41 accepted candidates and 3 owner revisions: `P001151` → `Lyubov Aleksandrova Vetskaya`; `P004592` → `Fedot Larionov Masyukevich`; and `P005221` → `Iogan Peters`.
- Staged output: Apply these decisions to the complete 7,446-record English name mapping in `outputs/english_name_transliteration_review_20260802/name_transliteration_staged_20260802.csv`.
- Russian canonical reminder: Before producing the next Russian canonical release, run a mixed Cyrillic–Latin character audit across every name-bearing field. Identify accidental Latin lookalikes embedded inside otherwise Cyrillic words while preserving intentional Latin initials or explicitly mixed-script source forms.
- Unicode punctuation reminder: Extend the deferred Russian audit to controlled geographic fields. Normalize `Санкт-Петербургская губерния` (hyphen-minus, `U+002D`) and `Санкт‑Петербургская губерния` (non-breaking hyphen, `U+2011`) to the canonical Russian form `Санкт-Петербургская губерния`. Treat them as one historical category; both current variants map to `Saint Petersburg Governorate` in the English layer.
- Known accidental cases: `P001151` contains Latin `p` in `Александpова`; `P004592` contains Latin `c` in `Маcюкевич`; and `P005221` contains Latin `c` in `Петерc`.
- Scope safeguard: This decision does not yet modify canonical Russian v5. Corrections require a separately staged canonical version and QA review.
- Approval status: English transliteration review approved; Russian mixed-script audit documented as mandatory deferred work.

## Decision 28 — Controlled translation Batch A and legal-status translation basis

- Date: 2026-08-02
- Batch A decision: Approve 37 proposed controlled English mappings and revise `Раскольничество` from `Schismatic (historical term)` to `Schismatic`. All 38 Batch A values are resolved with no holds.
- Legal-status history: Treat the owner-approved Item 17 Russian `legal_status_norm` vocabulary as authoritative. Preserve its gender, family-relation, penal, settler, exile-origin peasant, military, civil-rank, and exceptional distinctions in the English lookup table.
- Previously documented English terms: Use `Penal convict` for `Ссыльнокаторжный` and `Exile settler` for `Поселенец` as Batch B seed terms, following `docs/language_translation_strategy.md` and the approved sentence-case convention.
- Safeguard: Do not collapse the 61 normalized Russian legal-status categories merely for dashboard convenience; any broader grouping must be a separate derived field.
- Documentation: `docs/english_legal_status_translation_basis.md`.
- Approval status: Batch A approved; legal-status basis reviewed and documented before Batch B proposal preparation.

## Decision 29 — Recovery of complete prior legal-status translation options

- Date: 2026-08-02
- Source recovered: `outputs/translation_review_20260716/sakhalin_1890_english_translation_options.xlsx` contains Variant A, B, and C English options for the complete legal-status vocabulary; Variant A is the workbook's recommended historically explicit analytical vocabulary.
- Reconciliation: All 61 current canonical v5 `legal_status_norm` values match the prior workbook exactly, with zero missing and zero extra values.
- Correction to prior assessment: The earlier material contains a complete 61-value legal-status proposal, not merely the two examples previously located in documentation.
- Current review output: `outputs/english_controlled_translation_review_20260802/legal_status_translation_review_20260802.xlsx`.
- Approval status: Prior proposals recovered and reconciled; final owner selection remains pending for all 61 values.

## Decision 30 — Batch B1 legal-status approval and female co-owner reconciliation

- Date: 2026-08-05
- Legal-status decision: Apply all 61 owner selections from `legal_status_translation_review_20260802.xlsx`: 12 Variant A selections, 12 Variant B selections, 3 Variant C selections, and 34 owner revisions.
- Article convention: Use article-free controlled relationship labels. Standardize `Дочь солдатки` and `Сын солдатки` as `Child of soldier's wife`, and revise `Жена врача` to `Wife of doctor`.
- Reconciliation: The approved lookup covers all 61 canonical v5 `legal_status_norm` values, with zero missing values, extra values, or record-count mismatches.
- Approved output: `outputs/english_controlled_translation_review_20260802/legal_status_translation_approved_20260805.csv`.
- Female co-owner safeguard: Count the Cyrillic value `Совладелица` in Batch B family-status work. It occurs in 8 canonical records in both `family_status` and `family_status_norm`, and does not occur in `legal_status_norm`.
- Mixed-script check: The spelling `Cовладелица` with Latin `C` occurs zero times in canonical v5 and must not be treated as a separate category.
- Approval status: Batch B1 legal status approved and reconciled; `Совладелица` explicitly retained in the pending family-status inventory.

## Decision 31 — Batch B4 illness translation approval

- Date: 2026-08-05
- Decision: Approve all 25 canonical `illness_norm` English mappings: 12 Variant A selections, 9 Variant B selections, 1 Variant C selection, and 3 owner revisions.
- Consistency revision: Translate `Слепота; Психическое расстройство` as `Blind; Mental disorder`, matching the separately approved `Психическое расстройство` → `Mental disorder` component.
- Compound-value rule: Retain canonical component order and separate translated components with semicolon plus one space.
- Reconciliation: All 25 populated canonical illness categories are mapped exactly once, with zero missing values, extra values, blank English translations, or record-count mismatches.
- Approved output: `outputs/english_controlled_translation_review_20260802/illness_translation_approved_20260805.csv`.
- Approval status: Batch B4 illness translation approved and complete.

## Decision 32 — Batch B3 occupation translation approval

- Date: 2026-08-08
- Decision: Approve all 135 canonical `occupation_norm` English mappings: 129 proposed values accepted and 6 owner revisions.
- Confirmed consolidation: Map both `Катерный` and `На катере` to `Launch worker`. This is an intentional English analytical consolidation; the two Russian source categories remain distinct in canonical v5.
- Other review outcomes: Retain all other approved occupation labels without further consolidation or revision.
- Compound-value rule: Retain canonical component order and separate translated components with semicolon plus one space.
- Reconciliation: All 135 populated canonical occupation categories are mapped exactly once, with zero missing values, extra values, blank English translations, or record-count mismatches.
- Approved output: `outputs/english_controlled_translation_review_20260802/occupation_translation_approved_20260808.csv`.
- Approval status: Batch B3 occupation translation approved and complete.

## Decision 33 — Batch B2 family-status translation approval and Item 5 completion

- Date: 2026-08-09
- Decision: Approve all 37 canonical `family_status_norm` English mappings: 17 Variant A selections, 3 Variant B selections, 8 Variant C selections, and 9 owner revisions.
- Adoption terminology: Retain the owner-selected labels `Adopted daughter`, `Adopted son`, and `Adoptive father` for the three `Приемный...` categories.
- Approved consolidations: Use gender-neutral shared labels where selected, including `Household head`, `Cohabiting partner`, `Joint householder`, `Lodger`, `Hired worker`, and `Cook`.
- Female co-owner safeguard: `Совладелица` is mapped to `Joint householder` and reconciles to all 8 canonical records; the spelling uses Cyrillic `С`.
- Reconciliation: All 37 populated canonical family-status categories are mapped exactly once, with zero missing values, extra values, blank English translations, or record-count mismatches.
- Approved output: `outputs/english_controlled_translation_review_20260802/family_status_translation_approved_20260809.csv`.
- Item status: Controlled Category Translation Item 5 is complete across all 296 populated values in Batch A and Batch B.

## Decision 34 — Geographic translation approval and Item 6 completion

- Date: 2026-08-09
- Decision: Approve all 51 settlement and 100 populated normalized origin-place mappings. Accept 148 proposals and apply three owner revisions: `Пост Дуэ` → `Doue Post`; `Тарайское Зимовье` → `Tarayskoye Winter Settlement`; and `Рязанская губерния` → `Ryazan Governorate`.
- District status: Retain the three district mappings approved in Item 5 Batch A.
- Duplicate-English safeguards: Both Russian Unicode variants of `Санкт-Петербургская губерния` map to `Saint Petersburg Governorate`; `Прусский подданный` and `Прусская подданная` both map to `Prussian subject`. These are intentional many-to-one English mappings.
- Blank handling: Preserve all 838 blank `origin_place_norm` records as blank.
- Reconciliation: The approved lookup tables contain exactly 3 district, 51 settlement, and 100 origin-place source values, with zero duplicate Russian keys, zero blank English mappings, and zero unmapped populated values.
- Approved outputs: `outputs/english_geographic_translation_review_20260809/district_translation_approved_20260809.csv`; `settlement_translation_approved_20260809.csv`; `origin_place_translation_approved_20260809.csv`; and `geographic_translation_reconciliation_20260809.json`.
- Item status: Geographic Translation and Transliteration Item 6 is complete. Proceed to Item 7, English Dataset Build.

## Decision 35 — Compact English dataset v1 build

- Date: 2026-08-09
- Decision: Build `data/analytical/sakhalin_1890_en_v1.csv` from canonical `clean_sakhalin_1890_ru_v5_20260731.csv`, plus explicitly approved staged Russian corrections, using only the approved compact schema and versioned English name, controlled-category, and geographic lookups.
- Schema result: 23 English columns in the owner-approved order and exactly 7,446 output records.
- Identifier result: 7,446 unique, nonblank `person_id` values and 7,446 unique, nonblank `source_position_id` values; canonical row order is preserved.
- Mapping result: Zero unmapped populated translated values and zero Cyrillic characters in the English output. Per the owner amendment of 2026-08-09, transliterate archive prefixes `РГБ` → `RGB` and `РГАЛИ` → `RGALI` while preserving archive numbers and the `№` sign. Transliterate Cyrillic archive-number suffix letters to Latin (`а` → `a`, `б` → `b`, `в` → `v`, and so forth) so identifiers remain distinct without retaining Cyrillic.
- Value rules: Missing values remain empty CSV fields; `allowance_status` contains only `TRUE`, `FALSE`, or blank; all 204 recorded `age = 0` values remain zero.
- Reproducibility and lineage: The build is implemented in `scripts/build_english_dataset_v1_20260809.mjs`, with field lineage in `docs/english_dataset_field_lineage.md` and QA evidence under `outputs/qa/english_dataset_build_20260809/`.
- Revised output SHA-256 after the P000107 staged archive-code correction: `1b77d6330855763c54c32f21d247dc44471a69590db4fc00925c4e22eb8ac508`.
- Item status: English Dataset Build Item 7 is complete. Proceed to Item 8, Dataset Quality Review; the English v1 file remains a candidate until that review and owner approval are complete.

## Decision 36 — P000107 nonstandard archive-code recovery

- Date: 2026-08-09
- Russian staged correction: Set `P000107.notes_raw` from blank to the owner-supplied value `ДМЧ (Ялта). КП № 1716.` in `data/staging/archive_code_p000107_20260809/clean_sakhalin_1890_ru_v5_20260731_archive_code_staged.csv`.
- English transliteration: Set `P000107.archive_code` to `DMCh (Yalta). KP № 1716.`. Preserve the punctuation, archive number, and `№` sign; transliterate `ДМЧ` as `DMCh`, `Ялта` as `Yalta`, and `КП` as `KP`.
- Scope safeguard: The staged Russian candidate changes exactly one cell in one record. It preserves all 7,446 records, all 50 columns, identifier order, and every non-target value. Canonical Russian v5 remains unchanged.
- English result: Rebuild `sakhalin_1890_en_v1.csv`; archive-code counts become 7,223 `RGB`, 222 `RGALI`, 1 `DMCh`, and zero blanks. The complete English dataset contains zero Cyrillic characters.

## Decision 37 — Item 8 technical quality review

- Date: 2026-08-09
- QA decision: Submit the compact English v1 candidate for owner approval after an independent technical quality review returned `PASS` on every control.
- Structural reconciliation: 7,446 output records, 23 approved columns, exact staged-source row order, 7,446 unique `person_id` values, and 7,446 unique `source_position_id` values.
- Transformation reconciliation: Zero mismatches across all 23 fields, zero unmapped populated categories or places, exact person-level name lookup matches, and zero Cyrillic cells.
- Numeric and Boolean reconciliation: All populated numeric values are unsigned integers within their approved MySQL ranges; `allowance_status` contains only `TRUE`, `FALSE`, or blank; 204 valid `age = 0` records remain preserved.
- Household reconciliation: All 2,796 populated household groups retain exact membership after translation; 246 blank `household_id` records remain blank; no duplicate `person_seq` exists within a settlement.
- Exceptions: Zero QA exception rows. Accepted many-to-one mappings and the P000107 staged archive correction are documented separately as approved non-errors.
- Package: `outputs/qa/english_dataset_quality_review_20260809/english_dataset_quality_review_20260809.xlsx`, companion reconciliation CSVs, JSON quality report, empty exception file, and SHA-256 manifest.
- Approval status: Technical QA passed. Item 8 remains pending project-owner approval; do not begin the MySQL package until the owner approves this candidate.

## Decision 38 — English candidate approval and MySQL package

- Date: 2026-08-09
- Owner approval: Approve the compact English v1 dataset and the complete Item 8 quality-review package. Item 8 is complete.
- MySQL schema: Create `sakhalin_1890_en` for MySQL 8 using the approved field types, `utf8mb4`, `person_id` as primary key, a unique `source_position_id`, and indexes for geography, household, legal status, origin, occupation, and age.
- Loading rule: Use `LOAD DATA LOCAL INFILE`; convert empty nullable CSV fields to SQL `NULL`, preserve numeric zeroes, and convert CSV `TRUE`/`FALSE` to nullable Boolean `1`/`0`. The load script deliberately does not truncate an existing table.
- Validation package: Validate 7,446 records, identifier uniqueness, household groups, age zeroes and blanks, Boolean totals, archive-code totals, settlement sequence uniqueness, Cyrillic absence, district totals, and field-level NULL totals.
- Analysis package: Include starter queries for geography, age and sex, legal status, literacy, occupation, origin, arrival year, household size, allowance, and illness.
- Static QA: All 12 package controls passed, including schema order, character set, keys, NULL and Boolean conversion, validation coverage, analysis-query coverage, and documentation.
- Runtime reconciliation: The user's MySQL Workbench connection successfully loaded 7,446 rows into `sakhalin_1890_en`, with zero skipped records and zero warnings. Validation matched the expected CSV QA totals: 7,446 records, 2,796 populated household groups, correct NULL/Boolean totals, 7,223 RGB archive codes, 222 RGALI codes, 1 DMCh code, and zero blank archive codes. All displayed validation controls returned `PASS`; Item 9 is complete.
- Deliverables: `sql/01_create_english_dataset.sql`, `sql/02_load_english_dataset.sql`, `sql/03_validate_english_dataset.sql`, `sql/04_analysis_queries.sql`, `docs/mysql_english_dataset_import.md`, and `outputs/qa/mysql_package_20260809/mysql_package_static_qa_20260809.json`.
