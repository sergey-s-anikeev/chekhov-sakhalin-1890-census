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
