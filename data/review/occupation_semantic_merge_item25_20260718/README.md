# Item 25: semantically close `occupation_norm` values

Source reviewed: the latest Item 24 v2 staged dataset.

Profile:

- 7,446 records
- 1,474 nonblank `occupation_norm` records
- 5,972 blanks
- 135 distinct nonblank normalized values

## Recommended structure

Preserve `occupation_norm` as the owner-reviewed historical/linguistic value. If consolidation is approved, add a separate analytical field such as `occupation_group` rather than overwriting `occupation_norm`. This avoids losing gender, rank, specialization, and source wording.

## Strong merge candidates

- `Парикмахер` + `Цирюльник` → `Парикмахер`
- `Гончар` + `Горшечник` → `Гончар`
- `Папиросник` + `Делает папиросы` → `Папиросник`
- `Фельдшер` + `Фельдшерица` → `Фельдшер`
- `Учитель` + `Учительница` → `Учитель`
- `Рабочий` + `Рабочая` → `Рабочий`
- `Работник` + `Работница` → `Работник`
- `Чернорабочий` + `Чернорабочая` → `Чернорабочий`
- `Портной` + `Портниха` → `Портной`; keep `Швея` distinct or group only
- `При матери`, `При муже`, and `При отце` → analytical `При родственнике`, while retaining the relationship-specific normalized value

## Candidates requiring judgment

- `Булочник` + `Хлебопек` → possible broader `Пекарь`; specialization would be lost.
- `Земледелие` + `Хлебопашец` → possible `Земледелец`; one is an activity and the other a personal title.
- `Повар` + `Кухарка` → often equivalent, but `Кухарка` may carry a domestic-service distinction.

## Group only; do not merge directly

- `Мельник` and `На мельнице`
- `Банщик` and `Баня`
- `Младший надзиратель`, `Надзиратель`, and `Старший надзиратель`
- `Портной`/`Портниха` and `Швея` as a broader sewing family

Compound occupations separated by semicolons should map each component independently if an analytical grouping field is created. No dataset values were changed in this review.
