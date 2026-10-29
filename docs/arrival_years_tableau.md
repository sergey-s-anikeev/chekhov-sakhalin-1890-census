# Recorded arrival years — Tableau

Completed 2026-10-29. [Published dashboard](https://public.tableau.com/views/Sakhalin1890Recordedarrivalyears/Sakhalin1890Recordedarrivalyears), owner-supplied URL. [Saved screenshot](../tableau/screenshots/arrival_years_20261029.png), inspected locally.

Source: [arrival-year export](../tableau/data/arrival_year_cohorts01092026.csv), 26 annual rows covering 1865–1890 and 4,826 people. Arrival year is recorded for 64.8% of the full 7,446 records; 2,620 have no arrival year, including records for which arrival may not apply. No new CSV was generated.

The dashboard contains chronological count bars, a highlighted 1884 peak (548 people; 11.4% of recorded arrival years), and a decade/year-ending heatmap using the same counts. Heatmap fields are `INT([arrival_year] / 10) * 10` for decade and `[arrival_year] - [Decade]` for year ending. Blank cells outside 1865–1890 are outside the observed range, not zero arrival counts. The heatmap's color scale represents people, with equal-sized cells.

These are recorded arrival-year groups among people represented in 1890, not annual immigration flows. People who died, departed or were omitted before observation are not measured by these counts. The 1890 bar is not interpreted as a complete annual total.

Local screenshot inspection confirms chronological bars, 1884 = 548 in both panels, coverage/denominator notes and the interpretation caveats. Percentage tooltips and live workbook connections were not independently inspected. Item 5 of the [Tableau action plan](tableau_visualization_action_plan.md) is complete; item 6, household size and lodgers, is next.
