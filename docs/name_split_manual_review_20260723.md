# Name split manual review — 2026-07-23

## Scope

The owner reviewed 92 rows in the `Remaining Review` worksheet of
`name_split_manual_review_staged_candidate.xlsx`. Seventy-nine rows contained
new component decisions; 13 previously ambiguous rows were unchanged.

The 79 reviewed decisions comprised:

| Original review class | Records |
|---|---:|
| `complex_muslim_manual` | 72 |
| `single_muslim_manual` | 7 |
| **Total** | **79** |

## Implemented decisions

The reviewed values are stored in
`scripts/name_split_manual_exceptions_20260723.csv` and loaded by
`scripts/name_split.py` after the general exception table. Matching is by
`person_id` plus the expected `name_raw`, so a changed source value cannot
silently receive an obsolete decision.

| Implemented rule | Records | Meaning |
|---|---:|---|
| `reviewed_muslim_first_last` | 25 | Owner accepted a first-name and last-name split |
| `reviewed_muslim_first_only` | 4 | Owner accepted only a first name |
| `reviewed_muslim_unsplit_as_last` | 50 | Owner intentionally retained the complete source string in `last_name` |
| **Total** | **79** | |

These are person-level exceptions, not new automatic parsing rules. This
protects other Muslim and non-Russian names from unintended changes.

## Resulting staged version

The staged dataset is:

`data/staging/name_split_manual_review_all_20260723/clean_sakhalin_1890_ru_v4_20260717_names_staged.csv`

QA result:

| Measure | Count |
|---|---:|
| All records | 7,446 |
| `observed` | 7,433 |
| `ambiguous` | 13 |
| `manual_review` | 0 |
| Hard QA issues | 0 |

The 13 unchanged ambiguous single-token cases remain unresolved deliberately:
P001753, P002580, P002654, P002655, P002789, P002790, P006155, P006156,
P006157, P006229, P006308, P006309, and P006531.

## First-name spelling QA

`scripts/qa_first_name_spelling.py` audits accepted `first_name` tokens without
changing the staged dataset. It checks tokens against the curated lexicon using
sex, religion-derived naming model, dataset frequency, and edit distance. Known
historical variants are excluded from automatic suggestions.

The audit identified 24 records for review: 13 high-priority and 11
medium-priority. High priority includes the two supplied examples:

- P002626: `Алексейандр` → proposed `Александр`;
- P002628: `Алексейандр` → proposed `Александр`.

Other high-priority rows include probable spellings such as `Кирил`,
`Антрон`, `Палагея`, and `Семенд`, plus redacted or placeholder values (`Вик***`
and `N`). Medium-priority suggestions are intentionally conservative: they may
be valid Catholic, Lutheran, Armenian, or historical forms and require owner
confirmation.

No spelling proposal has been applied to the staged dataset.

## Patronymic and compound-name follow-up

A subsequent owner review added 12 person-level decisions. Four records receive
upstream `name_raw` corrections before splitting:

- P002626: `Александр Нездолиев`;
- P002628: `Александр Михаилов Богавец`;
- P003385: `Варвара Иларионова Портникова`;
- P006779: `Кирилл Анисимов Анисимов`.

Six records receive corrected component roles without a general parsing rule:

- P005130: `Габо` + `Гаджи Швили`;
- P005131: `Никола` + `Кехо Швили`;
- P005664: `Марианна` + `Короха Швили`;
- P004496: last name `Кют`, compound first name `Андрес Генрих`;
- P005396: no personal-name components;
- P006902: complete value `Ахмет Оглы Аскар` stored as `last_name`.

Review of the earlier 200-record workbook also recovered two Jewish-name
decisions that the generic three-token parser had overwritten:

- P003135: first name `Лея Пермут`, last name `Броха`;
- P004116: first name `Сара Хаса`, last name `Абезгауз`.

