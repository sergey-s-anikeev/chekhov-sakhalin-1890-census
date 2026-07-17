# Item 7 additional age verification

This read-only review identifies 49 records with integer `age` greater than 18 and either an explicit child relationship in `family_status_norm` or `legal_status_norm`, or `origin_place` equal to `На Сахалине`.

`origin_place = На Сахалине` is an explicit user-requested review flag. It does not by itself establish an age discrepancy.

These are review prompts, not confirmed errors. Adult sons, daughters, grandchildren, or stepchildren may be historically valid household relationships. Use `page_number` and the raw status fields to verify the source before proposing any correction.
