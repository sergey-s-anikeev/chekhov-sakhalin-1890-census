"""Read-only SQL replay and independent tally for child literacy by origin."""
import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / 'data/analytical/sakhalin_1890_en_v1.csv'
sql_file = root / 'sql/12_children_literacy_by_origin.sql'
with source.open(encoding='utf-8-sig', newline='') as handle:
    records = list(csv.DictReader(handle))
db = sqlite3.connect(':memory:')
db.row_factory = sqlite3.Row
db.execute('CREATE TABLE sakhalin_1890_en(age INTEGER, origin_place TEXT, literacy TEXT)')
db.executemany('INSERT INTO sakhalin_1890_en VALUES (?,?,?)', [
    (int(r['age']) if r['age'] else None, r['origin_place'] or None,
     r['literacy'] or None) for r in records
])
queries = [part.strip() for part in re.sub(r'--[^\n]*', '', sql_file.read_text(encoding='utf-8')).split(';') if part.strip()]
assert len(queries) == 2
results = [[dict(row) for row in db.execute(query)] for query in queries]
result = results[0]
assert len(result) == 8 and len(results[1]) == 4

counts4 = Counter()
counts2 = Counter()
for r in records:
    if not r['age'] or not 0 <= int(r['age']) <= 15:
        continue
    origin = {'On Sakhalin': 'On Sakhalin', 'In transit': 'In transit',
              '': 'Origin not recorded', 'Does not remember': 'Origin unknown'
              }.get(r['origin_place'], 'Recorded origin elsewhere')
    status = {'Literate': 'literate', 'Educated': 'educated',
              'Illiterate': 'illiterate', '': 'literacy_not_recorded'
              }.get(r['literacy'], 'unexpected_literacy')
    assert status != 'unexpected_literacy'
    for scope in ('0-15', '5-15') if int(r['age']) >= 5 else ('0-15',):
        counts4[scope, origin, 'children'] += 1
        counts4[scope, origin, status] += 1
        two_group = 'On Sakhalin' if origin == 'On Sakhalin' else 'All other origin records'
        counts2[scope, two_group, 'children'] += 1
        counts2[scope, two_group, status] += 1

def pct(numerator, denominator):
    return float((Decimal(numerator) * 100 / Decimal(denominator)).quantize(
        Decimal('0.1'), rounding=ROUND_HALF_UP)) if denominator else None

for table, independent in ((result, counts4), (results[1], counts2)):
    for row in table:
        key = row['age_scope'], row['origin_group']
        for field in ('children', 'literate', 'educated', 'illiterate', 'literacy_not_recorded'):
            assert row[field] == independent[*key, field], (key, field)
        recorded = row['children'] - row['literacy_not_recorded']
        assert row['literate_pct_all'] == pct(row['literate'], row['children'])
        assert row['literate_pct_recorded'] == pct(row['literate'], recorded)
assert sum(row['children'] for row in result if row['age_scope'] == '5-15') == 536
assert sum(row['literate'] for row in result if row['age_scope'] == '5-15') == 136
assert sum(row['children'] for row in result if row['age_scope'] == '0-15') == 1467
assert sum(row['children'] for row in results[1] if row['age_scope'] == '5-15') == 536
assert sum(row['children'] for row in results[1] if row['age_scope'] == '0-15') == 1467
hashes = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in (source, sql_file)}
assert hashes['data/analytical/sakhalin_1890_en_v1.csv'] == '1b77d6330855763c54c32f21d247dc44471a69590db4fc00925c4e22eb8ac508'
out = root / 'outputs/qa/children_literacy_origin_20261027'
out.mkdir(parents=True, exist_ok=True)
(out / 'validation.json').write_text(json.dumps({
    'status': 'PASS', 'method': 'Local SQLite replay and independent CSV tally; no live MySQL execution',
    'hashes': hashes, 'four_group_rows': result, 'two_group_rows': results[1]}, indent=2) + '\n', encoding='utf-8')
print('PASS: four-group and two-group results reconcile for both age scopes.')
