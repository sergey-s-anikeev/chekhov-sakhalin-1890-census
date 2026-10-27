-- Read-only MySQL 8+. Current resident records, not historical arrival flows.
-- No source categories are altered. Child scope: completed ages 0-15.

-- 1. Rank all residents by recorded arrival year; excludes missing arrival year.
-- Existing arrival_year_cohorts01092026.csv has the same people counts,
-- ordered chronologically. Optional export: arrival_year_ranked_20261019.csv.
SELECT arrival_year, COUNT(*) AS people,
       SUM(CASE WHEN age BETWEEN 0 AND 15 THEN 1 ELSE 0 END) AS children_0_15,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_recorded_arrivals_pct
FROM sakhalin_1890_en
WHERE arrival_year IS NOT NULL
GROUP BY arrival_year
ORDER BY people DESC, arrival_year;

-- 2. Child origin summary. In transit is not a birthplace or islander identity.
-- Optional export: children_origin_summary_20261019.csv.
WITH children_origin AS (
    SELECT CASE
        WHEN origin_place = 'On Sakhalin' THEN 'On Sakhalin'
        WHEN origin_place = 'In transit' THEN 'In transit'
        WHEN origin_place IS NULL THEN 'Not recorded'
        WHEN origin_place = 'Does not remember' THEN 'Origin unknown'
        ELSE 'Recorded origin elsewhere' END AS origin_group
    FROM sakhalin_1890_en WHERE age BETWEEN 0 AND 15
)
SELECT origin_group, COUNT(*) AS children,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_all_children_pct
FROM children_origin GROUP BY origin_group ORDER BY children DESC, origin_group;

-- 3. One aggregate source for extending all three children's dashboards.
-- Optional export: children_origin_dashboard_20261019.csv.
-- Sum children, never count rows. Filter ages 5-15 only for literacy views.
-- No person identifiers/names. Do not join to existing count aggregates:
-- those counts would repeat across these more detailed groups.
WITH children_origin AS (
    SELECT district, settlement, age, sex,
        COALESCE(literacy, 'Not recorded') AS literacy_status,
        CASE
            WHEN origin_place = 'On Sakhalin' THEN 'On Sakhalin'
            WHEN origin_place = 'In transit' THEN 'In transit'
            WHEN origin_place IS NULL THEN 'Not recorded'
            WHEN origin_place = 'Does not remember' THEN 'Origin unknown'
            ELSE 'Recorded origin elsewhere' END AS origin_group
    FROM sakhalin_1890_en WHERE age BETWEEN 0 AND 15
)
SELECT district, settlement, age, sex, literacy_status, origin_group,
       COUNT(*) AS children
FROM children_origin
GROUP BY district, settlement, age, sex, literacy_status, origin_group
ORDER BY district, settlement, age, sex, literacy_status, origin_group;

-- 4. Coverage and conflicting-field review. Not a chart export.
SELECT COUNT(*) AS people,
       COUNT(arrival_year) AS recorded_arrival_year,
       SUM(CASE WHEN arrival_year IS NULL THEN 1 ELSE 0 END) AS missing_arrival_year,
       SUM(CASE WHEN age BETWEEN 0 AND 15 THEN 1 ELSE 0 END) AS children,
       SUM(CASE WHEN age BETWEEN 0 AND 15 AND arrival_year IS NOT NULL THEN 1 ELSE 0 END) AS children_recorded_arrival,
       SUM(CASE WHEN age BETWEEN 0 AND 15 AND origin_place = 'On Sakhalin' AND arrival_year IS NOT NULL THEN 1 ELSE 0 END) AS sakhalin_origin_children_with_arrival
FROM sakhalin_1890_en;
