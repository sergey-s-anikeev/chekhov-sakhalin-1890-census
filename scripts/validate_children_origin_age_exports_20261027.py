"""Compare owner-supplied age-origin CSVs with the previously validated SQL results."""
import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path

root = Path(__file__).resolve().parents[1]
qa_path = root / 'outputs/qa/children_origin_age_20261019/validation.json'
expected_tables = json.loads(qa_path.read_text(encoding='utf-8'))['results']
files = [
    root / 'tableau/data/children_origin_age_profile_20261027.csv',
    root / 'tableau/data/children_origin_age__islanders_profile_20261027.csv',
]
report = {'status': 'PASS', 'method': 'Exact header and ordered row comparison with locally validated SQL results; live MySQL execution not inspected', 'files': []}
for path, expected in zip(files, expected_tables):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == list(expected[0]), (path.name, reader.fieldnames)
        actual = list(reader)
    assert len(actual) == len(expected) == 17, path.name
    for index, (row, reference) in enumerate(zip(actual, expected), start=1):
        for field, value in reference.items():
            observed = row[field]
            if value is None:
                assert observed in ('', 'NULL'), (path.name, index, field, observed, value)
            elif isinstance(value, (int, float)):
                assert Decimal(observed) == Decimal(str(value)), (path.name, index, field, observed, value)
            else:
                assert observed == value, (path.name, index, field, observed, value)
    report['files'].append({'path': path.relative_to(root).as_posix(), 'rows': len(actual),
                            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                            'comparison': 'MATCH'})
out = root / 'outputs/qa/children_origin_age_export_20261027'
out.mkdir(parents=True, exist_ok=True)
(out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('PASS: both 17-row origin-by-age CSVs match the validated SQL results exactly.')
