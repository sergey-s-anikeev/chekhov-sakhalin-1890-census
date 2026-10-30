# Household sizes and recorded lodgers

Completed 2026-10-30. [Published dashboard](https://public.tableau.com/views/Sakhalin1890Householdsizesandrecordedlodgers/Sakhalin1890Householdsizesandrecordedlodgers), owner-supplied URL. [Saved screenshot](../tableau/screenshots/households_lodgers_20261030.png), inspected locally.

Independent sources: [household-size frequencies](../tableau/data/household_size01092026.csv) and [settlement lodger summaries](../tableau/data/Lodgers_households_08092026.csv). The former counts household groups by size; the latter counts private households and recorded lodgers by district/settlement. They are not joined.

- Household-size bars use SUM(households) at each size, totaling 2,796 groups. One-person groups: 960; two-person: 775; together 1,735 (62.1%). The percentage tooltip uses `SUM([households]) / MIN({ FIXED : SUM([households]) })` to retain the full-source denominator after a table-calculation attempt returned 100% per bar.
- The all-settlement lodger indicator is `SUM([households_with_recorded_lodgers]) / SUM([private_households])`: 320 / 2,796 (11.4%). Its worksheet title is hidden; a horizontal dashboard container places a Text label beside the percentage sheet.
- Settlement bars use that same ratio within each settlement. A SUM(households_with_recorded_lodgers) filter of at least 1 omits zero-recorded-lodger settlements only from this chart. The District filter applies only to this chart. The overall indicator and size distribution remain all-district results.
- Alexandrovsky Post: 202 / 294 (68.7%); Doue Post: 22 / 40 (55.0%). Tooltips were configured with household denominators and recorded-lodger person counts; these are different units.

Household calculations exclude 246 people without a household ID. A one-person group does not necessarily establish explicit living-alone status; no recorded lodger does not prove none was present. The lodger source records 544 lodger persons and 40 people without a recorded household role; interpretation depends on recording coverage.

Local screenshot inspection confirms household-size counts, the 11.4% indicator, settlement percentages, zero-group exclusion note, District control and scope/coverage caveats. Live filtering, tooltips and source connections were not independently inspected. Item 6 of the [Tableau action plan](tableau_visualization_action_plan.md) is complete. Items 1–7 are complete; item 8, historical origin mapping, remains planned.
