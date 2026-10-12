# Analytical exports

## Preflight review — 2026-10-04

Rechecked 2026-10-12 with the same 40 current-query matches, two documented variants, and two starter exclusions. The [latest report](../../outputs/qa/tableau_preflight_20261012/README.md) includes 59 passed preparation assertions and exact import benchmarks. Actual Tableau import checks remain pending.

For the main interactive workbook, use the separate [local names-free practice source](../practice/README.md). These 44 files remain historical comparison snapshots. Do not join or union them together.

The [preflight audit](../../outputs/qa/tableau_preflight_20261004/README.md) compares all snapshots to current query logic using an in-memory SQLite replay, not a new MySQL execution. Forty match current queries; the allowance-No and top-30 household files match their documented variants. Two legacy files are excluded from the starter selection: `children_age_profile22082026.csv` (use the year-only clean file) and `origina_place_profile_07092026.csv` (earlier ranking without a matching current query; reproduce from person-level data if needed).

Matching the query does not make a file additive at every level. Use the top-five file without its subtotal; do not sum repeated cohort denominators, percentages, group medians, or group means. Preserve each query's age range, missing-value policy, exclusions, and percentage denominator. Follow the [calculation and publication specification](../../docs/tableau_preparation.md).

- Source table: **`sakhalin_1890_en`**
- SQL source: [`../../sql/04_analysis_queries.sql`](../../sql/04_analysis_queries.sql)
- Export dates encoded in filenames: **2026-08-22**, **2026-08-28**, **2026-09-01**, **2026-09-07**, and **2026-09-08**
- Inventory: **44 CSV files**; row counts below exclude headers.

These CSV files are static MySQL query results prepared for visualization from the 7,446-record English analytical dataset. SQL analysis and export preparation are complete; Tableau import validation and dashboard construction are the next stage. These files are CSV snapshots, not Tableau workbooks or extracts.

The SQL file contains the current analysis logic, but some exports represent earlier queries or manual variants, as noted below. When the source table or analysis logic changes, write a new dated export and reconcile its totals before using it in a visualization. Preserve earlier snapshots.

## Population and settlements

| CSV file | Rows | Contents |
|---|---:|---|
| `districts_by_population22082026.csv` | 3 | District population ranking |
| `settlements_by_population22082026.csv` | 51 | Population by settlement and district |
| `top5_by_population22082026.csv` | 5 | Five largest settlements and their shares of the complete population |
| `top5_by_population_witsubtotal_22082026.csv` | 6 | Five largest settlements plus their combined subtotal |

## Age and sex

| CSV file | Rows | Contents |
|---|---:|---|
| `age_and_sex_profile22082026.csv` | 6 | Age profile by district and sex |
| `median_age22082026.csv` | 1 | Median age of the complete population |
| `median_age_bysex22082026.csv` | 2 | Median age by sex |
| `children_age_profile_clean22082026.csv` | 36 | Child age distribution in completed years by sex, ages 0–17 |
| `children_age_profile22082026.csv` | 84 | Earlier child-age export using months for ages 0–2; superseded by the year-only export |
| `children_by_sex01092026.csv` | 2 | Male and female shares of the population aged 16 or younger |

## Legal status and literacy

| CSV file | Rows | Contents |
|---|---:|---|
| `legal_status_profile22082026.csv` | 41 | Complete legal-status distribution, including missing status |
| `legal_status_profile28082026.csv` | 4 | Four largest non-child legal-status categories |
| `legal_status_profile_share28082026.csv` | 4 | Four largest non-child legal-status categories and their shares of the complete population |
| `education_profile22082026.csv` | 8 | Literacy distribution by sex |
| `adult_education_profile2_01092026.csv` | 8 | Literacy distribution by sex for people aged 16 or older |
| `literacy_cohorts_07092026.csv` | 10 | Adult literacy by age band and sex; counts and percentages for `Literate`, `Educated`, `Illiterate`, and missing literacy |
| `literacy_occupation_08092026.csv` | 126 | Literacy counts and percentages within each recorded occupation, with missing-literacy coverage |

Despite its filename, `literacy_cohorts_07092026.csv` groups by age in 1890, not arrival year: ages 16–24, 25–34, 35–44, 45–54, and 55+. Its percentages include everyone in each age/sex group. In `literacy_occupation_08092026.csv`, literacy-category percentages use only people with recorded literacy; the missing-literacy percentage uses everyone in the occupation group. `Literate` and `Educated` remain separate categories.

## Occupation and migration

| CSV file | Rows | Contents |
|---|---:|---|
| `occupation_01092026.csv` | 50 | Fifty most frequently recorded occupations |
| `occupation_male_01092026.csv` | 5 | Five most frequently recorded male occupations |
| `occupation_female_01092026.csv` | 5 | Five most frequently recorded female occupations, excluding `Dependent on husband` and `No occupation` |
| `origin_place_01092026.csv` | 97 | Origin-place distribution excluding people recorded as born on Sakhalin |
| `origin_place_sakhalin_age01092026.csv` | 21 | Age distribution for people recorded as born on Sakhalin |
| `arrival_year_cohorts01092026.csv` | 26 | Arrival-year distribution |
| `arrival_year_1884profile01092026.csv` | 70 | Origin-place distribution for people who arrived in 1884 |
| `origina_place_profile_07092026.csv` | 20 | Ten ranked origin-place labels for each sex; earlier snapshot without a matching query in the current SQL file |
| `occupation_cohorts_07092026.csv` | 23 | Most common recorded occupation for each arrival year, with its count and share of the full arrival-year cohort |
| `Origin_diversity_08092026.csv` | 51 | Recorded origin-label diversity, origin coverage, and dominant origin by settlement |
| `Polish_profile_07092026.csv` | 29 | Settlements with recorded origins in the Kingdom of Poland under the query's 1890 geographic mapping; counts, settlement shares, and origin coverage |

