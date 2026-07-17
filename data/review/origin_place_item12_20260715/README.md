# Item 12 — origin_place profile and proposed review policy

Source: `data\staging\items7_8_age_followup_20260715\clean_sakhalin_1890_ru_v3_20260712_items7_8_staged_v3.csv` (7,446 records; 109 distinct values including blank).

## Proposed policy

- Preserve `origin_place` exactly as the source-facing field.
- Add/use a separate normalized field only after owner approval.
- Map `по пути`, `В пути следования`, and `На пути` to analytical value `В пути`.
- Treat foreign subjecthood separately from Russian administrative origin; do not infer country from ethnicity, religion, or name.
- Retain standard governorate/oblast values as written; review higher-level territories and exceptional values individually.
- Leave blank values blank.

No dataset fields were changed in this profiling step.
