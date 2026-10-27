# Recorded child literacy by settlement: preliminary school-location check

Prepared 2026-10-27. The question is whether literate children aged 5–15 are concentrated in settlements with schools, especially schools run by the church. This is a **preliminary descriptive check**, not evidence of where children learned to read or attended school.

## Existing output files

The saved child CSVs in [`tableau/data/`](../tableau/data/README.md) include age/sex, sex totals, literacy by age/sex, child counts by settlement, and now two child-origin-by-age tables. The existing arrival-year and origin-place CSVs are all-age analyses and do not provide children's origins by settlement. The [new arrival and child-origin SQL](../sql/09_arrival_children_origin_queries.sql) was locally validated, but its proposed CSV results have **not** been saved or registered. The two results of [origin-by-age SQL](../sql/10_children_origin_age_profile.sql) were registered on 2026-10-27 after exact comparison. The Tableau inventory now contains 50 CSV files.

The saved literacy and settlement CSVs cannot be combined to recover literacy by settlement: each omits the other's grouping. The approved [person-level English dataset](../data/analytical/sakhalin_1890_en_v1.csv) was therefore used for this read-only cross-tabulation. The reusable [settlement literacy SQL](../sql/11_children_literacy_by_settlement.sql) returns one row per district/settlement; query 2 checks totals. It has been replayed locally, but has not been run in live MySQL and no Tableau export has been created.

The more detailed [children's origin dashboard query](../sql/09_arrival_children_origin_queries.sql) can combine origin, literacy and location during local exploration. It is unnecessary for this settlement-only literacy check. Its 632 cells include 393 single-child cells, so publishing the full result would require a separate disclosure review and likely coarser aggregation.

## What the records show

Among 536 children aged 5–15 in 28 settlement groups, 136 are recorded Literate, 178 Illiterate, and 222 have no recorded literacy. The six settlements with at least 20 children contain 418 of 536 children and 121 of 136 recorded literate children. Large child populations account for much of this concentration. The rates below use **all children** in the settlement; the final column uses only children with a recorded literacy status.

| District / settlement | Children 5–15 | Literate | Illiterate | Not recorded | Literate / all | Literate / recorded |
|---|---:|---:|---:|---:|---:|---:|
| Tymovsky / Rykovskoe | 156 | 32 | 85 | 39 | 20.5% | 27.4% |
| Alexandrovsky / Korsakovskoe | 53 | 21 | 17 | 15 | 39.6% | 55.3% |
| Alexandrovsky / Alexandrovsky Post | 72 | 19 | 11 | 42 | 26.4% | 63.3% |
| Tymovsky / Malo-Tymovo | 32 | 18 | 6 | 8 | 56.3% | 75.0% |
| Alexandrovsky / Novo-Mikhaylovskoe | 58 | 17 | 16 | 25 | 29.3% | 51.5% |
| Tymovsky / Derbinskoe | 47 | 14 | 12 | 21 | 29.8% | 53.8% |
| **These six combined** | **418** | **121** | **147** | **150** | **28.9%** | **45.1%** |
| **Other 22 groups** | **118** | **15** | **31** | **72** | **12.7%** | **32.6%** |
| **All groups** | **536** | **136** | **178** | **222** | **25.4%** | **43.3%** |

Percentages among only children with recorded literacy are sensitive to missingness: for example, 42 of 72 children at Alexandrovsky Post lack a literacy entry. Age and sex composition can also differ by settlement. The six-group threshold is a descriptive display choice, not a school classification or a significance test. Small settlement rates are particularly unstable; all 28 rows are available in the [local QA result](../outputs/qa/children_literacy_settlement_20261027/validation.json).

## What is known about schools

- Chekhov reports a school at **Rykovskoe** in [Chapter X](https://ru.wikisource.org/wiki/Остров_Сахалин_(Чехов)/Глава_10), and a school and chapel at **Korsakovskoe** in his [description of the northern settlement](https://ru.wikisource.org/wiki/Остров_Сахалин_(Чехов)/Версия_2). Korsakovskoe in Alexandrovsky District is distinct from Korsakovsky Post in Korsakovsky District.
- [Chapter XIX](https://ru.wikisource.org/wiki/Остров_Сахалин_(Чехов)/Глава_19) says Derbinskoe's school held no classes in 1889–90 because it lacked a teacher. Yet 14 resident children aged 5–15 there are recorded Literate. These records cannot identify where or when they learned to read.
- Chapter XIX mentions priests' school activities, while also saying district chiefs and prison superintendents effectively ran the schools and exiles taught in them. These sources do **not** establish that each named school was a church or parish school. The project's census table has no school, enrolment, teacher, or attendance field.

## Next evidence needed

Locate an 1889–90 school register or contemporary school report with **settlement, operating dates, governing body, teacher, and pupils**. Match its settlement names to the census without assuming that church or chapel presence means a church school. Then compare school and non-school settlements with the same age range, show recorded and missing literacy separately, and inspect age/sex mix. Even a geographic association would not identify a child's school or prove a causal effect of schooling.

## Validation and export status

The local [QA report](../outputs/qa/children_literacy_settlement_20261027/validation.json) replays both SQL queries in SQLite and independently counts the approved CSV: 28 settlement groups, 536 children, and the expected literacy totals all match. The source dataset hash is checked. Run the SQL in MySQL before treating a saved CSV as a MySQL result; if exported for Tableau, register its filename, row count, scope and hash in the export inventory. The 48 existing CSVs and canonical data are unchanged.
