import pandas as pd

p = 'data/staging/name_raw_item1_20260711/clean_sakhalin_1890_ru_item1_name_v1.csv'
d = pd.read_csv(p, dtype=str, keep_default_na=False)
print(d.columns.tolist())
for label, mask in [('paren', d['name_raw'].str.contains(r'[()]', regex=True)), ('hyphen', d['name_raw'].str.contains('-', regex=False))]:
    x = d.loc[mask]
    print('---', label, len(x))
    print(x[['person_id','source_position_id','name_raw','name_alias','family_status','comments']].to_string(index=False))
for c in d.columns:
    m = d[c].astype(str).str.contains(r'[()]', regex=True)
    if m.any():
        print('FIELD PAREN', c, int(m.sum()))
        print(d.loc[m, ['person_id','source_position_id',c]].to_string(index=False))
