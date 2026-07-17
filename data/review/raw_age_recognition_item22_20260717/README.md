# Targeted raw-age recognition audit

## Scope

Raw source directory: `data/raw/raw_district_files/`

Compared against the latest staged dataset after Item 21. This is a review-only audit; no new dataset values were changed.

## Coverage

- Raw rows: 7,447
- Staged rows: 7,446
- Raw rows linked to staged people: 7,446
- One unmatched raw row is a blank extraction row on Korsakovsky page 475, not a person-age record.
- Matched non-plain raw age expressions: 838

## Symbol-removal findings

- 19 ages contain digits on both sides of struck angle-bracket content, such as `3<0>4`.
- All 19 now agree with the visible value after struck content is removed.
- This includes owner-corrected `P005199`: `2<0>5 (?)` resolves to `25`.
- Another 498 non-plain expressions have a clear visible integer and agree with staged `age`.
- `P003286` is retained as the prior owner-verified source-image override rather than the raw text-extraction value.
- No unresolved clear-integer mismatch remains.

## Precise-age findings requiring owner review

Eighteen records in `raw_age_semantic_mismatch_review.csv` contain clear fractional-year or year/month wording that is not fully represented by the staged `age` and `age_months` fields.

- Two likely `age` errors:
  - `P004910`: raw `1 / 2 г[ода]`; staged `age = 1`; proposed `age = 0`, `age_months = 6`.
  - `P006656`: raw `5 [есяцев]`; staged `age = 5`; proposed `age = 0`, `age_months = 5`.
- Two existing `age_months` values disagree with raw wording:
  - `P005959`: raw 1 year 9 months; staged 20 months; proposed 21.
  - `P006718`: raw 1 year 10 months; staged 16 months; proposed 22.
- Fourteen additional fractional-year or year/month expressions have blank `age_months`; proposed values are supplied in the review CSV.

These are proposals from the supplied raw district files, not applied corrections. The full raw expression and source block are retained for every review row.

## Owner decisions and staging

The owner validated the proposed semantic values for 15 of the 18 records. Those decisions are staged in `data/staging/raw_age_recognition_item22_20260717/`:

- 15 `age_months` values were updated.
- Two of those records also received `age` corrections: `P004910` from 1 to 0 and `P006656` from 5 to 0.
- `P004306`, `P005959`, and `P006718` were excluded because the structured name conflicts with the person named in `source_block_raw`; all their staged values remain unchanged.

The exclusions are documented in `owner_response/excluded_name_mismatch_cases.csv`. They require raw-extraction linkage review and must not inherit the age text merely from the currently attached source block.

## Additional extraction observation

Three structured raw rows have names that conflict with their attached `source_block_raw`: `P004306`, `P005959`, and `P006718`. They are excluded from age changes and preserved for separate linkage review.
