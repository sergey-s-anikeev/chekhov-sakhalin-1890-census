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

-- Male and female shares within the child population aged 16 or younger.
-- Missing ages are excluded by the age condition.
SELECT
    sex,
    COUNT(*) AS children,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        1
    ) AS child_group_share_pct
FROM sakhalin_1890_en
WHERE age <= 16
  AND sex IN ('Female', 'Male')
GROUP BY sex
ORDER BY sex;

-- Legal-status distribution.
SELECT legal_status, COUNT(*) AS people
FROM sakhalin_1890_en
GROUP BY legal_status
ORDER BY people DESC, legal_status;

-- Four largest legal-status categories by population, excluding child categories.
SELECT
    legal_status,
    COUNT(*) AS people
FROM sakhalin_1890_en
WHERE legal_status IS NOT NULL
  AND legal_status NOT LIKE 'Child of %'
GROUP BY legal_status
ORDER BY people DESC, legal_status
LIMIT 4;

-- Four largest non-child legal-status categories and their share of the complete population.
-- The denominator includes every person in the dataset, including child categories.
SELECT
    legal_status,
    COUNT(*) AS people,
    ROUND(
        COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sakhalin_1890_en),
        1
    ) AS population_share_pct
FROM sakhalin_1890_en
WHERE legal_status IS NOT NULL
  AND legal_status NOT LIKE 'Child of %'
GROUP BY legal_status
ORDER BY people DESC, legal_status
LIMIT 4;

-- Literacy by sex.
SELECT sex, literacy, COUNT(*) AS people
FROM sakhalin_1890_en
GROUP BY sex, literacy
ORDER BY sex, people DESC;

-- Adult literacy by sex (age 16 and older).
-- Records with a missing age are excluded by the age condition.
SELECT
    sex,
    literacy,
    COUNT(*) AS adults
FROM sakhalin_1890_en
WHERE age >= 16
GROUP BY sex, literacy
ORDER BY sex, adults DESC, literacy;

-- Most frequently recorded occupations.
SELECT occupation, COUNT(*) AS people
FROM sakhalin_1890_en
WHERE occupation IS NOT NULL
GROUP BY occupation
ORDER BY people DESC, occupation
LIMIT 50;

-- Five most frequently recorded occupations among males.
SELECT
    occupation,
    COUNT(*) AS people
FROM sakhalin_1890_en
WHERE sex = 'Male'
  AND occupation IS NOT NULL
GROUP BY occupation
ORDER BY people DESC, occupation
LIMIT 5;

-- Five most frequently recorded occupations among females.
SELECT
    occupation,
    COUNT(*) AS people
FROM sakhalin_1890_en
WHERE sex = 'Female'
  AND occupation IS NOT NULL
  AND occupation NOT IN ('Dependent on husband', 'No occupation')
GROUP BY occupation
ORDER BY people DESC, occupation
LIMIT 5;

-- Origins excluding people recorded as born/on Sakhalin.
SELECT origin_place, COUNT(*) AS people
FROM sakhalin_1890_en
WHERE origin_place IS NOT NULL
  AND origin_place <> 'On Sakhalin'
GROUP BY origin_place
ORDER BY people DESC, origin_place;

-- Age distribution for people recorded as born on Sakhalin.
-- Missing ages are excluded; recorded age zero remains valid.
SELECT
    age,
    COUNT(*) AS people
FROM sakhalin_1890_en
WHERE origin_place = 'On Sakhalin'
  AND age IS NOT NULL
GROUP BY age
ORDER BY age;

-- Arrival cohorts.
SELECT arrival_year, COUNT(*) AS people
FROM sakhalin_1890_en
WHERE arrival_year IS NOT NULL
GROUP BY arrival_year
ORDER BY arrival_year;

-- Origin-place distribution for people who arrived in 1884.
SELECT
    origin_place,
    COUNT(*) AS people
FROM sakhalin_1890_en
WHERE arrival_year = 1884
  AND origin_place IS NOT NULL
