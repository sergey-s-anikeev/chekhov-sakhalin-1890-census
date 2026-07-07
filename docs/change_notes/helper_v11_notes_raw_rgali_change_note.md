# Helper Script Update: `notes_raw` Archive Prefix Normalization

## Change

`normalize_notes_raw()` now supports two archive/source prefixes:

- `РГБ № <number>`
- `РГАЛИ № <number>`

The function also normalizes spacing artifacts introduced during PDF extraction:

```text
РГ Б № 4568   -> РГБ № 4568
РГ АЛИ № 146 -> РГАЛИ № 146
РГАЛИ №146   -> РГАЛИ № 146
```

## Validation update

`validate_output_csv()` now accepts both:

```text
РГБ № <number>
РГАЛИ № <number>
```

in the `notes_raw` field.

## Additional related fix

While testing the update, `normalize_household_number()` was also corrected so that numeric household numbers are not treated as trailing footnote digits.

Correct behavior:

```text
2. 26. -> 26
26     -> 26
```

This protects `household_number` and `source_position_id` during future district-level production runs.

## Test example

Input:

```text
РГ АЛИ № 146
```

Output:

```text
РГАЛИ № 146
```
