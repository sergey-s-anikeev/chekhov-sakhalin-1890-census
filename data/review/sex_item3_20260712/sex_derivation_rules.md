# Item 3 `sex` Derivation Rules

## Proposed vocabulary

- `Мужской`
- `Женский`
- blank when evidence is conflicting or insufficient

The Russian Sentence case vocabulary replaces the tracker’s earlier preliminary English lowercase examples.

## Evidence precedence

1. Explicit gendered wording in the source-preserving `legal_status`, reconciled with an approved `legal_status_norm` correction when the two imply different values.
2. Explicit gendered wording in `family_status`.
3. Reviewed Russian patronymic morphology in `name_raw` only when neither status field supplies explicit evidence.
4. Blank and owner review when explicit fields conflict or the available evidence is insufficient.

## Excluded evidence

Do not infer `sex` from occupation, religion, origin, household number, age, marital status, or demographic expectations. Do not infer from an unfamiliar first name, surname alone, or unreviewed foreign-name assumptions.

## Review safeguard

The initial proposal left all conflicts blank. The owner subsequently approved all 12 unresolved `sex` values. For the 10 grammatical conflicts, the owner-approved sex and `family_status` agreed, so the staged candidate corrects `legal_status` and leaves `family_status` unchanged. `sex_evidence` records the owner-approved derivation path.
