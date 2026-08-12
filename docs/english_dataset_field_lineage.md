# Compact English Dataset Field Lineage

## Status

Implemented on 2026-08-09 for `data/analytical/sakhalin_1890_en_v1.csv`.
Canonical Russian v5 remains authoritative and unchanged. The current English
candidate uses the owner-approved one-record Russian staged correction at
`data/staging/archive_code_p000107_20260809/`.

| Order | English field | Canonical source | Transformation |
|---:|:--|:--|:--|
| 1 | `person_id` | `person_id` | Preserved identifier. |
| 2 | `source_position_id` | `source_position_id` | Preserved source-position identifier. |
| 3 | `district` | `district` | Approved controlled translation lookup. |
| 4 | `settlement` | `settlement` | Approved geographic lookup. |
| 5 | `person_seq` | `person_order_in_settlement` | Renamed; integer value preserved. |
| 6 | `household_id` | `household_id` | Preserved text identifier; blank remains blank. |
| 7 | `household_type` | `household_type` | Approved controlled translation lookup. |
| 8 | `legal_status` | `legal_status_norm` | Approved legal-status lookup. |
| 9 | `full_name` | `name_raw` | Approved person-level transliteration lookup keyed by `person_id`. |
| 10 | `sex` | `sex` | Approved controlled translation lookup. |
| 11 | `family_status` | `family_status_norm` | Approved family-status lookup. |
| 12 | `age` | `age` | Integer preserved; recorded zero remains zero. |
| 13 | `age_months` | `age_months` | Integer preserved; recorded zero remains zero. |
| 14 | `religion` | `religion` | Approved controlled translation lookup. |
| 15 | `origin_place` | `origin_place_norm` | Approved geographic lookup; blank remains blank. |
| 16 | `arrival_year` | `arrival_year` | Integer preserved; blank remains blank. |
| 17 | `occupation` | `occupation_norm` | Approved occupation lookup. |
| 18 | `literacy` | `literacy` | Approved controlled translation lookup. |
| 19 | `marital_status` | `marriage_status_norm` | Approved controlled translation lookup. |
| 20 | `living_alone_status` | `living_alone_status` | Approved text lookup; blank is not converted to `FALSE`. |
| 21 | `allowance_status` | `allowance_status` | Approved nullable Boolean: `TRUE`, `FALSE`, or blank. |
| 22 | `illness` | `illness_norm` | Approved illness lookup. |
| 23 | `archive_code` | `notes_raw` | Preserve the archive number and `№`; transliterate `РГБ` → `RGB`, `РГАЛИ` → `RGALI`, and any Cyrillic suffix letter (`а`, `б`, `в`...) to its Latin romanization. Special staged value `ДМЧ (Ялта). КП № 1716.` becomes `DMCh (Yalta). KP № 1716.`. |

All translated populated values must match a versioned approved lookup. Missing
canonical values are exported as empty CSV fields, not placeholder strings.
