# Item 7 age review summary

This is a read-only review package based on `data/processed/clean_sakhalin_1890_ru_v3_20260712.csv`. No canonical or staged dataset was changed.

## Scope

- Full cohort: all 1,606 records with integer `age` from 0 through 18 inclusive.
- Blank-age exception inventory: 147 records.
- Initial flagged child review subset: 274 records (244 high priority; 30 medium priority).
- Owner-reviewed age-zero records: 202; all were confirmed with no age anomaly on 2026-07-13.
- Remaining under review: 75 records. This includes 3 age-zero records whose age is confirmed but whose blank family status remains a separate review flag.
- Every review row includes `page_number`, `person_id`, and `source_position_id` for source-book verification.

## Interpretation

Flags are prompts for manual source review, not corrections. Relationship or status evidence is never used to infer an age. `Свободного состояния` is treated as age-neutral. Child forms beginning with `Сын` or `Дочь` are treated as consistent for screening purposes. Adult household roles, service roles, blanks, and standalone adult legal statuses remain under review. The age-zero check is complete and confirmed without anomalies.

## Manual decision fields

Use `manual_decision` and `manual_notes` in the review CSVs. Suggested decisions are `confirmed`, `age correction`, `status correction`, or `needs further evidence`; no decision has been prefilled.
