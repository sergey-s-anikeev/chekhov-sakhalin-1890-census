# From Historical Census Records to an Analytical Dataset

## Sakhalin, 1890 — Full Portfolio Report

**Status:** Analytical draft, updated 4 October 2026. SQL analysis and CSV preparation are complete. Tableau charts, dashboard validation, and final visual presentation are pending.  
**Tools:** Python, MySQL 8, Git; Tableau planned.  
**Scope:** 7,446 person records, three districts, 51 settlements.  
**Companion:** [Short portfolio report](portfolio_report_short.md).

## Executive summary

This project transforms indexed records from Anton Chekhov's 1890 Sakhalin census into a traceable dataset for demographic and social analysis. The work combines historical-source extraction, reviewed normalization, an English analytical layer, database validation, and SQL analysis. Its analytical product is a reproducible description of the people represented in the processed source material.

The approved Russian dataset contains 7,446 records. A separate English dataset retains all records in 23 analytical columns. MySQL import and validation were completed, and 44 dated CSV snapshots were prepared for visualization. This report uses the approved English CSV and saved analytical exports; it does not claim a new database run.

Five findings guide the proposed visual narrative:

- **Records are concentrated geographically.** The five largest settlements account for 4,046 people, or 54.3% of the dataset.
- **The sex and age distributions differ.** The derived sex field classifies 66.1% of records as male. Median recorded age is 35 for males and 29 for females.
- **Recorded adult literacy differs substantially by sex.** Among people aged 16 or older with a recorded literacy category, 39.1% of males and 10.3% of females are classified as `Literate`. `Educated` is retained separately.
- **Small identified households are common.** One- and two-person households constitute 62.1% of the 2,796 populated household groups.
- **Coverage determines what can be concluded.** Age is populated for 98.0% of records, but occupation for only 19.8% and illness for 0.7%. Blank illness entries cannot be interpreted as evidence of good health.

The main contribution is a documented route from historical evidence to analysis, with clear denominators and preserved uncertainty. The findings describe this dataset; they do not establish complete coverage of Sakhalin's population or causal explanations for the observed differences.

## 1. Analytical objective and audience

The project addresses a practical data problem: historical records contain useful demographic information, but their document structure, inconsistent wording, and missing fields make direct comparison difficult. The objective is to convert those records into an auditable analytical resource and identify patterns that can be communicated responsibly.

The report is intended for a data-analyst portfolio reviewer and readers interested in historical population data. Success means producing reliable tables, interpretable metrics, documented limitations, and a clear visual narrative. This is an exploratory historical-data case study; no commercial performance target or financial impact is claimed.

The analysis asks:

1. How are the represented people distributed across districts and settlements?
2. What do the age and derived sex fields show about population structure?
3. How do recorded legal status and literacy vary?
4. What can origins and arrival years reveal within the limits of their coverage?
5. What household patterns can be measured reliably?
6. Which missing fields constrain interpretation and dashboard design?

## 2. Source, scope, and unit of analysis

The source is the published volume *“Perhaps my figures, too, will be of use.” Materials of A. P. Chekhov's Sakhalin Census. 1890* (Yuzhno-Sakhalinsk: Rubezh, 2005, 600 pages), as identified in the project's [statement of work](SOW.md). Extraction uses the searchable PDF text layer. OCR was not the primary extraction method.

One dataset row represents one named person record. The approved combined release includes 2,884 records from Alexandrovsky District, 3,242 from Tymovsky District, and 1,320 from Korsakovsky District. Counts in this report refer to the processed records, rather than a verified census of every island resident.

The Russian canonical release is `v5_20260731`, with 50 columns including normalization and provenance information. The English analytical file contains 23 columns and is derived from that release plus documented, approved staged corrections. It retains stable person and source-position identifiers. Household identification requires the combination of district, settlement, and household ID; the household number alone is not a global key.

