"""Read-only snapshot reconciliation. SQLite replay is not MySQL runtime validation."""
import csv
import argparse
from datetime import date
import hashlib
import json
import math
import re
import sqlite3
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def normal(value):
    if value is None or value in ('', 'NULL'):
        return ''
    try:
        return str(Decimal(str(value)).normalize())
    except InvalidOperation:
        return str(value)

def bag(rows, fields):
    return Counter(tuple(normal(row[f]) for f in fields) for row in rows)

def main(audit_date='2026-10-04'):
    date.fromisoformat(audit_date)
    out = ROOT / ('outputs/qa/tableau_preflight_' + audit_date.replace('-', ''))
    source = ROOT / 'data/analytical/sakhalin_1890_en_v1.csv'
    fields, rows = read(source)
    assert len(rows) == 7446 and len(fields) == 23
    assert len({r['person_id'] for r in rows}) == 7446
    assert digest(source) == '1b77d6330855763c54c32f21d247dc44471a69590db4fc00925c4e22eb8ac508'
    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    db.create_function('CONCAT', -1, lambda *v: ''.join(str(x) for x in v))
    db.create_function('FLOOR', 1, math.floor)
    numeric = {'person_seq', 'age', 'age_months', 'arrival_year', 'allowance_status'}
    db.execute('CREATE TABLE sakhalin_1890_en (' + ','.join(f'"{f}" {"INTEGER" if f in numeric else "TEXT"}' for f in fields) + ')')
    def convert(f, v):
        if v == '': return None
        if f == 'allowance_status': return int(v == 'TRUE')
        return int(v) if f in numeric else v
    db.executemany('INSERT INTO sakhalin_1890_en VALUES (' + ','.join('?' for _ in fields) + ')',
                   [tuple(convert(f, r[f]) for f in fields) for r in rows])
    sql_path = ROOT / 'sql/04_analysis_queries.sql'
    sql = re.sub(r'--[^\n]*', '', sql_path.read_text(encoding='utf-8-sig'))
    queries, pending = [], ''
    for char in sql:
        pending += char
        if char == ';' and sqlite3.complete_statement(pending):
            queries.append(pending.strip())
            pending = ''
    assert not pending.strip(), 'Incomplete SQL statement'
    results = []
    for number, query in enumerate(queries, 1):
        cursor = db.execute(query)
        results.append((number, [c[0] for c in cursor.description], [dict(r) for r in cursor.fetchall()]))
    variants = {
        'allowance_by_year_NO01092026.csv': "SELECT arrival_year, COUNT(*) AS people FROM sakhalin_1890_en WHERE allowance_status = 0 AND arrival_year IS NOT NULL GROUP BY arrival_year",
        'household_size_settlements01092026.csv': next(q for q in queries if "AS household_size" in q and 'LIMIT 10' in q).replace('LIMIT 10', 'LIMIT 30'),
    }
    audit = []
    for path in sorted((ROOT / 'tableau/data').glob('*.csv')):
        headers, saved = read(path)
        compatible = [(n, rs) for n, fs, rs in results if set(fs) == set(headers)]
        matches = [n for n, rs in compatible if bag(rs, headers) == bag(saved, headers)]
        best = min(compatible, key=lambda v: sum((bag(saved, headers) - bag(v[1], headers)).values()), default=None)
        item = {'file': path.name, 'rows': len(saved), 'sha256': digest(path),
                'matching_query_numbers': matches, 'status': 'MATCH' if matches else 'REVIEW',
                'literal_NULL_cells': sum(v == 'NULL' for r in saved for v in r.values())}
        if path.name in variants:
            variant_rows = [dict(r) for r in db.execute(variants[path.name])]
            item['variant_sql'] = variants[path.name]
            item['variant_matches'] = bag(variant_rows, headers) == bag(saved, headers)
            if item['variant_matches']:
                item['status'] = 'MATCH_DOCUMENTED_VARIANT'
        exclusions = {
            'children_age_profile22082026.csv': 'Historical mixed-unit age variant; use children_age_profile_clean22082026.csv for year-only charts.',
            'origina_place_profile_07092026.csv': 'Earlier ranking has no current query; excluded from starter sources. Recompute from person-level source if needed.'
        }
        if path.name in exclusions:
            item['starter_action'] = exclusions[path.name]
        if item['status'] == 'REVIEW' and best:
            n, expected = best
            item.update(nearest_query=n, saved_only_rows=list((bag(saved, headers)-bag(expected, headers)).elements())[:3],
                        current_only_rows=list((bag(expected, headers)-bag(saved, headers)).elements())[:3])
        audit.append(item)
    practice = ROOT / 'tableau/practice/sakhalin_1890_en_no_full_name_20261004.csv'
    pfields, prows = read(practice)
    retained = [f for f in fields if f != 'full_name']
    assert pfields == retained and len(prows) == len(rows)
    mismatches = sum(a[f] != b[f] for a, b in zip(rows, prows) for f in retained)
    assert mismatches == 0
    benchmarks = {}
    benchmark_queries = {
        'population_by_sex': 'SELECT sex, COUNT(*) AS people FROM sakhalin_1890_en GROUP BY sex',
        'age': 'SELECT COUNT(age) AS recorded_age, SUM(age IS NULL) AS missing_age, SUM(age = 0) AS age_zero, ROUND(AVG(age), 4) AS mean_age FROM sakhalin_1890_en',
        'age_scope': 'SELECT SUM(age BETWEEN 0 AND 17) AS ages_0_17, SUM(age BETWEEN 0 AND 16) AS ages_0_16, SUM(age >= 16) AS ages_16_plus, SUM(age BETWEEN 16 AND 17) AS overlapping_ages_16_17 FROM sakhalin_1890_en',
        'households': 'SELECT COUNT(*) AS household_groups, SUM(people) AS people_with_household_id FROM (SELECT COUNT(*) AS people FROM sakhalin_1890_en WHERE household_id IS NOT NULL GROUP BY district, settlement, household_id)',
        'allowance': 'SELECT SUM(allowance_status = 1) AS yes, SUM(allowance_status = 0) AS no, SUM(allowance_status IS NULL) AS missing, COUNT(allowance_status) AS recorded FROM sakhalin_1890_en',
        'top_five': 'SELECT SUM(people) AS people, 100.0 * SUM(people) / 7446 AS share_of_all_pct FROM (SELECT COUNT(*) AS people FROM sakhalin_1890_en GROUP BY settlement ORDER BY people DESC, settlement LIMIT 5)',
        'arrival': 'SELECT COUNT(arrival_year) AS recorded, SUM(arrival_year IS NULL) AS missing FROM sakhalin_1890_en',
    }
    for name, query in benchmark_queries.items():
        benchmarks[name] = [dict(r) for r in db.execute(query)]
    checks = {}
    def check(name, condition):
        checks[name] = bool(condition)
        assert condition, name
    check('age_missing_and_recorded_reconcile', benchmarks['age'][0]['recorded_age'] + benchmarks['age'][0]['missing_age'] == 7446)
    check('age_zero_preserved', benchmarks['age'][0]['age_zero'] == 204)
    check('household_groups', benchmarks['households'][0]['household_groups'] == 2796)
    check('missing_household_ids', 7446 - benchmarks['households'][0]['people_with_household_id'] == 246)
    check('allowance_missing_and_recorded_reconcile', sum(benchmarks['allowance'][0][k] for k in ('yes', 'no', 'missing')) == 7446)
    for filename in ('legal_status_arrival_07092026.csv', 'alone_status_arrival_07092026.csv'):
        _, saved = read(ROOT / 'tableau/data' / filename)
        for year in {r['arrival_year'] for r in saved}:
            group = [r for r in saved if r['arrival_year'] == year]
            totals = {int(r['cohort_people']) for r in group}
            check(f'{filename}:{year}:denominator', len(totals) == 1 and sum(int(r['people']) for r in group) == next(iter(totals)))
    _, top = read(ROOT / 'tableau/data/top5_by_population_witsubtotal_22082026.csv')
    subtotal = [r for r in top if r['settlement'] == 'Top 5 subtotal']
    details = [r for r in top if r['settlement'] != 'Top 5 subtotal']
    check('top_five_subtotal_equals_detail', len(subtotal) == 1 and sum(int(r['people']) for r in details) == int(subtotal[0]['people']))
    check('snapshots_accounted_for', len(audit) == 44 and Counter(r['status'] for r in audit) == {'MATCH': 40, 'MATCH_DOCUMENTED_VARIANT': 2, 'REVIEW': 2})
    report = {'date': audit_date, 'source_sha256': digest(source), 'sql_sha256': digest(sql_path),
              'source_rows': len(rows), 'source_columns': len(fields), 'practice_columns': len(pfields),
              'practice_sha256': digest(practice), 'retained_cell_mismatches': mismatches,
              'omitted_field': 'full_name', 'affected_person_ids': [r['person_id'] for r in rows],
              'district_counts': dict(Counter(r['district'] for r in rows)),
              'missing_counts': {f: sum(r[f] == '' for r in rows) for f in fields},
              'age_zero_count': sum(r['age'] == '0' for r in rows),
              'allowance_counts': dict(Counter(r['allowance_status'] for r in rows)),
              'queries_replayed': len(queries), 'exports': audit, 'benchmarks': benchmarks, 'checks': checks,
              'method': 'SQLite in-memory replay of current SQL with CONCAT/FLOOR compatibility functions. Numeric formatting and blank/NULL export markers normalized for comparison; row order ignored. MySQL collation may differ. No live MySQL or Tableau validation claimed.'}
    out.mkdir(parents=True, exist_ok=True)
    (out / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = [f'# Tableau preflight — {audit_date}', '', report['method'], '',
             '## Practice-file verification', '',
             '- 7,446 rows; 22 retained columns; full_name omitted for every source person.',
             '- Exact row order and retained values preserved; zero retained-cell mismatches.',
             '- Source hash matches the approved English release. Original source and historical CSVs are unchanged.',
             '- audit.json records hashes, all affected IDs, missing-value counts, and snapshot differences.', '',
             '## Historical export reconciliation', '', '| File | Rows | Result | Current query |', '|---|---:|---|---|']
    lines += [f"| {r['file']} | {r['rows']} | {r['status']} | {', '.join(map(str, r['matching_query_numbers'])) or 'See review notes'} |" for r in audit]
    lines += ['', '## Review notes', '',
              '- 40 snapshots match current SQL values; two match the documented allowance-No and top-30-household variants.',
              '- The older mixed-unit child-age file is excluded in favor of children_age_profile_clean22082026.csv.',
              '- The earlier origina_place_profile_07092026.csv ranking is excluded from starter sources because it has no matching current query.',
              '- All historical snapshots are preserved. Current-match status does not establish that subtotals, percentages, or repeated denominators are additive.',
              '- Tableau runtime and live MySQL checks were not performed.', '',
              '## Reproduction', '',
              'Run scripts/build_tableau_practice_20261004.mjs with the bundled node_modules path, then scripts/audit_tableau_exports_20261004.py. The builder refuses to overwrite a different versioned practice file.']
    lines += ['', '## Import benchmarks', '', f'All {len(checks)} preparation assertions passed. Actual Tableau testing remains pending.', '', '| Scope | Expected values |', '|---|---|']
    for name, values in benchmarks.items():
        lines.append(f'| {name} | ' + '; '.join(', '.join(f'{k}={v}' for k, v in row.items()) for row in values) + ' |')
    lines += ['', f'Repeat this dated audit with `python scripts/audit_tableau_exports_20261004.py --date {audit_date}`. The report is tied to the hashes in audit.json.']
    (out / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'queries': len(queries), 'statuses': dict(Counter(r['status'] for r in audit)), 'retained_cell_mismatches': mismatches}, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default='2026-10-04', help='Explicit report date in YYYY-MM-DD format')
    main(parser.parse_args().date)
