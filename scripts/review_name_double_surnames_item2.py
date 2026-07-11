"""Create a review inventory and non-canonical staging candidate for Item 2.

No canonical data is edited. Hyphenated names are classified conservatively;
derived surname fields remain proposed until the project owner approves mappings.
"""
from pathlib import Path
import hashlib
import json
import re
import pandas as pd

INPUT = Path('data/staging/name_raw_item1_20260711/clean_sakhalin_1890_ru_item1_name_v1.csv')
STAMP = '20260711'
REVIEW = Path(f'data/review/name_double_surnames_item2_{STAMP}')
STAGING = Path(f'data/staging/name_double_surnames_item2_{STAMP}')
QA = Path(f'outputs/qa/name_double_surnames_item2_{STAMP}')
for p in (REVIEW, STAGING, QA): p.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT, dtype=str, keep_default_na=False)

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()

def classify(name):
    value = name.strip()
    if not value:
        return 'empty_artifact', 'Blank name', '', 'blank'
    if '(' in value or ')' in value:
        return 'parenthetical_expression', 'Parentheses retained for manual classification', '', 'review'
    if value.endswith('-') or value.startswith('-'):
        return 'empty_artifact', 'Dangling hyphen; do not manufacture an alias', '', 'review'
    if re.search(r'\b[1-4]-[йя]\b', value):
        return 'ordinal_name_marker', 'Ordinal marker is not a surname split', '', 'preserve'
    words = value.split()
    hyphen_words = [w for w in words if '-' in w]
    if not hyphen_words:
        return 'none', '', '', 'not_affected'
    last = words[-1]
    first_hyphen = words[0]
    ethnic_prefixes = ('Оглы', 'Ага-', 'Пир-', 'Мула-', 'Шай-', 'Мине-', 'Курман-', 'Зара-', 'Пен-', 'Абыкизы')
    if any(any(w.startswith(x) for x in ethnic_prefixes) for w in hyphen_words) or (len(words) == 1 and '-' in last):
        return 'ethnic_or_compound_name', 'Hyphenated given/ethnic construction; not safely separable as surnames', '', 'preserve'
    if '-' in first_hyphen and len(words) > 1:
        return 'compound_given_name', 'Hyphen occurs in given-name position; preserve full name', '', 'preserve'
    if '-' in last:
        left, right = last.split('-', 1)
        # A candidate only: owner must decide whether this is a double surname
        return 'surname_compound_candidate', 'Hyphenated final token may be a double surname; distinguish from a fixed complex surname', right, 'review'
    return 'unresolved_text', 'Hyphenated expression requires source-context review', '', 'review'

rows = []
for _, r in df.iterrows():
    n = r['name_raw']
    if '(' in n or ')' in n or '-' in n:
        cls, reason, alt, status = classify(n)
        rows.append({
            'person_id': r['person_id'], 'source_position_id': r['source_position_id'],
            'name_raw': n, 'name_alias_existing': r.get('name_alias', ''),
            'expression_type': cls, 'classification_reason': reason,
            'name_norm_proposed': re.sub(r'\s+', ' ', n).strip(),
            'surname_alternative_proposed': alt,
            'name_note_proposed': reason,
            'decision_status': status,
        })
inv = pd.DataFrame(rows)
inv.to_csv(REVIEW / 'name_double_surnames_item2_inventory.csv', index=False, encoding='utf-8-sig')

# Parenthetical name inventory is intentionally complete and can be zero rows.
paren = inv[inv['expression_type'].eq('parenthetical_expression')]
paren.to_csv(REVIEW / 'name_parenthetical_item2_inventory.csv', index=False, encoding='utf-8-sig')

