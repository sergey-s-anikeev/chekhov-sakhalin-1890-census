# Limitations

## Source Limitations

This project uses historical person-level census records from 1890. The data reflects the categories, wording, omissions, and administrative logic of the original source.

The analysis should be understood as a structured exploration of recorded census categories, not as a complete reconstruction of lived experience on Sakhalin.

## Extraction Limitations

The project currently uses a searchable PDF text layer. Although this is preferable to OCR, text extraction may still introduce artifacts, including:

- broken words;
- invisible separators;
- incorrect spacing;
- mixed Latin/Cyrillic characters;
- footnote digits attached to field values;
- page headers or repeated headings accidentally captured in text.

These issues are handled through documented cleaning rules and QA checks.

## Historical Category Limitations

Several fields require historical interpretation:

- legal/social status;
- family status;
- religion/confession;
- origin place;
- occupation;
- marriage status.

Cleaned values are analytical standardizations. Raw source values should be preserved wherever possible.

## Geographic Limitations

Settlement names and origin places may not map directly to modern geography.

Historical administrative units are normalized against an 1890 reference framework where possible.

Some origin-place values may remain unresolved and require manual review.

## Data Completeness Limitations

Full-district processing and review are complete for the project's 7,446 recorded people across Alexandrovsky, Tymovsky, and Korsakovsky. The approved Russian v5 and English v1 datasets supersede the earlier sample-validation stage.

Completion of this extraction does not establish that the surviving source covers every person living on Sakhalin in 1890. Describe chart totals as people in the recorded dataset. Field omissions and uneven source coverage remain analytical limitations.

## Data Publication Limitations

The repository contains reviewed person-level datasets, including names. Its current external visibility and the scope of previous publication review have not been independently verified here. The original source PDF remains excluded under the repository policy.

Removing full_name alone does not anonymize the remaining records. Stable IDs, archive references, household membership, and rare attribute combinations can link to named sources. Prefer purpose-specific aggregates for the initial public Tableau dashboard; retain person-level files for local research and practice. See [Tableau preparation and publication](tableau_preparation.md).

Public outputs should prioritize:

- code;
- documentation;
- controlled vocabularies;
- methodology;
- QA reports;
- aggregated data;
- small sample records where appropriate.

## Interpretation Limits

The project maps and analyzes recorded source categories. It does not claim that these categories fully represent identity, lived experience, legal reality, or social status beyond the logic of the historical source.

All cleaned categories are analytical standardizations and should remain traceable to source-derived values.

## Current Project Limitation

English v1 was approved under Decision 38 on 2026-08-09, and the documented MySQL import passed validation. CSV preparation and snapshot reconciliation are documented as of 2026-10-04. Actual Tableau import, interactive filter checks, dashboard validation, and the final public-release selection remain pending.

