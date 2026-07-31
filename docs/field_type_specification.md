# Field Type and Number-Format Specification

Applies to canonical release `v4_20260717` and subsequent releases unless an owner-approved schema revision supersedes it.

## Text-preserved fields

The following values are serialized and interpreted as text even when they contain digits:

- `person_id`
- `source_position_id`
- `district_code`
- `settlement_order`
- `household_id`
- archival references in `notes_raw`
- textual household markers and details

This preserves leading zeros, compound identifiers, suffixes, and source wording. In particular, `settlement_order` remains two digits and identifier components must not be converted to numeric storage.

## Integer-or-blank fields

The following fields contain only unsigned integer text or blank in CSV serialization:

- `person_order_in_settlement`
- `page_number`
- `age`
- `age_months`
- `arrival_year`

`age` stores completed years. `age_months` stores total completed months under the approved Item 8, Item 22, and Item 23 rules. Explicit precise values take precedence; otherwise whole-year ages 1 and 2 derive 12 and 24 months.

## Identifier requirements

- `person_id` follows the exact global sequence `P000001`–`P007446`.
- `source_position_id` is nonblank and unique.
- `settlement_order` is exactly two digits.
- Leading zeros in identifier components are preserved.
- CSV serialization must preserve row order and identifier values exactly.

## Canonical v4 verification

Reverified 2026-07-18 against `data/processed/clean_sakhalin_1890_ru_v4_20260717.csv`:

- 7,446 records and 36 columns.
- Zero integer-format exceptions.
- Zero malformed two-digit settlement orders.
- Zero person-sequence exceptions.
- Zero duplicate person or source-position identifiers.
- Zero blank source-position identifiers.
- Zero blank `age_months` values among records aged 0–2.

Machine-readable exception inventories remain in `outputs/qa/canonical_v4_20260717/`. Both exception CSV files contain headers only because no exceptions were found.
