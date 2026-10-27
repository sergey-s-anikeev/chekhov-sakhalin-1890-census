-- Read-only MySQL 8+. Recorded literacy among residents aged 5–15.
-- Keep district and settlement together; identical settlement names may recur.
-- Query 1 is the optional Tableau export. Query 2 is validation only.
-- Residence and recorded literacy do not establish school attendance or school type.

-- 1. One row per settlement with children aged 5–15.
SELECT district, settlement,
       COUNT(*) AS children_5_15,
       SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END) AS literate,
       SUM(CASE WHEN literacy = 'Educated' THEN 1 ELSE 0 END) AS educated,
       SUM(CASE WHEN literacy = 'Illiterate' THEN 1 ELSE 0 END) AS illiterate,
       SUM(CASE WHEN literacy IS NULL THEN 1 ELSE 0 END) AS literacy_not_recorded,
       SUM(CASE WHEN literacy IS NOT NULL AND literacy NOT IN ('Literate', 'Educated', 'Illiterate')
                THEN 1 ELSE 0 END) AS other_recorded_literacy,
       ROUND(100.0 * SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END)
             / COUNT(*), 1) AS literate_pct_all,
       ROUND(100.0 * SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN literacy IS NOT NULL THEN 1 ELSE 0 END), 0), 1)
             AS literate_pct_recorded
FROM sakhalin_1890_en
WHERE age BETWEEN 5 AND 15
GROUP BY district, settlement
ORDER BY literate DESC, children_5_15 DESC, district, settlement;

-- 2. Expected: 536 children, 136 Literate, 0 Educated,
-- 178 Illiterate, 222 missing; total among recorded literacy: 314.
SELECT COUNT(*) AS children_5_15,
       SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END) AS literate,
       SUM(CASE WHEN literacy = 'Educated' THEN 1 ELSE 0 END) AS educated,
       SUM(CASE WHEN literacy = 'Illiterate' THEN 1 ELSE 0 END) AS illiterate,
       SUM(CASE WHEN literacy IS NULL THEN 1 ELSE 0 END) AS literacy_not_recorded,
       SUM(CASE WHEN literacy IS NOT NULL THEN 1 ELSE 0 END) AS literacy_recorded
FROM sakhalin_1890_en
WHERE age BETWEEN 5 AND 15;
