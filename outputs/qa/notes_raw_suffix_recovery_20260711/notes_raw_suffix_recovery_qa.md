# Item 4: `notes_raw` suffix recovery QA

## Scope

This report documents a staged recovery of archive-reference suffixes in `notes_raw`. The canonical processed datasets were not modified.

## Inputs

- Canonical comparison source: `data/processed/clean_sakhalin_1890_ru.csv`
- Duplicate inventory: `data/review/notes_raw_duplicates_item4_20260711/notes_raw_duplicate_inventory.csv`
- Owner-confirmed true duplicates: `data/review/notes_raw_duplicates_item4_20260711/owner_confirmed_true_duplicates.txt`
- Uploaded raw page extracts: `data/review/notes_raw_duplicates_item4_20260711/raw_page_extracts/`
- Owner manual overrides:
  - `P001792`: `РГБ № 4300а`
  - `P007384`: `РГБ № 6152a`

## Results

- Source records: 7,446
- Staged records: 7,446
- Changed records: 41
- Suffixes recovered from uploaded page extracts: 37
- Owner manual overrides: 2
- Existing indexed values reformatted without a hyphen: 2
- Unmatched suffix evidence: 0
- Low-confidence matches: 0
- Unexpected duplicate values after correction: 0

## Structural QA

- Record count preserved: pass
- `person_id` values and order preserved: pass
- `source_position_id` values and order preserved: pass
- Only `notes_raw` changed: pass
- Indexed archive references use the approved no-space/no-hyphen format: pass

## Outputs

- Staged candidate: `data/staging/notes_raw_suffix_recovery_20260711/clean_sakhalin_1890_ru_notes_raw_item4_v1.csv`
- Record-level mapping and diff: `data/staging/notes_raw_suffix_recovery_20260711/notes_raw_suffix_mapping.csv`
- Match evidence: `outputs/qa/notes_raw_suffix_recovery_20260711/notes_raw_suffix_match_evidence.csv`
- Machine-readable QA: `outputs/qa/notes_raw_suffix_recovery_20260711/notes_raw_suffix_recovery_qa.json`
- SHA-256 artifact manifest: `outputs/qa/notes_raw_suffix_recovery_20260711/notes_raw_suffix_artifact_manifest.csv`

Canonical data remains unchanged pending project-owner approval.