`occupation_cohorts_07092026.csv` excludes missing occupations from ranking but includes them in the cohort-share denominator; arrival years with no recorded occupation are omitted. Ties resolve alphabetically, and compound occupation labels remain intact.

`Origin_diversity_08092026.csv` includes `On Sakhalin` among recorded origin labels. Dominant-origin percentages use recorded origins only; ties resolve alphabetically. Distinct-label counts describe the recorded categories, not an ethnic-diversity index.

`Polish_profile_07092026.csv` includes the general `Kingdom of Poland` label and ten governorates defined in [the historical origin reference](../../docs/reference/origin_place_reference_1890.md). Shares use the complete settlement population. Geographic origin does not establish ethnicity or modern citizenship.

## Arrival cohorts and recorded marriage

| CSV file | Rows | Contents |
|---|---:|---|
| `legal_status_arrival_07092026.csv` | 154 | Legal-status composition within each recorded arrival year, including missing legal status |
| `alone_status_arrival_07092026.csv` | 48 | Living-alone status within each recorded arrival year, including missing status |
| `marital_status_arrival_07092026.csv` | 26 | Recorded marriage on Sakhalin by arrival year, with missing marital-status counts |
| `Sakhalin_marriage_cohorts_08092026.csv` | 52 | Recorded marriage on Sakhalin by five-year arrival cohort, adult age band, and sex; shares of all group members and of those with recorded marital status |
| `legal_allowance_cohorts_07092026.csv` | 60 | Allowance counts by five-year arrival cohort and legal status; shares of all group members and of those with recorded allowance status |

Arrival-year and arrival-cohort analyses exclude missing arrival years. Legal-status and living-alone shares use everyone in the same arrival year, including people with a missing status. The annual marriage export includes all ages and uses the complete arrival-year cohort as its denominator.

Five-year cohorts are calendar-aligned (for example, 1880–1884 and 1885–1889). The final 1890–1894 label is a partial cohort observed in 1890. The adult marriage export requires age 16 or older and groups by age in 1890, not age at arrival or marriage.

Recorded Sakhalin marriages include `Married on Sakhalin`, `Married on Sakhalin; Widowed`, and `Married in homeland and on Sakhalin`. These measures describe recorded marriage history, not necessarily current marital status. Percentages ending in `_all` use every person in the group; percentages ending in `_recorded` exclude missing values for the measured status. A zero recorded-status denominator produces SQL `NULL`.

## Households

| CSV file | Rows | Contents |
|---|---:|---|
| `household_size01092026.csv` | 14 | Household-size distribution for populated household identifiers |
| `household_size_settlements01092026.csv` | 30 | Thirty largest private households with district and settlement context |
| `Lodgers_households_08092026.csv` | 48 | Private-household counts, recorded lodgers, missing household roles, and mean household sizes by settlement |

The current SQL query returns the ten largest private households. The 30-row household export is an earlier, broader snapshot.

The lodger export groups only private-household records with a populated household ID, using district, settlement, and household ID together. Its lodger percentage uses all such households in each settlement. A household with no recorded lodger may still contain people with missing roles; absence of a recorded lodger does not prove absence of lodgers.

## Allowance

| CSV file | Rows | Contents |
|---|---:|---|
| `allowance01092026.csv` | 3 | Allowance status distribution: yes, no, and not recorded |
| `allowance_by_year01092026.csv` | 22 | Arrival-year distribution for people receiving an allowance |
| `allowance_by_year_NO01092026.csv` | 26 | Arrival-year distribution for people not receiving an allowance; manual `allowance_status = 0` variant |
| `allowance_by_sex01092026.csv` | 2 | Allowance recipients and allowance rate within each sex |

## Illness and completeness

| CSV file | Rows | Contents |
|---|---:|---|
| `illness01092026.csv` | 25 | Illness-category distribution |
| `illness_2_01092026.csv` | 28 | Illness-category distribution by sex |
| `completeness_min_01092026.csv` | 10 | Ten settlements with the lowest analytical-field completion |
| `completeness_max_01092026.csv` | 10 | Ten settlements with the highest analytical-field completion |

The completeness score assesses 11 fields: legal status, age, religion, origin place, arrival year, occupation, literacy, marital status, living-alone status, allowance status, and illness.

## Queries without a corresponding export

The current SQL file also contains **Extended analysis 3: Origin concentration within settlements** and **Extended analysis 6: Private households containing multiple non-child legal statuses**. No corresponding CSV is present in this folder. Run and export these queries separately if their results are needed for the dashboard.

## Data conventions

- Blank ages are excluded from age calculations; recorded age zero remains valid.
- `NULL` represents a missing SQL value, not a category such as `No occupation`.
- `TRUE` and `FALSE` are meaningful allowance values; a blank allowance value is missing.
- Use the year-only child-age export for the current child-age visualization.
- Age thresholds differ by query: the child-age distribution covers ages 0–17, the child-sex share covers ages 0–16, and adult analyses start at age 16. Label each visualization with its actual scope.
- Aggregates have different grains and filters. Do not sum repeated cohort totals or join these files without checking the grouping keys and denominators.
- Export descriptions and row counts document the saved CSVs; they do not imply that every snapshot has been rerun against the latest SQL.
