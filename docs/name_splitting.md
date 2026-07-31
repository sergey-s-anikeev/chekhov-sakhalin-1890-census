# Observed personal-name splitting

## Purpose

The pipeline creates three analytical and searchable fields from `name_raw`:

```text
first_name
patronymic_name
last_name
```

It is an observed-name parser. It does not compose surnames or patronymics from
household relationships, `family_status`, presumed parents, or source order
between people.

Implementation files:

- `../scripts/name_split.py` — parser and QA output;
- `../scripts/name_lexicon.csv` — curated given-name evidence;
- `../scripts/name_split_exceptions.csv` — owner-reviewed record exceptions;
- `../scripts/name_split_manual_exceptions_20260723.csv` — 79 owner-reviewed
  Muslim-name decisions from the full-dataset review;
- `../scripts/name_raw_corrections_patronymic_review_20260723.csv` — four
  owner-reviewed upstream spelling corrections;
- `../scripts/name_split_patronymic_review_exceptions_20260723.csv` — twelve
  reviewed patronymic, compound-name, unknown-name, and restored Jewish-name
  decisions;
- `../scripts/name_first_name_review_decisions_20260723.csv` — complete log of
  24 reviewed first-name QA decisions;
- `../scripts/name_split_first_name_review_exceptions_20260723.csv` — seven new
  first-name and placeholder corrections applied by the parser;
- `../scripts/name_split_manual_overrides_20260723.csv` — dated manual
  `name_raw`/`name_alias` decisions;
- `../scripts/apply_name_split_manual_review.py` — applies those decisions by
  `person_id` before splitting;
- `../scripts/test_name_split.py` — regression tests.

## Required upstream normalization

Run the splitter only after the reviewed `name_raw` normalization stage. The
current input is:

```text
../data/staging/name_raw_four_component_ordinal_20260720/
clean_sakhalin_1890_ru_v4_20260717_name_raw_staged.csv
```

That stage:

- separates approved fourth-token surname aliases into `name_alias`;
- preserves owner-approved multi-part names;
- normalizes ordinal markers to forms such as `1-й`, `2-й`, and `2-я`;
- corrects `P000064` to `Василий Герасимов`;
- leaves complex Muslim and uncertain multi-given names source-faithful.

The splitter never changes `name_raw` or `name_alias`.

## Design principles

1. Source order is the default.
2. Directly observed values and reviewed exceptions are allowed.
3. Family-derived name components are forbidden in this pipeline.
4. Two-token names do not require lexicon recognition.
5. Complex Muslim structures are reviewed manually.
6. A second given name is never silently converted into a patronymic.
7. Rare exceptions are explicit and auditable rather than broad heuristics.
8. Uncertain structures remain outside accepted analytical results through
   `manual_review` or `ambiguous` status; tentative components are explicitly
   marked `observed_tentative`.
9. Catholic and Lutheran names preserve source order; given-name recognition
   alone never causes reordering.

## Input columns

Required columns are:

| Column | Use |
|---|---|
| `person_id` | Stable identity and reviewed-exception key |
| `name_raw` | Upstream-normalized source name |
| `sex` | Given-name and morphology context |
| `religion` | Naming-model and manual-routing context |

`name_alias` is preserved as input context. It is not parsed or substituted
unless an explicit owner-reviewed exception authorizes that behavior.

The parser intentionally does not require `family_status`, `household_id`,
`mother_id`, or `father_id`.

## Preparation

The parser normalizes whitespace and edge punctuation in an internal copy.
Hyphens remain part of the name token.

Ordinal tokens are ignored for structural parsing:

```text
1-й  2-й  3-й  1-я  2-я
```

They remain unchanged in `name_raw`.

## Naming models

`religion` maps to a contextual naming model:

| Evidence | Model |
|---|---|
| Orthodox, Old Believer, Schismatic, Molokan | `russian_historical` |
| Catholic or Roman Catholic | `catholic` |
| Lutheran | `lutheran` |
| Muslim or Mohammedan | `muslim` |
| Jewish or Armenian Gregorian | `other_documented` |
| Other or blank | `unknown` |

Religion is not treated as ethnicity and does not reorder an otherwise clear
two-token name.

## Parsing rules

Rules are evaluated in the order below.

### 1. Reviewed exceptions

`name_split_exceptions.csv` takes precedence. Each exception matches
`person_id` and the expected normalized `name_raw`; aliases are also validated
when relevant.

Current exception classes include:

- compound Catholic/Polish given name;
- non-Russian triple given name;
- Korean/Chinese compound surname;
- exceptional infant-name structure;
- an owner-reviewed alias used as the analytical primary name.

Example:

```text
P001550
name_raw         = Август Вильгельм Генрих Меллартек
first_name       = Август Вильгельм Генрих
patronymic_name  = [empty]
last_name        = Меллартек
```

### 2. Complex Muslim names

A Muslim/Mohammedan name containing three or more semantic tokens is not split
automatically. The record receives:

```text
parse_status         = manual_review
parse_rule           = complex_muslim_manual
manual_review_reason = complex_muslim_name_requires_manual_splitting
```

