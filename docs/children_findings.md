# Children's dashboards: findings and review

Recorded 2026-10-14. Scope describes this project's available records, not a complete estimate of Sakhalin's historical population.

## Age and sex, ages 0–15

The dataset contains 1,467 children aged 0–15: 726 female (49.5%) and 741 male (50.5%). Missing ages are excluded; age zero is retained. Counts are concentrated at younger ages. The chart alone cannot explain that pattern or establish mortality, migration or birth-rate trends.

## Recorded literacy, ages 5–15

Among 536 children aged 5–15, 136 are recorded as Literate (25.4%), 178 as Illiterate (33.2%) and 222 have no recorded literacy (41.4%). No children in this subset have the separate Educated category. Among the 314 with recorded literacy, 43.3% are recorded as Literate; this is a different denominator and must not be presented as the share of all children.

One boy aged five and one aged six are recorded as Literate. These observations motivated including ages five and six. Literacy does not establish school attendance, and missing literacy does not establish illiteracy. Small age groups and varying recording coverage limit age/sex comparisons.

## Screenshot review — 2026-10-14

The owner reported reviewing both published dashboards and saved six PNG screenshots in [`tableau/screenshots/`](../tableau/screenshots/). Local visual inspection confirmed:

- Age dashboard total view: 1,467, with Female 726 and Male 741.
- Literacy dashboard total view: 536; displayed age range 5–15; missing literacy remains visible; percentage bars reach 100%.
- Both dashboards have separate female and male screenshots, showing that their charts respond to sex selection.
- Initial review found summaries did not follow sex selection. The owner corrected the dashboards and replaced the screenshots on 2026-10-14.
- Updated literacy screenshots show Female 274 and Male 262; the total view shows 536.
- Updated age screenshots show Female 726 and Male 741 in both chart and summary; the total view shows 1,467.

The owner review and displayed summary-filter acceptance checks are complete. Screenshots establish displayed states, not every possible live interaction or the contents of workbook connections. The current PNGs are the corrected versions; the initial review findings are retained in this narrative.

## Settlement distribution, ages 0–15

Added 2026-10-19, using the [validated settlement export](../tableau/data/children_by_settlement_20261014.csv).

The 1,467 recorded children are distributed across 51 settlement groups. Seven groups contain no recorded children; this describes the available records, not proof that no children lived in those places. Grouping uses district and settlement together.

Rykovskoe has the largest child count: 363 among 1,266 recorded people (28.7%). Alexandrovsky Post has a larger recorded population, 1,338, but fewer children: 236 (17.6%). Thus, a larger settlement population does not necessarily imply either more children or a higher child share.

Child counts and shares answer different questions. Arkovo III has 15 children among only 35 recorded people (42.9%), compared with Rykovskoe's 363 among 1,266 (28.7%). Arkovo III's higher proportion describes a much smaller group; population denominators should accompany comparisons of shares.

These percentages include all recorded people in each settlement, including missing ages. Across the full dataset 147 people have missing ages; they cannot be classified into the age-defined child numerator. Missing-age coverage and the availability of records can affect comparisons.

Earlier settlement establishment is a hypothesis for subsequent historical investigation, not a demonstrated cause of higher child shares. No founding-date comparison has been performed. Settlement function, migration and population composition are other questions to examine before explaining the pattern.

## Next analysis

The project owner decided on 2026-10-27 to skip a numerical comparison with Chekhov's published figures. Historical passages remain as contextual source references. The current analytical question is whether recorded child literacy varies by settlement and how any variation relates to documented school locations. See the [preliminary settlement literacy check](children_literacy_settlements_20261027.md). Settlement-founding-date research remains pending.

On 2026-10-19, the [Chapter XIX schools and literacy reference](reference/chekhov_ch19_schools_literacy.md) was added with the Russian original, bibliographic citation, an English working translation and details of a published English edition. Its all-age sex-specific literacy rates, children's origin-specific rates and school enrolment figures use different populations. Statistical reconciliation and verification of the published English passage remain pending.

## Arrival and origin follow-up — 2026-10-19

See [arrival cohorts and child origins](arrival_children_origin.md) for existing-query reuse, verified counts and connections to the age, literacy and settlement dashboards. Among ages 0–15, 1,240 records say On Sakhalin, 47 name origins elsewhere, 102 say In transit and 78 have no recorded origin. In transit remains separate; origin is not an islander identity. Only 42 children have a recorded arrival year, so arrival-cohort analysis cannot describe all children or establish parental migration timing.

The [age-specific origin tables](children_origin_age_profile.md) preserve both detailed categories and the On Sakhalin/complement comparison, with reproducible SQL. At age eight, 52 of 54 records lack origin. On 2026-10-27, the project owner reported verifying the original records: these origins are unrecorded in the source, and the concentration at this age is a coincidence rather than a processing issue. The investigation is closed on that basis. Missing origins remain unchanged and must not be interpreted as a migration peak.

The owner published a [detailed origin-by-age dashboard](https://public.tableau.com/views/ChildrensrecordedoriginbyageSakhalin1890/Dashboard1) and an [earlier two-group origin view](https://public.tableau.com/shared/ZMWP4CSS2) on 2026-10-27. Both screenshots are saved and were visually inspected; the detailed chart keeps elsewhere, In transit and missing origins separate and includes the age-eight note. See the [Tableau view record](children_origin_age_profile.md#tableau-views--2026-10-27). Live workbook connections were not independently inspected.

The [literacy-by-origin check](children_literacy_by_origin_20261027.md) compares ages 5–15: 78 of 355 children labelled On Sakhalin and 10 of 42 with a named origin elsewhere are recorded Literate (22.0% and 23.8% of all children in each group). Among children with recorded literacy, the shares are 41.9% and 40.0%; missing literacy and the small elsewhere group limit inference. In transit and missing origins remain separate. No school-attendance conclusion follows.

A requested two-group display combines every other origin record: On Sakhalin 78/355 (22.0%) versus the complement 58/181 (32.0%) recorded Literate among ages 5–15. The complement includes 74 In transit and 65 missing-origin children; it is not a born-outside group. Literacy coverage differs, reducing the recorded-only rate gap to 41.9% versus 45.3%. See the same [origin comparison](children_literacy_by_origin_20261027.md) for counts and the 0–15 scope check.
