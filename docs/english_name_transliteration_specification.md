# English Personal-Name Transliteration Specification

## Status

Approved by the project owner on 2026-08-02 for Item 4 of the compact English
analytical dataset.

## Standard

Use a simplified ASCII implementation of the BGN/PCGN Russian romanization
system for compact English `full_name` values.

The simplification is intentional:

- use ordinary Latin characters suitable for CSV, MySQL, and Tableau;
- do not use diacritics, prime marks, typographic quotation marks, or middle
  dots;
- omit soft and hard signs from the output while applying the approved
  transliteration of surrounding letters;
- use `yo` for `ё` if it occurs in a future canonical version;
- retain `person_id` as the reliable link to the authoritative Cyrillic value.

This is an analytical-display standard rather than a fully reversible scholarly
transliteration. The canonical Russian dataset remains authoritative.

## Core rules

1. Generate `full_name` from canonical `name_raw`.
2. Preserve token order exactly, except for the approved formatting of numbered
   disambiguators.
3. Transliterate personal names; do not translate, modernize, correct, or infer
   them.
4. Preserve hyphens inside names.
5. Preserve existing Latin initials and periods.
6. Preserve source masking such as `***`.
7. Use conventional capitalization for each name token.
8. Do not infer missing components or expand initials.
9. Produce one nonblank `full_name` for every populated `name_raw`.
10. Require zero accidental Cyrillic characters in final `full_name` values.

## Principal letter forms

The implementation will follow simplified BGN/PCGN forms including:

| Cyrillic | ASCII output |
|:--:|:--|
| `Ж ж` | `Zh zh` |
| `Й й` | `Y y` |
| `Х х` | `Kh kh` |
| `Ц ц` | `Ts ts` |
| `Ч ч` | `Ch ch` |
| `Ш ш` | `Sh sh` |
| `Щ щ` | `Shch shch` |
| `Ы ы` | `Y y` |
| `Э э` | `E e` |
| `Ю ю` | `Yu yu` |
| `Я я` | `Ya ya` |
| `Ь ь` | omitted |
| `Ъ ъ` | omitted |

`Е е` uses `Ye ye` initially and in the positional contexts defined by the
BGN/PCGN system; otherwise it uses `E e`. The implementation must include
unit-tested examples before release.

## Approved examples

| Canonical `name_raw` | English `full_name` |
|:--|:--|
| `Иван Иванов` | `Ivan Ivanov` |
| `Емельян Ипполитов` | `Yemelyan Ippolitov` |
| `Авдотья` | `Avdotya` |
| `Илья` | `Ilya` |
| `Юрий` | `Yuriy` |
| `Федор` | `Fedor` |
| `Харитон` | `Khariton` |
| `Щербаков` | `Shcherbakov` |
| `Абдул-Малик Джаксамбетов` | `Abdul-Malik Dzhaksambetov` |
| `N. N. Генальский` | `N. N. Genalskiy` |
| `Вик*** Негилев` | `Vik*** Negilev` |

## Numbered-name rule

Convert Russian ordinal disambiguators such as `1-й`, `2-й`, `1-я`, and `2-я`
to neutral parenthetical identifiers while preserving their position:

| Canonical `name_raw` | English `full_name` |
|:--|:--|
| `Андрей Иванов 1-й` | `Andrey Ivanov (1)` |
| `Анна 2-я Петрова` | `Anna (2) Petrova` |

The number distinguishes otherwise similar source records and must not be
discarded.

## Approved descriptive non-name exception

Canonical `Человек неизвестного звания` is descriptive text rather than a
personal name. Translate it as:

`Person of unknown rank`

This exception must be implemented through an explicit reviewed lookup rather
than the general transliteration function.

## Exception review scope

Before release, create and review an inventory covering:

- Muslim and other non-Russian naming traditions;
- Catholic, Lutheran, Jewish, and Armenian names;
- names with four or more tokens;
- one-token records;
- hyphenated names;
- Latin initials or mixed scripts;
- masked characters and unusual punctuation;
- numbered disambiguators;
- the approved descriptive non-name exception;
- any transliteration collisions where different Cyrillic values produce the
  same Latin value.

The exception lookup takes precedence over the general transliteration
function and must remain versioned and auditable.

## Quality requirements

- exactly 7,446 output names and no blank `full_name` values;
- exact one-to-one reconciliation by `person_id` to canonical `name_raw`;
- zero unapproved Cyrillic characters;
- preservation of approved punctuation, masking, numbering, and token order;
- inventory and owner review of all exception classes;
- collision report for distinct Cyrillic names mapping to the same English
  name;
- reproducible script, reviewed lookup, and versioned QA evidence.

## References

- BGN/PCGN 1947 Russian romanization system, checked in November 2022:
  https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1116602/ROMANIZATION_OF_RUSSIAN_2022_final.pdf
- Library of Congress ALA-LC Romanization Tables:
  https://www.loc.gov/catdir/cpso/roman
- ISO 9:1995 overview:
  https://www.iso.org/standard/3589.html

