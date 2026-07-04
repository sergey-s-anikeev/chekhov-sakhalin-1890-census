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

The current workflow is being validated on an extraction sample before scaling to the full source.

Until full extraction is complete, the dataset should not be interpreted as a complete population database.

## Data Publication Limitations

The full raw PDF and full person-level dataset are not published until copyright, access, and ethical considerations are reviewed.

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

The extraction workflow has been designed, but it still needs validation on a 300–500 record sample before scaling to the full dataset.

