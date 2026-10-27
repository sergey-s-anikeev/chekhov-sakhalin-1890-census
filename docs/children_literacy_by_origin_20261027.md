# Children's recorded literacy by recorded origin

Prepared 2026-10-27 from the approved [English analytical dataset](../data/analytical/sakhalin_1890_en_v1.csv). Reproduce with [read-only SQL](../sql/12_children_literacy_by_origin.sql); see the [local validation](../outputs/qa/children_literacy_origin_20261027/validation.json). The principal comparison uses ages **5–15**, matching the published literacy dashboard. The 0–15 scope is shown to expose the effect of much younger children.

“On Sakhalin” and “Recorded origin elsewhere” are source-origin groupings. In transit and missing origin do not establish birthplace and remain separate. The table does not classify anyone's ethnicity or attendance at school.

## Two groups: On Sakhalin versus all other origin records

Here **all other origin records** combines named origins elsewhere (42 children), In transit (74), and missing origin (65). It is a complement to the On Sakhalin label, **not a count of children born outside the island**. Query 2 in the linked SQL reproduces these totals directly.

| Ages 5–15 | Children | Literate | Illiterate | Literacy not recorded | Literate / all | Literate / recorded literacy |
|---|---:|---:|---:|---:|---:|---:|
| On Sakhalin | 355 | 78 | 108 | 169 | 22.0% | 41.9% |
| All other origin records | 181 | 58 | 70 | 53 | 32.0% | 45.3% |
| **Total** | **536** | **136** | **178** | **222** | **25.4%** | **43.3%** |

The all-children rate is **10.0 percentage points higher** in the combined other group. But literacy is missing for 47.6% of On Sakhalin children (169/355), compared with 29.3% of the other group (53/181). Among only those with a recorded literacy status, the difference is **3.4 points** (41.9% versus 45.3%). The combined other group's 58 literate children include 10 with a named origin elsewhere, 32 In transit, and 16 with no origin recorded. It cannot support a claim that children born outside Sakhalin were more literate.

For the full ages 0–15, the corresponding all-children shares are 78/1,240 (6.3%) versus 58/227 (25.6%). This larger gap mainly reflects the concentration of ages 0–4 in the On Sakhalin group. Excluding age eight from the 5–15 comparison does not erase the pattern: 78/354 (22.0%) versus 43/128 (33.6%) of all children. These are scope checks, not adjusted effects.

## Ages 5–15: principal comparison

| Recorded origin | All children | Literate | Illiterate | Literacy not recorded | Literate / all | Literate / recorded literacy |
|---|---:|---:|---:|---:|---:|---:|
| On Sakhalin | 355 | 78 | 108 | 169 | 22.0% | 41.9% |
| Recorded origin elsewhere | 42 | 10 | 15 | 17 | 23.8% | 40.0% |
| In transit | 74 | 32 | 26 | 16 | 43.2% | 55.2% |
| Origin not recorded | 65 | 16 | 29 | 20 | 24.6% | 35.6% |
| **Total** | **536** | **136** | **178** | **222** | **25.4%** | **43.3%** |

The direct On Sakhalin/elsewhere difference is small: **1.8 percentage points** among all children, with only 42 children in the elsewhere group. Among those with a literacy entry, the order reverses slightly (41.9% versus 40.0%). Missing literacy is substantial in both groups: 169/355 (47.6%) and 17/42 (40.5%) respectively. These are descriptive differences, not evidence of an origin effect. The In transit group has a higher recorded literate share but cannot be treated as the born-elsewhere group.

## Why ages 0–15 give a different impression

| Recorded origin | All children | Literate | Illiterate | Literacy not recorded | Literate / all | Literate / recorded literacy |
|---|---:|---:|---:|---:|---:|---:|
| On Sakhalin | 1,240 | 78 | 140 | 1,022 | 6.3% | 35.8% |
| Recorded origin elsewhere | 47 | 10 | 15 | 22 | 21.3% | 40.0% |
| In transit | 102 | 32 | 27 | 43 | 31.4% | 54.2% |
| Origin not recorded | 78 | 16 | 29 | 33 | 20.5% | 35.6% |
| **Total** | **1,467** | **136** | **211** | **1,120** | **9.3%** | **39.2%** |

There are 885 On Sakhalin children aged 0–4, compared with five with a recorded origin elsewhere. No child aged 0–4 in either of these two groups is recorded Literate. Thus the much lower 0–15 share for On Sakhalin is strongly affected by age composition. The 5–15 view is more appropriate for the current literacy question, while still retaining missing literacy.

## Interpretation and next check

These results do not show a clear literacy advantage for children whose recorded origin names a place outside Sakhalin at ages 5–15. A closer comparison would inspect age and sex together, because the 42-child elsewhere group may differ in composition. None of these figures identifies school attendance or a church school. For the separate geographic hypothesis, see [literacy by settlement](children_literacy_settlements_20261027.md) and seek contemporary school-location records.

The two SQL results have eight rows for the four-group detail and four rows for the two-group summary. Both are locally validated against independent source tallies. No CSV export was created and live MySQL execution was not checked.
