"""Inventory Item 5 controlled categories and seed Batch A translations."""
import csv, json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'data/processed/clean_sakhalin_1890_ru_v5_20260731.csv'
OUT=ROOT/'outputs/english_controlled_translation_review_20260802'
OUT.mkdir(parents=True,exist_ok=True)
FIELDS={
 'district':'district','household_type':'household_type','sex':'sex','religion':'religion',
 'literacy':'literacy','marriage_status_norm':'marital_status','living_alone_status':'living_alone_status',
 'allowance_status':'allowance_status','legal_status_norm':'legal_status',
 'family_status_norm':'family_status','occupation_norm':'occupation','illness_norm':'illness'}
PROPOSALS={
 'Тымовский':'Tymovsky District','Александровский':'Alexandrovsky District','Корсаковский':'Korsakovsky District',
 'Частное':'Private household','Казарма':'Barracks','Дом':'House','Другое':'Other','Тюрьма':'Prison',
 'Метеорологическая станция':'Meteorological station','Школа':'School','Телеграф':'Telegraph office',
 'Баня':'Bathhouse','Мастерская':'Workshop','Лазарет':'Infirmary','Мужской':'Male','Женский':'Female',
 'Православное':'Eastern Orthodox','Католическое':'Roman Catholic','Магометанское':'Muslim',
 'Лютеранское':'Lutheran','Иудейское':'Jewish','Раскольничество':'Schismatic (historical term)',
 'Армяно-григорианское':'Armenian Apostolic','Старообрядчество':'Old Believer','Молоканское':'Molokan',
 'Неграмотен':'Illiterate','Грамотен':'Literate','Образован':'Educated',
 'Женат на родине':'Married in homeland','Холост':'Single','Вдов':'Widowed',
 'Женат на Сахалине':'Married on Sakhalin','Женат в другом регионе':'Married in another region',
 'Женат на Сахалине; Вдов':'Married on Sakhalin; Widowed',
 'Женат на родине и на Сахалине':'Married in homeland and on Sakhalin','Одинок':'Living alone',
 'FALSE':'FALSE','TRUE':'TRUE'}
SENSITIVE={'Магометанское':'Modern neutral English term; source wording is historical.',
 'Раскольничество':'Potentially pejorative historical category; review display label.',
 'Старообрядчество':'Preserve distinction from Раскольничество.','Молоканское':'Transliterate denomination name.'}
with SRC.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
batch_a=[]; batch_b=[]
for source,target in FIELDS.items():
 c=Counter(r[source] for r in rows if r[source]!='')
 for value,count in sorted(c.items(),key=lambda x:(-x[1],x[0])):
  item={'source_field':source,'english_field':target,'russian_value':value,'count':count,
        'proposed_english':PROPOSALS.get(value,''),'review_note':SENSITIVE.get(value,'')}
  (batch_a if source in {'district','household_type','sex','religion','literacy','marriage_status_norm','living_alone_status','allowance_status'} else batch_b).append(item)
data={'records':len(rows),'batch_a':batch_a,'batch_b':batch_b,
      'domain_counts':{s:len({r[s] for r in rows if r[s]!=''}) for s in FIELDS}}
(OUT/'controlled_translation_inventory_20260802.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'records':len(rows),'batch_a':len(batch_a),'batch_b':len(batch_b),'domain_counts':data['domain_counts']},ensure_ascii=False,indent=2))
