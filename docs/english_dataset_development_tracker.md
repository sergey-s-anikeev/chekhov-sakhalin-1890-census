# English Dataset Development Tracker

## Purpose

Develop a compact English-only analytical dataset derived from canonical
`v5_20260731` for MySQL analysis, Tableau visualization, and an international
portfolio audience.

The Russian canonical dataset remains authoritative. The English dataset is a
separate derived analytical product and must never overwrite or replace the
canonical Russian files.

## Status Key

- `[x]` Approved and completed
- `[~]` In progress
- `[ ]` Pending
- `[R]` Ready for owner review
- `[B]` Blocked pending owner decision or evidence

## Development Rules

1. Build only from `data/processed/clean_sakhalin_1890_ru_v5_20260731.csv`.
2. Preserve `person_id` and sufficient source traceability in every derived row.
3. Translate categories and geographic values through explicit reviewed lookup
   tables, not ad hoc row-level substitutions.
4. Transliterate personal names consistently; never translate personal names.
5. Preserve all 7,446 records unless the owner explicitly approves a filtered
   analytical product.
6. Do not infer missing historical values during translation.
7. Keep SQL `NULL` handling distinct from meaningful values such as `FALSE`,
   `0`, `Unknown`, or `Not recorded`.
8. Produce versioned outputs, complete QA evidence, hashes, and reconciliation
   to canonical v5.
9. Do not generate the English dataset until the compact column set is approved.

## 1. Analytical-Layer Direction — `[x]` Approved and completed

- [x] Select a compact English-only dataset as the preferred downstream format.
- [x] Confirm that canonical `v5_20260731` remains Russian and authoritative.
- [x] Confirm MySQL and Tableau as the primary target applications.
- [x] Record the decision in `docs/decision_log.md` and
  `docs/language_translation_strategy.md`.

## 2. Compact Column Selection — `[x]` Approved and completed

- [x] Profile every canonical v5 column for analytical value, traceability, and
  redundancy.
- [x] Prepare recommended `Include`, `Exclude`, or `Canonical only`
  classifications for all 50 fields.
- [x] Prepare proposed English field names, rationales, populated/blank counts,
  distinct counts, and representative values.
- [x] Create the owner-review workbook with editable decisions and a live
  completion summary.
- [x] Retain `source_position_id` for audit traceability.
- [x] Include one combined `full_name`, sourced from canonical `name_raw`;
  retain split name components in canonical only.
- [x] Retain `name_alias` in canonical only.
- [x] Include `household_id` and `household_type`; retain
  `household_details` in canonical only.
- [x] Retain `age_months` for infant and young-child precision.
- [x] Use normalized analytical fields in the compact layer and retain their
  detailed counterparts in canonical only.
- [x] Retain free-text `comments`, `household_details`, and detailed `illness`
  in canonical only; include normalized `illness_norm` as `illness`.
- [x] Approve final English column names, order, and definitions.

Completion gate: the project owner approves one exact compact schema before
translation or dataset generation begins.

Approved compact schema (23 fields, in output order):

| Order | Canonical source field | English output field |
|---:|:--|:--|
| 1 | `person_id` | `person_id` |
| 2 | `source_position_id` | `source_position_id` |
| 3 | `district` | `district` |
| 4 | `settlement` | `settlement` |
| 5 | `person_order_in_settlement` | `person_seq` |
| 6 | `household_id` | `household_id` |
| 7 | `household_type` | `household_type` |
| 8 | `legal_status_norm` | `legal_status` |
| 9 | `name_raw` | `full_name` |
| 10 | `sex` | `sex` |
| 11 | `family_status_norm` | `family_status` |
| 12 | `age` | `age` |
| 13 | `age_months` | `age_months` |
| 14 | `religion` | `religion` |
| 15 | `origin_place_norm` | `origin_place` |
| 16 | `arrival_year` | `arrival_year` |
| 17 | `occupation_norm` | `occupation` |
| 18 | `literacy` | `literacy` |
| 19 | `marriage_status_norm` | `marital_status` |
| 20 | `living_alone_status` | `living_alone_status` |
| 21 | `allowance_status` | `allowance_status` |
| 22 | `illness_norm` | `illness` |
| 23 | `notes_raw` | `archive_code` |

All other canonical fields remain available in canonical v5 but are omitted
from the compact English dataset. The five explicitly excluded technical fields
are `district_code`, `parse_status`, `parse_confidence`,
`patronymic_name_proposed`, and `proposal_rule`.

Owner-review workbook:

