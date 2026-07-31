# Last-name book discrepancy review — 2026-07-31

The project owner completed all 249 decisions in the `Discrepancies` worksheet
of `outputs/qa/last_name_book_verification_20260723/last_name_discrepancy_review_20260723.xlsx`.
The review contains 200 `Keep staged` decisions and 49 `Correct manually`
decisions.

The decisions were validated and applied with
`scripts/apply_last_name_book_review.py` to the preceding complete name-split
stage. The new staged dataset is:

`data/staging/name_split_last_name_book_review_20260731/clean_sakhalin_1890_ru_v4_20260717_names_last_name_review_staged.csv`

The stage retains 7,446 records, 50 columns, stable identifier order, and the
existing canonical v4 data. Forty-five records have material changes and four
manual decisions confirm values already present in the source stage. The
material changes include 41 last-name changes, two first-name changes, two
patronymic removals, and seven alias additions. A field-level diff and QA
summary are stored in `outputs/qa/name_split_last_name_book_review_20260731/`.

For `P005626`, the owner-confirmed result is `first_name = Рарица`, blank
`patronymic_name`, and `last_name = Марина`. This supersedes the earlier
automatic reversal of the two source tokens. `Рарица` is also recorded as an
owner-reviewed historical first name for spelling QA.

This output remains staged. It is not a canonical release and has not been
added to the canonical manifest. Further updates should build from this stage
unless the project owner gives different direction.

## Subsequent owner name-component updates

Two additional owner instructions were recorded on 2026-07-31 and applied to
a successor stage:

- `P001396` (`Пост Александровский`): `last_name` changed from `Синицина` to
  `Синицына`. The source transcription in `name_raw` remains unchanged.
- `P002542` (`Танги`, `Марфа Ипполитова`): the owner confirmed the already
  staged result with blank `patronymic_name` and `last_name = Ипполитова`.

The successor staged dataset is
`data/staging/name_split_owner_updates_20260731/clean_sakhalin_1890_ru_v4_20260717_names_owner_updates_staged.csv`.
The explicit correction input is
`scripts/name_component_owner_corrections_20260731.csv`; its field-level diff
and QA evidence are in `outputs/qa/name_split_owner_updates_20260731/`.

## Тодор Марин household update

The owner subsequently clarified the name structure for household 14 in
`Мало-Тымово`. For household head `P005625`, `Тодор` was added to
`name_alias`, while the existing structured name `Федор Марин` was retained.
For children `P005627`–`P005631`, `Тодор` was moved from `last_name` to
`patronymic_name`; sons received `last_name = Марин` and daughters received
`last_name = Марина`.

The explicit six-record input is
`scripts/family_todor_marin_owner_corrections_20260731.csv`. The successor
staged dataset is
`data/staging/name_split_todor_marin_family_20260731/clean_sakhalin_1890_ru_v4_20260717_names_todor_marin_family_staged.csv`,
with its diff and QA evidence in
`outputs/qa/name_split_todor_marin_family_20260731/`. This stage remains
non-canonical.
