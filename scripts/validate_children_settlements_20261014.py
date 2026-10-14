"""Validate settlement SQL locally without exporting or modifying source data."""
import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'data/analytical/sakhalin_1890_en_v1.csv'
query = ROOT / 'sql/08_children_by_settlement_queries.sql'
with source.open(encoding='utf-8-sig', newline='') as f:
    records = list(csv.DictReader(f))
db = sqlite3.connect(':memory:')
db.row_factory = sqlite3.Row
db.execute('CREATE TABLE sakhalin_1890_en(district TEXT, settlement TEXT, age INTEGER, sex TEXT)')
db.executemany('INSERT INTO sakhalin_1890_en VALUES (?,?,?,?)', [
    (r['district'], r['settlement'], int(r['age']) if r['age'] else None, r['sex']) for r in records])
rows = [dict(r) for r in db.execute(re.sub(r'--[^\n]*', '', query.read_text(encoding='utf-8')))]
expected_people = Counter((r['district'], r['settlement']) for r in records)
expected_children = Counter((r['district'], r['settlement']) for r in records if r['age'] and 0 <= int(r['age']) <= 15)
assert len(rows) == len(expected_people) == 51
for r in rows:
    key = (r['district'], r['settlement'])
    assert r['settlement_people'] == expected_people[key]
    assert r['children'] == expected_children[key]
    assert r['children'] == r['female_children'] + r['male_children']
    assert r['children'] + r['residents_16_plus'] + r['age_not_recorded'] == r['settlement_people']
    assert r['age_recorded'] + r['age_not_recorded'] == r['settlement_people']
    assert abs(r['children_share_settlement_pct'] - 100*r['children']/r['settlement_people']) <= 0.051
for field, total in [('settlement_people',7446),('children',1467),('female_children',726),('male_children',741),('age_not_recorded',147)]:
    assert sum(r[field] for r in rows) == total
hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in [source, query]}
assert hashes[source.relative_to(ROOT).as_posix()] == '1b77d6330855763c54c32f21d247dc44471a69590db4fc00925c4e22eb8ac508'
out = ROOT / 'outputs/qa/children_settlements_20261014'
out.mkdir(parents=True, exist_ok=True)
(out / 'validation.json').write_text(json.dumps(dict(status='PASS', method='Local SQLite replay and independent source tallies; MySQL CSV export pending.', hashes=hashes, results=rows), indent=2)+'\n', encoding='utf-8')
print(json.dumps(dict(status='PASS', rows=len(rows), top_by_count=rows[:5], zero_child_settlements=sum(r['children']==0 for r in rows)), indent=2))