The [field-lineage document](english_dataset_field_lineage.md) maps each English field to its source. Historical origin labels are not assumed to represent modern countries, citizenship, or ethnicity.

## 3. Data preparation and quality assurance

### 3.1 Extraction and reviewed normalization

The processing workflow extracts page text, identifies settlement headings and person records, maps numbered source fields, and preserves printed page references. Reviewed normalization addresses extraction artifacts and inconsistent representations while retaining source-derived evidence in the Russian layer.

Substantive corrections are documented through scripts, explicit mappings, and owner review. Approved releases are versioned, supported by QA artifacts and hashes, and preserved as historical outputs. Ambiguous historical categories are not silently merged for presentation convenience.

The sex field needs a specific qualification. It is derived using reviewed gendered legal-status wording, household-role wording, and, where necessary, reviewed patronymic morphology. Conflicts were referred for owner review. Full coverage of this derived field is therefore not evidence that the source contained a complete standalone sex column. The [derivation rules](../data/review/sex_item3_20260712/sex_derivation_rules.md) document the procedure.

### 3.2 Specific cleaning challenges and documented decisions

Cleaning required distinguishing errors printed in the published source from artifacts introduced during extraction and normalization. The following examples show how the review process handled field assignment, category text, and chronological consistency. Russian strings below are quoted source evidence; explanations remain in English.

The early 500-record review used sample-specific person IDs. The locators below use stable `source_position_id` values and printed page numbers; current full-dataset IDs were checked against canonical v5 to avoid confusing sample IDs with release IDs.

| Issue and source locator | Evidence in the review documentation | Documented handling and analytical significance |
|---|---|---|
| Misprinted name-field number — `3-33-013-0024`, p. 429; current `P006419` | The name was printed under `5.` instead of `4.` (sample `P000245`). | The name, household role, age, religion, origin, and allowance were manually reassigned to the intended fields. The review recorded age zero and a four-month age note. This prevented a numbering error from shifting several variables at once. |
| Shifted sequence of category numbers — `3-38-004-0004`, p. 440; current `P006600` | Name was marked `5.`, age `6.`, religion `7.`, and origin `8.` (sample `P000426`). | Fields were manually reassigned. Arrival year remained blank because the corrected record contained no arrival-year entry. The origin text under the printed `8.` label was not treated as a year. |
| Name occupying the legal-status field — `3-35-027-0046`, p. 436; current `P006540` | Field `3.` contained a name, and legal status was absent in the original record (sample `P000366`). | The person fields were reassigned and legal status was left blank. Repairing the record structure did not justify inventing the missing category. |
| Misspelled legal-status text — `3-29-037-0090`, p. 420; current `P006254` | The review records `Сс[ылно]каторжный` as a source typo/spelling variant (sample `P000128`). | It was normalized to `Ссыльнокаторжный` and added to reusable normalization rules. The English analytical mapping is `Penal convict`; the malformed spelling did not become a separate analytical category. |
| Year printed in a religion category — `3-30-030-0040`, p. 425; current `P006352` | The reviewer confirmed `1882` in printed religion field `6.` and again in arrival-year field `8.` (sample `P000178`; archive reference RGB No. 5829). | The sample review preserved and documented the religion anomaly rather than guessing a faith. In current canonical v5, religion is blank and arrival year is `1882`; the historical sample decision should not be mistaken for the current field value. |

**Evidence:** [Record-level manual decisions](../outputs/qa/manual_review_decisions.csv), [sample anomaly review](../outputs/qa/anomaly_review_final_documentation.md), and [current Russian canonical release](../data/processed/clean_sakhalin_1890_ru_v5_20260731.csv).

Category text also required extraction-specific repair. The sample review documents a bracket-restoration spacing artifact in the religion field: `Правосл [авного]` became `Правосл авное`. A reusable rule joined the restored word fragment and normalized it to `Православное` (Eastern Orthodox). This was a spacing/normalization problem, distinct from the confirmed printed category-number errors above.

