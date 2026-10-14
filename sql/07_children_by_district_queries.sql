-- Proposed next visualization: children aged 0-15 by district.
-- Read-only MySQL query; Decision 40. No source changes.
-- Export as children_by_district_20261014.csv after validation.
-- One row per district. Denominator includes all recorded people in district,
-- including missing ages; age_not_recorded makes this coverage visible.
SELECT
    district,
    COUNT(*) AS district_people,
    SUM(CASE WHEN age BETWEEN 0 AND 15 THEN 1 ELSE 0 END) AS children,
    SUM(CASE WHEN age BETWEEN 0 AND 15 AND sex = 'Female' THEN 1 ELSE 0 END) AS female_children,
    SUM(CASE WHEN age BETWEEN 0 AND 15 AND sex = 'Male' THEN 1 ELSE 0 END) AS male_children,
    SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END) AS age_not_recorded,
    ROUND(100.0 * SUM(CASE WHEN age BETWEEN 0 AND 15 THEN 1 ELSE 0 END) / COUNT(*), 1) AS children_share_district_pct
FROM sakhalin_1890_en
GROUP BY district
ORDER BY children DESC, district;
