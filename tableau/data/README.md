# Analytical exports

- Source table: **`sakhalin_1890_en`**
- SQL source: [`../../sql/04_analysis_queries.sql`](../../sql/04_analysis_queries.sql)
- Export dates: **2026-08-22**, **2026-08-28**, and **2026-09-01**

These CSV files are static MySQL query results prepared for visualization. Re-run the corresponding SQL query and replace the export when the source table or analysis logic changes.

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

## Households

| CSV file | Rows | Contents |
|---|---:|---|
| `household_size01092026.csv` | 14 | Household-size distribution for populated household identifiers |
| `household_size_settlements01092026.csv` | 30 | Thirty largest private households with district and settlement context |

The current SQL query returns the ten largest private households. The 30-row household export is an earlier, broader snapshot.

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

## Data conventions

- Blank ages are excluded from age calculations; recorded age zero remains valid.
- `NULL` represents a missing SQL value, not a category such as `No occupation`.
- `TRUE` and `FALSE` are meaningful allowance values; a blank allowance value is missing.
- Use the year-only child-age export for the current child-age visualization.
