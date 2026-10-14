# Children's recorded literacy visualization

## Latest review — 2026-10-14

Owner review and screenshot corrections completed 2026-10-14. Updated single-sex screenshots confirm literacy totals of Female 274 / Male 262 and age-summary totals of Female 726 / Male 741. The displayed summary-filter checks pass. See [findings and review](children_findings.md). Workbook connection internals were not independently inspected.

Published dashboard: [Recorded literacy among children aged 5–15](https://public.tableau.com/views/Recordedliteracyamongchildrenaged515/Dashboard1). URL supplied by the owner on 2026-10-13. The web retrieval tool could not inspect the page; the later screenshot review confirms the displayed layout, selected filter states and percentage bars; live interactions were reviewed by the owner. The saved 75-row CSV has been verified against SQL; see [export QA](../outputs/qa/children_literacy_export_20261013/validation.json).

Updated 2026-10-13. Export scope: Children aged 0–15 (Decision 40). Visualization scope: ages 5–15 inclusive (Decision 42). Retain the full export and filter the literacy sheets in Tableau. This includes the one recorded literate child at age five and the one at age six, without asserting a historical school-entry rule.

## Export from MySQL

1. Open [`sql/06_children_literacy_queries.sql`](../sql/06_children_literacy_queries.sql) in Workbench and select the existing project schema.
2. Run query 2 to check totals against the table below.
3. Run query 1 and export only that result, with column headers and UTF-8 encoding, to `tableau/data/children_literacy_age_sex_20261013.csv`.
4. Expect 75 data rows and four columns: `age`, `sex`, `literacy_status`, `children`. Their summed count must be 1,467. Count people with SUM(children), never the number of CSV rows.

| Recorded literacy | Children | Share of all 1,467 children |
|---|---:|---:|
| Literate | 136 | 9.3% |
| Educated | 0 | 0.0% |
| Illiterate | 211 | 14.4% |
| Not recorded | 1,120 | 76.3% |
| Total | 1,467 | 100.0% |

There are 726 female and 741 male children. Literacy is recorded for 347 children (23.7%). These are source-record categories, not inferred school attendance. Blank literacy does not establish illiteracy, even at young ages. Keep Literate and Educated separate; the latter has no observed child records and will not appear in the export. The query emits observed combinations only. Missing ages are excluded; age zero is retained.

The [local QA report](../outputs/qa/children_literacy_20261013/README.md) verifies all 75 groups and reconciles each age/sex total to the first dashboard's CSV. This is SQLite validation of the supplied SQL, not evidence of a live MySQL run or an exported file.

## Build in Tableau Public's browser editor

Create a new visualization and upload this single aggregate CSV. Do not join it to the age-only CSV: each age/sex count is now split into literacy categories, so a join could repeat the earlier counts.

1. Set Age to a whole-number dimension and use **Discrete** (blue) on Columns, sorted ascending. Add Age to Filters and select 5–15 inclusive.
2. Put **SUM(Children)** on Rows; select Bars.
3. Put **Literacy Status** on Color, using a neutral gray for Not recorded. Ensure **Analysis > Stack Marks > On**.
4. Put **Sex** on Filters and show the filter, initially selecting both sexes.
5. Title the sheet **Recorded literacy among children aged 5–15**.
6. Add a separate text sheet using SUM(Children). Apply both Age and Sex filters to all related literacy sheets using the same data source. With ages 5–15 and both sexes selected, the total must be **536**. The unfiltered export still totals 1,467. Keep the first age-distribution dashboard at 0–15.

For a percentage view, duplicate the count sheet. On SUM(Children), choose **Quick Table Calculation > Percent of Total**, then **Edit Table Calculation > Specific Dimensions**. Check only **Literacy Status**; leave Age unchecked. This calculates within each age, not across all ages. If Sex is also placed in the view, leave it unchecked to calculate separately within each age/sex group. Each stacked bar should total 100%. Keep the original count chart or counts in tooltips so small groups remain visible.

Do not filter out Not recorded in the main view: that would change the denominator to recorded literacy only. For ages 5–15, a separately labelled recorded-only analysis would use 314 children; 136/314 = 43.3% describes the recorded subset, not all children’s literacy. The earlier full-export benchmarks (347 recorded among ages 0–15) do not apply to the filtered chart. Avoid interpreting missing records as a random sample.

Reference: [Tableau table calculations and Specific Dimensions](https://help.tableau.com/current/pro/desktop/en-gb/calculations_tablecalculations.htm), checked 2026-10-13.

## Finish and record

- First validate the full export against the 0–15 table above. Then check the filtered 5–15 chart: Female 274, Male 262, total 536; Literate 136, Educated 0, Illiterate 178, Not recorded 222. Literacy recorded: 314. These filtered benchmarks were tallied from the approved English source on 2026-10-13.
- Compare each age's total with the first age dashboard; adding literacy must not change the population.
- Add the note: **Ages 5–15 inclusive. Missing ages excluded. Missing literacy shown separately; no literacy status inferred.**
- Completed 2026-10-13: registered the 75-row literacy CSV and its SHA-256 after exact SQL reconciliation. The inventory now contains 47 files.
- Completed 2026-10-13: owner supplied the published dashboard URL recorded above. Published-view checks remain open.
