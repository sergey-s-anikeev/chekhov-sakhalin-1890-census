# Children aged 0–15 — validation, 2026-10-12

All checks passed using local SQLite execution. Live MySQL execution, result exports, and Tableau checks remain pending.

- Both child queries in the main SQL file match the separate correction script exactly apart from whitespace.
- Age distribution: 32 rows, total 1,467 children.
- Sex distribution: Female 726 (49.5%); Male 741 (50.5%). The two output totals reconcile.
- Ages 16+: 5,832; missing age: 147. These plus children equal 7,446 without overlap.
- All 204 recorded zero ages remain included.
- Previous age output: 1,545 → 1,467 (78 records excluded from the result).
- Previous sex output: 1,510 → 1,467 (43 records excluded from the result).
- No source values or historical CSV files were changed. Source hash still matches the approved release.

`validation.json` includes exact affected person IDs, all query results, before/after counts, and hashes. Run `python scripts/validate_children_0_15_20261012.py` to reproduce.