`outputs/english_dataset_column_review_20260802/english_compact_column_review_20260802.xlsx`

## 3. English Value and NULL Specification — `[x]` Approved and completed

Approved rule:

- Missing values will be exported as empty CSV fields. The CSV will not contain
  placeholder strings such as `NULL`, `N/A`, or `Not recorded` merely to
  represent missingness.
- Meaningful values such as numeric `0` and Boolean `FALSE` must not be changed
  to blanks.
- MySQL loading logic will convert empty nullable fields to SQL `NULL`.
- Tableau may apply reader-friendly display labels without changing the stored
  source value.
- `allowance_status` will remain Boolean: CSV `TRUE` means yes, CSV `FALSE`
  means no, and a blank means missing. MySQL will store these as nullable
  Boolean values (`1`, `0`, and `NULL`), while Tableau may display `Yes`, `No`,
  and `Not recorded` as presentation labels.
- `age = 0` is a valid recorded numeric value and must remain distinct from a
  blank age.

- [x] Define the distinction between blank source values and English values such
  as `Unknown`, `Not recorded`, `Not applicable`, and `No`.
- [x] Define MySQL-compatible data types and nullable fields.
- [x] Define Boolean representation for CSV, MySQL, and Tableau.
- [x] Define capitalization rules for English categories.
- [x] Define punctuation and delimiter rules for compound categories.
- [x] Approve field-level examples and edge cases.

Approved specification:

`docs/english_dataset_value_null_specification.md`

## 4. Personal-Name Transliteration — `[x]` Approved and completed

- [x] Select one transliteration standard suitable for an English-language
  portfolio and historical Russian names.
- [x] Define treatment of soft and hard signs, `Ё`, historical spellings,
  hyphens, initials, and non-Russian naming traditions.
- [x] Define how canonical `name_raw` is converted into compact English
  `full_name`, including multi-token names and numbered disambiguators.
- [x] Review the non-standard `name_raw` value `Человек неизвестного звания`
  before generating `full_name`.
- [x] Create a reproducible transliteration script or reviewed name lookup.
- [x] Produce a targeted review inventory for ambiguous or exceptional names.
- [x] Confirm that every populated canonical `name_raw` maps to one English
  `full_name` without changing the underlying historical value.

Approved specification:

`docs/english_name_transliteration_specification.md`

Owner-review workbook:

`outputs/english_name_transliteration_review_20260802/english_name_transliteration_review_20260802.xlsx`

Candidate and QA status:

- 7,446 candidate names generated;
- zero blank candidates;
- zero Cyrillic characters remaining;
- zero collisions between distinct canonical names;
- 44 high-priority records reviewed by the owner;
- 1,295 broadly flagged exception records retained in the extended inventory.

Owner review completed with 41 approvals and 3 revisions. The approved staged
mapping is:

`outputs/english_name_transliteration_review_20260802/name_transliteration_staged_20260802.csv`

Approved owner revisions:

- `P001151` → `Lyubov Aleksandrova Vetskaya`;
- `P004592` → `Fedot Larionov Masyukevich`;
- `P005221` → `Iogan Peters`.

Deferred Russian canonical dependency:

- [ ] Before the next Russian canonical release, run a mixed Cyrillic–Latin
  character audit across all name-bearing fields. Distinguish accidental Latin
  lookalikes embedded in Cyrillic words from intentional Latin initials such as
  `N. N.`. Known accidental cases include `P001151`, `P004592`, and `P005221`.

- [ ] During the same Russian-version review, run Unicode punctuation
  normalization across controlled geographic values. Reconcile
  `Санкт-Петербургская губерния` (hyphen-minus, `U+002D`) and
  `Санкт‑Петербургская губерния` (non-breaking hyphen, `U+2011`) to the single
  canonical form `Санкт-Петербургская губерния`. Stage and QA the correction
  before the next Russian canonical release; canonical v5 remains unchanged
  during the English review.

## 5. Controlled Category Translation — `[x]` Complete

Item 5 is divided into two review batches:

- **Batch A — Approved:** 38 values covering district,
  household type, sex, religion, literacy, marital status, living-alone status,
  and allowance status. The owner approved 37 proposals and revised
  `Раскольничество` from `Schismatic (historical term)` to `Schismatic`.
- **Batch B — Approved:** 258 values covering legal status, family status,
  occupation, and illness. All four domains are owner-approved and reconciled
  to canonical v5 with zero missing or extra populated values.

Owner-review workbook:

`outputs/english_controlled_translation_review_20260802/controlled_category_translation_review_20260802.xlsx`

