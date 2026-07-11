# Approved Item 2 derived-field definitions

## `name_raw`

Source-faithful reviewed name text. It is retained unchanged, including hyphens.

## `name_norm`

An analytical normalized name. For approved women’s hyphenated surname forms, it retains the left component as the maiden surname and removes the hyphen-connected husband surname. It may also apply an approved spacing repair or remove a dangling hyphen. Fixed complex surnames, compound given names, ordinal markers, and ethnic-name constructions remain unchanged unless the owner has explicitly marked a correction.

## `name_alias`

The existing Item 1 alias field. For an approved women’s maiden-surname–husband-surname construction, it receives the right surname component (the husband surname). It may also receive another owner-approved name portion. Existing values are preserved unless an approved Item 2 value is explicitly supplied.

## `name_note`

English review rationale for an approved Item 2 derived-field decision. It does not replace source evidence.

No `surname_alternative` or `surname_alternative_proposed` column is created in the staged dataset.
