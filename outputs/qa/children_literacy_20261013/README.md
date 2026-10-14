# Children's literacy query validation — 2026-10-13

PASS: local SQLite execution reconciles every group with an independent source tally and every age/sex total with the first dashboard's registered CSV.

- Export query returns 75 observed groups and 1,467 children (726 female; 741 male).
- Literate: 136; Educated: 0; Illiterate: 211; Not recorded: 1,120.
- Literacy recorded for 347 children; no unexpected literacy categories.
- English source SHA-256 matches the approved release; no source values changed.
- MySQL execution, CSV export and Tableau validation are still pending.

Reproduce with `python scripts/validate_children_literacy_20261013.py`. Hashes and totals are in `validation.json`.