Approved Batch A mapping:

`outputs/english_controlled_translation_review_20260802/controlled_translation_batch_a_approved_20260802.csv`

Legal-status translation basis reviewed before Batch B drafting:

`docs/english_legal_status_translation_basis.md`

Batch B1 legal-status owner review (61 values; exact reconciliation to the
earlier three-variant workbook):

`outputs/english_controlled_translation_review_20260802/legal_status_translation_review_20260802.xlsx`

Approved Batch B1 mapping and reconciliation:

`outputs/english_controlled_translation_review_20260802/legal_status_translation_approved_20260805.csv`

`outputs/english_controlled_translation_review_20260802/legal_status_translation_reconciliation_20260805.json`

Family-status safeguard: `Совладелица` is explicitly counted in Batch B with
8 canonical records. It occurs in `family_status` and `family_status_norm`, not
in `legal_status_norm`. The mixed-script spelling `Cовладелица` (Latin `C`) has
zero occurrences and must not be introduced into the English lookup source.

Batch B2 family-status owner review (37 values; exact reconciliation to the
earlier three-variant workbook):

`outputs/english_controlled_translation_review_20260802/family_status_translation_review_20260805.xlsx`

Approved Batch B2 family-status mapping and reconciliation:

`outputs/english_controlled_translation_review_20260802/family_status_translation_approved_20260809.csv`

`outputs/english_controlled_translation_review_20260802/family_status_translation_reconciliation_20260809.json`

Batch B3 occupation owner review (135 values; complete fresh proposal set with
12 ambiguous, historical, dependency-status, or workplace descriptions flagged
for focused review):

`outputs/english_controlled_translation_review_20260802/occupation_translation_review_20260805.xlsx`

Approved Batch B3 occupation mapping and reconciliation:

`outputs/english_controlled_translation_review_20260802/occupation_translation_approved_20260808.csv`

`outputs/english_controlled_translation_review_20260802/occupation_translation_reconciliation_20260808.json`

Batch B4 illness owner review (25 values; exact reconciliation to the earlier
three-variant workbook):

`outputs/english_controlled_translation_review_20260802/illness_translation_review_20260805.xlsx`

Approved Batch B4 illness mapping and reconciliation:

`outputs/english_controlled_translation_review_20260802/illness_translation_approved_20260805.csv`

`outputs/english_controlled_translation_review_20260802/illness_translation_reconciliation_20260805.json`

Create complete Russian-to-English lookup tables for every approved included
categorical field. Candidate domains include:

- [x] district;
- [x] household type;
- [x] sex;
- [x] legal status;
- [x] family status;
- [x] religion;
- [x] occupation;
- [x] literacy;
- [x] marriage status;
- [x] living-alone status;
- [x] allowance status;
- [x] illness category.

For each lookup:

- [x] inventory every distinct Russian value, including blank;
- [x] propose one English value;
- [x] preserve historical distinctions unless the owner approves grouping;
- [x] identify gender-specific Russian categories and decide whether the compact
  English layer retains or consolidates them;
- [x] review all proposed mappings;
- [x] record owner decisions in versioned lookup tables;
- [x] verify zero unmapped populated values.

## 6. Geographic Translation and Transliteration — `[x]` Complete

- [x] Inventory all included district, settlement, and origin-place values.
- [x] Choose consistent English forms for districts and settlements.
- [x] Translate administrative units such as governorates and oblasts while
  transliterating proper names.
- [x] Preserve distinctions among specific places, broad regions, transit
  statuses, foreign subjecthood, and `On Sakhalin`-type values.
- [x] Review ambiguous historical toponyms separately.
- [x] Create approved geographic lookup tables with zero unmapped values.

Owner-review workbook created on 2026-08-09:
`outputs/english_geographic_translation_review_20260809/geographic_translation_review_20260809.xlsx`.
The canonical inventory contains 3 district labels (already approved in Item 5
Batch A), 51 settlement labels, and 100 populated normalized origin-place
labels. The 838 blank `origin_place_norm` records remain blank. The owner
approved all 151 settlement/origin labels: 148 proposals accepted and 3
revised. Versioned district, settlement, and origin-place lookup tables
reconcile with zero unmapped populated values. Item 6 is complete; the next
workstream is Item 7, English Dataset Build.

## 7. English Dataset Build — `[x]` Complete

- [x] Create a reproducible build script using canonical v5 and approved lookup
  tables only.
