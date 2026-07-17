# Review of substantive `arrival_year` anomalies

Source reviewed: `data/staging/occupation_item18_20260717/clean_sakhalin_1890_ru_v3_20260712_items7_8_item12_item16_item18_staged.csv`.

This is a review-only artifact. No canonical or staged data values were changed.

## Profile

- Rows: 7,446
- Populated `arrival_year`: 4,826
- Blank `arrival_year`: 2,620
- All populated values are four-digit integers.
- Range: 1865-1890.
- Values after the 1890 census year: 0.
- Rows with both numeric age and arrival year: 4,806.
- Negative implied arrival age: 4.

The implied arrival age is calculated as `age - (1890 - arrival_year)`. It is a screening measure, not exact proof: census date, birthday, and age rounding can explain a one-year boundary difference.

## Findings

Four rows are exported to `arrival_year_substantive_anomalies.csv`:

- 3 high-priority rows have a multi-field contradiction or a stronger age conflict.
- 1 medium-priority row is only one year beyond the arithmetic boundary and may reflect census-date or age-rounding effects.

Twenty-six people have implied arrival ages over 60, including three over 70. These are unusual but not intrinsically impossible and have therefore not been classified as substantive anomalies.

## Review boundary

The CSV records the initial screening results. Owner decisions in `owner_response/` supersede the preliminary severity labels: `P003355`, `P004849`, and `P005024` were accepted unchanged, while `P005199` received an approved `age` correction from `2` to `25`.

The expanded cross-field check found `P003355` as the only record with both a populated `arrival_year` and `origin_place = На Сахалине`, including case-insensitive matching. It is retained as an owner-reviewed exception. No unresolved `arrival_year` anomaly remains.
