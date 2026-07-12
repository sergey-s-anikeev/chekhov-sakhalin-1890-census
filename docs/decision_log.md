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
- Decision: Approve all 100 distinct `legal_status` mappings including blank, incorporating the 12 owner corrections supplied in `legal_status_review_owner.xlsx`. Retain Russian gender distinctions, retain approved `Сын` and `Дочь` forms with parent variants, normalize `Поселенка` to `Поселка`, remove approved geographic qualifiers from `legal_status_norm`, and move `Богаделец` to `illness` for the five affected records.
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