GROUP BY origin_place
ORDER BY people DESC, origin_place;

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

-- Ten largest private households, with their settlements.
-- Household size counts all people sharing the same populated household identifier.
SELECT
    district,
    settlement,
    household_id,
    COUNT(*) AS household_size
FROM sakhalin_1890_en
WHERE household_id IS NOT NULL
  AND household_type = 'Private household'
GROUP BY district, settlement, household_id
ORDER BY household_size DESC, district, settlement, household_id
LIMIT 10;

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

-- Arrival-year distribution for people receiving an allowance.
SELECT
    arrival_year,
    COUNT(*) AS people
FROM sakhalin_1890_en
WHERE allowance_status = 1
  AND arrival_year IS NOT NULL
GROUP BY arrival_year
ORDER BY arrival_year;

-- Percentage of each sex receiving an allowance.
-- The denominator is the complete population of that sex.
SELECT
    sex,
    COUNT(*) AS total_people,
    SUM(allowance_status = 1) AS people_receiving_allowance,
    ROUND(
        SUM(allowance_status = 1) * 100.0 / COUNT(*),
        1
    ) AS receiving_allowance_pct
FROM sakhalin_1890_en
GROUP BY sex
ORDER BY sex;

-- Illness categories, excluding blanks.
SELECT illness, COUNT(*) AS people
FROM sakhalin_1890_en
WHERE illness IS NOT NULL
GROUP BY illness
ORDER BY people DESC, illness;

-- Illness-category distribution by sex, excluding blanks.
SELECT
    sex,
    illness,
    COUNT(*) AS people
FROM sakhalin_1890_en
WHERE illness IS NOT NULL
GROUP BY sex, illness
ORDER BY sex, people DESC, illness;

-- Ten settlements with the lowest completion of core analytical fields.
-- The eleven fields assessed are legal status, age, religion, origin place,
-- arrival year, occupation, literacy, marital status, living-alone status,
-- allowance status, and illness.
WITH settlement_completeness AS (
    SELECT
        district,
        settlement,
        COUNT(*) AS people,
        SUM(
            (legal_status IS NOT NULL) +
            (age IS NOT NULL) +
            (religion IS NOT NULL) +
            (origin_place IS NOT NULL) +
            (arrival_year IS NOT NULL) +
            (occupation IS NOT NULL) +
            (literacy IS NOT NULL) +
            (marital_status IS NOT NULL) +
            (living_alone_status IS NOT NULL) +
            (allowance_status IS NOT NULL) +
            (illness IS NOT NULL)
        ) AS completed_fields,
        COUNT(*) * 11 AS possible_fields
    FROM sakhalin_1890_en
    GROUP BY district, settlement
)
SELECT
    district,
    settlement,
    people,
    completed_fields,
    possible_fields,
    ROUND(completed_fields * 100.0 / possible_fields, 1) AS completion_pct
FROM settlement_completeness
ORDER BY completion_pct, people DESC, district, settlement
LIMIT 10;

-- Ten settlements with the highest completion of core analytical fields.
WITH settlement_completeness AS (
    SELECT
        district,
        settlement,
        COUNT(*) AS people,
        SUM(
            (legal_status IS NOT NULL) +
            (age IS NOT NULL) +
            (religion IS NOT NULL) +
            (origin_place IS NOT NULL) +
            (arrival_year IS NOT NULL) +
            (occupation IS NOT NULL) +
            (literacy IS NOT NULL) +
            (marital_status IS NOT NULL) +
            (living_alone_status IS NOT NULL) +
            (allowance_status IS NOT NULL) +
            (illness IS NOT NULL)
        ) AS completed_fields,
        COUNT(*) * 11 AS possible_fields
    FROM sakhalin_1890_en
    GROUP BY district, settlement
)
SELECT
    district,
    settlement,
    people,
    completed_fields,
    possible_fields,
    ROUND(completed_fields * 100.0 / possible_fields, 1) AS completion_pct
FROM settlement_completeness
ORDER BY completion_pct DESC, people DESC, district, settlement
LIMIT 10;
