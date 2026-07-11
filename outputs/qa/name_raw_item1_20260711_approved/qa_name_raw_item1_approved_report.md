# Item 1 Final QA: Approved `name_raw` Decisions

## Status

Owner decisions have been applied to a versioned staged candidate. Canonical datasets remain unchanged.

## Owner Decisions

- Decision records: **43**
- Approved: **28**
- Modified: **15**
- Rejected: **0**
- Deferred: **0**
- Decision application mismatches: **0**

## Applied Changes

- Changed records: **37**
- Field-level differences: **60**
- `name_raw` changes: **37**
- Populated `name_alias` values: **14**
- `family_status` changes: **2**
- `comments` changes: **7**

## Structural QA

- Staged records: **7,446**
- Expected 24-column schema: **True**
- `name_alias` immediately follows `name_raw`: **True**
- Unique `person_id`: **True**
- Unique `source_position_id`: **True**
- Identifier and row order unchanged: **True**
- District ordering unchanged: **True**
- Blank `name_raw`: **0**
- Only approved fields changed: **True**
- Residual role leakage: **0**
- Residual age text: **0**
- Angle-bracket markup: **0**
- Square-bracket markup: **0**

## Preserved Source Descriptions

The following records remain unchanged because the reviewed field contains no recoverable personal name: `P003380`, `P004099`, `P005396`, `P007204`.

## Canonical Safeguard

- Canonical SHA-256 unchanged: **True**
- No canonical dataset or canonical manifest entry was modified.
