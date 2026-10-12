# Tableau preflight — 2026-10-12

SQLite in-memory replay of current SQL with CONCAT/FLOOR compatibility functions. Numeric formatting and blank/NULL export markers normalized for comparison; row order ignored. MySQL collation may differ. No live MySQL or Tableau validation claimed.

## Practice-file verification

- 7,446 rows; 22 retained columns; full_name omitted for every source person.
- Exact row order and retained values preserved; zero retained-cell mismatches.
- Source hash matches the approved English release. Original source and historical CSVs are unchanged.
- audit.json records hashes, all affected IDs, missing-value counts, and snapshot differences.

## Historical export reconciliation

| File | Rows | Result | Current query |
|---|---:|---|---|
| adult_education_profile2_01092026.csv | 8 | MATCH | 15 |
| age_and_sex_profile22082026.csv | 6 | MATCH | 6 |
| allowance01092026.csv | 3 | MATCH | 29 |
| allowance_by_sex01092026.csv | 2 | MATCH | 31 |
| allowance_by_year01092026.csv | 22 | MATCH | 30 |
| allowance_by_year_NO01092026.csv | 26 | MATCH_DOCUMENTED_VARIANT | See review notes |
| alone_status_arrival_07092026.csv | 48 | MATCH | 25 |
| arrival_year_1884profile01092026.csv | 70 | MATCH | 22 |
| arrival_year_cohorts01092026.csv | 26 | MATCH | 21 |
| children_age_profile22082026.csv | 84 | REVIEW | See review notes |
| children_age_profile_clean22082026.csv | 36 | MATCH | 9 |
| children_by_sex01092026.csv | 2 | MATCH | 10 |
| completeness_max_01092026.csv | 10 | MATCH | 35 |
| completeness_min_01092026.csv | 10 | MATCH | 34 |
| districts_by_population22082026.csv | 3 | MATCH | 5 |
| education_profile22082026.csv | 8 | MATCH | 14 |
| household_size01092026.csv | 14 | MATCH | 27 |
| household_size_settlements01092026.csv | 30 | MATCH_DOCUMENTED_VARIANT | See review notes |
| illness01092026.csv | 25 | MATCH | 32 |
| illness_2_01092026.csv | 28 | MATCH | 33 |
| legal_allowance_cohorts_07092026.csv | 60 | MATCH | 37 |
| legal_status_arrival_07092026.csv | 154 | MATCH | 23 |
| legal_status_profile22082026.csv | 41 | MATCH | 11 |
| legal_status_profile28082026.csv | 4 | MATCH | 12 |
| legal_status_profile_share28082026.csv | 4 | MATCH | 13 |
| literacy_cohorts_07092026.csv | 10 | MATCH | 36 |
| literacy_occupation_08092026.csv | 126 | MATCH | 43 |
| Lodgers_households_08092026.csv | 48 | MATCH | 40 |
| marital_status_arrival_07092026.csv | 26 | MATCH | 24 |
| median_age22082026.csv | 1 | MATCH | 7 |
| median_age_bysex22082026.csv | 2 | MATCH | 8 |
| occupation_01092026.csv | 50 | MATCH | 16 |
| occupation_cohorts_07092026.csv | 23 | MATCH | 26 |
| occupation_female_01092026.csv | 5 | MATCH | 18 |
| occupation_male_01092026.csv | 5 | MATCH | 17 |
| Origin_diversity_08092026.csv | 51 | MATCH | 39 |
| origin_place_01092026.csv | 97 | MATCH | 19 |
| origin_place_sakhalin_age01092026.csv | 21 | MATCH | 20 |
| origina_place_profile_07092026.csv | 20 | REVIEW | See review notes |
| Polish_profile_07092026.csv | 29 | MATCH | 44 |
| Sakhalin_marriage_cohorts_08092026.csv | 52 | MATCH | 42 |
| settlements_by_population22082026.csv | 51 | MATCH | 1 |
| top5_by_population22082026.csv | 5 | MATCH | 3 |
| top5_by_population_witsubtotal_22082026.csv | 6 | MATCH | 4 |

## Review notes

- 40 snapshots match current SQL values; two match the documented allowance-No and top-30-household variants.
- The older mixed-unit child-age file is excluded in favor of children_age_profile_clean22082026.csv.
- The earlier origina_place_profile_07092026.csv ranking is excluded from starter sources because it has no matching current query.
- All historical snapshots are preserved. Current-match status does not establish that subtotals, percentages, or repeated denominators are additive.
- Tableau runtime and live MySQL checks were not performed.

## Reproduction

Run scripts/build_tableau_practice_20261004.mjs with the bundled node_modules path, then scripts/audit_tableau_exports_20261004.py. The builder refuses to overwrite a different versioned practice file.

## Import benchmarks

All 59 preparation assertions passed. Actual Tableau testing remains pending.

| Scope | Expected values |
|---|---|
| population_by_sex | sex=Female, people=2525; sex=Male, people=4921 |
| age | recorded_age=7299, missing_age=147, age_zero=204, mean_age=30.9253 |
| age_scope | ages_0_17=1545, ages_0_16=1510, ages_16_plus=5832, overlapping_ages_16_17=78 |
| households | household_groups=2796, people_with_household_id=7200 |
| allowance | yes=2550, no=4328, missing=568, recorded=6878 |
| top_five | people=4046, share_of_all_pct=54.337899543378995 |
| arrival | recorded=4826, missing=2620 |

Repeat this dated audit with `python scripts/audit_tableau_exports_20261004.py --date 2026-10-12`. The report is tied to the hashes in audit.json.
