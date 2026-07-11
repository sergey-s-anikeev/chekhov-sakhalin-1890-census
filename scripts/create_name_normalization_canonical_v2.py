"""Create the owner-approved Item 1 + Item 2 canonical release artifacts.

The prior canonical files are never overwritten. Item 2 ``name_norm`` values
replace ``name_raw`` in the new release; ``name_norm`` and ``name_note`` remain
review/QA fields and are not included in the 24-column canonical schema.
"""
from pathlib import Path
import hashlib
import json
import pandas as pd

DATE = '20260711'
VERSION = 'v2'
CURRENT = Path('data/processed/clean_sakhalin_1890_ru.csv')
STAGED = Path('data/staging/name_double_surnames_item2_20260711_approved/clean_sakhalin_1890_ru_item2_name_v1.csv')
OUT_DIR = Path('data/processed')
QA_DIR = Path(f'outputs/qa/name_normalization_canonical_{VERSION}_{DATE}')
QA_DIR.mkdir(parents=True, exist_ok=True)

COMBINED = OUT_DIR / f'clean_sakhalin_1890_ru_{VERSION}_{DATE}.csv'
DISTRICT_OUTPUTS = {
    'Александровский': OUT_DIR / f'clean_alexandrovsky_ru_{VERSION}_{DATE}.csv',
    'Тымовский': OUT_DIR / f'clean_tymovsky_ru_{VERSION}_{DATE}.csv',
    'Корсаковский': OUT_DIR / f'clean_korsakovsky_ru_{VERSION}_{DATE}.csv',
}

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

old = pd.read_csv(CURRENT, dtype=str, keep_default_na=False)
staged = pd.read_csv(STAGED, dtype=str, keep_default_na=False)

if len(old) != 7446 or len(staged) != 7446:
    raise ValueError('Expected 7,446 records in both current and staged inputs')
if old['person_id'].tolist() != staged['person_id'].tolist():
    raise ValueError('person_id order changed before canonical release')
if old['source_position_id'].tolist() != staged['source_position_id'].tolist():
    raise ValueError('source_position_id changed before canonical release')
if staged['person_id'].duplicated().any() or staged['source_position_id'].duplicated().any():
    raise ValueError('Duplicate stable identifier found')

release = staged.copy()
release['name_raw'] = release['name_norm']
release = release.drop(columns=['name_norm', 'name_note'])

expected = old.columns.tolist()
expected.insert(expected.index('name_raw') + 1, 'name_alias')
if release.columns.tolist() != expected:
    raise ValueError(f'Unexpected release schema: {release.columns.tolist()}')
if len(release.columns) != 24:
    raise ValueError('Canonical release must contain exactly 24 columns')

release.to_csv(COMBINED, index=False, encoding='utf-8-sig')
for district, path in DISTRICT_OUTPUTS.items():
    release.loc[release['district'].eq(district)].to_csv(path, index=False, encoding='utf-8-sig')

ordered = pd.concat(
    [pd.read_csv(path, dtype=str, keep_default_na=False) for path in DISTRICT_OUTPUTS.values()],
    ignore_index=True,
)
if not ordered.equals(release):
    raise ValueError('Combined release is not the exact ordered district concatenation')

diff_rows = []
for _, old_row in old.iterrows():
    new_row = release.loc[release['person_id'].eq(old_row['person_id'])].iloc[0]
    for field in release.columns:
        old_value = old_row[field] if field in old.columns else ''
        new_value = new_row[field]
        if old_value != new_value:
            diff_rows.append({
                'person_id': old_row['person_id'],
                'source_position_id': old_row['source_position_id'],
                'field': field,
                'old_value': old_value,
                'new_value': new_value,
            })
diff = pd.DataFrame(diff_rows)
diff.to_csv(QA_DIR / 'canonical_v2_record_field_diff.csv', index=False, encoding='utf-8-sig')

field_counts = diff['field'].value_counts().rename_axis('field').reset_index(name='changed_records')
field_counts.to_csv(QA_DIR / 'canonical_v2_field_change_counts.csv', index=False, encoding='utf-8-sig')

artifacts = [COMBINED, *DISTRICT_OUTPUTS.values()]
manifest = pd.DataFrame([
    {'path': str(path).replace('\\', '/'), 'sha256': sha256(path), 'rows': len(pd.read_csv(path, dtype=str)), 'columns': 24}
    for path in artifacts
])
manifest.to_csv(QA_DIR / 'canonical_v2_artifact_manifest.csv', index=False, encoding='utf-8-sig')

qa = {
    'release_version': VERSION,
    'approval_date': '2026-07-11',
    'current_canonical_sha256': sha256(CURRENT),
    'new_combined_sha256': sha256(COMBINED),
    'records': len(release),
    'columns': len(release.columns),
    'new_columns': ['name_alias'],
    'changed_records': int(diff['person_id'].nunique()),
    'field_change_counts': {row.field: int(row.changed_records) for row in field_counts.itertuples()},
    'populated_name_alias': int(release['name_alias'].ne('').sum()),
    'blank_name_raw': int(release['name_raw'].eq('').sum()),
    'duplicate_person_id': int(release['person_id'].duplicated().sum()),
    'duplicate_source_position_id': int(release['source_position_id'].duplicated().sum()),
    'person_id_order_unchanged': old['person_id'].tolist() == release['person_id'].tolist(),
    'source_position_id_unchanged': old['source_position_id'].tolist() == release['source_position_id'].tolist(),
    'district_order_unchanged': old['district'].tolist() == release['district'].tolist(),
    'combined_equals_ordered_district_concatenation': ordered.equals(release),
    'district_counts': release['district'].value_counts(sort=False).to_dict(),
    'name_norm_present': 'name_norm' in release.columns,
    'name_note_present': 'name_note' in release.columns,
    'surname_alternative_present': 'surname_alternative' in release.columns,
    'prior_canonical_files_overwritten': False,
}
(QA_DIR / 'canonical_v2_qa_report.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding='utf-8')
report = '# Canonical name-normalization v2 QA report\n\n'
report += '\n'.join(f'- **{key}**: `{value}`' for key, value in qa.items())
report += '\n\nThe owner-approved Item 1 and Item 2 changes are incorporated in a new versioned release. Previous canonical files remain unchanged.\n'
(QA_DIR / 'canonical_v2_qa_report.md').write_text(report, encoding='utf-8')
print(json.dumps(qa, ensure_ascii=False, indent=2))
