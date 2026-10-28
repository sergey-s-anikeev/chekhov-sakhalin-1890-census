# Sakhalin, 1890: Turning Historical Census Records into Analytical Evidence

**Short portfolio report — draft, updated 4 October 2026**  
**Tools:** Python, MySQL 8, Git; Tableau visualization planned.  
**Scope:** 7,446 person records across three districts and 51 settlements.  
**Detailed methodology and evidence:** [Full report](portfolio_report_full.md).

## The problem

Indexed historical census records contain demographic and social information, but document structure, inconsistent categories, and missing fields make them difficult to analyze directly. This project converts records from the published materials of Anton Chekhov's 1890 Sakhalin census into a traceable dataset and examines the patterns that the available evidence can support.

The unit of analysis is one named person record. Results describe the processed source material; complete coverage of Sakhalin's historical population is not established.

## The approach

The workflow extracts text from searchable PDFs, structures person records, and applies reviewed normalization rules. A versioned Russian dataset preserves historical values and provenance. A separate English analytical layer contains 23 columns with transliterated names, approved category mappings, and stable identifiers.

MySQL scripts create, load, validate, and analyze the dataset. The documented import loaded all 7,446 rows without skipped records or warnings. English-layer QA found zero transformation mismatches, unmapped populated values, or exception rows. SQL analysis produced 44 saved CSV snapshots, including earlier query variants, for visualization.

## Concrete data-cleaning examples

- **Incorrect category numbers:** On printed page 429, a name was labelled `5.` instead of `4.`. On page 440, a shifted sequence affected name, age, religion, and origin. Reviewed reassignment restored the fields; arrival year remained blank where no year was supplied.
- **Incorrect category text:** A misspelled legal-status label was normalized to the category mapped as `Penal convict`. Another record printed `1882` in the religion field as well as the arrival-year field; review documented the anomaly without guessing a religion. [Manual-review evidence](../outputs/qa/manual_review_decisions.csv).
- **Arrival-year checks:** Release notes identify `1976` instead of `1876` as an anomaly example, without a record-level locator. A separately traceable age/year conflict in `P005199` was resolved by correcting age `2 → 25`, while retaining arrival year `1887`. [Release notes](release_notes.md#12-numeric-range-qa); [approved correction](../outputs/qa/arrival_year_item21_20260717/arrival_year_item21_applied_diff.csv).
- **Footnotes and editorial markup:** Extensive annotations complicated record boundaries and numeric extraction. Documented examples include an age inflated by a footnote digit (`56 + 1 → 561`), truncated ages restored through review (`3 → 36`, `4 → 47`), and age/religion text split back into the correct fields. The evidence confirms these parsing problems without attributing every truncation or field shift to a footnote. Cleanup required field-specific rules to remove reference markers while preserving genuine numbers. [Age-correction evidence](../data/review/age_item7_20260713/owner_response/age_corrections_approved.csv); [parsing and correction notes](release_notes.md#10-critical-manual-review-corrections).

These cases demonstrate reviewed field recovery, controlled normalization, and consistency checks while preserving uncertainty. [The full report](portfolio_report_full.md#32-specific-cleaning-challenges-and-documented-decisions) provides source locators and distinguishes historical review decisions from current release values.

## Key findings

| Finding | Evidence | Interpretation |
|---|---|---|
| Geographic concentration | The five largest settlements contain 4,046 people, or 54.3% of all records. | Overall results are strongly influenced by a small number of settlements. |
| Different age/sex composition | The derived sex field is 66.1% male; median recorded ages are 35 for males and 29 for females. | The represented groups differ in composition; the analysis does not establish the causes. |
| District differences in male share | Male records account for 60.4% in Alexandrovsky, 67.8% in Tymovsky and 74.3% in Korsakovsky. Each denominator is the full recorded district population. | Differences in settlement development and migration phases are owner-proposed explanations that remain untested. |
| A substantial literacy difference | Among adults aged 16+ with recorded literacy, 39.1% of males and 10.3% of females carry the `Literate` label. | A 28.9 percentage-point difference remains when missing literacy is excluded; `Educated` remains a separate category. |
| Small households are common | One- and two-person groups account for 62.1% of 2,796 identified households. | Household counts reveal structure but do not directly measure living-alone status. |

Using all adults rather than only those with recorded literacy, the corresponding `Literate` shares are 33.3% for males and 9.2% for females. The denominator changes the result and must be visible to the reader. Percentage-point differences are calculated before rounding.

## The main analytical limitation

Field coverage varies sharply: age is available for 98.0% of records, occupation for 19.8%, and illness for 0.7%. Occupational rankings therefore describe a limited recorded subset, and blank illness entries cannot establish that a person was healthy. Arrival-year counts describe people represented in 1890, rather than annual immigration flows.

The sex field is derived from reviewed historical wording and naming evidence. Historical legal and geographic categories also require interpretation. None of the reported associations establishes causality, and the dataset is not treated as a probability sample of all island residents.

## Outcome and next step

The project delivers a validated English analytical dataset, a preserved Russian source-of-truth layer, documented transformation decisions, reusable SQL, and analytical exports. It demonstrates extraction, cleaning, provenance management, quality assurance, SQL aggregation and window functions, and careful communication of uncertainty.

The next deliverable is a Tableau dashboard centered on settlement concentration, demographic composition, legal status, literacy, and household structure. Charts and dashboard validation are pending. The final portfolio version will add verified visuals and public project links.

**Project files:** [Main README](../README.md) · [SQL analysis](../sql/04_analysis_queries.sql) · [Export inventory](../tableau/data/README.md) · [Full report with sources and calculations](portfolio_report_full.md).
