"""Apply owner-reviewed Item 2 decisions to a staged candidate only.

The owner-approved review normalizes selected names into ``name_norm`` and
places the corresponding alternative surname/name portion in the existing
``name_alias`` field. It never changes ``name_raw`` and never creates a
surname-alternative field.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import pandas as pd

STAMP = '20260711'
INPUT = Path('data/staging/name_raw_item1_20260711/clean_sakhalin_1890_ru_item1_name_v1.csv')
BASE_INVENTORY = Path(f'data/review/name_double_surnames_item2_{STAMP}/name_double_surnames_item2_inventory.csv')
OWNER_WORKBOOK = Path(r'C:/Users/User/Downloads/name_double_surnames_item2_inventory_reviewed.xlsx')
REVIEW = Path(f'data/review/name_double_surnames_item2_{STAMP}/owner_response')
STAGING = Path(f'data/staging/name_double_surnames_item2_{STAMP}_approved')
QA = Path(f'outputs/qa/name_double_surnames_item2_{STAMP}_approved')
for folder in (REVIEW, STAGING, QA):
    folder.mkdir(parents=True, exist_ok=True)

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()

base = pd.read_csv(BASE_INVENTORY, dtype=str, keep_default_na=False)
review = pd.read_excel(OWNER_WORKBOOK, sheet_name=0, header=1, dtype=str, keep_default_na=False)
review = review.drop(columns=[c for c in review.columns if str(c).startswith('Unnamed')], errors='ignore')
review = review[review['person_id'].ne('')].copy()
required = list(base.columns)
if list(review.columns) != required:
    raise ValueError(f'Workbook columns do not match review inventory: {list(review.columns)}')
if len(review) != len(base) or set(review.person_id) != set(base.person_id):
    raise ValueError('Workbook person_id set does not match the 75-record Item 2 inventory')
if review.person_id.duplicated().any():
    raise ValueError('Workbook contains duplicate person_id values')

# Context fields cannot be changed by the review workflow. `name_alias_existing`
# is display-only context; its workbook values must match the original inventory.
protected = ['source_position_id', 'name_raw']
merged = base.merge(review, on='person_id', suffixes=('_base', '_review'), validate='one_to_one')
for field in protected:
    mismatches = merged[merged[f'{field}_base'] != merged[f'{field}_review']]
    if len(mismatches):
        raise ValueError(f'Protected field changed in owner workbook: {field}')

allowed_statuses = {'correct', 'preserve'}
if not set(review['decision_status']).issubset(allowed_statuses):
    raise ValueError('decision_status must contain only correct or preserve')

alias_context_unchanged = (
    merged['name_alias_existing_base'].fillna('').eq(merged['name_alias_existing_review'].fillna('')).all()
)
if not alias_context_unchanged:
    raise ValueError('Unexpected edits in display-only name_alias_existing column')

shutil.copy2(OWNER_WORKBOOK, REVIEW / 'name_double_surnames_item2_inventory_reviewed_20260711.xlsx')

review = review.set_index('person_id')
approved = review[review['decision_status'].eq('correct')].copy()
approved_out = approved.reset_index()[[
    'person_id', 'source_position_id', 'name_raw', 'name_norm_proposed',
    'surname_alternative_proposed', 'name_note_proposed', 'decision_status'
]].rename(columns={
    'name_norm_proposed': 'name_norm_approved',
    'surname_alternative_proposed': 'name_alias_approved',
    'name_note_proposed': 'name_note_approved',
})
approved_out.to_csv(REVIEW / 'name_double_surnames_item2_approved_decisions_20260711.csv', index=False, encoding='utf-8-sig')

df = pd.read_csv(INPUT, dtype=str, keep_default_na=False)
stage = df.copy()
stage['name_norm'] = stage['name_raw']
stage['name_note'] = ''

for pid, decision in approved.iterrows():
    mask = stage['person_id'].eq(pid)
    stage.loc[mask, 'name_norm'] = decision['name_norm_proposed']
    alt = decision['surname_alternative_proposed'].strip()
    if alt:
        stage.loc[mask, 'name_alias'] = alt
    stage.loc[mask, 'name_note'] = decision['name_note_proposed']

output = STAGING / 'clean_sakhalin_1890_ru_item2_name_v1.csv'
stage.to_csv(output, index=False, encoding='utf-8-sig')

diff_rows = []
for _, old in df.iterrows():
    new = stage.loc[stage.person_id.eq(old.person_id)].iloc[0]
    for field in ['name_alias', 'name_norm', 'name_note']:
        old_value = old[field] if field in old.index else ''
        new_value = new[field]
        if old_value != new_value:
            diff_rows.append({
                'person_id': old.person_id,
                'source_position_id': old.source_position_id,
                'field': field,
                'old_value': old_value,
                'new_value': new_value,
                'change_type': 'approved_item2_derived_field',
            })
diff = pd.DataFrame(diff_rows)
diff.to_csv(QA / 'name_double_surnames_item2_approved_diff.csv', index=False, encoding='utf-8-sig')

definitions = """# Approved Item 2 derived-field definitions

