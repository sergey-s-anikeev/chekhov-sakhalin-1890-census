"""Validate two age-origin SQL tables and write their documentation and QA."""
import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'data/analytical/sakhalin_1890_en_v1.csv'
sql = ROOT / 'sql/10_children_origin_age_profile.sql'
with source.open(encoding='utf-8-sig', newline='') as f:
    records = list(csv.DictReader(f))
db = sqlite3.connect(':memory:')
db.row_factory = sqlite3.Row
db.execute('CREATE TABLE sakhalin_1890_en(age INTEGER, origin_place TEXT)')
db.executemany('INSERT INTO sakhalin_1890_en VALUES (?,?)', [
    (int(r['age']) if r['age'] else None, r['origin_place'] or None) for r in records])
queries = [q.strip() for q in re.sub(r'--[^\n]*', '', sql.read_text(encoding='utf-8')).split(';') if q.strip()]
assert len(queries) == 2
results = [[dict(r) for r in db.execute(q)] for q in queries]
counts = Counter()
for r in records:
    if not r['age'] or not 0 <= int(r['age']) <= 15:
        continue
    origin = r['origin_place']
    category = {'On Sakhalin': 'on_sakhalin', 'In transit': 'in_transit',
                '': 'origin_not_recorded', 'Does not remember': 'origin_unknown'}.get(origin, 'origin_elsewhere')
    for age in (int(r['age']), None):
        counts[age, 'all_children'] += 1
        counts[age, category] += 1
def pct(n, d):
    return float((Decimal(n) * 100 / Decimal(d)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
assert all(len(t) == 17 and [r['age'] for r in t] == list(range(16)) + [None] for t in results)
for r in results[0]:
    a, n = r['age'], r['all_children']
    assert n == counts[a, 'all_children']
    for field in ('origin_elsewhere', 'in_transit', 'origin_not_recorded', 'origin_unknown'):
        assert r[field] == counts[a, field]
        assert r[field + '_pct'] == pct(r[field], n)
for r in results[1]:
    a, n = r['age'], r['all_children']
    assert n == counts[a, 'all_children']
    assert r['on_sakhalin'] == counts[a, 'on_sakhalin']
    assert r['all_other_origins'] == n - r['on_sakhalin']
    for field in ('on_sakhalin', 'all_other_origins'):
        assert r[field + '_pct'] == pct(r[field], n)
assert counts[None, 'all_children'] == 1467
assert counts[None, 'on_sakhalin'] == 1240
assert counts[None, 'origin_unknown'] == 0
assert counts[8, 'origin_not_recorded'] == 52
hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (source, sql)}
assert hashes[source.relative_to(ROOT).as_posix()] == '1b77d6330855763c54c32f21d247dc44471a69590db4fc00925c4e22eb8ac508'
lines = ['# Children’s origin by age — counts and shares', '',
         'Saved 2026-10-19. Children aged 0–15, completed years, both sexes. Each percentage uses **all children of the same age**, including On Sakhalin. Total-row percentages use all 1,467 children.', '',
         'Source: [approved English dataset](../data/analytical/sakhalin_1890_en_v1.csv). Reproduce both tables with [SQL queries 1 and 2](../sql/10_children_origin_age_profile.sql). Percentages are rounded independently to one decimal, so complementary shares may sum to 100.1%.', '',
         '## 1. Detailed groups outside the On Sakhalin label', '',
         'Cells show count (percentage of all children at that age). The displayed categories do not sum to 100% because On Sakhalin is omitted from this first table. No children have the explicit Does not remember label; SQL retains an Origin unknown control column, omitted here because every value is zero.', '',
         '| Age | All children | Recorded origin elsewhere | In transit | Origin not recorded |',
         '|---|---:|---:|---:|---:|']
def cell(r, field):
    return f"{r[field]:,} ({r[field + '_pct']:.1f}%)"
for r in results[0]:
    lines.append('| ' + ' | '.join([str(r['age']) if r['age'] is not None else '**Total**', f"{r['all_children']:,}"] + [cell(r, f) for f in ('origin_elsewhere', 'in_transit', 'origin_not_recorded')]) + ' |')
lines += ['', '## 2. On Sakhalin versus all other origin records', '',
          '**All other origin records is not a migrant count.** It combines named origins elsewhere, In transit and missing origins (and explicit unknown origins if present). In transit does not establish birthplace; missing origin cannot establish migration. On Sakhalin is the recorded source label, not an ethnic or indigenous identity.', '',
          '| Age | All children | On Sakhalin | All other origin records |', '|---|---:|---:|---:|']
for r in results[1]:
    lines.append('| ' + ' | '.join([str(r['age']) if r['age'] is not None else '**Total**', f"{r['all_children']:,}", cell(r, 'on_sakhalin'), cell(r, 'all_other_origins')]) + ' |')
lines += ['', '## Interpretation and validation', '',
          "- At age eight, 52 of 54 children (96.3%) have no recorded origin. Source review closed on 2026-10-27: the project owner reports verifying the original records and confirming that these origins are unrecorded in the source, with the concentration at this age a coincidence rather than a processing issue. This records the owner's verification, not an independent repeat review. The other two records remain On Sakhalin (1) and In transit (1). Preserve the missing values; this pattern is not evidence of a migration peak.",
          '- The age-15 percentages describe just 11 children. Keep counts visible when comparing small age groups.',
          '- Each SQL result contains 16 age rows and one Total row. Exclude the Total row before summing results in Tableau to avoid double-counting.',
          '- Local SQLite execution matches independent source tallies for every count and percentage. On 2026-10-27, the owner supplied both 17-row CSV results; [export QA](../outputs/qa/children_origin_age_export_20261027/validation.json) confirms their headers and values match the validated results. Live MySQL execution logs were not inspected. Source data were not changed.',
          '- [QA results and hashes](../outputs/qa/children_origin_age_20261019/validation.json). Reproduce with `python scripts/validate_children_origin_age_20261019.py`.',
          '- [Arrival/origin context and dashboard connections](arrival_children_origin.md).', '']
(ROOT / 'docs/children_origin_age_profile.md').write_text('\n'.join(lines), encoding='utf-8')
out = ROOT / 'outputs/qa/children_origin_age_20261019'
out.mkdir(parents=True, exist_ok=True)
(out / 'validation.json').write_text(json.dumps(dict(status='PASS', method='SQLite replay and independent Python counts/decimal percentages', hashes=hashes, results=results), indent=2) + '\n', encoding='utf-8')
print('PASS: both 17-row tables match source counts and within-age percentages; source unchanged.')
