import pandas as pd

source = 'data/review/name_double_surnames_item2_20260711/name_double_surnames_item2_inventory.csv'
review = r'C:\Users\User\Downloads\name_double_surnames_item2_inventory_reviewed.xlsx'

base = pd.read_csv(source, dtype=str, keep_default_na=False)
book = pd.read_excel(review, sheet_name=0, header=1, dtype=str, keep_default_na=False)
print('review columns:', list(book.columns))
print('review rows:', len(book))
print('name_alias_existing values:', book['name_alias_existing'].value_counts(dropna=False).to_dict())
book = book.drop(columns=[c for c in book.columns if str(c).startswith('Unnamed')], errors='ignore')
book = book[book['person_id'].ne('')]
merged = base.merge(book, on='person_id', suffixes=('_base', '_review'), how='outer', indicator=True)
print('merge:', merged['_merge'].value_counts().to_dict())
for c in base.columns:
    rc = c + '_review'
    bc = c + '_base'
    if rc in merged and bc in merged:
        changes = merged[merged[rc].fillna('') != merged[bc].fillna('')]
        if len(changes):
            print('\nCHANGED', c, len(changes))
            print(changes[['person_id', bc, rc]].to_csv(index=False))