Straightforward two-token Muslim names still use `First + Last`:

Hyphenated two-token Muslim names are an exception. Hyphenation can conceal
particles or multiple semantic elements, so all such records receive
`hyphenated_two_token_muslim_manual` and must be reviewed.

The controlling owner rule for all Muslim names is:

1. accept `first_name + last_name` only when both components are identifiable;
2. if a reliable split is not possible, place the complete `name_raw` string in
   `last_name` and leave `first_name` and `patronymic_name` empty;
3. use `first_name` only only when the complete source value is explicitly
   confirmed as a given name;
4. do not populate `patronymic_name` for Muslim structures.

The consolidated 2026-07-23 re-review contains all 197 Muslim records and
includes the 13 hyphenated two-token cases. The completed decisions produce:

- 122 `first_name + last_name` records;
- 68 records with the complete `name_raw` in `last_name`;
- 7 `first_name`-only records;
- zero Muslim patronymics.

The consolidated source is `name_split_muslim_review_all_20260723.csv`. It
supersedes the earlier 79-record Muslim exception file. All 197 records now
receive reviewed-exception provenance, including otherwise straightforward
two-token names.

The final 13 single-token ambiguous records were subsequently reviewed without
component changes and accepted as surnames. They are stored in
`name_split_ambiguous_review_exceptions_20260723.csv` with
`reviewed_single_token_last` provenance.

The fully reviewed staged dataset contains 7,446 observed records, with no
ambiguous, manual-review, unresolved, or hard-QA cases.

```text
Абдул-Малик Джаксамбетов
```

### 3. One semantic token

If the token is a curated given name:

```text
first_name = token
patronymic_name = [empty]
last_name = [empty]
```

No family surname or patronymic is added.

The reviewed descriptor `Некрещеная` is stored in `last_name`. An unrecognized
non-Muslim single token is tentatively stored as `last_name` with an ambiguous
status. An unrecognized Muslim single token is sent to manual review.

### 4. Two semantic tokens

Default order:

```text
First + Last
```

This rule does not require lexicon recognition and supports hyphenated tokens.
For Catholic and Lutheran records, source order is always retained unless an
owner-reviewed exception provides contrary evidence. This prevents a familiar
second token from incorrectly reversing an unfamiliar first token.

For other naming models, if only the second token is a curated first name, the
parser uses:

```text
Last + First
```

No patronymic is populated for a two-token name.

### 5. Three semantic tokens

Default order:

```text
First + Patronymic + Last
```

When exactly the second token is identifiable as the first name, use:

```text
Last + First + Patronymic
```

When exactly the third token is identifiable as the first name, use:

```text
Patronymic + Last + First
```

#### Catholic and Lutheran names

Catholic and Lutheran records use a source-order rule before the general
three-token order detector. These populations contain both Russianized
patronymics and compound European given names.

If the middle token has clear historical patronymic morphology, accept:

```text
First + Patronymic + Last
```

Examples include `Францов`, `Юганов`, `Казимиров`, `Людвигов`, `Францова`,
and standard long forms ending in `-ович`, `-евич`, `-овна`, or `-евна`.
The result receives:

```text
parse_rule       = catholic_lutheran_patronymic
parse_status     = observed
parse_confidence = high
```

If the middle token is not patronymic-like, interpret the first two tokens as
a tentative compound given name and the final token as the tentative surname:

```text
first_name       = token 1 + token 2
patronymic_name  = [empty]
last_name        = token 3
parse_rule       = catholic_lutheran_compound_given_manual
parse_status     = manual_review
parse_confidence = medium
```

Both populated components receive `observed_tentative` provenance. This is a
review proposal, not an accepted analytical result. Once approved, the record
is added to `name_split_exceptions.csv` and becomes an observed reviewed
exception.

Approved examples from the second 200-record review are:

```text
Ян Генрих Биндер           -> Ян Генрих / [empty] / Биндер
Замель Ян Радзин           -> Замель Ян / [empty] / Радзин
Мац Иоганов Лектор Лехтола -> Мац Иоганов Лектор / [empty] / Лехтола
```

#### Two consecutive given names

If the first and second tokens are both curated given names and the second is
not already patronymic-like, the parser does not accept a patronymic silently.

For the Russian historical model it produces a review proposal:

```text
Федор Иван Храпылин

first_name                  = Федор
patronymic_name             = [empty]
last_name                   = Храпылин
patronymic_name_proposed    = Иванов
parse_status                = manual_review
```

The proposed patronymic is excluded from the three accepted analytical fields
until owner review.

For Jewish, Armenian, Muslim, or unknown models, no Russian patronymic is
proposed. The record is flagged as a possible compound given name. Catholic
and Lutheran records follow the dedicated source-order rule above.

### 6. Four or more semantic tokens

For Catholic and Lutheran records, all tokens except the last are populated as
a tentative compound `first_name`; the last token is populated as a tentative
`last_name`. The result receives `catholic_lutheran_multi_given_manual`, medium
confidence, and manual-review status. Reviewed records are promoted through the
exception table.

