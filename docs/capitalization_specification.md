# Capitalization Specification

## Approved rule

Normalized Russian categorical values use **Sentence case**: capitalize the first letter of the value and retain normal lowercase for subsequent words except proper nouns, abbreviations, and identifiers.

Examples:

- `Грамотен`
- `Неграмотен`
- `Образован`
- `Свободного состояния`
- `Сын крестьянина из ссыльных`
- `Армяно-григорианское`

## Scope

Apply Sentence case to controlled categorical fields and approved derived normalized fields, including `legal_status_norm`, `family_status_norm`, `religion`, `literacy`, and future normalized categorical fields.

Do not apply blanket title-casing or capitalization changes to source-preserving or free-text fields. Preserve reviewed capitalization in `name_raw`, `name_alias`, `legal_status`, `family_status`, `origin_place`, `occupation`, `marriage_status`, `illness`, `comments`, and `notes_raw` unless a separate field-specific review explicitly approves a correction.

`comments` may contain lowercase text, uppercase text, abbreviations, names, or sentence fragments as recorded. Lowercase is therefore not restricted to `comments`; it remains valid in every source-preserving or free-text field.

Boolean codes and identifiers are outside Sentence case. Retain approved forms such as `TRUE`, `FALSE`, person identifiers, source-position identifiers, and archival codes.
