# Origin Place Reference List, 1890

## Purpose

This reference list documents canonical values used to normalize the `origin_place` field in the Chekhov Sakhalin 1890 Census project.

The list is intended to support reproducible cleaning of historical place-of-origin values extracted from the PDF source. Source values may appear in abbreviated, genitive, bracket-restored, or typo-affected forms. The normalized output should use the canonical values below when the mapping is clear.

## Field Name

- Final dataset field: `origin_place`
- User-facing description: place of origin / origin location

## Normalization Rule

Use canonical 1890 administrative-unit names where possible.

Examples:

| Source value | Canonical value |
|---|---|
| `Каменецк-Подольская` | `Подольская губерния` |
| `Каменец-Подольская` | `Подольская губерния` |
| `Курляндского` | `Курляндская губерния` |
| `Курлядской` | `Курляндская губерния` |
| `Петербургской` | `Санкт-Петербургская губерния` |
| `Петраковской` | `Петроковская губерния` |
| `Астроханской` | `Астраханская губерния` |
| `Донской` | `Область Войска Донского` |
| `Финляндской` | `Великое княжество Финляндское` |
| `На Сахалине` | `На Сахалине` |
| `По пути` | `По пути` |

If a value cannot be confidently mapped, preserve the cleaned source value and flag it for manual review rather than guessing.

## Canonical Values

### Main governorates of the Russian Empire, 1890

- Архангельская губерния
- Астраханская губерния
- Бакинская губерния
- Бессарабская губерния
- Виленская губерния
- Витебская губерния
- Владимирская губерния
- Вологодская губерния
- Волынская губерния
- Воронежская губерния
- Вятская губерния
- Гродненская губерния
- Екатеринославская губерния
- Елисаветпольская губерния
- Енисейская губерния
- Иркутская губерния
- Казанская губерния
- Калужская губерния
- Киевская губерния
- Ковенская губерния
- Костромская губерния
- Курляндская губерния
- Курская губерния
- Кутаисская губерния
- Лифляндская губерния
- Минская губерния
- Могилёвская губерния
- Московская губерния
- Нижегородская губерния
- Новгородская губерния
- Олонецкая губерния
- Оренбургская губерния
- Орловская губерния
- Пензенская губерния
- Пермская губерния
- Подольская губерния
- Полтавская губерния
- Псковская губерния
- Рязанская губерния
- Самарская губерния
- Санкт-Петербургская губерния
- Саратовская губерния
- Симбирская губерния
- Смоленская губерния
- Ставропольская губерния
- Таврическая губерния
- Тамбовская губерния
- Тверская губерния
- Тифлисская губерния
- Тобольская губерния
- Томская губерния
- Тульская губерния
- Уфимская губерния
- Харьковская губерния
- Херсонская губерния
- Черниговская губерния
- Эриванская губерния
- Эстляндская губерния
- Ярославская губерния

### Polish governorates, 1890

- Варшавская губерния
- Калишская губерния
- Келецкая губерния
- Ломжинская губерния
- Люблинская губерния
- Петроковская губерния
- Плоцкая губерния
- Радомская губерния
- Седлецкая губерния
- Сувалкская губерния

### Finnish governorates, 1890

- Абоско-Бьёрнеборгская губерния
- Вазаская губерния
- Выборгская губерния
- Куопиоская губерния
- Нюландская губерния
- Санкт-Михельская губерния
- Тавастгусская губерния
- Улеаборгская губерния

### Oblasts, 1890

- Акмолинская область
- Амурская область
- Дагестанская область
- Забайкальская область
- Закаспийская область
- Карсская область
- Кубанская область
- Область Войска Донского
- Приморская область
- Самаркандская область
- Семипалатинская область
- Семиреченская область
- Сыр-Дарьинская область
- Терская область
- Тургайская область
- Уральская область
- Ферганская область
- Якутская область

### Special administrative units

- Артвинский округ
- Батумский округ
- Бухарский эмират
- Великое княжество Финляндское
- Закатальский округ
- Сахалинский отдел
- Сухумский округ
- Хивинское ханство
- Черноморский округ Кубанской области

### Supplemental non-administrative source values

- На Сахалине
- По пути
- Прусскоподданная
- Прусскоподданный
- из Чибисани

## QA Notes

- Unknown `origin_place` values should be reviewed manually.
- Values that look like occupations should not be auto-corrected; preserve them and flag for source anomaly review.
- Values such as `На Сахалине`, `По пути`, `Прусскоподданный`, and `Прусскоподданная` are meaningful source values and should be preserved.
- Administrative-unit mapping is based on the 1890 reference framework used in this project, not modern geography.

## Maintenance

When a new legitimate origin-place value appears in the source, add it to the appropriate reference section. When a typo or spelling variant appears, add it to the normalization map rather than adding it as a new canonical value.

Recommended file location in the repository:

```text
docs/reference/origin_place_reference_1890.md
```
