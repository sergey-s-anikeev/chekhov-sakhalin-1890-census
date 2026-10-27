-- Read-only MySQL 8+. Children aged 0-15; completed ages, both sexes.
-- Each percentage uses ALL children at that age, including On Sakhalin.
-- Total row uses all 1,467 children, not an average of age percentages.
-- Keep missing and non-geographic origins separate from named origins elsewhere.

-- 1. Detailed origin groups by age, plus total.
WITH age_counts AS (
    SELECT age, COUNT(*) AS all_children,
        SUM(CASE WHEN origin_place = 'On Sakhalin' THEN 1 ELSE 0 END) AS on_sakhalin,
        SUM(CASE WHEN origin_place IS NOT NULL
                  AND origin_place NOT IN ('On Sakhalin', 'In transit', 'Does not remember') THEN 1 ELSE 0 END) AS origin_elsewhere,
        SUM(CASE WHEN origin_place = 'In transit' THEN 1 ELSE 0 END) AS in_transit,
        SUM(CASE WHEN origin_place IS NULL THEN 1 ELSE 0 END) AS origin_not_recorded,
        SUM(CASE WHEN origin_place = 'Does not remember' THEN 1 ELSE 0 END) AS origin_unknown
    FROM sakhalin_1890_en
    WHERE age BETWEEN 0 AND 15
    GROUP BY age
), with_total AS (
    SELECT * FROM age_counts
    UNION ALL
    SELECT NULL, SUM(all_children), SUM(on_sakhalin), SUM(origin_elsewhere),
           SUM(in_transit), SUM(origin_not_recorded), SUM(origin_unknown)
    FROM age_counts
)
SELECT age, CASE WHEN age IS NULL THEN 'Total' ELSE 'Age' END AS row_type,
       all_children, origin_elsewhere,
       ROUND(100.0 * origin_elsewhere / all_children, 1) AS origin_elsewhere_pct,
       in_transit, ROUND(100.0 * in_transit / all_children, 1) AS in_transit_pct,
       origin_not_recorded,
       ROUND(100.0 * origin_not_recorded / all_children, 1) AS origin_not_recorded_pct,
       origin_unknown,
       ROUND(100.0 * origin_unknown / all_children, 1) AS origin_unknown_pct
FROM with_total ORDER BY age IS NULL, age;

-- 2. On Sakhalin versus all other origin records, plus total.
-- All other includes named elsewhere, In transit, missing and unknown origins.
-- This complement is NOT a migrant count or a confirmed non-Sakhalin-born count.
WITH age_counts AS (
    SELECT age, COUNT(*) AS all_children,
        SUM(CASE WHEN origin_place = 'On Sakhalin' THEN 1 ELSE 0 END) AS on_sakhalin
    FROM sakhalin_1890_en WHERE age BETWEEN 0 AND 15 GROUP BY age
), with_total AS (
    SELECT * FROM age_counts
    UNION ALL
    SELECT NULL, SUM(all_children), SUM(on_sakhalin) FROM age_counts
)
SELECT age, CASE WHEN age IS NULL THEN 'Total' ELSE 'Age' END AS row_type,
       all_children, on_sakhalin,
       ROUND(100.0 * on_sakhalin / all_children, 1) AS on_sakhalin_pct,
       all_children - on_sakhalin AS all_other_origins,
       ROUND(100.0 * (all_children - on_sakhalin) / all_children, 1) AS all_other_origins_pct
FROM with_total ORDER BY age IS NULL, age;

-- Each result has 16 age rows and one Total row. Exclude row_type = 'Total'
-- before aggregating in Tableau, otherwise the population will be doubled.
