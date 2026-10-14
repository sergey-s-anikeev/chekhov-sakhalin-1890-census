# Children by settlement

Prepared 2026-10-14 at the owner's request. Scope: ages 0–15 (Decision 40), not the literacy-specific 5–15 subset. District is contextual grouping/filtering; the unit of analysis is district plus settlement.

## Question and interpretation

Where are recorded children concentrated, and how much of each settlement's recorded population do they represent?

Distinguish child count from child share. Large settlements need not have larger shares. The owner's hypothesis that earlier settlement establishment contributes to higher child shares is recorded for investigation, not established by these census results. Testing it requires sourced establishment dates and attention to settlement function, migration, sex/age composition and record coverage. Arrival year of a resident is not a settlement founding date.

## Export

Run [`sql/08_children_by_settlement_queries.sql`](../sql/08_children_by_settlement_queries.sql) in the existing MySQL schema and save the result with UTF-8 headers as `tableau/data/children_by_settlement_20261014.csv`.

Expected: 51 rows, one per district/settlement combination; 7,446 people, 1,467 children (726 female, 741 male), 147 missing ages. Retain the seven settlements with zero recorded children. The saved export was registered and matched exactly to validated SQL results on 2026-10-14; inventory now contains 48 CSVs. See `outputs/qa/children_settlements_20261014/export_validation.json`.

Local checks passed: [`validation.json`](../outputs/qa/children_settlements_20261014/validation.json). Reproduce with `scripts/validate_children_settlements_20261014.py`. This is SQLite validation, not a live MySQL execution log.

## Suggested dashboard

- Horizontal bars: settlement versus number of children, sorted descending; use district as color or filter. Initially show all settlements, with scrolling if needed.
- Second view: settlement versus child share, with child and population counts in the tooltip. Small settlements can have high shares based on few records; avoid interpreting rank alone.
- Optional scatterplot for the size hypothesis: recorded settlement population on X, child share on Y, one point per district/settlement. This assesses association with size, not establishment date or causation.
- Use a label combining settlement and district to avoid merging identically named places. Do not join this aggregate to the earlier age/literacy files.

For percentages, prefer a calculated ratio `SUM([children]) / SUM([settlement_people])` formatted as a percentage. This works for both a settlement and a selected district summary. Do not sum or average the exported percentage column. Its values are already on a 0–100 scale.

The main denominator includes all recorded people, including missing ages. The alternative `children_share_known_age_pct` uses only recorded ages; label it explicitly if used. Show `age_not_recorded` in the tooltip. A zero child count means no children recorded in the available dataset, not proof none lived there.

## Benchmarks: five largest child counts

| Settlement | District | Children | Recorded people | Child share |
|---|---|---:|---:|---:|
| Rykovskoe | Tymovsky | 363 | 1,266 | 28.7% |
| Alexandrovsky Post | Alexandrovsky | 236 | 1,338 | 17.6% |
| Derbinskoe | Tymovsky | 142 | 632 | 22.5% |
| Novo-Mikhaylovskoe | Alexandrovsky | 113 | 446 | 25.3% |
| Korsakovskoe | Alexandrovsky | 83 | 260 | 31.9% |

Keep the existing district-only query as a reference; it is no longer the next planned dashboard. No source records, categories or existing CSVs were changed.

## Completion — 2026-10-14

The owner reported completion and saved `tableau/screenshots/children_by_settlement_20261014.png`. Local inspection confirms distinct count/share titles, aligned settlement order, one District filter, a color legend and the denominator note. The saved CSV has 51 rows covering 7,446 people and 1,467 children. Public URL receipt and independent live filter checks remain pending; a screenshot alone cannot verify filter behavior.
