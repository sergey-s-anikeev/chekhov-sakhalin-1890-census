# Anomaly Review Final Documentation

## Scope

This document records the manual anomaly review round for `clean_sample_500.csv`.

The reviewed sample contains the first 500 parsed person records from the uploaded Korsakovskiy okrug PDF sample.

## Reviewed Records

| person_id | Field | Decision | Final handling |
|---|---|---|---|
| `P000128` | `legal_status` | Source typo / spelling variant in `legal_status` | Normalized to `Ссыльнокаторжный` |
| `P000178` | `religion` | Confirmed source typo: `1882` appears in religion field | Preserved as printed and documented as confirmed source anomaly |
| `P000245` | `category_code` | Source category-code typo: name printed under `5.` instead of `4.` | Fields manually reassigned; age set to `0`, comments set to `4 месяца` |
| `P000366` | `category_code` | Source category-code typo / missing legal status | `legal_status` left blank; person fields manually reassigned |
| `P000423` | `religion` | Spacing artifact caused by source/PDF text: `Правосл [авного]` became `Правосл авное` | Normalized to `Православное`; reusable bracket-spacing rule added |
| `P000426` | `category_code` | Source category-code shift | Fields manually reassigned to the final schema |
| `P000143` | `origin_place` | Inflected / unresolved origin-place form | Normalized `Курляндского` to `Курляндская губерния` using `MAIN_GUBERNIAS_1890` |
| `P000452` | `origin_place` | Variant origin-place form | Normalized `Каменецк-Подольская` to `Подольская губерния` using `MAIN_GUBERNIAS_1890` |

## Reusable Rule Updates

### Square-bracket restoration spacing

A new normalization rule was added before square-bracket removal:

```text
Правосл [авного] -> Правосл[авного] -> Православного -> Православное
```

This rule removes extraction spaces before restored word parts in square brackets. It is especially relevant for one-word fields such as `religion` and `occupation`.

### Origin-place mapping

The 1890 administrative-unit normalization now includes:

```text
Каменецк-Подольская -> Подольская губерния
Каменецк-Подольской -> Подольская губерния
Курляндского -> Курляндская губерния
```

These are mapped against the `MAIN_GUBERNIAS_1890` controlled reference list.

### Confirmed year-like religion anomaly

The QA workflow now allows a year-like value in `religion` only when it is documented as a confirmed source anomaly. For this sample, the preserved value is:

```text
P000178 / religion = 1882
```

## QA Outcome

After applying manual decisions:

- Row count remains `500`.
- Unknown origin places: `0`.
- Unknown legal statuses: `0`.
- Unknown family statuses: `0`.
- Unknown religions: `0`.
- Unresolved source anomalies: `0`.
- Confirmed source anomalies preserved as printed: `1` (`P000178`).

## Reproducibility

The applied manual decisions are stored in:

```text
outputs/qa/manual_review_decisions.csv
```

The cleaned sample is stored in:

```text
data_processed/clean_sample_500.csv
```

The updated QA reports are stored in:

```text
outputs/qa/sample_500_qa_report.md
outputs/qa/sample_500_qa_report.json
```

The reusable normalization rules are implemented in:

```text
scripts/sakhalin_conversion_helpers_v11.py
```
