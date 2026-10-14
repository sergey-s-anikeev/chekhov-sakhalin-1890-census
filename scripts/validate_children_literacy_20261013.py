"""Validate proposed literacy SQL against immutable English v1; no CSV export."""
import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'data/analytical/sakhalin_1890_en_v1.csv'
sql_path = ROOT / 'sql/06_children_literacy_queries.sql'
with source.open(encoding='utf-8-sig', newline='') as stream:
    rows = list(csv.DictReader(stream))
db = sqlite3.connect(':memory:')
db.row_factory = sqlite3.Row
db.execute('CREATE TABLE sakhalin_1890_en (age INTEGER, sex TEXT, literacy TEXT)')
db.executemany('INSERT INTO sakhalin_1890_en VALUES (?, ?, ?)', [
    (int(r['age']) if r['age'] else None, r['sex'] or None, r['literacy'] or None)
    for r in rows])
queries = [q.strip() for q in re.sub(r'--[^\n]*', '', sql_path.read_text(encoding='utf-8')).split(';') if q.strip()]
assert len(queries) == 2
results = [[dict(r) for r in db.execute(q)] for q in queries]
expected = Counter((int(r['age']), r['sex'], r['literacy'] or 'Not recorded')
                   for r in rows if r['age'] and 0 <= int(r['age']) <= 15)
actual = {(r['age'], r['sex'], r['literacy_status']): r['children'] for r in results[0]}
assert actual == expected
assert len(actual) == len(results[0])
assert list(results[1][0].values()) == [1467, 726, 741, 136, 0, 211, 1120, 0]
with (ROOT / 'tableau/data/children_age_0_15_10122026.csv').open(encoding='utf-8-sig', newline='') as stream:
    age_totals = {(int(r['age']), r['sex']): int(r['children']) for r in csv.DictReader(stream)}
collapsed = Counter()
for (age, sex, status), count in actual.items():
    collapsed[age, sex] += count
assert collapsed == age_totals
hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in [source, sql_path]}
assert hashes[source.relative_to(ROOT).as_posix()] == '1b77d6330855763c54c32f21d247dc44471a69590db4fc00925c4e22eb8ac508'
out = ROOT / 'outputs/qa/children_literacy_20261013'
out.mkdir(parents=True, exist_ok=True)
report = dict(status='PASS', date='2026-10-13', method='Local SQLite execution; live MySQL, CSV export, and Tableau validation pending.',
              hashes=hashes, export_rows=len(actual), totals=results[1][0], source_value_changes=0)
(out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
(out / 'README.md').write_text(f'''# Children's literacy query validation — 2026-10-13

PASS: local SQLite execution reconciles every group with an independent source tally and every age/sex total with the first dashboard's registered CSV.

- Export query returns {len(actual)} observed groups and 1,467 children (726 female; 741 male).
- Literate: 136; Educated: 0; Illiterate: 211; Not recorded: 1,120.
- Literacy recorded for 347 children; no unexpected literacy categories.
- English source SHA-256 matches the approved release; no source values changed.
- MySQL execution, CSV export and Tableau validation are still pending.

Reproduce with `python scripts/validate_children_literacy_20261013.py`. Hashes and totals are in `validation.json`.
''', encoding='utf-8')
print(json.dumps(report))
