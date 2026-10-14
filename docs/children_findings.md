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

## Next analysis

Compare children aged 0–15 by district using [`sql/07_children_by_district_queries.sql`](../sql/07_children_by_district_queries.sql). Show counts and the share of each district's recorded population. Include missing-age counts so readers can see the limits of the age-defined numerator. Do not interpret the share as a complete historical population estimate.
