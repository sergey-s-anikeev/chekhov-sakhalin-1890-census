"""Verify the approved children's queries locally without changing any CSV."""
import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/qa/children_0_15_20261012'
source = ROOT / 'data/analytical/sakhalin_1890_en_v1.csv'
with source.open(encoding='utf-8-sig', newline='') as stream:
    rows = list(csv.DictReader(stream))
db = sqlite3.connect(':memory:')
db.row_factory = sqlite3.Row
db.execute('CREATE TABLE sakhalin_1890_en (person_id TEXT, sex TEXT, age INTEGER)')
db.executemany('INSERT INTO sakhalin_1890_en VALUES (?, ?, ?)',
               [(r['person_id'], r['sex'], int(r['age']) if r['age'] else None) for r in rows])
def sql(path):
    return re.sub(r'--[^\n]*', '', path.read_text(encoding='utf-8-sig'))
path = ROOT / 'sql/05_children_0_15_queries.sql'
queries = [q.strip() for q in sql(path).split(';') if q.strip()]
main_text = re.sub(r'\s+', ' ', sql(ROOT / 'sql/04_analysis_queries.sql'))
assert len(queries) == 3
assert all(re.sub(r'\s+', ' ', q) in main_text for q in queries[:2])
results = [[dict(r) for r in db.execute(q)] for q in queries]
assert len(results[0]) == 32 and sum(r['children'] for r in results[0]) == 1467
assert results[1] == [dict(sex='Female', children=726, child_group_share_pct=49.5),
                      dict(sex='Male', children=741, child_group_share_pct=50.5)]
assert list(results[2][0].values()) == [7446, 1467, 726, 741, 0, 5832, 147, 204]
by_sex = Counter()
for row in results[0]:
    by_sex[row['sex']] += row['children']
assert dict(by_sex) == {'Female': 726, 'Male': 741}
changes = []
for filename, old_max in [('children_age_profile_clean22082026.csv', 17), ('children_by_sex01092026.csv', 16)]:
    with (ROOT / 'tableau/data' / filename).open(encoding='utf-8-sig', newline='') as stream:
        old_rows = list(csv.DictReader(stream))
    before = sum(int(r['children']) for r in old_rows)
    removed = [dict(person_id=r['person_id'], age=int(r['age']), sex=r['sex']) for r in rows if r['age'] and 16 <= int(r['age']) <= old_max]
    assert before - len(removed) == 1467
    changes.append(dict(file=filename, old_max_age=old_max, before=before, after=1467,
                        removed_count=len(removed), removed_records=removed))
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [source, path, ROOT / 'sql/04_analysis_queries.sql']}
assert hashes[str(source.relative_to(ROOT))] == '1b77d6330855763c54c32f21d247dc44471a69590db4fc00925c4e22eb8ac508'
report = dict(date='2026-10-12', status='PASS', definition='Children aged 0–15',
              method='SQLite local query execution and comparison; MySQL execution and CSV exports pending.',
              hashes=hashes, query_results=results, output_changes=changes, source_value_changes=0)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'validation.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
(OUT / 'README.md').write_text('''# Children aged 0–15 — validation, 2026-10-12

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
''', encoding='utf-8')
print('PASS: child queries agree; 1,467 children; 32 age rows; Female 726, Male 741; source unchanged.')