The upstream corrections are stored in
`scripts/name_raw_corrections_patronymic_review_20260723.csv`. All 12 splits are
stored in `scripts/name_split_patronymic_review_exceptions_20260723.csv`.
The resulting staged dataset is under
`data/staging/name_split_patronymic_review_20260723/`. It retains 7,433 observed
and 13 ambiguous records and passes all hard QA checks.

## Completed first-name QA

The owner completed all 24 rows in
`name_split_manual_review_and_first_name_qa_20260723_rev1.xlsx`:

- 9 rows were marked `Correct`;
- 15 rows were marked `Keep current`;
- P002626 and P002628 were already corrected by the preceding patronymic review;
- 7 additional record-level corrections were applied.

The seven new exceptions remove placeholder `N` values from both first and
patronymic fields for P002785, P002795, P002802, and P002881; correct P000835 to
`Николай`; P001260 to `Петр`; and P004361 to `Степан`.

The 15 retained forms are recorded as reviewed outcomes and excluded from
future spelling suggestions. The previously confirmed compound first name
`Андрес Генрих` for P004496 is excluded as well. After these decisions, the
first-name spelling QA queue is empty.

The complete decision log is
`scripts/name_first_name_review_decisions_20260723.csv`; applied exceptions are
in `scripts/name_split_first_name_review_exceptions_20260723.csv`. The resulting
staged output is under `data/staging/name_split_first_name_review_20260723/`.

## Complete Muslim-name re-review

All 197 Muslim records were assembled into a new owner-review workbook. The
population consists of 143 current `first + last` splits, 50 complete strings
stored in `last_name`, and 4 first-name-only cases.

The parser now routes all 13 hyphenated two-token Muslim names to manual review
using `hyphenated_two_token_muslim_manual`. This fixes the earlier whitespace
tokenization gap affecting values such as `Оглы-Мамет Тали-Кербалай`,
`Оглы-Эфенди Ибрагим`, and `Шихова-Хан Бибиш`.

The owner-review hierarchy is:

- reliable structure: `first_name + last_name`;
- unreliable structure: complete `name_raw` in `last_name`;
- genuine single given name: `first_name` only;
- `patronymic_name` always empty.

The review workbook is
`outputs/qa/name_split_muslim_review_20260723/all_muslim_names_review_197_20260723.xlsx`.
Final decisions must be entered in its `All Muslim Names` worksheet.

### Completed and applied

All 197 decisions were completed and validated:

| Workbook decision | Records |
|---|---:|
| `Approve current` | 167 |
| `Correct split` | 9 |
| `Use full string as last` | 21 |
| **Total** | **197** |

After interpreting literal `NULL` component entries as empty database values,
the accepted results are:

| Result structure | Records |
|---|---:|
| `first_name + last_name` | 122 |
| Complete `name_raw` in `last_name` | 68 |
| `first_name` only | 7 |
| Muslim patronymic populated | 0 |

Thirty records changed relative to the preceding staged output; 167 were
reconfirmed without component changes. The consolidated exception table is
`scripts/name_split_muslim_review_all_20260723.csv` and supersedes the earlier
79-record Muslim exception table for pipeline execution.

The applied staged version is
`data/staging/name_split_muslim_review_applied_20260723/clean_sakhalin_1890_ru_v4_20260717_names_staged.csv`.
It contains 7,433 observed and 13 ambiguous records, no manual-review records,
no hard QA issues, and no remaining first-name spelling candidates.

## Final ambiguous-record review

The remaining 13 single-token records were reviewed with no requested
component changes. Their tentative `last_name` values were promoted to
owner-reviewed surnames using `reviewed_single_token_last`.

The decisions are stored in
`scripts/name_split_ambiguous_review_exceptions_20260723.csv`. The final staged
version is
`data/staging/name_split_all_reviews_applied_20260723/clean_sakhalin_1890_ru_v4_20260717_names_staged.csv`.

Final QA status:

| Measure | Count |
|---|---:|
| Records | 7,446 |
| `observed` | 7,446 |
| `ambiguous` | 0 |
| `manual_review` | 0 |
| `unresolved` | 0 |
| Hard QA issues | 0 |
| First-name spelling candidates | 0 |