- [x] Generate a versioned output under `data/analytical/`.
- [x] Use English column names and the approved compact column order.
- [x] Preserve exactly one output row per canonical `person_id`.
- [x] Apply approved MySQL-compatible NULL and Boolean rules.
- [x] Never modify canonical v5 during the build.
- [x] Generate a field-level transformation specification and source lineage.

Provisional output name:

Implemented output:

`data/analytical/sakhalin_1890_en_v1.csv`

Build result (2026-08-09): 7,446 records, 23 approved columns, 7,446
unique `person_id` values, 7,446 unique `source_position_id` values, zero
unmapped populated values, and zero Cyrillic characters in the English output.
Archive prefixes are transliterated as `РГБ` → `RGB` and `РГАЛИ` → `RGALI`,
while archive numbers remain unchanged. Nullable allowance values are exactly
`TRUE`, `FALSE`, or blank, and all 204 recorded `age = 0` values are preserved.
The next workstream is Item 8, Dataset Quality Review.

The final name and version date will be set when the schema and mappings are
approved.

## 8. Dataset Quality Review — `[x]` Approved and complete

- [x] Confirm 7,446 output records and unique `person_id` values.
- [x] Confirm exact row-order reconciliation with the staged Russian source.
- [x] Confirm the approved compact schema and column order.
- [x] Confirm zero unmapped populated categories or places.
- [x] Confirm zero Cyrillic values in English-only fields.
- [x] Confirm all transliterated names map to the correct Russian records.
- [x] Confirm numeric formats, ranges, and Boolean values.
- [x] Confirm component and household relationships remain internally
  consistent after column reduction.
- [x] Produce Russian-to-English reconciliation tables and exception files.
- [x] Calculate SHA-256 hashes for the candidate and all approved mapping inputs.
- [x] Submit the complete candidate and QA package for owner approval.

Technical QA completed on 2026-08-09 with status `PASS`. The package confirms
7,446 records, 23 columns, exact row order, unique identifiers, zero field-level
transformation mismatches, zero unmapped values, zero Cyrillic cells, zero QA
exceptions, 2,796 preserved populated household groups, and zero duplicate
`person_seq` values within settlements. The project owner approved the candidate
package on 2026-08-09. Item 8 is complete.

## 9. MySQL Package — `[x]` Complete

- [x] Create `sql/01_create_english_dataset.sql` with explicit data types,
  primary key, nullable fields, and useful indexes.
- [x] Create `sql/02_load_english_dataset.sql` and documented import instructions.
- [x] Create `sql/03_validate_english_dataset.sql` for row count, uniqueness,
  NULL, range, and category checks.
- [x] Create analysis queries for district, settlement, age, sex, legal status,
  literacy, occupation, household, and migration-origin questions.
- [x] Test loading into MySQL and reconcile results to CSV QA totals.

Static package QA passed all controls on 2026-08-09. The schema exactly matches
the approved 23-column order, uses `utf8mb4`, enforces identifier keys, converts
empty nullable CSV fields to SQL `NULL`, and maps `TRUE`/`FALSE` to nullable
Boolean values. Workbench loaded 7,446 rows with zero skipped records and zero
warnings; the validation result set matched all expected totals and showed
`PASS` for every control.

## 10. Tableau Readiness — `[~]` Ten named dashboards published; remaining independent validation paused

