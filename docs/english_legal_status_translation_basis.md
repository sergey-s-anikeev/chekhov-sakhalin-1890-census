# English Legal-Status Translation Basis

## Purpose

This note records the authoritative project history that must guide Batch B
English translation of canonical `legal_status_norm` values.

## Prior approved Russian normalization work

Item 17 of the Russian normalization review established the complete controlled
`legal_status_norm` vocabulary. The owner approved 100 source-value mappings,
including blank, with zero unmapped records. The review deliberately preserved
gender distinctions among penal-convict, exile-settler, peasant-from-exile, and
child/parent forms. It also normalized the feminine settler form as `Поселка`
and related forms such as `Сын поселки`.

Authoritative evidence:

- `data/review/legal_status_item17_20260712/legal_status_norm_approved_mapping.csv`
- `data/review/legal_status_item17_20260712/owner_response/legal_status_review_owner.xlsx`
- `docs/normalization_review_tracker.md`, Item 17 progress entries

These Russian distinctions must not be collapsed silently in English. Each of
the 61 canonical normalized values requires an explicit English mapping.

## Earlier complete English translation-options workbook

The earlier workbook
`outputs/translation_review_20260716/sakhalin_1890_english_translation_options.xlsx`
contains three English variants for the complete legal-status vocabulary:

- Variant A — historically explicit analytical English, recommended;
- Variant B — compact dashboard labels;
- Variant C — publication-aligned or literary wording.

Initial reconciliation on 2026-08-02 confirmed that all 61 current canonical v5
`legal_status_norm` values match values in that workbook exactly, with zero
missing and zero extra legal-status values. Variant A therefore supplied the
starting Batch B1 proposals for owner review.

## Previously documented English terminology

`docs/language_translation_strategy.md` already records these examples:

| Russian normalized value | Previously documented English value |
|:--|:--|
| `Ссыльнокаторжный` | `Penal Convict` |
| `Поселенец` | `Exile Settler` |

For the compact dataset's approved sentence-case convention, these seed terms
become `Penal convict` and `Exile settler` unless the owner explicitly revises
them during Batch B review.

## Required Batch B rules

1. Use the owner-approved Russian `legal_status_norm` vocabulary as the source,
   not raw `legal_status` variants.
2. Preserve gender and family-relation distinctions in the mapping table even
   when an English noun is gender-neutral.
3. Preserve distinctions between penal convicts, exile settlers,
   peasants originating from the exile population, administrative exiles,
   free-status persons, military ranks, civil ranks, and occupations appearing
   as legal status.
4. Use sentence case in final English analytical values.
5. Flag historical Imperial Russian ranks and ambiguous social categories for
   focused owner review.
6. Do not merge categories solely to make Tableau display simpler. Any later
   analytical grouping must be a separate derived classification.

## Status

Reviewed on 2026-08-02 before preparation of the Batch B English proposals.
Owner decisions were applied on 2026-08-05: 12 Variant A selections, 12 Variant
B selections, 3 Variant C selections, and 34 owner revisions. The resulting 61
mappings reconcile exactly to canonical v5, with zero missing values, extra
values, or record-count mismatches. Batch B1 legal-status translation is
approved; broader analytical grouping, if later desired, remains a separate
derived classification.

Controlled relationship labels follow an article-free pattern. Accordingly,
`Дочь солдатки` and `Сын солдатки` both use `Child of soldier's wife`, while
`Жена врача` uses `Wife of doctor`.