Arrival-year cleaning involved three different checks:

1. **Recover valid years lost by normalization.** The [release notes, section 4](release_notes.md#4-arrival-year-extraction), document an early routine that discarded valid years as formatting artifacts. Year normalization was rewritten to preserve valid four-digit values while removing genuine artifacts and footnotes.
2. **Flag implausible numeric values.** The [release notes, section 12](release_notes.md#12-numeric-range-qa), give `1976` instead of `1876` as an example motivating arrival-year range checks. Those notes do not provide a record locator or establish whether this specific error was printed or introduced during extraction. It is therefore reported as a documented anomaly example, not as a verified record-level source correction.
3. **Review age and arrival year together.** For current `P005199` (`2-24-328-1163`, p. 351), age `2` combined with arrival year `1887` implied an arrival before birth when evaluated against 1890. Owner review identified a recognition/cleanup error in age and approved `2 → 25`. Arrival year `1887` and the recorded origin remained unchanged. The [approved diff](../outputs/qa/arrival_year_item21_20260717/arrival_year_item21_applied_diff.csv) records exactly one age-cell change; the [review completion note](../data/review/arrival_year_20260717/owner_response/arrival_year_review_completion.md) explains the decision.

The completed arrival-year review found 4,826 populated four-digit values ranging from 1865 to 1890. Three other flagged records were accepted unchanged after review. This illustrates the central cleaning principle: an automated flag prompts investigation; it does not by itself establish which field is wrong or authorize a replacement.

#### Footnotes, editorial markup, and lost age digits

The source's extensive footnotes and editorial annotations made parsing more difficult than extracting a regular table. Footnote paragraphs could enter person-record text, inline reference digits could become part of names or ages, and numbered content complicated the distinction between a field label and a field value. The [record parser](../scripts/create_raw_records_from_pages_v3.py) explicitly cuts the field-parsing block at the archival reference to prevent subsequent footnote paragraphs from entering person fields. The [methodology](methodology.md#record-detection-and-source-anomalies) also documents wrapped age lines and numeric values that could be mistaken for record starts or category labels.

The evidence shows several distinct failure modes:

- **Extra digits from footnote markers.** The [numeric QA notes](release_notes.md#12-numeric-range-qa) give `56 + footnote 1 → 561` and `45 + footnote 1 → 451` as examples. Such artifacts inflate ages and require range checks and source review. The [manual-correction notes](release_notes.md#10-critical-manual-review-corrections) also show footnote digits attached to a person's name.
- **Lost digits in extracted ages.** The [approved age corrections](../data/review/age_item7_20260713/owner_response/age_corrections_approved.csv) document `P005013`, p. 340, corrected from `3` to `36`, and `P001574`, p. 123, from `4` to `47`. Both corrected values are present in canonical v5. These are verified examples of incomplete age values; the decision table does not establish that a footnote caused each individual truncation.
- **Digits separated by editorial markup.** The [raw-age audit](../data/review/raw_age_recognition_item22_20260717/README.md) found 19 age expressions with digits on both sides of crossed-out angle-bracket content. For `P005199`, raw `2<0>5 (?)` resolves to `25` after removing the crossed-out content. Reading only the first integer would yield `2`. Crossed-out text and uncertainty marks required their own parsing rules rather than being treated as footnote markers.
- **Values assigned to the wrong category.** The manual-correction notes show `5. 44. Раскольн[ица].`, where age and religion were combined in field `5`. Reviewed recovery assigned age `44` and the normalized religion to separate columns. This documents a field-assignment failure in the annotated source layout; it does not establish a footnote as the cause of that particular case.

Cleanup therefore used field-specific rules: remove identified reference digits from selected text fields, preserve substantive numbers in ages and years, interpret editorial markup, and review ambiguous field boundaries against source locators. Generic digit removal could itself damage the data: the [year normalizer](../scripts/sakhalin_conversion_helpers_v12.py) explicitly avoids trailing-footnote cleanup because an entire value such as `1887` would otherwise be erased. These problems mattered analytically because truncated adult ages could enter child-age groups, while shifted category values could distort status or religion counts.

### 3.3 English analytical layer and MySQL

Personal names are transliterated; controlled categories and geographic labels use approved translation mappings. Missing values remain empty in the English CSV and become SQL `NULL` during import. Recorded age zero remains valid. Allowance uses three states: yes, no, and missing.

The MySQL package separates table creation, loading, validation, and analytical queries. Primary and unique keys protect person and source identifiers. The documented Workbench import loaded 7,446 rows with zero skipped records and zero warnings; all displayed validation controls passed.

### 3.4 Evidence supporting analytical readiness

| Control | Documented result |
|---|---|
| English output dimensions | 7,446 rows; 23 columns |
| Person and source-position identifiers | 7,446 unique values each |
| Row order and field transformations | Zero mismatches |
| Populated category/place mappings | Zero unmapped values |
| English-only field review | Zero Cyrillic cells |
| Household reconciliation | 2,796 populated groups preserved |
| English dataset QA exceptions | Zero exception rows |

These results come from the [English quality report](../outputs/qa/english_dataset_quality_review_20260809/english_dataset_quality_report_20260809.json) and [MySQL import record](mysql_english_dataset_import.md). During preparation of this draft, the English file's hash matched the approved hash, its dimensions and field coverage were recalculated, and the principal findings were checked against saved exports and source records. Passing technical checks demonstrates internal consistency; it does not prove that every historical statement in the source is accurate.

## 4. Analytical method and metric definitions

The analysis is descriptive. It uses counts, within-group shares, medians, rankings, and comparisons across recorded categories. No causal model, forecast, or population-wide significance claim is made.

| Metric | Definition and denominator |
|---|---|
| Dataset share | Group count divided by all 7,446 records |
| Median age | Median of nonmissing completed-year ages; recorded zero retained |
| Adult literacy | Age 16 or older; separate shares among all adults and those with a recorded literacy category |
| Household size | Person count within district + settlement + populated household ID |
| Arrival-year share | Count for that year divided by 4,826 records with a recorded arrival year |
| Allowance share | Recipients divided by all records, or separately by records with known allowance status |
| Field coverage | Nonblank values divided by all 7,446 records |

Percentages are rounded to one decimal unless otherwise stated. Percentage-point differences are calculated before rounding, so they may differ from subtraction of the displayed percentages. The saved top-five settlement export rounds percentages to whole numbers; this report recalculates 54.3% from its counts. Rounded components may not sum to 100%.

Age thresholds follow the relevant query. The existing child-age distribution covers ages 0–17, the child-sex share covers ages 0–16, and adult literacy starts at 16. These outputs must not be combined as mutually exclusive age groups. Five-year arrival cohorts are calendar-aligned; the label 1890–1894 contains only observations available in 1890.

## 5. Findings

### 5.1 The represented population is concentrated in a few settlements

| District | Records | Share of dataset |
|---|---:|---:|
| Tymovsky | 3,242 | 43.5% |
| Alexandrovsky | 2,884 | 38.7% |
| Korsakovsky | 1,320 | 17.7% |

Across 51 settlements, Alexandrovsky Post has 1,338 records and Rykovskoe has 1,266. Together they account for 2,604 people, or 35.0% of the dataset. Adding Derbinskoe, Novo-Mikhaylovskoe, and Andree-Ivanovskoe brings the top-five total to 4,046, or 54.3%.

This concentration means overall statistics are strongly influenced by the largest settlements. District-level comparisons and settlement filters should accompany the headline totals. Counts alone do not establish settlement density, urbanization, or relative completeness of historical coverage.

**Evidence:** [District totals](../tableau/data/districts_by_population22082026.csv), [settlement totals](../tableau/data/settlements_by_population22082026.csv), and [top-five counts](../tableau/data/top5_by_population_witsubtotal_22082026.csv).  
**Figure 1 completed, 2026-10-28:** [Sakhalin 1890 — Settlement concentration](https://public.tableau.com/views/Sakhalin1890Settlementconcentration/Settlementconcentration), with ranked settlement bars, District filter, selected-population total and fixed all-district top-five note. [Saved screenshot](../tableau/screenshots/settlement_concentration_20261028.png). Publication is owner-reported; the screenshot was inspected locally. Live interactions and workbook connections were not independently inspected.

### 5.2 Male records predominate, and median ages differ

The derived sex field contains 4,921 male records (66.1%) and 2,525 female records (33.9%). The median age among recorded ages is 33 overall, 35 for males, and 29 for females. Age is missing for 147 people, or 2.0% of the dataset.

District comparison added 2026-10-28 following the owner's Tableau exploration:

| District | Male records | All records | Male share |
|---|---:|---:|---:|
| Alexandrovsky | 1,742 | 2,884 | 60.4% |
| Tymovsky | 2,198 | 3,242 | 67.8% |
| Korsakovsky | 981 | 1,320 | 74.3% |

The male share increases across these three district groups. Differences in settlement development and migration phases are possible explanations proposed by the owner; this comparison does not test their effects. Each percentage uses all recorded people in its district, including those without recorded age. The comparison is reported by district rather than as a continuous geographic gradient.

The results establish a difference in the composition of the represented groups. They do not explain why the difference exists. Historical selection, legal status, migration, family composition, and survival could all affect the observed distribution; this analysis does not isolate their effects.

**Evidence:** [Age/sex profile](../tableau/data/age_and_sex_profile22082026.csv), [overall median](../tableau/data/median_age22082026.csv), and [medians by sex](../tableau/data/median_age_bysex22082026.csv).  
**Figure 2 completed, 2026-10-28:** [Published dashboard](https://public.tableau.com/views/Sakhalin1890Sexcompositionbydistrictandrecordedages/Sakhalin1890Sexcompositionandrecordedages), URL supplied by the owner. The [saved screenshot](../tableau/screenshots/sex_composition_recorded_ages_20261028.png) confirms Female 2,525, Male 4,921, a District filter and explicitly all-district median/coverage notes. District filtering and percentage tooltips are owner-reported; live interactions and workbook connections were not independently inspected. See [action-plan item 2](tableau_visualization_action_plan.md). A full age pyramid would require an additional age-band aggregation; it is not supplied by the district summary alone.

### 5.3 Exile settlers are the largest recorded legal-status category

`Exile settler` accounts for 3,366 records (45.2%) and `Penal convict` for 1,372 (18.4%). `Free-status person` accounts for 862 (11.6%). Child-status categories remain distinct, including 748 `Child of exile settler` and 459 `Child of penal convict` records.

These categories describe the source's administrative classifications. A child-status label does not establish the child's own conviction history, and a non-child label does not guarantee an adult age. The top-four non-child export is a filtered ranking whose percentages still use the entire dataset; it is not a complete distribution.

**Evidence:** [Full legal-status distribution](../tableau/data/legal_status_profile22082026.csv) and [filtered status shares](../tableau/data/legal_status_profile_share28082026.csv).  
**Figure 3 completed, 2026-10-28:** [Published combined-status pie](https://public.tableau.com/views/Sakhalin1890Combinedlegalandsocialstatusgroups/Sakhalin1890Combinedlegalandsocialstatusgroups), with [saved screenshot](../tableau/screenshots/legal_status_groups_20261028.png). The owner also reported preparing the full ranked bar view. Display groups combine the three principal exile categories with their corresponding child-status labels: settler 4,114 (55.3%), convict 1,831 (24.6%), peasant 522 (7.0%); free-status person remains 862 (11.6%); Other is 117 (1.6%), including 24 missing. These are display groupings, not verified families or age classes. See [definitions and publication evidence](legal_status_tableau.md); rounded shares sum to 100.1%.

### 5.4 The literacy difference persists under two denominators

| Adults aged 16+ | Female | Male |
|---|---:|---:|
| All adults with recorded age | 1,762 | 4,070 |
| Recorded literacy category | 1,579 | 3,466 |
| `Literate` | 162 | 1,356 |
| `Educated`, retained separately | 4 | 19 |
| `Literate` / all adults | 9.2% | 33.3% |
| `Literate` / recorded literacy | 10.3% | 39.1% |

The male–female difference is 24.1 percentage points using all adults and 28.9 percentage points using recorded literacy only. These percentages measure the specific `Literate` label, rather than a reconstructed modern literacy definition. Missing literacy affects the denominator, while different age and status compositions may also influence the comparison.

The saved age-band analysis shows a higher male `Literate` share in every adult age band when all members of each age/sex group are counted. This strengthens the descriptive finding, but does not establish a causal effect of sex or adjust for all other compositional differences.

**Evidence:** [Adult literacy counts](../tableau/data/adult_education_profile2_01092026.csv) and [age-band literacy](../tableau/data/literacy_cohorts_07092026.csv).  
**Figure 4 completed, 2026-10-29:** [Recorded adult literacy by sex](https://public.tableau.com/views/Sakhalin1890Recordedadultliteracybysex/Sakhalin1890Recordedadultliteracybysex), with [saved screenshot](../tableau/screenshots/adult_literacy_by_sex_20261029.png). Three panels show counts, all-adult shares and recorded-only shares by sex; Educated remains separate. The screenshot confirms the key counts, rates and explanation of 787 missing literacy records. Publication is owner-reported; live connections and tooltips were not inspected. [Detailed dashboard record](adult_literacy_tableau.md).

### 5.5 Origins are diverse; arrival years describe people observed in 1890

Origin is populated for 6,608 people (88.7%), across 98 distinct English labels. `On Sakhalin` accounts for 1,254 records, or 19.0% of recorded origins. Among labels excluding `On Sakhalin`, the largest are Tambov Governorate (214), Samara Governorate (186), and Kiev Governorate (179).

Arrival year is recorded for 4,826 people (64.8%). Within this subset, 1884 is the largest recorded year, with 548 people (11.4%). This is a retrospective distribution among people represented in the 1890 records. It is not an annual immigration series: people who died, departed, or were omitted before observation are not measured by that year's count.

The origin field also includes labels such as `In transit`. Its categories should be shown as recorded origin labels, not automatically mapped to nationality. Historical boundaries require explicit geographic interpretation before any map is created.

**Evidence:** [English dataset](../data/analytical/sakhalin_1890_en_v1.csv), [origin distribution](../tableau/data/origin_place_01092026.csv), and [arrival-year distribution](../tableau/data/arrival_year_cohorts01092026.csv).  
**Figure 5 completed, 2026-10-29:** [Recorded arrival years](https://public.tableau.com/views/Sakhalin1890Recordedarrivalyears/Sakhalin1890Recordedarrivalyears), with [saved screenshot](../tableau/screenshots/arrival_years_20261029.png). Chronological bars and a decade/year-ending heatmap show the same annual counts, including 1884 = 548, with coverage and retrospective-count caveats. Publication is owner-reported; the screenshot was inspected locally. [Scope and evidence](arrival_years_tableau.md).

### 5.6 Small households are common, and some contain recorded lodgers

The household-size export contains 2,796 populated household groups. Of these, 960 contain one person and 775 contain two: together, 1,735 groups (62.1%). These counts describe identified groups rather than a verified inventory of every dwelling.

The private-household lodger export covers 7,200 people in 2,796 households. It identifies 320 households with at least one recorded lodger (11.4%) and 544 recorded lodgers in total. Forty included people have no recorded household role. Another 246 dataset records have blank household IDs and do not enter these household calculations.

A one-person group is not interchangeable with an explicit living-alone status. Likewise, a household without a recorded lodger is not proof that no lodger was present.

**Evidence:** [Household-size distribution](../tableau/data/household_size01092026.csv) and [lodger summaries](../tableau/data/Lodgers_households_08092026.csv).  
**Figure 6 completed, 2026-10-30:** [Household sizes and recorded lodgers](https://public.tableau.com/views/Sakhalin1890Householdsizesandrecordedlodgers/Sakhalin1890Householdsizesandrecordedlodgers), with [saved screenshot](../tableau/screenshots/households_lodgers_20261030.png). Size-frequency bars, the all-settlement indicator 320 / 2,796 (11.4%) and settlement lodger-share bars are displayed with coverage notes. The District filter affects only the settlement panel, which omits zero-recorded-lodger settlements. Publication is owner-reported; the screenshot was inspected locally. [Dashboard record](households_lodgers_tableau.md).

### 5.7 Allowance coverage supports comparison, but missingness still matters

Allowance is recorded as yes for 2,550 people, no for 4,328, and missing for 568. Recipients represent 34.2% of all records, or 37.1% of the 6,878 records with known allowance status. Using all people of each sex as the denominator, the recipient shares are 34.4% for males and 33.9% for females.

The similar overall percentages do not establish equal access or equal treatment. The groups may differ in age, legal status, arrival year, and recording completeness. The existing legal-status/arrival-cohort export provides a basis for a more detailed descriptive comparison.

**Evidence:** [Allowance totals](../tableau/data/allowance01092026.csv), [allowance by sex](../tableau/data/allowance_by_sex01092026.csv), and [allowance by status/cohort](../tableau/data/legal_allowance_cohorts_07092026.csv).

## 6. Missingness and interpretation limits

| Field | Populated | Missing | Coverage |
|---|---:|---:|---:|
| Derived sex | 7,446 | 0 | 100.0% |
| Legal status | 7,422 | 24 | 99.7% |
| Age | 7,299 | 147 | 98.0% |
| Allowance | 6,878 | 568 | 92.4% |
| Origin | 6,608 | 838 | 88.7% |
| Literacy | 5,418 | 2,028 | 72.8% |
| Marital status | 5,341 | 2,105 | 71.7% |
| Arrival year | 4,826 | 2,620 | 64.8% |
| Occupation | 1,474 | 5,972 | 19.8% |
| Living-alone status | 442 | 7,004 | 5.9% |
| Illness | 53 | 7,393 | 0.7% |

Coverage was recalculated from nonblank fields in the English dataset. Overall literacy coverage includes all ages and therefore differs from the adult-only denominators above.

The strongest constraints are:

- **Unknown population coverage:** a validated release does not establish that every historical resident is represented. There is no documented probability-sampling design supporting inference to an unobserved population.
- **Selective recording:** missingness may vary with age, settlement, legal status, or source practice. Blanks cannot generally be treated as negative answers or assumed missing at random.
- **Sparse fields:** occupational rankings describe recorded occupations among a small subset. The 53 illness entries cannot support a population disease-prevalence estimate. The same caution applies to living-alone status.
- **Historical meaning:** translations improve access but do not make historical labels equivalent to modern classifications. Derived sex and normalized categories retain methodological assumptions.
- **Time and causality:** the records describe an observation in 1890, including retrospective arrival and marriage information. Cohort differences cannot by themselves establish assimilation, policy effects, or changes over time.
- **Unequal aggregation:** settlement completeness varies, and some extreme percentages come from very small settlements. For example, the highest saved completeness score is 87.6% for an 11-person settlement; the lowest is 13.3% for a 13-person settlement. The score is a share of populated field slots, not a probability that a record is correct.

Some earlier project documents still describe the sample-stage plan. This draft uses the approved release, quality reports, and current files for project status. A final documentation pass should align those older descriptions before publication.

## 7. Dashboard and communication plan

The first Tableau version should prioritize geography, age/sex composition, legal status, literacy, and household structure. These subjects have interpretable measures and stronger supporting coverage. Occupation and illness belong in supporting views with prominent coverage information.

The [Tableau visualization action plan](tableau_visualization_action_plan.md), agreed 2026-10-27, retains the six whole-population figures proposed below, records the completed children's segment as item 7, and adds a planned historical Russian Empire map of recorded origins as item 8. The map requires reviewed historical geography; it is not yet a published figure. This report's October 4 status and planned-figure text remain a draft and need reconciliation with the later Tableau publications before final portfolio release.

Each view should state its unit, date context, denominator, exclusions, and missing count. Aggregate CSVs have different grains and cannot safely be combined through arbitrary joins. Repeated cohort totals must not be summed as independent observations. Filtering a saved percentage does not recalculate its denominator; dynamic percentages require compatible counts at the required grain or the person-level source.

Before publication, validate displayed counts against SQL outputs, check filters, distinguish unknown from no, and show the effect of denominator choices. Historical maps remain optional until settlement locations and boundaries are reliably documented.

## 8. Deliverables and demonstrated skills

Completed deliverables include the reviewed Russian release, the approved English analytical CSV, versioned cleaning and translation logic, QA evidence, four MySQL scripts, and 44 analytical CSV snapshots. The dashboard and visual portfolio presentation remain pending.

The case demonstrates document-to-table extraction, data cleaning with provenance, controlled translation, relational-key design, missing-value handling, SQL aggregation, common table expressions, window functions, and quality reconciliation. It also demonstrates analytical judgment: limiting claims to the evidence, choosing explicit denominators, and identifying where attractive visualizations could overstate the data.

The measurable outcome is an analysis-ready dataset of 7,446 traceable records with documented QA and reusable query results. No unmeasured time saving, business impact, or completed visualization work is claimed.

## 9. Evidence and reproduction notes

The principal inputs are the [English CSV](../data/analytical/sakhalin_1890_en_v1.csv), [analysis SQL](../sql/04_analysis_queries.sql), and [export inventory](../tableau/data/README.md). The English file's verified SHA-256 is:

```text
1b77d6330855763c54c32f21d247dc44471a69590db4fc00925c4e22eb8ac508
```

Report calculations can be reproduced as follows:

| Result | Calculation or filter |
|---|---|
| Top-five settlement share | 4,046 / 7,446 × 100 |
| Male share | 4,921 / 7,446 × 100 |
| Adult literacy, recorded only | Filter age ≥ 16; `Literate` count / nonmissing literacy count, separately by sex |
| Small-household share | (960 + 775) / 2,796 × 100 |
| Households with recorded lodgers | Sum `households_with_recorded_lodgers` / sum `private_households` × 100 |
| Known-status allowance share | 2,550 / (2,550 + 4,328) × 100 |
| 1884 arrival share | 548 / 4,826 × 100 |
| Field coverage | Count nonblank values / 7,446 × 100 |

The export inventory records older query variants and two extended analyses without a corresponding CSV. Do not assume that running the current SQL reproduces every historical snapshot exactly. Follow the [import and validation guide](mysql_english_dataset_import.md) for a new database run and preserve dated output versions.

## 10. Remaining work for the final portfolio release

1. Review this draft's narrative and select the findings that should lead the portfolio presentation.
2. Follow the [eight-item Tableau action plan](tableau_visualization_action_plan.md): complete the six proposed whole-population figures, incorporate the completed children's segment, and develop the origin map only after its historical geography is reviewed. Replace planned-figure notes with actual images and captions.
3. Reconcile older source, methodology, and limitations documents with the completed release stage.
4. Add the final repository and dashboard links, then review both report versions for consistent figures and claims.

The current report is a substantive analytical draft. It is ready for editorial review and visualization planning, while the visual evidence and final publication packaging remain to be completed.
