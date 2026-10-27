"""Read-only local SQL replay and independent CSV tally for settlement literacy."""
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
sql_file = root / 'sql/11_children_literacy_by_settlement.sql'
with source.open(encoding='utf-8-sig', newline='') as handle:
    records = list(csv.DictReader(handle))
queries = [part.strip() for part in re.sub(r'--[^\n]*', '', sql_file.read_text(encoding='utf-8')).split(';') if part.strip()]
assert len(queries) == 2

db = sqlite3.connect(':memory:')
db.row_factory = sqlite3.Row
db.execute('CREATE TABLE sakhalin_1890_en(district TEXT, settlement TEXT, age INTEGER, literacy TEXT)')
db.executemany('INSERT INTO sakhalin_1890_en VALUES (?,?,?,?)', [
    (r['district'], r['settlement'], int(r['age']) if r['age'] else None, r['literacy'] or None)
    for r in records
])
results = [[dict(row) for row in db.execute(query)] for query in queries]

independent = Counter()
for r in records:
    if not r['age'] or not 5 <= int(r['age']) <= 15:
        continue
    key = (r['district'], r['settlement'])
    independent[key, 'children_5_15'] += 1
    status = r['literacy'] or 'literacy_not_recorded'
    field = {'Literate': 'literate', 'Educated': 'educated',
             'Illiterate': 'illiterate'}.get(status, status)
    if field not in ('literate', 'educated', 'illiterate', 'literacy_not_recorded'):
        field = 'other_recorded_literacy'
    independent[key, field] += 1
assert len(results[0]) == 28
for row in results[0]:
    key = (row['district'], row['settlement'])
    for field in ('children_5_15', 'literate', 'educated', 'illiterate',
                  'literacy_not_recorded', 'other_recorded_literacy'):
        assert row[field] == independent[key, field], (key, field)
    assert sum(row[field] for field in ('literate', 'educated', 'illiterate',
                                       'literacy_not_recorded', 'other_recorded_literacy')) == row['children_5_15']
    def pct(numerator, denominator):
        return float((Decimal(numerator) * 100 / Decimal(denominator)).quantize(
            Decimal('0.1'), rounding=ROUND_HALF_UP)) if denominator else None
    recorded = row['children_5_15'] - row['literacy_not_recorded']
    assert row['literate_pct_all'] == pct(row['literate'], row['children_5_15'])
    assert row['literate_pct_recorded'] == pct(row['literate'], recorded)
totals = results[1][0]
assert totals == {'children_5_15': 536, 'literate': 136, 'educated': 0,
                  'illiterate': 178, 'literacy_not_recorded': 222, 'literacy_recorded': 314}
assert sum(row['children_5_15'] for row in results[0]) == 536
hashes = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in (source, sql_file)}
assert hashes['data/analytical/sakhalin_1890_en_v1.csv'] == '1b77d6330855763c54c32f21d247dc44471a69590db4fc00925c4e22eb8ac508'
report = {'status': 'PASS', 'method': 'Local SQLite replay and independent CSV tally; no live MySQL run',
          'hashes': hashes, 'totals': totals, 'settlement_rows': len(results[0]),
          'settlements': results[0]}
out = root / 'outputs/qa/children_literacy_settlement_20261027'
out.mkdir(parents=True, exist_ok=True)
(out / 'validation.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('PASS: 28 settlement rows; 536 children; 136 Literate, 178 Illiterate, 222 missing.')
