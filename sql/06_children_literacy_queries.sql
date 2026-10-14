-- Children aged 0-15: recorded literacy by completed age and sex.
-- MySQL 8+, read-only. Decision 40; approved source categories unchanged.
-- Export query 1 only as children_literacy_age_sex_20261013.csv (UTF-8, headers).
-- One row per observed age/sex/literacy group; absent groups are not exported.
-- Missing literacy is a display category, never inferred as Illiterate.
-- No percentages or repeated denominators: compute shares from summed counts.

-- 1. Visualization export.
SELECT
    age,
    sex,
    COALESCE(literacy, 'Not recorded') AS literacy_status,
    COUNT(*) AS children
FROM sakhalin_1890_en
WHERE age BETWEEN 0 AND 15
GROUP BY age, sex, COALESCE(literacy, 'Not recorded')
ORDER BY age, sex, literacy_status;

-- 2. Validation only; do not append this result to the export.
-- Expected: total 1467; Female 726; Male 741; Literate 136;
-- Educated 0; Illiterate 211; not recorded 1120; unexpected categories 0.
SELECT
    COUNT(*) AS children,
    SUM(CASE WHEN sex = 'Female' THEN 1 ELSE 0 END) AS female_children,
    SUM(CASE WHEN sex = 'Male' THEN 1 ELSE 0 END) AS male_children,
    SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END) AS literate_children,
    SUM(CASE WHEN literacy = 'Educated' THEN 1 ELSE 0 END) AS educated_children,
    SUM(CASE WHEN literacy = 'Illiterate' THEN 1 ELSE 0 END) AS illiterate_children,
    SUM(CASE WHEN literacy IS NULL THEN 1 ELSE 0 END) AS literacy_not_recorded,
    SUM(CASE WHEN literacy IS NOT NULL AND literacy NOT IN ('Literate', 'Educated', 'Illiterate') THEN 1 ELSE 0 END) AS unexpected_literacy
FROM sakhalin_1890_en
WHERE age BETWEEN 0 AND 15;
