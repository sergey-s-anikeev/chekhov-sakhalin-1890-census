# Visualization data

Export date: **2026-08-22**  
Source table: **`sakhalin_1890_en`**  
SQL source: [`../../sql/04_analysis_queries.sql`](../../sql/04_analysis_queries.sql)

| CSV file | SQL query |
|---|---|
| `districts_by_population22082026.csv` | District population ranking |
| `settlements_by_population22082026.csv` | Population by district and settlement |
| `top5_by_population22082026.csv` | Five largest settlements and their share of the complete population |
| `top5_by_population_witsubtotal_22082026.csv` | Five largest settlements, followed by their combined subtotal |
| `age_and_sex_profile22082026.csv` | Age and sex profile |
| `median_age22082026.csv` | Median age for the total population |
| `median_age_bysex22082026.csv` | Median age by sex |
| `children_age_profile_clean22082026.csv` | Child age distribution in completed years by sex (ages 0–17) |
| `children_age_profile22082026.csv` | Earlier child age distribution using months for ages 0–2; superseded by the clean year-only export |
| `legal_status_profile22082026.csv` | Legal-status distribution |
| `education_profile22082026.csv` | Literacy by sex |

The CSV files are exported analytical results intended for subsequent visualization. Use `children_age_profile_clean22082026.csv` for the current child-age visualization. Blank ages are excluded from median calculations; recorded age zero remains valid.
