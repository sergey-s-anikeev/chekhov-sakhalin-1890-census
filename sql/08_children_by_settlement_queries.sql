-- Children aged 0-15 by settlement (Decision 40).
-- Read-only MySQL. Export as children_by_settlement_20261014.csv.
-- Grain: district + settlement; includes settlements with zero children.
-- Main percentage denominator includes missing ages; report coverage separately.
-- Percentages are 0-100 values, not fractions. Never sum/average these percentages
-- across settlements: recompute from summed counts for the selected population.
SELECT
    district,
    settlement,
    COUNT(*) AS settlement_people,
    SUM(CASE WHEN age BETWEEN 0 AND 15 THEN 1 ELSE 0 END) AS children,
    SUM(CASE WHEN age BETWEEN 0 AND 15 AND sex = 'Female' THEN 1 ELSE 0 END) AS female_children,
    SUM(CASE WHEN age BETWEEN 0 AND 15 AND sex = 'Male' THEN 1 ELSE 0 END) AS male_children,
    SUM(CASE WHEN age >= 16 THEN 1 ELSE 0 END) AS residents_16_plus,
    COUNT(age) AS age_recorded,
    SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END) AS age_not_recorded,
    ROUND(100.0 * SUM(CASE WHEN age BETWEEN 0 AND 15 THEN 1 ELSE 0 END) / COUNT(*), 1) AS children_share_settlement_pct,
    ROUND(100.0 * SUM(CASE WHEN age BETWEEN 0 AND 15 THEN 1 ELSE 0 END) / NULLIF(COUNT(age), 0), 1) AS children_share_known_age_pct
FROM sakhalin_1890_en
GROUP BY district, settlement
ORDER BY children DESC, district, settlement;
