# Revised `age_months` rule for whole-year ages 1 and 2

Owner-approved rule revision:

- If `age = 1` and `age_months` is blank, derive `age_months = 12`.
- If `age = 2` and `age_months` is blank, derive `age_months = 24`.
- Preserve every existing `age_months` value based on an explicit precise-age expression.
- Do not infer or change another age group under this rule.

The rule improves statistical coverage while preserving the distinction between a derived whole-year conversion and more precise source evidence. The affected-record inventory identifies derived values with `basis = derived_from_whole_completed_year_age`.
