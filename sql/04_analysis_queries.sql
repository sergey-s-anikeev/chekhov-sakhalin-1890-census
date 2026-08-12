-- Starter analytical queries for MySQL and Tableau reconciliation.

-- Population by district and settlement.
SELECT district, settlement, COUNT(*) AS people
FROM sakhalin_1890_en
GROUP BY district, settlement
ORDER BY district, people DESC, settlement;

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