## `name_raw`

Source-faithful reviewed name text. It is retained unchanged, including hyphens.

## `name_norm`

An analytical normalized name. For approved women’s hyphenated surname forms, it retains the left component as the maiden surname and removes the hyphen-connected husband surname. It may also apply an approved spacing repair or remove a dangling hyphen. Fixed complex surnames, compound given names, ordinal markers, and ethnic-name constructions remain unchanged unless the owner has explicitly marked a correction.

## `name_alias`

The existing Item 1 alias field. For an approved women’s maiden-surname–husband-surname construction, it receives the right surname component (the husband surname). It may also receive another owner-approved name portion. Existing values are preserved unless an approved Item 2 value is explicitly supplied.

## `name_note`

English review rationale for an approved Item 2 derived-field decision. It does not replace source evidence.

No `surname_alternative` or `surname_alternative_proposed` column is created in the staged dataset.
"""
(REVIEW / 'name_double_surnames_item2_approved_field_definitions.md').write_text(definitions, encoding='utf-8')

qa = {
    'input_sha256': sha(INPUT),
    'owner_workbook_sha256': sha(OWNER_WORKBOOK),
    'staged_sha256': sha(output),
    'input_rows': len(df),
    'staged_rows': len(stage),
    'owner_review_rows': len(review),
    'approved_correct_rows': len(approved),
    'approved_name_norm_changes': int((stage['name_norm'] != df['name_raw']).sum()),
    'approved_name_alias_changes': int((stage['name_alias'] != df['name_alias']).sum()),
    'approved_name_note_values': int((stage['name_note'] != '').sum()),
    'name_raw_changed': int((stage['name_raw'] != df['name_raw']).sum()),
    'name_alias_existing_context_unchanged': bool(alias_context_unchanged),
    'surname_alternative_column_present': bool('surname_alternative' in stage.columns),
    'surname_alternative_proposed_column_present': bool('surname_alternative_proposed' in stage.columns),
    'person_id_order_unchanged': bool(df['person_id'].tolist() == stage['person_id'].tolist()),
    'source_position_id_unchanged': bool(df['source_position_id'].tolist() == stage['source_position_id'].tolist()),
    'canonical_touched': False,
}
(QA / 'name_double_surnames_item2_approved_qa.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding='utf-8')
report = '# Item 2 approved QA report\n\n' + '\n'.join(f'- **{key}**: `{value}`' for key, value in qa.items())
report += '\n\nThe canonical datasets remain unchanged. The staged candidate has no `surname_alternative` or `surname_alternative_proposed` column.\n'
(QA / 'name_double_surnames_item2_approved_qa.md').write_text(report, encoding='utf-8')
print(json.dumps(qa, ensure_ascii=False, indent=2))
