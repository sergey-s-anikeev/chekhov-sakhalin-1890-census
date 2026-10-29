# Recorded adult literacy by sex

Completed 2026-10-29. [Published dashboard](https://public.tableau.com/views/Sakhalin1890Recordedadultliteracybysex/Sakhalin1890Recordedadultliteracybysex), owner-supplied URL. [Saved screenshot](../tableau/screenshots/adult_literacy_by_sex_20261029.png), inspected locally.

Source: [adult literacy export](../tableau/data/adult_education_profile2_01092026.csv). Adults here means recorded age 16+, the project's analytical threshold. Missing ages are excluded. Three panels show counts, shares of all adults within each sex, and shares among adults with recorded literacy within each sex. Educated is kept separate from Literate.

| Recorded literacy | Female | Male |
|---|---:|---:|
| Literate | 162 | 1,356 |
| Educated | 4 | 19 |
| Illiterate | 1,413 | 2,091 |
| Not recorded | 183 | 604 |
| **All adults** | **1,762** | **4,070** |
| **With recorded literacy** | **1,579** | **3,466** |

There are 5,832 adults; literacy is missing for 787 (13.5%). The Literate shares among all adults are Female 9.2% and Male 33.3%; excluding missing literacy changes them to 10.3% and 39.1%. The recorded-only denominator still includes Educated. Percentages are rounded independently.

These are descriptive differences in the available records. Missing literacy does not establish illiteracy, and recorded literacy does not establish school attendance. Comparisons do not adjust for differences in age, legal status or other composition.

Local screenshot inspection confirms the three panels, key counts and percentages, consistent category colors, retained Educated segments and the missingness/school-attendance explanation. Live workbook source connections and tooltips were not independently inspected. Item 4 of the [Tableau plan](tableau_visualization_action_plan.md) is complete; item 5, recorded arrival years, is next.
