# Tableau visualization action plan

Agreed 2026-10-27. Items 1–6 are the whole-population figures proposed in the [full portfolio report](portfolio_report_full.md#7-dashboard-and-communication-plan). Item 7 is the completed children's segment. Item 8 adds a historical map of recorded origins of people represented on Sakhalin in 1890. This is a visualization plan, not a request for new SQL or CSV extracts. Use the saved aggregate files cited below; keep their different populations and grains separate.

For each new view, state the population, unit, denominator, missing coverage and date context. Check displayed totals and filter behavior against the [export inventory](../tableau/data/README.md) and documented figures before publication. Save a screenshot, public URL and short interpretation when a view is finished. Do not join unrelated aggregate snapshots just to make a dashboard.

## 1. Settlement concentration — completed 2026-10-28

- [x] Build ranked bars for **all recorded people** by settlement, colored or filtered by district. Use [settlement counts](../tableau/data/settlements_by_population22082026.csv); compare against the [top-five result](../tableau/data/top5_by_population_witsubtotal_22082026.csv).
- [x] Show the top-five combined count **4,046 / 7,446 (54.3%)** in a separate note or indicator. Do not sum a subtotal row together with its component settlements.
- [x] Label the figure as counts of people in the available records, not settlement population density or completeness.

Published: [Sakhalin 1890 — Settlement concentration](https://public.tableau.com/views/Sakhalin1890Settlementconcentration/Settlementconcentration). Owner supplied the URL on 2026-10-28. The [saved screenshot](../tableau/screenshots/settlement_concentration_20261028.png) was inspected locally: it shows the ranked bars, District filter, horizontally aligned selected-population total of 7,446, fixed all-district top-five note and scope caption. District-filter setup and total-sheet linkage were completed by the owner during authoring. Live interactions and workbook connections were not independently inspected. Item 2 is next.

## 2. Sex composition and recorded ages — completed 2026-10-28

- [x] Show female and male counts or shares for all **7,446** records, with median recorded ages **29** and **35** respectively. Use [district/sex counts and age coverage](../tableau/data/age_and_sex_profile22082026.csv) and [median age by sex](../tableau/data/median_age_bysex22082026.csv).
- [x] Keep the **147 missing ages** visible as a coverage note. Median age describes records with age available; do not infer causes of the sex or age differences.
- [x] Do not call the district/sex summary a full age pyramid; that requires age-band counts at the right grain.

Published: [Sakhalin 1890 — Sex composition by district and recorded ages](https://public.tableau.com/views/Sakhalin1890Sexcompositionbydistrictandrecordedages/Sakhalin1890Sexcompositionandrecordedages), owner-supplied URL received 2026-10-28. The [saved screenshot](../tableau/screenshots/sex_composition_recorded_ages_20261028.png) was inspected locally: Female 2,525, Male 4,921, District filter, all-district median ages Female 29 / Male 35 / Overall 33, and 147 missing ages (2.0%) are displayed. District filtering and percentage tooltips are owner-reported; live interactions and workbook connections were not independently inspected. The [full report, section 5.2](portfolio_report_full.md#52-male-records-predominate-and-median-ages-differ) and [short report](portfolio_report_short.md) record the district male shares (60.4%, 67.8%, 74.3%) and retain development/migration phases as untested explanations. Item 3, legal status, is next.

Proposed dashboard title: **Sakhalin 1890 — Sex composition by district and recorded ages**.

Proposed Tableau description (under 231 characters): Explore female and male shares across Sakhalin's three districts in 1890. The male share ranges from 60.4% to 74.3%. Median-age indicators cover all districts; 147 records have no recorded age.

## 3. Legal status — completed 2026-10-28

- [x] Build ranked bars from the [complete legal-status distribution](../tableau/data/legal_status_profile22082026.csv), showing count and share of all **7,446** records (owner-reported authoring completion).
- [x] Preserve the distinct source categories in the detailed worksheet; explain child-status labels and the display grouping used in the companion pie.
- [x] Retain the full distribution as the detailed authoring view and account for all records in the pie through an explicit Other category.

Published [combined-status pie dashboard](https://public.tableau.com/views/Sakhalin1890Combinedlegalandsocialstatusgroups/Sakhalin1890Combinedlegalandsocialstatusgroups); [screenshot](../tableau/screenshots/legal_status_groups_20261028.png) inspected locally. The four principal groups contain 4,114, 1,831, 862 and 522 people; Other contains 117, including 24 missing statuses. See [group definitions, historical context and evidence limits](legal_status_tableau.md). The bar view remains owner-reported; its separate public URL is not registered. Item 4 is next.

## 4. Adult literacy — completed 2026-10-29

- [x] Build separate panels, or another clearly labelled comparison, for `Literate / all adults aged 16+` and `Literate / adults with recorded literacy`, by sex. Use [adult literacy counts](../tableau/data/adult_education_profile2_01092026.csv); recalculate each rate from counts within its denominator.
- [x] Keep `Educated`, `Illiterate` and missing literacy separate. Show the missing-literacy count or share beside the rates.
- [x] Explain that the two denominators answer different questions and that recorded literacy does not establish school attendance.

Published: [Recorded adult literacy by sex](https://public.tableau.com/views/Sakhalin1890Recordedadultliteracybysex/Sakhalin1890Recordedadultliteracybysex), owner-supplied link received 2026-10-29. The [saved screenshot](../tableau/screenshots/adult_literacy_by_sex_20261029.png) confirms counts and both percentage panels. See [scope, denominators and findings](adult_literacy_tableau.md). Item 5 is next.

## 5. Recorded arrival years — completed 2026-10-29

- [x] Build bars by year from the [arrival-year distribution](../tableau/data/arrival_year_cohorts01092026.csv). Caption them **“Recorded arrival years among people represented in 1890.”**
- [x] Show coverage: **4,826 / 7,446** records have an arrival year. Identify 1884 as the largest recorded year (**548**), subject to the saved result's scope.
- [x] Do not interpret the bars as annual immigration flows; the records do not include all people who arrived and later died or departed.
- [x] Add a decade/year-ending heatmap companion using the same annual counts, preserving blanks outside 1865–1890.

Published: [Recorded arrival years](https://public.tableau.com/views/Sakhalin1890Recordedarrivalyears/Sakhalin1890Recordedarrivalyears), owner-supplied URL received 2026-10-29. The [saved screenshot](../tableau/screenshots/arrival_years_20261029.png) was inspected locally. [Dashboard scope and evidence](arrival_years_tableau.md). Item 6 is next.

## 6. Household size and lodgers — planned

- [ ] Show the [household-size distribution](../tableau/data/household_size01092026.csv) for **2,796 identified household groups**; one- and two-person groups total **1,735 (62.1%)**.
- [ ] Add a separate recorded-lodger indicator using the [lodger summary](../tableau/data/Lodgers_households_08092026.csv): **320 households with recorded lodgers**, among 2,796 private households in that result. Keep its definition and denominator visible.
- [ ] Note that **246 people have no household ID** and that no recorded lodger does not prove none was present.

## 7. Children's segment — completed

- [x] Publish children aged 0–15 by age and sex: [dashboard](https://public.tableau.com/views/Sakhalin1890Childrenaged015/Dashboard1).
- [x] Publish recorded literacy at ages 5–15: [dashboard](https://public.tableau.com/views/Recordedliteracyamongchildrenaged515/Dashboard1).
- [x] Publish children aged 0–15 by settlement, showing counts and shares: [dashboard](https://public.tableau.com/views/Sakhalin1890Childrenbysettlement/Sakhalin1890Childrenbysettlement).
- [x] Publish recorded origin by age with On Sakhalin, elsewhere, In transit and not recorded separated: [dashboard](https://public.tableau.com/views/ChildrensrecordedoriginbyageSakhalin1890/Dashboard1). The earlier [two-group view](https://public.tableau.com/shared/ZMWP4CSS2) is retained as a companion.
- [x] Save nine screenshots across these views; see [children's findings](children_findings.md) and [origin analysis](children_origin_age_profile.md). The owner supplied the URLs and reviewed the dashboards; saved screenshots were inspected locally. Open live workbook/source checks remain recorded in the [development tracker](english_dataset_development_tracker.md).

## 8. Origins of Sakhalin residents: Russian Empire map — planned

- [ ] Define the map population as **people represented in the 1890 Sakhalin records with a mappable recorded origin**, rather than ethnic “islanders” or all historical migrants. Start from [origin-place counts](../tableau/data/origin_place_01092026.csv) and the [historical origin reference](reference/origin_place_reference_1890.md). This saved export has **5,354 records across 97 non-`On Sakhalin` labels**; it includes non-geographic responses. For the full 7,446-record context, separately report **1,254 `On Sakhalin`** and **838 blank origins** rather than treating either as mapped locations in the export.
- [ ] Build a reviewed 1890-era place lookup: source label, historical administrative unit, representative point or boundary, map source/citation, confidence and treatment of ambiguous labels. Select a historically suitable Russian Empire base/boundary source and document its date and permitted use. Do not rely on Tableau's automatic modern geocoding for governorates and other historical places.
- [ ] Keep `On Sakhalin`, `In transit`, blank/not recorded, unknown and non-geographic responses distinct. Exclude unmappable values from the map marks but report their counts beside the map. Label any locations outside the Empire separately rather than forcing them into imperial units.
- [ ] Prefer proportional symbols at documented representative locations unless reliable historical boundary polygons are obtained. If using a filled-region map, verify every polygon and label against the historical source and explain that color shows **record counts**, not a population-adjusted origin rate.
- [ ] Reconcile mapped and unmapped counts to the 5,354-record origin export, and reconcile that export plus 1,254 `On Sakhalin` and 838 blank origins to all 7,446 records. Test every location displayed, add a coverage note and caption, then save the Tableau link and screenshot. Avoid interpreting a recorded origin label as nationality, citizenship or proof of a person's migration route.

The owner paused additional CSV extracts and general review on 2026-10-27. Items 1–6 can be designed from existing snapshots. Item 8 needs researched map geography before construction; any new lookup or export should be a separately documented, reviewed artifact if work resumes.
