# Project Rules

These rules govern all work on the Sakhalin 1890 Census clean working core.

1. Historical accuracy takes priority over formal consistency.
2. Values must never be fabricated or inferred from indirect evidence.
3. Ambiguous cases must be sent for manual review.
4. Source datasets and approved processed datasets are immutable release artifacts and must not be overwritten in place.
5. Data changes must be implemented through reproducible scripts or explicit, reviewable correction inputs.
6. Before any change, present the proposed plan and identify every affected record.
7. After any change, provide a diff and the applicable QA results.
8. Files must not be deleted without explicit permission from the project owner.
9. Canonical categories, controlled vocabularies, and normalization rules must not be changed autonomously.
10. One work stage must produce one coherent, reviewable set of changes.
11. Russian historical values and normalized dataset values must not be translated merely because the documentation language is English.
12. Documentation, code comments, reports, logs, headings, status messages, and explanatory text must be written in professional English unless the project owner explicitly requests otherwise.

## Operational safeguards

- Never edit a canonical processed CSV manually.
- Preserve stable identifiers, source references, schema order, encoding, and approved district ordering.
- Perform experiments and reproductions only in isolated staging locations.
- Treat QA output as evidence tied to specific file hashes; rerun QA whenever an input changes.
- Do not designate a new canonical file without explicit owner approval.
- Create a new versioned file or release package for every proposed replacement; update the canonical manifest only after review and approval.
- Preserve prior canonical versions as historical records unless the project owner explicitly authorizes their removal.
- Do not delete, move, rename, or overwrite historical project files without explicit owner permission.
