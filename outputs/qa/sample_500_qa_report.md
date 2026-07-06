# QA Report: clean_sample_500.csv

## Summary

- Clean CSV: `clean_sample_500.csv`
- Reparsed raw input: `raw_extracted_sample_500_reparsed.csv`
- Row count: **500**
- Scope: first 500 parsed person records from the uploaded Korsakovskiy okrug PDF sample
- QA status: hard validation checks completed; manual anomaly-review decisions applied

## Soft Review Counts

| Check | Count |
|---|---:|
| Unknown origin places | 0 |
| Unknown legal statuses | 0 |
| Unknown family statuses | 0 |
| Unknown religions | 0 |
| Unresolved source anomalies | 0 |
| Confirmed source anomalies preserved as printed | 1 |

## Unknown Origin Places

No values flagged.

## Unknown Legal Statuses

No values flagged.

## Unknown Family Statuses

No values flagged.

## Unknown Religions

No values flagged.

## Confirmed Source Anomalies Preserved as Printed

| person_id | source_position_id | page | settlement | name_raw | field | value | reason |
|---|---|---:|---|---|---|---|---|
| `P000178` | `3-30-030-0040` | 425 | Поро-ан-Томари | Андрей Федоров Савельев | `religion` | `1882` | religion field contains a year-like value; probable source misprint |

## Manual Decisions Applied

| person_id | Field | Source value | Decision / action |
|---|---|---|---|
| `P000128` | `legal_status` | `Сс[ылно]каторжный` | normalize to Ссыльнокаторжный |
| `P000178` | `religion` | `1882` | preserve printed value in religion; keep as confirmed source anomaly, not unresolved QA item |
| `P000245` | `category_code` | `name field printed as 5.; should be 4.` | manually assign name/family_status/age/religion/origin/allowance to correct fields |
| `P000366` | `category_code` | `field 3 contains name; legal_status is absent in original` | leave legal_status blank; manually assign name/family_status/age/religion/literacy to correct fields |
| `P000423` | `religion` | `Правосл авное` | normalize to Православное |
| `P000426` | `category_code` | `field numbering shifted: name marked as 5., age as 6., religion as 7., origin as 8.` | manually assign legal_status/name/family_status/age/religion/origin/literacy/marriage/allowance to correct fields |
| `P000143` | `origin_place` | `Курляндского` | normalize to Курляндская губерния |
| `P000452` | `origin_place` | `Каменецк-Подольская` | normalize to Подольская губерния |

## Rule Updates Applied

- `normalize_source_markup()` now removes extraction spaces before square-bracketed restored word parts before bracket removal. Example: `Правосл [авного]` → `Православного` → `Православное`.
- `origin_place` normalization now maps `Каменецк-Подольская` to `Подольская губерния` using the `MAIN_GUBERNIAS_1890` reference list.
- `origin_place` normalization now maps `Курляндского` to `Курляндская губерния` using the `MAIN_GUBERNIAS_1890` reference list.
- QA now allows a confirmed year-like value in `religion` only as a documented source anomaly, not as a trailing-footnote error.

## Notes

- Soft-review values are not silently corrected. Each manual correction is recorded in `manual_review_decisions.csv`.
- The confirmed source typo `P000178 / religion = 1882` is preserved as printed.
- All previously unresolved legal-status, family-status, religion, and origin-place values are now resolved for this 500-record sample.
