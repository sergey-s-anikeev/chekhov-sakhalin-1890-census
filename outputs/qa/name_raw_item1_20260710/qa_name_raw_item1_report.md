# Item 1 QA Report: `name_raw` Verification

## Status

Ready for project-owner review. No canonical dataset was modified.

## Input Integrity

- Canonical records: **7,446**
- Canonical SHA-256 unchanged: **True**
- Canonical schema matches the approved 23 columns: **True**
- Unique `person_id`: **True**
- Unique `source_position_id`: **True**
- Blank canonical `name_raw`: **0**

## Review Results

- Exception records: **43**
- Records with proposed actions: **43**
- Proposed field-level differences: **59**
- Pending owner decisions: **43**
- High-confidence proposals: **9**
- Medium-confidence proposals: **21**
- Low-confidence proposals: **13**

### Exception counts

- `age_text`: **2**
- `alias_or_parentage_phrase`: **6**
- `double_surname_item2`: **5**
- `long_multiword_name`: **3**
- `no_explicit_personal_name`: **4**
- `parenthetical_text_item2`: **10**
- `role_or_description_text`: **5**
- `unexpected_lowercase_or_word_split`: **24**

## Preview Validation

- Preview records: **7,446**
- Original canonical columns unchanged in preview: **True**
- `person_id` order unchanged: **True**
- Blank proposed names: **0**

The preview contains proposal columns only. It is not a canonical replacement and none of its proposed values are approved yet.

## Required Owner Decision

Complete `owner_decision` in `name_raw_proposed_corrections.csv` with an approved decision for each row. Medium- and low-confidence proposals should be checked against source evidence before approval.

Allowed decision values are `approve`, `reject`, `modify`, and `defer`. Add the replacement instruction to `reviewer_notes` for `modify`, and explain `reject` decisions where useful.

## Limitations

- The source PDFs are not present in the clean repository, so medium- and low-confidence proposals require source verification.
- Parenthetical and double-surname classifications remain provisional until Item 2.
- The exception inventory is exhaustive for the documented Item 1 heuristics, not a claim that every historical name can be linguistically validated without source review.
