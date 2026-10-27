# Children’s origin by age — counts and shares

Saved 2026-10-19. Children aged 0–15, completed years, both sexes. Each percentage uses **all children of the same age**, including On Sakhalin. Total-row percentages use all 1,467 children.

Source: [approved English dataset](../data/analytical/sakhalin_1890_en_v1.csv). Reproduce both tables with [SQL queries 1 and 2](../sql/10_children_origin_age_profile.sql). Percentages are rounded independently to one decimal, so complementary shares may sum to 100.1%.

## 1. Detailed groups outside the On Sakhalin label

Cells show count (percentage of all children at that age). The displayed categories do not sum to 100% because On Sakhalin is omitted from this first table. No children have the explicit Does not remember label; SQL retains an Origin unknown control column, omitted here because every value is zero.

| Age | All children | Recorded origin elsewhere | In transit | Origin not recorded |
|---|---:|---:|---:|---:|
| 0 | 204 | 0 (0.0%) | 1 (0.5%) | 1 (0.5%) |
| 1 | 219 | 1 (0.5%) | 2 (0.9%) | 0 (0.0%) |
| 2 | 215 | 0 (0.0%) | 7 (3.3%) | 4 (1.9%) |
| 3 | 166 | 2 (1.2%) | 9 (5.4%) | 3 (1.8%) |
| 4 | 127 | 2 (1.6%) | 9 (7.1%) | 5 (3.9%) |
| 5 | 106 | 3 (2.8%) | 13 (12.3%) | 1 (0.9%) |
| 6 | 84 | 7 (8.3%) | 4 (4.8%) | 3 (3.6%) |
| 7 | 64 | 13 (20.3%) | 6 (9.4%) | 1 (1.6%) |
| 8 | 54 | 0 (0.0%) | 1 (1.9%) | 52 (96.3%) |
| 9 | 46 | 3 (6.5%) | 3 (6.5%) | 2 (4.3%) |
| 10 | 52 | 4 (7.7%) | 11 (21.2%) | 2 (3.8%) |
| 11 | 39 | 2 (5.1%) | 9 (23.1%) | 0 (0.0%) |
| 12 | 34 | 1 (2.9%) | 8 (23.5%) | 1 (2.9%) |
| 13 | 22 | 1 (4.5%) | 4 (18.2%) | 2 (9.1%) |
| 14 | 24 | 3 (12.5%) | 10 (41.7%) | 1 (4.2%) |
| 15 | 11 | 5 (45.5%) | 5 (45.5%) | 0 (0.0%) |
| **Total** | 1,467 | 47 (3.2%) | 102 (7.0%) | 78 (5.3%) |

## 2. On Sakhalin versus all other origin records

**All other origin records is not a migrant count.** It combines named origins elsewhere, In transit and missing origins (and explicit unknown origins if present). In transit does not establish birthplace; missing origin cannot establish migration. On Sakhalin is the recorded source label, not an ethnic or indigenous identity.

| Age | All children | On Sakhalin | All other origin records |
|---|---:|---:|---:|
| 0 | 204 | 202 (99.0%) | 2 (1.0%) |
| 1 | 219 | 216 (98.6%) | 3 (1.4%) |
| 2 | 215 | 204 (94.9%) | 11 (5.1%) |
| 3 | 166 | 152 (91.6%) | 14 (8.4%) |
| 4 | 127 | 111 (87.4%) | 16 (12.6%) |
| 5 | 106 | 89 (84.0%) | 17 (16.0%) |
| 6 | 84 | 70 (83.3%) | 14 (16.7%) |
| 7 | 64 | 44 (68.8%) | 20 (31.3%) |
| 8 | 54 | 1 (1.9%) | 53 (98.1%) |
| 9 | 46 | 38 (82.6%) | 8 (17.4%) |
| 10 | 52 | 35 (67.3%) | 17 (32.7%) |
| 11 | 39 | 28 (71.8%) | 11 (28.2%) |
| 12 | 34 | 24 (70.6%) | 10 (29.4%) |
| 13 | 22 | 15 (68.2%) | 7 (31.8%) |
| 14 | 24 | 10 (41.7%) | 14 (58.3%) |
| 15 | 11 | 1 (9.1%) | 10 (90.9%) |
| **Total** | 1,467 | 1,240 (84.5%) | 227 (15.5%) |

## Interpretation and validation

- At age eight, 52 of 54 children (96.3%) have no recorded origin. Source review closed on 2026-10-27: the project owner reports verifying the original records and confirming that these origins are unrecorded in the source, with the concentration at this age a coincidence rather than a processing issue. This records the owner's verification, not an independent repeat review. The other two records remain On Sakhalin (1) and In transit (1). Preserve the missing values; this pattern is not evidence of a migration peak.
- The age-15 percentages describe just 11 children. Keep counts visible when comparing small age groups.
- Each SQL result contains 16 age rows and one Total row. Exclude the Total row before summing results in Tableau to avoid double-counting.
- Local SQLite execution matches independent source tallies for every count and percentage. On 2026-10-27, the owner supplied both 17-row CSV results; [export QA](../outputs/qa/children_origin_age_export_20261027/validation.json) confirms their headers and values match the validated results. Live MySQL execution logs were not inspected. Source data were not changed.
- [QA results and hashes](../outputs/qa/children_origin_age_20261019/validation.json). Reproduce with `python scripts/validate_children_origin_age_20261019.py`.
- [Arrival/origin context and dashboard connections](arrival_children_origin.md).

## Tableau views — 2026-10-27

The owner supplied two published links: an [On Sakhalin versus all other origin records view](https://public.tableau.com/shared/ZMWP4CSS2) and the [detailed four-category dashboard](https://public.tableau.com/views/ChildrensrecordedoriginbyageSakhalin1890/Dashboard1). The corresponding saved screenshots are [two-group](../tableau/screenshots/children_origin_by_age_20261027.png) and [four-category](../tableau/screenshots/children_origin_by_age_full_20261027.png). Local inspection of both screenshots confirms an age-0–15 stacked percentage layout, age-eight missing-origin emphasis in the detailed dashboard and a displayed category note in the two-group view. The published pages and workbook connections were not independently inspected.

The detailed dashboard uses `children_origin_age_profile_20261027.csv`; it separates On Sakhalin (derived as all children minus the four other count columns), recorded origin elsewhere, In transit and origin not recorded. The explicit Origin unknown control is zero for all 16 ages and has no visible segment. The two-group view uses `children_origin_age__islanders_profile_20261027.csv`. In both views, the age-specific denominator is `all_children`; `row_type = Total` must be excluded from the age chart. The detailed screenshot states that 52 of 54 age-eight children (96.3%) have no recorded origin and warns against interpreting this as a migration peak.
