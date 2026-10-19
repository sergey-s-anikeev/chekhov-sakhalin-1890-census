# Tableau source preparation and publication

## Current inventory — 2026-10-19

Three children's dashboards and seven screenshots are documented. Settlement dashboard: [Sakhalin 1890 — Children by settlement](https://public.tableau.com/views/Sakhalin1890Childrenbysettlement/Sakhalin1890Childrenbysettlement). The [full audit](../outputs/qa/tableau_preflight_20261019_full_inventory/README.md) covers 48 CSVs, including literacy and settlement exports: 42 current matches, four documented variants, two known legacy exclusions. Independent live settlement-filter checks remain open; URL registration does not establish those checks.

## Latest review — 2026-10-14

Owner review and screenshot corrections completed 2026-10-14. Updated single-sex screenshots confirm literacy totals of Female 274 / Male 262 and age-summary totals of Female 726 / Male 741. The displayed summary-filter checks pass. See [findings and review](children_findings.md). Workbook connection internals were not independently inspected.

Updated 2026-10-13. First dashboard: [Sakhalin 1890 — Children aged 0–15](https://public.tableau.com/views/Sakhalin1890Childrenaged015/Dashboard1). The owner reports completion and publication and supplied this URL on 2026-10-13. The earlier editor screenshot showed Female 726, Male 741 and total 1,467. The published page could not be inspected with the web retrieval tool; the later owner review and updated screenshots verify displayed layout and selected filter states; workbook source connections remain uninspected.

Next: [children’s literacy export and Tableau instructions](children_literacy_tableau.md). Decision 42 focuses the literacy visualization on ages 5–15 (536 children), using a Tableau filter; the export and overall children’s definition remain 0–15. Published literacy dashboard: [Recorded literacy among children aged 5–15](https://public.tableau.com/views/Recordedliteracyamongchildrenaged515/Dashboard1) (owner-supplied URL, 2026-10-13). The saved CSV passed local SQL reconciliation; owner review and screenshot checks were completed on 2026-10-14.

## Approved children's definition — Decision 40

Use **Children aged 0–15** (`age BETWEEN 0 AND 15`) for every output in the children's analytical block. This source-informed convention follows Chekhov's inclusion of fifteen-year-olds in Chapter XVII, rather than asserting legal adulthood at 16. Preserve zero ages and report unknown age separately; never infer age from `Child of ...` status.

The corrected queries are in `sql/04_analysis_queries.sql` and the standalone `sql/05_children_0_15_queries.sql`. Expected totals: 1,467 children, Female 726 (49.5%), Male 741 (50.5%). The registered replacement files are `children_age_0_15_10122026.csv` and `children_by_sex_0_15_10122026.csv`. Both were verified against the corrected queries on 2026-10-12; see `outputs/qa/tableau_preflight_20261012_csv_register/`. Keep previous snapshots as historical files.

The [children's validation report](../outputs/qa/children_0_15_20261012/README.md) verifies the correction locally. Earlier general preflight reports remain evidence for their recorded SQL hashes; they predate this change.

## Sources and intended use

| Source | Purpose | One row represents |
|---|---|---|
| `data/analytical/sakhalin_1890_en_v1.csv` | Approved English research master; retain names for future research | One recorded person |
| `tableau/practice/sakhalin_1890_en_no_full_name_20261004.csv` | Local Tableau practice; 7,446 rows and 22 columns | One recorded person, with full_name omitted |
| `tableau/data/*.csv` | Historical SQL results for comparison or individual charts | The grouping documented in the export inventory |

The practice copy removes only `full_name`. Every other value and the source row order remain unchanged. All IDs from P000001 through P007446 are affected by this column omission; the QA JSON enumerates them. The original English and Russian releases are unchanged. This is a local practice derivative, not an anonymized or approved public release.

Use the person-level practice source for the main interactive workbook. Do not join or union the 46 current and historical exports into that table. Specialized aggregates may be independent worksheet sources, with their own filters and denominators. Dashboard filters across independent sources require explicit mapping and testing.

## Import specification

- Import UTF-8 CSV with comma delimiter, double-quote text qualifier, and one header row.
- Set `person_id`, `source_position_id`, `person_seq`, `household_id`, and `archive_code` as dimensions. Keep identifiers as text; `person_seq` may be a whole-number dimension.
- Set `age` and `age_months` as whole numbers. Use AVG or MEDIAN for age summaries; never use SUM(age) as a resident profile statistic.
- Set `arrival_year` as a whole-number dimension. It is a historical year, not a date serial or an amount to sum.
- Set `allowance_status` as nullable Boolean; check TRUE, FALSE, and null separately.
- Keep categorical fields as text dimensions. Preserve explicit categories such as `No occupation`, `Literate`, and `Educated` without merging them.
- Blank CSV values must become null. Recorded zero age remains zero. A missing illness does not establish health; missing living-alone status does not mean living with others.
- Do not automatically assign modern geographic roles to historical place names. Use bars initially; maps require a reviewed historical coordinate lookup.

## Calculations and denominator rules

For the single person-level source, population is `COUNTD([person_id])`.

Use `AVG([age])` or `MEDIAN([age])` alongside `COUNT([age])` and a missing-age count. These exclude null age and include recorded zero.

For allowance, create a row-level indicator `IF [allowance_status] = TRUE THEN 1 ELSE 0 END`. The all-person rate is `SUM([Allowance yes]) / COUNTD([person_id])`. The recorded-status rate uses `COUNT([allowance_status])` as denominator, with an explicit zero-denominator guard returning null. Format ratios as percentages.

For a category distribution in the currently visible population, use Percent of Total with the intended partition, and test it after filtering. For a share of the entire dataset, use `COUNTD([person_id]) / MIN({ FIXED : COUNTD([person_id]) })`. Ordinary dimension filters do not change that FIXED denominator; context, data-source, and extract filters can. Label the chosen scope and test it. A top-five view must not silently redefine the denominator as the five displayed settlements.

Historical `_pct` columns contain percentage points (for example 18 means 18%, not 1800%). Divide by 100 before applying Tableau percentage formatting, or display the numeric value with a percent suffix. Never SUM these columns. Do not average group percentages to produce an overall rate: sum eligible numerators and their corresponding nonduplicated denominators, then divide.

## Resolved export traps

| Trap | Required treatment |
|---|---|
| `top5_by_population_witsubtotal_22082026.csv` contains detail and subtotal | Use the five-row file for a chart. If using the six-row file, exclude `Top 5 subtotal` from the detail view. Never sum both. |
| Repeated `cohort_people` in legal-status and living-alone exports | At one arrival year, use MIN or MAX for the displayed cohort total. Across years, obtain one denominator per year; summing repeated values or taking one overall MAX is wrong. Prefer the person-level source. |
| Precomputed medians and averages | Recalculate from people when filters change. Do not average group medians or unweighted group means. |
| Top-N files omit other categories | Label them Top 5, Top 4, Top 50, or Top 30 as applicable. Use the full source for reranking after filters and for full-population shares. |
| Female occupation export has extra exclusions | It excludes `Dependent on husband` and `No occupation`; do not present it as directly comparable to an unrestricted male ranking without explaining the scope. |
| Historical child thresholds differ | The older CSVs use 0–17 and 0–16. Replace both for current use with the approved 0–15 queries. The unchanged 16+ analyses complement the new child scope; label them Residents aged 16+. |
| Earlier child-age files | Both the mixed-unit and 0–17 year-only snapshots are historical. Use children_age_0_15_10122026.csv for the current children's block. |
| Household IDs repeat across places | Group by district, settlement, and household_id together. Exclude missing household IDs. Apply `household_type = 'Private household'` only for private-household analyses. |
| Household sizes repeated on person rows | A person-weighted mean is not an average household size. Aggregate to one row per household before averaging. |
| Household top-30 export versus SQL top-10 | Both are documented scopes. The audit checks the saved file against a LIMIT 30 variant; use the current query for a current top-10 result. |
| Missing values | Preserve nulls; display aliases may say Not recorded. Do not replace null age with zero or null allowance with FALSE. Some SQL exports use a literal NULL marker; normalize only documented missing-value columns on import. |
| Final arrival cohort | Label 1890–1894 as partial, observed in 1890. Missing arrival years are excluded. |
| Recorded marriage and origins | Sakhalin marriage measures recorded history, not necessarily current marital status. Origin labels do not establish ethnicity. |
| Missing advanced exports | Origin concentration and mixed non-child household statuses have queries but no saved CSV. Export only if needed; absence does not block the main workbook. |

The latest snapshot checks and exact import benchmarks are recorded in [the 2026-10-12 report](../outputs/qa/tableau_preflight_20261012/README.md). The 2026-10-04 report is retained as historical evidence. Checks compare values against a local SQLite replay of SQL; they do not establish a new MySQL execution or Tableau validation.

## Starter selection and decisions

| Need | Use | Decision |
|---|---|---|
| Interactive exploration | The 22-column names-free practice file | Main local source; no joins required. |
| District and settlement validation | districts_by_population22082026.csv and settlements_by_population22082026.csv | Compare counts; do not attach them to person rows. |
| Top-five chart | top5_by_population22082026.csv, or a calculation from the main source | Exclude the separate subtotal file from chart input. Retain the full-population denominator for a share of all recorded residents. |
| Child ages in years | Corrected query in sql/05_children_0_15_queries.sql | Use children_age_0_15_10122026.csv; do not substitute the old 0–17 snapshot. |
| Origin rankings by sex | Main person-level source | Earlier origina_place_profile_07092026.csv stays outside the starter selection; its original query is not established. |
| Household comparison | household_size01092026.csv | All populated composite household IDs. The private top-30 snapshot is a different scope and must be labeled separately. |

The two historical REVIEW flags are resolved for preparation by excluding those files from the starter selection. They are not claims of corrupt data or newly verified query provenance. No historical file is deleted or rewritten.

## Exact import benchmarks

These values were recalculated from approved English v1 on 2026-10-12. Check with all Tableau filters cleared unless the scope below specifies otherwise.

| Measure | Expected result |
|---|---:|
| Person rows / distinct person IDs | 7,446 / 7,446 |
| Female / Male | 2,525 / 4,921 |
| Recorded age / missing age | 7,299 / 147 |
| Recorded age zero | 204 |
| Mean recorded age | 30.9253 years (30.9 to one decimal) |
| Approved children aged 0–15 | 1,467 (Female 726; Male 741) |
| Ages 0–17 / 0–16 / 16+ | 1,545 / 1,510 / 5,832 |
| Ages 16–17 (overlap between 0–17 and 16+) | 78 |
| Composite household groups with an ID | 2,796 |
| People with / without a household ID | 7,200 / 246 |
| Allowance TRUE / FALSE / missing | 2,550 / 4,328 / 568 |
| Recorded allowance denominator | 6,878 |
| Recorded arrival year / missing | 4,826 / 2,620 |
| Top-five settlements combined | 4,046 people; 54.3379% of all 7,446 people |

Examples of errors these checks expose:

- Summing top-five details and their subtotal gives 8,092, double the correct 4,046.
- Summing the displayed rounded top-five percentages can differ from the ratio calculated from counts. Use 4,046 / 7,446 for the combined share.
- An allowance rate among all people uses 2,550 / 7,446; a rate among recorded statuses uses 2,550 / 6,878. Both can be valid, with different labels.
- The historical 0–17 and 16+ groups overlap by 78 people. Under Decision 40, use 1,467 children aged 0–15 + 5,832 residents aged 16+ + 147 missing ages = 7,446.
- Household means must use one observation per composite household. Averaging household size repeated on person rows overweights larger households.

## Person-level publication recommendation

Keep the full named English dataset for research and the future searchable-name project. Omitting `full_name` from a visualization file is sensible data minimization, but the practice copy still has `person_id`, `source_position_id`, `person_seq`, `archive_code`, and household/location detail that can link back to named records. Even removing these fields would not guarantee anonymity: rare combinations of age, occupation, origin, and settlement may identify records.

For the first public dashboard, prefer purpose-specific aggregate files containing only the dimensions, counts, and denominators needed by the charts. Exclude full names, person/source/archive identifiers, person sequence, and household identifiers from public aggregates. Review very small groups and revealing combinations, especially illness or legal-status breakdowns. Aggregation alone is not an automatic anonymity guarantee; any small-group suppression rule must be documented, including its effect on totals. No arbitrary suppression or category changes have been applied here.

Tableau Public is a publication platform. Workbooks and data published there are not private; hiding a visualization on a profile does not restrict access by URL. Download controls are not a substitute for deciding what data to publish. Remove unwanted fields from the actual export before connecting the public workbook, and do not package the research master as another data source.

The repository already contains named person-level datasets. A reduced Tableau file cannot undo exposure if those files have previously been public. Repository visibility, source reuse rights, and previous release scope have not been independently verified in this preparation stage. English analytical approval in Decision 38 is evidence of dataset approval, not proof that all external publication conditions have been reviewed.

Reference: [Tableau Public FAQ](https://help.tableau.com/current/pro/desktop/en-us/public_faq.htm), checked 2026-10-04.

## Popular first names and resident profiles

Use canonical v5's reviewed `first_name` component, linked locally by `person_id`, for a future first-name analysis. Do not take the first token of English `full_name`: the project handles different name orders and naming traditions. English first-name labels need a documented component-level transliteration and review; the existing full-name mapping alone does not establish that mapping.

Prepare a separate aggregate with sex, reviewed first-name label, and count. Report name coverage and include all tied most-common names or state an explicit tie rule. Publish no surnames, patronymics, or individual identifiers in that table. Keep the linkage and detailed research data locally.

A profile can show most common first name, mean/median recorded age, and literacy distribution for the same clearly defined population (all residents or an explicit adult age range). Label it a statistical summary, not a reconstructed person. The modal name, mean age, and modal literacy may belong to different people. If the question instead concerns residents bearing one name, calculate all statistics within that name group and state its sample size. Names and profiles are a proposed later analysis, not generated or approved by this preparation step.

## Acceptance checks still requiring Tableau

1. Confirm 7,446 people: Alexandrovsky 2,884, Tymovsky 3,242, Korsakovsky 1,320.
2. Confirm 204 recorded zero ages and missing-value/Boolean counts against the QA JSON.
3. Verify 2,796 populated household groups using the composite grouping; 246 records have no household ID.
4. Compare a literacy distribution, median age, and settlement ranking with SQL snapshots using identical scope.
5. Change district, sex, and age filters; confirm the population and percentage denominators behave as labeled. Verify top-N ranking scope.
6. Inspect the exact sources and fields in any public workbook before publication.
