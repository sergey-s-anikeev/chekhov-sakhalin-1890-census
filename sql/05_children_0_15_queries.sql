-- Sakhalin children's analytical block: Children aged 0-15.
-- Approved 2026-10-12, Decision 40. MySQL 8+; select your existing schema first.
-- Read-only queries: no table/data changes. Age is completed years.
-- Includes recorded age zero; excludes missing age. Child-of legal status
-- is a relationship/status label and is not used to determine eligibility.
-- Queries 1 and 2 replace the two child queries in 04_analysis_queries.sql.

-- 1. Export this result as children_age_0_15_10122026.csv.
-- Expected: 32 rows (16 ages x 2 sexes), 1,467 children in total.
SELECT
    sex,
    age,
    COUNT(*) AS children
FROM sakhalin_1890_en
WHERE age BETWEEN 0 AND 15
  AND sex IN ('Female', 'Male')
GROUP BY sex, age
ORDER BY age, sex;

-- 2. Export this result as children_by_sex_0_15_10122026.csv.
-- Expected: Female 726 (49.5%); Male 741 (50.5%).
-- Percentage denominator is all 1,467 children, not all census records.
SELECT
    sex,
    COUNT(*) AS children,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        1
    ) AS child_group_share_pct
FROM sakhalin_1890_en
WHERE age BETWEEN 0 AND 15
  AND sex IN ('Female', 'Male')
GROUP BY sex
ORDER BY sex;

-- 3. Validation only; keep separate from the two chart data sources.
-- Expected: 7446, 1467, 726, 741, 0, 5832, 147, 204 respectively.
SELECT
    COUNT(*) AS total_people,
    SUM(CASE WHEN age BETWEEN 0 AND 15 THEN 1 ELSE 0 END) AS children_0_15,
    SUM(CASE WHEN age BETWEEN 0 AND 15 AND sex = 'Female' THEN 1 ELSE 0 END) AS female_children,
    SUM(CASE WHEN age BETWEEN 0 AND 15 AND sex = 'Male' THEN 1 ELSE 0 END) AS male_children,
    SUM(CASE WHEN age BETWEEN 0 AND 15 AND (sex IS NULL OR sex NOT IN ('Female', 'Male')) THEN 1 ELSE 0 END) AS children_other_or_missing_sex,
    SUM(CASE WHEN age >= 16 THEN 1 ELSE 0 END) AS residents_16_plus,
    SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END) AS age_not_recorded,
    SUM(CASE WHEN age = 0 THEN 1 ELSE 0 END) AS recorded_age_zero
FROM sakhalin_1890_en;