definitions = """# Item 2 proposed derived fields

These definitions are proposals pending owner review; `name_raw` remains unchanged.

| Field | Proposed definition |
|---|---|
| `name_norm` | Whitespace-normalized presentation of `name_raw`; preserve Cyrillic spelling, hyphens, ordinal markers, and any source parentheses. |
| `surname_alternative` | Optional second/former surname component only when source context supports an actual double or alternative surname. Blank for fixed complex surnames (for example, `Галкин-Враской`, `Сухово-Кобылин`) unless separately approved. |
| `name_note` | Short English review note describing a parenthetical, compound, religious, baptismal, former-surname, artifact, or unresolved expression. |
| `name_alias` | Existing approved alias field from Item 1; retained and not overwritten by this item. |

No Item 2 classification is approved for canonical release yet. Proposed aliases are review inputs only.
"""
(REVIEW / 'name_double_surnames_item2_field_definitions.md').write_text(definitions, encoding='utf-8')

# Staged candidate: preserve existing columns and append proposal fields.
stage = df.copy()
stage['name_norm'] = stage['name_raw'].map(lambda x: re.sub(r'\s+', ' ', x).strip())
notes = {r['person_id']: r['name_note_proposed'] for r in rows}
alts = {r['person_id']: (r['surname_alternative_proposed'] if r['decision_status'] == 'review' and r['expression_type'] == 'surname_compound_candidate' else '') for r in rows}
stage['surname_alternative'] = stage['person_id'].map(alts).fillna('')
stage['name_note'] = stage['person_id'].map(notes).fillna('')
stage.to_csv(STAGING / 'clean_sakhalin_1890_ru_item2_name_v1_proposed.csv', index=False, encoding='utf-8-sig')

# Proposed diff: schema plus populated proposal fields; no name_raw changes.
diff_rows = []
for pid in stage['person_id']:
    old = df.loc[df.person_id.eq(pid)].iloc[0]
    new = stage.loc[stage.person_id.eq(pid)].iloc[0]
    for field in ['name_norm', 'surname_alternative', 'name_note']:
        nv = new[field]
        if nv:
            diff_rows.append({'person_id': pid, 'source_position_id': new['source_position_id'], 'field': field, 'old_value': '', 'new_value': nv, 'change_type': 'proposed_derived_field'})
diff = pd.DataFrame(diff_rows)
diff.to_csv(QA / 'name_double_surnames_item2_proposed_diff.csv', index=False, encoding='utf-8-sig')

qa = {
    'input_sha256': sha(INPUT), 'staged_sha256': sha(STAGING / 'clean_sakhalin_1890_ru_item2_name_v1_proposed.csv'),
    'input_rows': len(df), 'staged_rows': len(stage), 'inventory_rows': len(inv),
    'parenthetical_name_rows': int(len(paren)), 'hyphenated_name_rows': int(inv['name_raw'].str.contains('-', regex=False).sum()),
    'name_raw_changed': int((df['name_raw'] != stage['name_raw']).sum()),
    'person_id_order_unchanged': bool(df['person_id'].tolist() == stage['person_id'].tolist()),
    'source_position_id_unchanged': bool(df['source_position_id'].tolist() == stage['source_position_id'].tolist()),
    'existing_name_alias_unchanged': bool(df['name_alias'].tolist() == stage['name_alias'].tolist()),
    'classification_counts': inv['expression_type'].value_counts().to_dict(),
    'review_required_count': int((inv['decision_status'] == 'review').sum()),
    'proposed_alias_count': int((stage['surname_alternative'] != '').sum()),
    'canonical_touched': False,
}
(QA / 'name_double_surnames_item2_qa.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding='utf-8')
report = '# Item 2 QA report\n\n'
report += '\n'.join(f'- **{k}**: `{v}`' for k, v in qa.items() if k != 'classification_counts')
report += '\n- **classification_counts**: `' + json.dumps(qa['classification_counts'], ensure_ascii=False) + '`\n'
report += '\nThe candidate is staged and pending owner review. `name_raw` and canonical datasets were not changed. Parenthetical expressions in `name_raw`: 0; parentheses found elsewhere remain outside this item.\n'
(QA / 'name_double_surnames_item2_qa.md').write_text(report, encoding='utf-8')

print(json.dumps(qa, ensure_ascii=False, indent=2))
