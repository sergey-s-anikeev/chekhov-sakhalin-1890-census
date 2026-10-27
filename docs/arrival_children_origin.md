# Arrival cohorts and children's recorded origins

Prepared 2026-10-19. Read-only source analysis; no canonical values changed. New SQL: [`09_arrival_children_origin_queries.sql`](../sql/09_arrival_children_origin_queries.sql). Local QA: [`validation.json`](../outputs/qa/arrival_children_origin_20261019/validation.json).

## Existing results and arrival ranking

`sql/04_analysis_queries.sql` already contains annual arrival counts, exported as `tableau/data/arrival_year_cohorts01092026.csv` (26 years, chronological order). The new query 1 ranks the same counts and adds counts of people who are children at the census, not children at arrival. Exact comparison with the existing CSV passed.

| Arrival year | Recorded residents | Share of 4,826 with arrival year |
|---|---:|---:|
| 1884 | 548 | 11.4% |
| 1886 | 489 | 10.1% |
| 1885 | 474 | 9.8% |
| 1887 | 464 | 9.6% |
| 1883 | 429 | 8.9% |

Arrival year is missing for 2,620 of 7,446 people. These counts describe residents in the available census records by reported arrival year, not the original annual migration flow. They omit earlier arrivals who died, left or are outside the dataset. They do not demonstrate stable migration or births. The 1890 cohort is observed during the census year, not necessarily a full year of arrivals.

Only 42 of 1,467 children have a recorded arrival year; 1,425 lack one. One child labelled On Sakhalin also has a recorded arrival year. Preserve that combination for source review; do not infer a corrected birthplace or arrival history. Missing arrival year is not evidence of local birth. A resident's arrival year must not be assigned to their children or treated as a household/parental arrival cohort without validated relationships.

## Children's origins, ages 0–15

The existing origin-place profile excludes On Sakhalin and is all-age; the existing Sakhalin-origin age profile is also not the requested complete child-origin breakdown. New query 2 provides:

| Recorded origin group | Children | Share of all 1,467 |
|---|---:|---:|
| On Sakhalin | 1,240 | 84.5% |
| Recorded origin elsewhere | 47 | 3.2% |
| In transit | 102 | 7.0% |
| Not recorded | 78 | 5.3% |

This is a display grouping of recorded origins, not ethnic identity, indigenous status or citizenship. In transit does not specify birthplace and remains separate. The named origins elsewhere are Ust-Kara 31, Primorye Oblast 10, Irkutsk Governorate 3, and Amur Oblast, Siberia and Transbaikal Oblast one each. The source also contains Does not remember among all-age records; SQL explicitly preserves that as Origin unknown if present. None occur in this child subset. Source labels are not rewritten.

## Connect to the existing dashboards

Query 3 supplies one aggregate source with district, settlement, completed age, sex, literacy status, origin group and child count. Expected 632 rows; SUM(children) = 1,467. Local reconciliation reproduces every existing child age/sex and literacy group and all settlement child counts (including zero-child settlements by comparison).

- [Age and sex dashboard](https://public.tableau.com/views/Sakhalin1890Childrenaged015/Dashboard1): add an origin-composition sheet and, in a duplicate workbook using query 3, an Origin Group filter. Keep ages 0–15.
- [Literacy dashboard](https://public.tableau.com/views/Recordedliteracyamongchildrenaged515/Dashboard1): use query 3 with ages 5–15. Expected 536: On Sakhalin 355, elsewhere 42, In transit 74, Not recorded 65. Keep missing literacy visible and calculate percentages within the selected age/sex/origin population. Comparisons are descriptive, not causal evidence about schooling.
- [Settlement dashboard](https://public.tableau.com/views/Sakhalin1890Childrenbysettlement/Sakhalin1890Childrenbysettlement): add origin composition of children per district/settlement, using query 3. A percentage of children by origin uses the settlement's child count as denominator. This differs from the existing children/all-residents share. Query 3 contains only children and cannot supply the all-resident denominator; retain the existing settlement source for that view. Query 3 omits settlements without children, whose child-origin composition is undefined.
- Show annual arrivals as a separate context chart from the existing arrival CSV or query 1. Do not join its cohort totals to child records or infer parent-child links.

Do not join query 3 to existing aggregate charts: their counts would be repeated across finer groups. Use separate sources or a duplicated workbook rebuilt from query 3. Query 3 exports no names or person/source identifiers, but its fine grouping produces 393 one-child cells among 632 rows (and 565 rows with fewer than five children) in the current source. These cells may disclose combinations of age, sex, settlement, origin and literacy about individuals. Use this result for **local exploration**; review a coarser source with fewer dimensions and sparse-cell handling before publishing on Tableau Public. The existing dashboards have not been modified remotely.

## Execution and export

Run the new script in the existing MySQL schema. Proposed exports from this script remain unsaved: query 1 `arrival_year_ranked_20261019.csv` (26 rows), query 2 `children_origin_summary_20261019.csv` (4 rows), query 3 `children_origin_dashboard_20261019.csv` (632 rows). Query 4 is a coverage check, not a chart source. Separately, the two results of `sql/10_children_origin_age_profile.sql` were supplied on 2026-10-27 and registered in [the export inventory](../tableau/data/README.md). The current inventory is 50 CSVs.

## Age profiles saved for reference — 2026-10-19

Historical source: [Chekhov's Chapter XV extract and note 12](reference/chekhov_ch15_origin_place_ru.md) records 5,791 respondents to his province question and discusses population turnover. The supplied Russian text is preserved for future comparison; its population coverage and denominators have not yet been reconciled with this dataset.

Both requested tables, with counts and percentages of the complete same-age population, are saved in [Children’s origin by age](children_origin_age_profile.md). Their CSV results are now registered: [detailed origin groups](../tableau/data/children_origin_age_profile_20261027.csv) and [On Sakhalin versus all other origin records](../tableau/data/children_origin_age__islanders_profile_20261027.csv). Reproduce with `sql/10_children_origin_age_profile.sql`. The complement of On Sakhalin includes transit and missing origins and must not be labelled migrants. The age-eight investigation was closed on 2026-10-27 following the project owner's verification of the original records: the 52 missing origins are unrecorded in the source, and their concentration at age eight was reported as a coincidence rather than a processing issue. Missing values are retained and do not establish migration.

The owner chose to skip a numerical comparison with Chekhov's figures. The next child analysis uses [recorded literacy by settlement](children_literacy_settlements_20261027.md) to investigate a possible relationship with documented school locations; no school-type classification has been approved.

An initial [recorded literacy by origin comparison](children_literacy_by_origin_20261027.md) is now available for ages 5–15, with the 0–15 age-scope effect shown separately. Its eight-row SQL result has been locally validated but has no saved CSV export.
