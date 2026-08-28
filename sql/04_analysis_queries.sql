-- Starter analytical queries for MySQL and Tableau reconciliation.

-- Population by district and settlement.
SELECT district, settlement, COUNT(*) AS people
FROM sakhalin_1890_en
GROUP BY district, settlement
ORDER BY district, people DESC, settlement;

-- Settlements ranked globally by population; settlement names are unique.
SELECT settlement, COUNT(*) AS people
FROM sakhalin_1890_en
GROUP BY settlement
ORDER BY people DESC;

-- Five largest settlements and their share of the complete population.
-- COUNT(*) calculates each settlement population after grouping.
-- SUM(COUNT(*)) OVER () calculates the population across all settlement groups.
-- ROUND(..., 0) displays whole percentages; LIMIT 5 returns the five largest settlements.
SELECT
    settlement,
    COUNT(*) AS people,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        0
    ) AS population_share_pct
FROM sakhalin_1890_en
GROUP BY settlement
ORDER BY people DESC
LIMIT 5;

-- Five largest settlements, followed by their combined subtotal.
-- The first CTE aggregates individual records to one row per settlement.
WITH settlement_population AS (
    SELECT
        settlement,
        COUNT(*) AS people
    FROM sakhalin_1890_en
    GROUP BY settlement
),
-- The second CTE calculates the total population and ranks settlements.
ranked_settlements AS (
    SELECT
        settlement,
        people,
        SUM(people) OVER () AS total_people,
        ROW_NUMBER() OVER (ORDER BY people DESC) AS population_rank
    FROM settlement_population
),
-- The third CTE retains only the five highest-ranked settlements.
top_five AS (
    SELECT *
    FROM ranked_settlements
    WHERE population_rank <= 5
)
-- UNION ALL appends the top-five subtotal as the final result row.
SELECT
    settlement,
    people,
    population_share_pct
FROM (
    SELECT
        settlement,
        people,
        ROUND(people * 100.0 / total_people, 0) AS population_share_pct,
        population_rank AS display_order
    FROM top_five

    UNION ALL

    SELECT
        'Top 5 subtotal' AS settlement,
        SUM(people) AS people,
        ROUND(
            SUM(people) * 100.0 / MAX(total_people),
            0
        ) AS population_share_pct,
        6 AS display_order
    FROM top_five
) AS top_five_with_subtotal
ORDER BY display_order;

-- District population ranking.
-- COUNT(*) counts all person records within each district.
-- GROUP BY returns one aggregated row per district.
-- DESC ranks districts from the largest to the smallest population.
SELECT
    district,
    COUNT(*) AS people
FROM sakhalin_1890_en
GROUP BY district
ORDER BY people DESC;

-- Age and sex profile. NULL age remains separate from recorded age zero.
SELECT district, sex,
       COUNT(*) AS people,
       SUM(age IS NULL) AS age_not_recorded,
       ROUND(AVG(age), 1) AS average_recorded_age,
       MIN(age) AS minimum_recorded_age,
       MAX(age) AS maximum_recorded_age
FROM sakhalin_1890_en
GROUP BY district, sex
ORDER BY district, sex;

-- Median age for the total population. Blank ages are excluded; age zero remains valid.
WITH ordered_ages AS (
    SELECT
        age,
        ROW_NUMBER() OVER (ORDER BY age) AS position_number,
        COUNT(*) OVER () AS total_people
    FROM sakhalin_1890_en
    WHERE age IS NOT NULL
)
SELECT AVG(age) AS median_age
FROM ordered_ages
WHERE position_number IN (
    FLOOR((total_people + 1) / 2),
    FLOOR((total_people + 2) / 2)
);

-- Median age by sex. Blank ages are excluded; age zero remains valid.
WITH ordered_ages_by_sex AS (
    SELECT
        sex,
        age,
        ROW_NUMBER() OVER (
            PARTITION BY sex
            ORDER BY age
        ) AS position_number,
        COUNT(*) OVER (
            PARTITION BY sex
        ) AS total_people
    FROM sakhalin_1890_en
    WHERE age IS NOT NULL
)
SELECT
    sex,
    AVG(age) AS median_age
FROM ordered_ages_by_sex
WHERE position_number IN (
    FLOOR((total_people + 1) / 2),
    FLOOR((total_people + 2) / 2)
)
GROUP BY sex
ORDER BY sex;

-- Child age distribution in completed years by sex (ages 0-17).
-- This query uses only the age column; age_months is not included.
-- Keep both sex values in the result for visualization filtering.
-- To export one sex only, replace the IN condition with sex = 'Female' or sex = 'Male'.
SELECT
    sex,
    age,
    COUNT(*) AS children
FROM sakhalin_1890_en
WHERE age BETWEEN 0 AND 17
  AND sex IN ('Female', 'Male')
GROUP BY sex, age
ORDER BY age, sex;

-- Legal-status distribution.
SELECT legal_status, COUNT(*) AS people
FROM sakhalin_1890_en
GROUP BY legal_status
ORDER BY people DESC, legal_status;

-- Literacy by sex.
SELECT sex, literacy, COUNT(*) AS people
FROM sakhalin_1890_en
GROUP BY sex, literacy
ORDER BY sex, people DESC;

-- Most frequently recorded occupations.
SELECT occupation, COUNT(*) AS people
FROM sakhalin_1890_en
WHERE occupation IS NOT NULL
GROUP BY occupation
ORDER BY people DESC, occupation
LIMIT 50;

-- Origins excluding people recorded as born/on Sakhalin.
SELECT origin_place, COUNT(*) AS people
FROM sakhalin_1890_en
WHERE origin_place IS NOT NULL
  AND origin_place <> 'On Sakhalin'
GROUP BY origin_place
ORDER BY people DESC, origin_place;

-- Arrival cohorts.
SELECT arrival_year, COUNT(*) AS people
FROM sakhalin_1890_en
WHERE arrival_year IS NOT NULL
GROUP BY arrival_year
ORDER BY arrival_year;

-- Household-size distribution for populated household identifiers.
WITH household_sizes AS (
    SELECT district, settlement, household_id, COUNT(*) AS household_size
    FROM sakhalin_1890_en
    WHERE household_id IS NOT NULL
    GROUP BY district, settlement, household_id
)
SELECT household_size, COUNT(*) AS households
FROM household_sizes
GROUP BY household_size
ORDER BY household_size;

-- Allowance status. NULL means not recorded, not FALSE.
SELECT CASE
         WHEN allowance_status = 1 THEN 'Yes'
         WHEN allowance_status = 0 THEN 'No'
         ELSE 'Not recorded'
       END AS allowance_label,
       COUNT(*) AS people
FROM sakhalin_1890_en
GROUP BY allowance_label
ORDER BY people DESC;

-- Illness categories, excluding blanks.
SELECT illness, COUNT(*) AS people
FROM sakhalin_1890_en
WHERE illness IS NOT NULL
GROUP BY illness
ORDER BY people DESC, illness;