- [ ] Test direct CSV import into Tableau.
- [ ] Verify field types, aliases, geographic roles, and default aggregations.
- [ ] Confirm that identifiers are treated as dimensions rather than measures.
- [ ] Confirm that age, year, and Boolean fields behave correctly.
- [x] Create a Tableau data-source specification: `docs/tableau_preparation.md` (2026-10-04).
- [x] Prepare a separate local practice CSV without full_name and verify all 7,446 retained records and values.
- [x] Audit historical snapshots against current analytical logic and document variants and excluded legacy files; see `outputs/qa/tableau_preflight_20261004/`.
- [x] Refresh pre-import checks on 2026-10-12: 59 assertions passed; exact demographic, missing-value, household, subtotal, and cohort-denominator benchmarks are in `outputs/qa/tableau_preflight_20261012/`.
- [x] Record Decision 40, Children aged 0–15; correct both child queries and verify 1,467 children locally (`outputs/qa/children_0_15_20261012/`). This supersedes the earlier child-scope checks, not the historical evidence.
- [x] Register and reconcile both supplied 0–15 CSV exports with the corrected SQL: `children_age_0_15_10122026.csv` and `children_by_sex_0_15_10122026.csv`; see `outputs/qa/tableau_preflight_20261012_csv_register/`. This verifies saved results, not MySQL execution logs.
- [x] Review both published children’s dashboards and save six screenshots (owner report, 2026-10-14).
- [x] Inspect the saved total, female and male screenshots locally.
- [x] Correct summary-filter mismatches: literacy total must change to 274/262; age summary must follow selection or be explicitly labelled unfiltered. Confirmed in owner review and updated screenshots, 2026-10-14.
- [x] Validate displayed children’s filters and summary counts against SQL/CSV benchmarks (updated screenshots, 2026-10-14).
- [x] Build the first children’s age-and-sex dashboard (owner completion report; editor screenshot shows the expected totals).
- [x] Record the owner-supplied public dashboard URL on 2026-10-13: [Sakhalin 1890 — Children aged 0–15](https://public.tableau.com/views/Sakhalin1890Childrenaged015/Dashboard1).
- [x] Review published children’s dashboard layout and filter states (owner review and screenshots, 2026-10-14).
- [ ] Independently inspect published workbook data-source connections.
- [x] Prepare and locally validate the next children’s literacy SQL and authoring guide.
- [x] Record Decision 42: filter literacy charts to ages 5–15 while preserving the 0–15 export and overall children’s definition.
- [x] Set the literacy chart Age filter to 5–15 (owner report, 2026-10-13).
- [x] Verify Age 5–15 applies to all related literacy sheets and reconcile the filtered total of 536 (274 female; 262 male). Confirmed in owner review and updated screenshots, 2026-10-14.
- [x] Register the saved 75-row literacy CSV and reconcile it exactly with local SQL results (2026-10-13); live MySQL execution logs were not inspected.
- [x] Record completion/publication of the literacy dashboard based on the owner-supplied URL (2026-10-13): [Recorded literacy among children aged 5–15](https://public.tableau.com/views/Recordedliteracyamongchildrenaged515/Dashboard1).
- [x] Verify the published literacy dashboard’s layout, filters and percentage calculations. Confirmed in owner review and updated screenshots, 2026-10-14.
- [x] Register both owner-supplied origin-by-age CSVs and their exact local result validation (2026-10-27); see `tableau/data/README.md`.
- [x] Record the [two-group origin-by-age share link](https://public.tableau.com/shared/ZMWP4CSS2) and save its screenshot (owner supplied, 2026-10-27).
- [x] Record the [detailed four-category origin-by-age dashboard](https://public.tableau.com/views/ChildrensrecordedoriginbyageSakhalin1890/Dashboard1) and save its screenshot with the age-eight missing-origin note (owner supplied, 2026-10-27).
- [x] Inspect both origin screenshots locally for displayed categories, age range and caveat; live Tableau pages and data-source connections remain unverified.

## 11. Documentation and Release — `[~]` Approved analytical release; publication verification pending

- [x] Update the data dictionary for the approved compact English schema (2026-10-04).
- [x] Document translation and transliteration standards and limitations (name, legal-status, geographic, and value specifications).
- [x] Document every excluded canonical field and the reason for exclusion (`docs/data_dictionary.md`).
- [x] Add MySQL and Tableau usage instructions (`docs/mysql_english_dataset_import.md`; `docs/tableau_preparation.md`).
- [x] Record known historical-language limitations and non-equivalent terms (`docs/limitations.md`; translation specifications).
- [x] Create release notes and a machine-readable QA report (`docs/release_notes.md`; `outputs/qa/english_dataset_quality_review_20260809/english_dataset_quality_report_20260809.json`).
- [x] Obtain owner approval before designating the English analytical dataset as
  the current analytical release.
- [x] Commit the approved analytical release without changing the canonical Russian designation (local Git commit `abaa760`).
- [ ] Verify external upload/publication status and source reuse conditions; local commit evidence does not establish remote visibility or publication clearance.

Reconciled 2026-10-04 against Decisions 35–38 and the existing QA package. Historical progress-log entries below retain the status recorded on their original dates. Future Russian-version reviews remain open. No Tableau runtime checks or external publication have been marked complete by this documentation update.

Rechecked 2026-10-12: documentation/release checkmarks remain supported. The outstanding Item 10 checks require Tableau itself; the outstanding Item 11 check concerns external publication evidence. Neither is a missing CSV-preparation task. Current edits and preparation outputs are local and uncommitted; the completed commit item above refers specifically to the previously approved English release.

Reconciled 2026-10-13: first dashboard construction and URL receipt are complete based on the owner report and earlier editor screenshot. General source tests and published-view validation remain open; the web retrieval tool could not inspect the supplied page. Follow-up on 2026-10-13: the literacy CSV is now present and validated, and the owner supplied its dashboard URL. See `outputs/qa/children_literacy_export_20261013/validation.json`.

## Dashboard review — 2026-10-14

Owner review and screenshot corrections completed 2026-10-14. Updated single-sex screenshots confirm literacy totals of Female 274 / Male 262 and age-summary totals of Female 726 / Male 741. The displayed summary-filter checks pass. See [findings and review](children_findings.md). Workbook connection internals were not independently inspected.

- [x] Write `docs/children_findings.md` with scopes, denominators and limitations.
- [x] Prepare and locally validate `sql/07_children_by_district_queries.sql`.
- [x] Prepare and locally validate settlement-level analysis (owner direction, 2026-10-14): 51 groups, 1,467 children; district query retained as reference.
- [x] Export/register the settlement comparison and build its visualization (owner completion, screenshot inspection and exact export QA, 2026-10-14).
- [x] Record the settlement dashboard public URL (2026-10-19; supplied 2026-10-14): [Sakhalin 1890 — Children by settlement](https://public.tableau.com/views/Sakhalin1890Childrenbysettlement/Sakhalin1890Childrenbysettlement).
- [ ] Verify live District filter behavior on both settlement charts.
- [x] Reconcile all 48 CSVs in the general audit: 42 current matches, four documented variants and two known exclusions (2026-10-19).
- [x] Add settlement findings with population denominators and interpretation limits (2026-10-19).
- [x] Document the published origin-by-age views and screenshot evidence (2026-10-27); four named children’s dashboards and one additional shared view are now recorded.

The owner paused further review and CSV extracts on 2026-10-27. Open application checks and unsaved SQL outputs remain documented, without implying that new exports or a Chekhov numerical comparison are planned.

The owner agreed an [eight-item Tableau visualization plan](tableau_visualization_action_plan.md): six original whole-population figures, the completed children's segment (item 7), and a historical Russian Empire origin map (item 8). The map is planned; its place lookup and historical geography have not been prepared or validated.

### Settlement concentration — 2026-10-28

- [x] Complete action-plan item 1: ranked settlement bars for all recorded people, District filter, linked total sheet and fixed all-district top-five note.
- [x] Record the owner-supplied [published dashboard](https://public.tableau.com/views/Sakhalin1890Settlementconcentration/Settlementconcentration) and [saved screenshot](../tableau/screenshots/settlement_concentration_20261028.png).
- [x] Inspect the screenshot locally: total 7,446, top five 4,046 (54.3%), scope caption and horizontal total-label layout are displayed. Independent live interactions and source connections remain unverified.

Current record: ten named dashboards (four children's dashboards, settlement concentration, sex composition, combined legal/social status, adult literacy, recorded arrival years and household sizes/lodgers), one additional shared origin view, and fifteen screenshots. Items 1–7 are complete; item 8, the historical origin map, remains planned.

## Progress Log

Household sizes and lodgers completed 2026-10-30: [published dashboard](https://public.tableau.com/views/Sakhalin1890Householdsizesandrecordedlodgers/Sakhalin1890Householdsizesandrecordedlodgers) and [screenshot](../tableau/screenshots/households_lodgers_20261030.png) registered. Local inspection confirms size bars, 11.4% overall indicator, settlement percentages and scope notes. Item 6 is complete; items 1–7 are complete and item 8 remains planned. [Dashboard record](households_lodgers_tableau.md).

Recorded arrival years completed 2026-10-29: [published dashboard](https://public.tableau.com/views/Sakhalin1890Recordedarrivalyears/Sakhalin1890Recordedarrivalyears) and [screenshot](../tableau/screenshots/arrival_years_20261029.png) registered. Local inspection confirms annual bars, a decade heatmap, 1884 = 548, and coverage/interpretation notes. Item 5 is complete; item 6 is next. [Dashboard record](arrival_years_tableau.md).

Adult literacy completed 2026-10-29: [published dashboard](https://public.tableau.com/views/Sakhalin1890Recordedadultliteracybysex/Sakhalin1890Recordedadultliteracybysex) and [screenshot](../tableau/screenshots/adult_literacy_by_sex_20261029.png) registered. Local screenshot inspection confirms counts, two denominators, separate Educated and missing-literacy categories, and interpretation notes. Item 4 is complete; item 5 is next. [Dashboard record](adult_literacy_tableau.md).

Legal/social status completed 2026-10-28: [published pie dashboard](https://public.tableau.com/views/Sakhalin1890Combinedlegalandsocialstatusgroups/Sakhalin1890Combinedlegalandsocialstatusgroups) and [screenshot](../tableau/screenshots/legal_status_groups_20261028.png) registered; five groups reconcile to 7,446. The detailed bars are owner-reported. Item 3 is complete and item 4, adult literacy, is next. [Definitions and evidence](legal_status_tableau.md) include the child-group caveat and historical rights summaries.

Sex-composition dashboard completed 2026-10-28: owner supplied the [public URL](https://public.tableau.com/views/Sakhalin1890Sexcompositionbydistrictandrecordedages/Sakhalin1890Sexcompositionandrecordedages), and the [saved screenshot](../tableau/screenshots/sex_composition_recorded_ages_20261028.png) was inspected locally. It confirms Female 2,525 / Male 4,921, the District filter, all-district medians 29 / 35 / 33, and 147 missing ages. District interactions and percentage tooltips are owner-reported; live connections were not inspected. Action-plan item 2 is complete.

| Date | Stage | Status | Summary | Evidence |
|:--|:--|:--|:--|:--|
| 2026-10-12 | Tableau pre-import follow-up | Preparation checks passed; application checks pending | Reconciled all 44 snapshots, retained two legacy exclusions, and passed 59 assertions covering counts, missingness, household grouping, subtotals, and cohort denominators. Preserved all source records and historical CSVs. | `outputs/qa/tableau_preflight_20261012/`; `docs/tableau_preparation.md` |
| 2026-08-01 | English analytical-layer direction | Approved | Selected a compact English-only dataset for MySQL and Tableau while retaining canonical v5 as the authoritative Russian source. | `docs/decision_log.md`; `docs/language_translation_strategy.md` |
| 2026-08-01 | Compact column selection | Pending owner review | Dataset generation is paused until the exact included and excluded columns are approved. | This tracker, Section 2 |
| 2026-08-02 | Compact column review workbook | Ready for owner review | Profiled all 50 canonical fields and prepared recommendations, proposed English names, rationale, usage statistics, decision dropdowns, and a live completion summary. | `outputs/english_dataset_column_review_20260802/english_compact_column_review_20260802.xlsx` |
| 2026-08-02 | Compact column selection | Approved | Owner completed all 50 decisions and approved a 23-field compact schema, including `person_seq`, `full_name`, and `archive_code`. | `outputs/english_dataset_column_review_20260802/english_compact_column_review_20260802.xlsx`; this tracker, Section 2 |
| 2026-08-02 | English value and NULL specification | In progress | Approved empty CSV fields for missing values, with meaningful `0` and `FALSE` preserved and conversion to SQL `NULL` deferred to MySQL loading. | This tracker, Section 3; `docs/decision_log.md`, Decision 24 |
| 2026-08-02 | Allowance Boolean convention | Approved | Keep `allowance_status` as `TRUE`, `FALSE`, or blank in CSV; load as nullable Boolean in MySQL and optionally display as `Yes`, `No`, or `Not recorded` in Tableau. Confirmed that `age = 0` is a valid value rather than missingness. | This tracker, Section 3; `docs/decision_log.md`, Decision 24 |
| 2026-08-02 | English value and NULL specification | Approved | Approved data types, nullability, capitalization, compound delimiters, field interpretation, and mandatory distinct-value review for explicit unknown or applicability categories. | `docs/english_dataset_value_null_specification.md`; `docs/decision_log.md`, Decision 25 |
| 2026-08-02 | Personal-name transliteration rules | Approved; implementation pending | Approved simplified ASCII BGN/PCGN, direct `name_raw` to `full_name` conversion, parenthetical numbered-name markers, punctuation preservation, and `Person of unknown rank` as a reviewed exception. | `docs/english_name_transliteration_specification.md`; `docs/decision_log.md`, Decision 26 |
| 2026-08-02 | Name transliteration candidate | Ready for owner review | Generated all 7,446 candidate names with zero blanks, zero Cyrillic remnants, and zero collision groups. Prepared 44 priority records for owner decisions and a 1,295-record extended exception inventory. | `outputs/english_name_transliteration_review_20260802/english_name_transliteration_review_20260802.xlsx`; `scripts/build_english_name_transliteration_review_20260802.py` |
| 2026-08-02 | Name transliteration owner review | Approved | Completed all 44 priority decisions: 41 approvals and 3 revised English names. Generated the staged 7,446-record mapping and deferred a mixed-script audit for the next Russian canonical release. | `outputs/english_name_transliteration_review_20260802/english_name_transliteration_review_20260802.xlsx`; `outputs/english_name_transliteration_review_20260802/name_transliteration_staged_20260802.csv`; `docs/decision_log.md`, Decision 27 |
| 2026-08-02 | Controlled category translation inventory | In progress | Inventoried all 296 populated controlled values. Prepared 38 Batch A translations for owner review and a complete 258-value Batch B inventory for historically sensitive translation work. | `outputs/english_controlled_translation_review_20260802/controlled_category_translation_review_20260802.xlsx` |
| 2026-08-02 | Controlled translation Batch A | Approved | Approved 37 proposed mappings and revised `Раскольничество` to `Schismatic`; no holds remain. Reviewed prior legal-status decisions and documented `Penal convict` and `Exile settler` as authoritative Batch B seed terms while preserving the 61-value Russian normalized vocabulary. | `outputs/english_controlled_translation_review_20260802/controlled_translation_batch_a_approved_20260802.csv`; `docs/english_legal_status_translation_basis.md`; `docs/decision_log.md`, Decision 28 |
| 2026-08-02 | Batch B1 legal-status proposal recovery | Ready for owner review | Recovered the earlier three-variant translation workbook and reconciled all 61 current canonical `legal_status_norm` values exactly, with zero missing or extra values. Prepared Variant A/B/C owner review. | `outputs/translation_review_20260716/sakhalin_1890_english_translation_options.xlsx`; `outputs/english_controlled_translation_review_20260802/legal_status_translation_review_20260802.xlsx`; `docs/decision_log.md`, Decision 29 |
| 2026-08-09 | Geographic translation and transliteration | Approved; Item 6 complete | Approved all 51 settlement and 100 origin-place mappings, including three owner revisions. Generated versioned district, settlement, and origin-place lookup tables with zero unmapped populated values; retained 838 blank origins. | `outputs/english_geographic_translation_review_20260809/`; `docs/decision_log.md`, Decision 34 |
| 2026-08-09 | English dataset build | Built; Item 7 complete | Generated the compact 23-column English v1 dataset with 7,446 reconciled records, unique identifiers, zero unmapped populated values, approved nullable Boolean handling, and field-level lineage. | `data/analytical/sakhalin_1890_en_v1.csv`; `outputs/qa/english_dataset_build_20260809/`; `docs/english_dataset_field_lineage.md`; `docs/decision_log.md`, Decision 35 |
| 2026-08-09 | Archive-code transliteration amendment | Applied and QA passed | Revised `archive_code` to use `RGB` and `RGALI`; transliterated 40 Cyrillic archive suffix letters while preserving numbers and `№`. Rebuilt v1 with 7,223 RGB codes, 222 RGALI codes, and zero Cyrillic characters. | `data/analytical/sakhalin_1890_en_v1.csv`; `outputs/qa/english_dataset_build_20260809/`; `docs/decision_log.md`, Decision 35 |
| 2026-08-09 | Missing archive code P000107 | Staged and applied to English v1 | Added owner-supplied `ДМЧ (Ялта). КП № 1716.` to `notes_raw` in a one-record Russian staged candidate; canonical v5 remains unchanged. English `archive_code` is `DMCh (Yalta). KP № 1716.`. Rebuilt v1 with zero blank archive codes and QA passed. | `data/staging/archive_code_p000107_20260809/`; `outputs/qa/archive_code_p000107_20260809/`; `docs/decision_log.md`, Decision 36 |
| 2026-08-09 | Item 8 dataset quality review | QA passed; pending owner approval | Independently reconciled all 23 fields and 7,446 records to the staged Russian source and approved lookups. Found zero row-order, mapping, language, household-membership, sequence, numeric, Boolean, or exception failures. Prepared the review workbook, reconciliation CSVs, JSON report, exception file, and SHA-256 manifest. | `outputs/qa/english_dataset_quality_review_20260809/`; `docs/decision_log.md`, Decision 37 |
| 2026-08-09 | Item 8 owner approval | Approved and complete | Owner approved the compact English v1 candidate and its complete technical QA package. | `outputs/qa/english_dataset_quality_review_20260809/`; `docs/decision_log.md`, Decision 38 |
| 2026-08-09 | Item 9 MySQL package | Complete; Workbench load reconciled | Created the MySQL 8 schema, safe CSV loader, validation suite, starter analysis queries, and Workbench import guide. Workbench loaded 7,446 rows with zero skipped records or warnings; all validation controls passed and matched the CSV QA totals. | `sql/`; `docs/mysql_english_dataset_import.md`; `outputs/qa/mysql_package_20260809/`; `docs/decision_log.md`, Decision 38 |