Other unreviewed four-or-more-token structures are sent to manual review with
blank components. They are not automatically interpreted as
`First + Patronymic + Last + Alias`; alias separation belongs to the upstream
normalization stage.

## Output fields

| Field | Description |
|---|---|
| `first_name` | Accepted observed/reviewed given name; may contain reviewed compound given names |
| `patronymic_name` | Accepted observed patronymic |
| `last_name` | Accepted observed/reviewed surname |
| `first_name_source` | `observed`, `observed_tentative`, or `reviewed_exception` |
| `patronymic_source` | Component provenance |
| `last_name_source` | Component provenance |
| `parse_status` | `observed`, `ambiguous`, `manual_review`, or `unresolved` |
| `parse_confidence` | `high`, `medium`, or `low` |
| `parse_rule` | Deterministic rule identifier |
| `name_order_detected` | Accepted source order |
| `naming_model` | Religion-derived context |
| `manual_review_reason` | Reason an owner decision is required |
| `patronymic_name_proposed` | Nonaccepted Russian short-patronymic proposal |
| `proposal_rule` | Rule that produced the proposal |

There are no `inferred_from_father`, `inferred_from_mother`, or household-derived
provenance values.

## Reproducible run

From the repository root:

```powershell
python scripts/apply_name_split_manual_review.py `
  data/staging/name_raw_four_component_ordinal_20260720/clean_sakhalin_1890_ru_v4_20260717_name_raw_staged.csv `
  data/staging/name_split_manual_review_20260723/normalized_input.csv `
  scripts/name_split_manual_overrides_20260723.csv `
  --diff-output outputs/qa/name_split_manual_review_20260723/manual_review_applied_diff.csv

python scripts/name_split.py `
  data/staging/name_split_manual_review_20260723/normalized_input.csv `
  data/staging/name_split_manual_review_20260723/clean_sakhalin_1890_ru_v4_20260717_names_staged.csv `
  --qa-dir outputs/qa/name_split_manual_review_20260723 `
  --fail-on-qa-error
```

Run regression tests after any rule, lexicon, or exception change:

```powershell
python scripts/test_name_split.py
```

The parser uses only the Python standard library and writes UTF-8 CSV with a
BOM.

The final 2026-07-23 staged candidate contains 7,446 records and passes all hard
QA checks. It incorporates the upstream/manual normalization decisions, the
complete 197-record Muslim-name re-review, first-name corrections, patronymic
corrections, restored Jewish-name decisions, and the final 13 single-token
surname approvals. All 7,446 records have `parse_status = observed`; no records
remain `ambiguous`, `manual_review`, or `unresolved`.

The audit command for accepted first names is:

```powershell
python scripts/qa_first_name_spelling.py `
  data/staging/name_split_manual_review_all_20260723/clean_sakhalin_1890_ru_v4_20260717_names_staged.csv `
  outputs/qa/name_split_manual_review_all_20260723/first_name_spelling_candidates.csv `
  --summary outputs/qa/name_split_manual_review_all_20260723/first_name_spelling_summary.json
```

This audit is non-destructive. It proposes nearby curated spellings and flags
placeholders/redactions, but does not correct the staged dataset. Historical
variants and non-Russian names must be owner-reviewed before promotion to an
exception.

## QA artifacts

With `--qa-dir`, the parser writes:

| Artifact | Purpose |
|---|---|
| `name_split_qa_summary.json` | Status/rule counts and hard-check result |
| `name_split_qa_issues.csv` | Structural validation failures |
| `name_split_manual_review.csv` | Manual, ambiguous, and unresolved records |
| `first_name_spelling_candidates.csv` | Non-destructive spelling/placeholder review queue for accepted first names |

Hard QA verifies:

1. only controlled parse statuses are emitted;
2. every populated component has matching provenance;
3. no family-inferred provenance exists;
4. every manual-review record has a reason;
5. reviewed exceptions match their expected input values.

The regression suite includes owner-reviewed examples for:

- standard Russian three-part names;
- two-token source order without lexicon recognition;
- alternate `Last + First + Patronymic` order;
- ordinal tokens in different positions;
- standalone children without family enrichment;
- single-token surnames and `Некрещеная`;
- simple and complex Muslim names;
- flagged second-given-name patronymic proposals;
- Catholic and Lutheran compound-given-name handling;
- Catholic and Lutheran source-order preservation and Russianized patronymics;
- reviewed Korean/Chinese and alias exceptions.

## Statistical use

Primary first-name and surname rankings should use:

```text
parse_status = observed
component source = observed or reviewed_exception
```

Do not include `patronymic_name_proposed` in published patronymic frequencies or
search indexes until it has been reviewed and promoted to an accepted value.

Report `manual_review`, `ambiguous`, and `unresolved` counts as data-quality
categories.

## Search use

Search filters may index accepted `first_name`, `patronymic_name`, and
`last_name`. Keep `name_alias` as a separate searchable field. Search results
should display `name_raw`, `person_id`, component provenance, and parse status.

Comparison keys may be case-folded and optionally treat `е`/`ё` as equivalent,
but historical display values must remain unchanged.
