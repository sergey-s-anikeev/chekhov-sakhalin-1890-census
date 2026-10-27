-- Read-only MySQL 8+. Compare recorded child literacy by origin label.
-- Two age scopes: 5-15 for the published literacy view; 0-15 as a scope check.
-- In transit and missing origin do not establish a birthplace.
-- Missing literacy remains separate from recorded Illiterate.

-- 1. Four groups: preserve named elsewhere, In transit and missing origin.

WITH categorized AS (
    SELECT age, literacy,
           CASE
               WHEN origin_place = 'On Sakhalin' THEN 'On Sakhalin'
               WHEN origin_place = 'In transit' THEN 'In transit'
               WHEN origin_place IS NULL THEN 'Origin not recorded'
               WHEN origin_place = 'Does not remember' THEN 'Origin unknown'
               ELSE 'Recorded origin elsewhere'
           END AS origin_group
    FROM sakhalin_1890_en
    WHERE age BETWEEN 0 AND 15
), scoped AS (
    SELECT '0-15' AS age_scope, origin_group, literacy FROM categorized
    UNION ALL
    SELECT '5-15' AS age_scope, origin_group, literacy FROM categorized
    WHERE age BETWEEN 5 AND 15
)
SELECT age_scope, origin_group,
       COUNT(*) AS children,
       SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END) AS literate,
       SUM(CASE WHEN literacy = 'Educated' THEN 1 ELSE 0 END) AS educated,
       SUM(CASE WHEN literacy = 'Illiterate' THEN 1 ELSE 0 END) AS illiterate,
       SUM(CASE WHEN literacy IS NULL THEN 1 ELSE 0 END) AS literacy_not_recorded,
       ROUND(100.0 * SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END)
             / COUNT(*), 1) AS literate_pct_all,
       ROUND(100.0 * SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN literacy IS NOT NULL THEN 1 ELSE 0 END), 0), 1)
             AS literate_pct_recorded
FROM scoped
GROUP BY age_scope, origin_group
ORDER BY age_scope, origin_group;

-- 2. Two-group display requested by the owner.
-- "All other origin records" combines named elsewhere, In transit and
-- missing/unknown origin. It is not a count of children born outside Sakhalin.
WITH scoped AS (
    SELECT '0-15' AS age_scope, origin_place, literacy
    FROM sakhalin_1890_en WHERE age BETWEEN 0 AND 15
    UNION ALL
    SELECT '5-15' AS age_scope, origin_place, literacy
    FROM sakhalin_1890_en WHERE age BETWEEN 5 AND 15
)
SELECT age_scope,
       CASE WHEN origin_place = 'On Sakhalin' THEN 'On Sakhalin'
            ELSE 'All other origin records' END AS origin_group,
       COUNT(*) AS children,
       SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END) AS literate,
       SUM(CASE WHEN literacy = 'Educated' THEN 1 ELSE 0 END) AS educated,
       SUM(CASE WHEN literacy = 'Illiterate' THEN 1 ELSE 0 END) AS illiterate,
       SUM(CASE WHEN literacy IS NULL THEN 1 ELSE 0 END) AS literacy_not_recorded,
       ROUND(100.0 * SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END)
             / COUNT(*), 1) AS literate_pct_all,
       ROUND(100.0 * SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN literacy IS NOT NULL THEN 1 ELSE 0 END), 0), 1)
             AS literate_pct_recorded
FROM scoped
GROUP BY age_scope, origin_group
ORDER BY age_scope, origin_group;
