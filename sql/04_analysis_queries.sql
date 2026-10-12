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

-- Legal-status composition within each arrival-year cohort.
-- Missing arrival years are excluded; missing legal status remains a separate group.
-- Percentages use everyone with the same recorded arrival year as the denominator.
SELECT
    arrival_year,
    legal_status,
    COUNT(*) AS people,
    SUM(COUNT(*)) OVER (PARTITION BY arrival_year) AS cohort_people,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY arrival_year),
        1
    ) AS cohort_share_pct
FROM sakhalin_1890_en
WHERE arrival_year IS NOT NULL
GROUP BY arrival_year, legal_status
ORDER BY arrival_year, people DESC, legal_status;

-- Recorded marriage on Sakhalin by arrival-year cohort.
-- Includes compound labels recording a marriage on Sakhalin, even if also widowed.
-- This measures recorded marriage history, not necessarily current marriage status.
-- All people in the cohort are included, regardless of age or missing marital status.
SELECT
    arrival_year,
    COUNT(*) AS cohort_people,
    SUM(marital_status IS NULL) AS marital_status_not_recorded,
    SUM(CASE WHEN marital_status IN (
        'Married on Sakhalin',
        'Married on Sakhalin; Widowed',
        'Married in homeland and on Sakhalin'
    ) THEN 1 ELSE 0 END) AS recorded_married_on_sakhalin,
    ROUND(
        SUM(CASE WHEN marital_status IN (
            'Married on Sakhalin',
            'Married on Sakhalin; Widowed',
            'Married in homeland and on Sakhalin'
        ) THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        1
    ) AS recorded_married_on_sakhalin_pct
FROM sakhalin_1890_en
WHERE arrival_year IS NOT NULL
GROUP BY arrival_year
ORDER BY arrival_year;

-- Living-alone status within each arrival-year cohort.
-- NULL means not recorded; it must not be interpreted as not living alone.
SELECT
    arrival_year,
    living_alone_status,
    COUNT(*) AS people,
    SUM(COUNT(*)) OVER (PARTITION BY arrival_year) AS cohort_people,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY arrival_year),
        1
    ) AS cohort_share_pct
FROM sakhalin_1890_en
WHERE arrival_year IS NOT NULL
GROUP BY arrival_year, living_alone_status
ORDER BY arrival_year, people DESC, living_alone_status;

-- Most common recorded occupation within each arrival-year cohort.
-- Missing occupations cannot rank, but remain in the cohort percentage denominator.
-- Cohorts with no recorded occupation are omitted.
-- Meaningful non-employment categories remain eligible; ties resolve alphabetically.
-- Compound occupation labels are counted as recorded, without splitting them.
WITH occupation_counts AS (
    SELECT
        arrival_year,
        occupation,
        COUNT(*) AS people,
        SUM(COUNT(*)) OVER (PARTITION BY arrival_year) AS cohort_people
    FROM sakhalin_1890_en
    WHERE arrival_year IS NOT NULL
    GROUP BY arrival_year, occupation
),
ranked_occupations AS (
    SELECT
        arrival_year,
        occupation,
        people,
        cohort_people,
        ROW_NUMBER() OVER (
            PARTITION BY arrival_year
            ORDER BY people DESC, occupation
        ) AS occupation_rank
    FROM occupation_counts
    WHERE occupation IS NOT NULL
)
SELECT
    arrival_year,
    occupation,
    people,
    cohort_people,
    ROUND(people * 100.0 / cohort_people, 1) AS cohort_share_pct
FROM ranked_occupations
WHERE occupation_rank = 1
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

-- Extended analysis 1: Adult literacy by age band and sex.
-- Shares use all people in each age/sex group, including missing literacy.
-- Literate and Educated are reported separately; no category is reclassified.
WITH adult_age_bands AS (
    SELECT sex, literacy,
        CASE
            WHEN age < 25 THEN '16-24'
            WHEN age < 35 THEN '25-34'
            WHEN age < 45 THEN '35-44'
            WHEN age < 55 THEN '45-54'
            ELSE '55+'
        END AS age_band
    FROM sakhalin_1890_en
    WHERE age >= 16
)
SELECT age_band, sex, COUNT(*) AS people,
    SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END) AS literate_people,
    SUM(CASE WHEN literacy = 'Educated' THEN 1 ELSE 0 END) AS educated_people,
    SUM(CASE WHEN literacy = 'Illiterate' THEN 1 ELSE 0 END) AS illiterate_people,
    SUM(CASE WHEN literacy IS NULL THEN 1 ELSE 0 END) AS literacy_not_recorded,
    ROUND(100.0 * SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END) / COUNT(*), 1) AS literate_pct,
    ROUND(100.0 * SUM(CASE WHEN literacy = 'Educated' THEN 1 ELSE 0 END) / COUNT(*), 1) AS educated_pct,
    ROUND(100.0 * SUM(CASE WHEN literacy = 'Illiterate' THEN 1 ELSE 0 END) / COUNT(*), 1) AS illiterate_pct,
    ROUND(100.0 * SUM(CASE WHEN literacy IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS literacy_not_recorded_pct
FROM adult_age_bands
GROUP BY age_band, sex
ORDER BY age_band, sex;

-- Extended analysis 2: Allowance by legal status and five-year arrival cohort.
-- Calendar-aligned cohorts: 1880-1884, 1885-1889, 1890-1894, etc.
-- Final cohort is partial: these are records observed in 1890.
-- Missing legal status remains visible; missing arrival years are excluded.
WITH arrival_cohorts AS (
    SELECT FLOOR(arrival_year / 5.0) * 5 AS cohort_start,
        legal_status, allowance_status
    FROM sakhalin_1890_en
    WHERE arrival_year IS NOT NULL
)
SELECT cohort_start, CONCAT(cohort_start, '-', cohort_start + 4) AS arrival_cohort,
    legal_status, COUNT(*) AS people,
    SUM(CASE WHEN allowance_status = 1 THEN 1 ELSE 0 END) AS allowance_yes,
    SUM(CASE WHEN allowance_status = 0 THEN 1 ELSE 0 END) AS allowance_no,
    SUM(CASE WHEN allowance_status IS NULL THEN 1 ELSE 0 END) AS allowance_not_recorded,
    ROUND(100.0 * SUM(CASE WHEN allowance_status = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS allowance_pct_all,
    ROUND(100.0 * SUM(CASE WHEN allowance_status = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(allowance_status), 0), 1) AS allowance_pct_recorded
FROM arrival_cohorts
GROUP BY cohort_start, legal_status
ORDER BY cohort_start, people DESC, legal_status;

-- Extended analysis 3: Origin concentration within settlements.
-- Both shares use people with a recorded origin; On Sakhalin is included.
-- Ratio above 1 indicates greater representation than in the dataset overall.
-- Adjustable screening thresholds, not statistical significance criteria.
-- Require adequate settlement coverage and counts before ranking concentrations.
-- The overall origin baseline is calculated before screening any settlements.
-- Missing origins can still be selective even when these thresholds are met.
WITH concentration_settings AS (
    SELECT 50 AS min_settlement_people,
        50.0 AS min_origin_coverage_pct,
        20 AS min_recorded_origin_people,
        5 AS min_origin_group_people
),
origin_counts AS (
    SELECT district, settlement, origin_place, COUNT(*) AS people
    FROM sakhalin_1890_en
    WHERE origin_place IS NOT NULL
    GROUP BY district, settlement, origin_place
),
origin_totals AS (
    SELECT district, settlement, origin_place, people,
        SUM(people) OVER (PARTITION BY district, settlement) AS settlement_known_origin,
        SUM(people) OVER (PARTITION BY origin_place) AS origin_people_all,
        SUM(people) OVER () AS all_known_origin
    FROM origin_counts
),
settlement_totals AS (
    SELECT district, settlement, COUNT(*) AS settlement_people
    FROM sakhalin_1890_en
    GROUP BY district, settlement
)
SELECT o.district, o.settlement, o.origin_place, o.people,
    s.settlement_people, o.settlement_known_origin,
    s.settlement_people - o.settlement_known_origin AS origin_not_recorded,
    ROUND(100.0 * o.settlement_known_origin / s.settlement_people, 1) AS origin_coverage_pct,
    o.origin_people_all, o.all_known_origin,
    ROUND(100.0 * o.people / o.settlement_known_origin, 1) AS origin_share_in_settlement_pct,
    ROUND(100.0 * o.origin_people_all / o.all_known_origin, 1) AS origin_share_overall_pct,
    ROUND(1.0 * o.people * o.all_known_origin
        / (o.settlement_known_origin * o.origin_people_all), 2) AS concentration_ratio
FROM origin_totals o
JOIN settlement_totals s
    ON o.district = s.district AND o.settlement = s.settlement
CROSS JOIN concentration_settings c
WHERE s.settlement_people >= c.min_settlement_people
  AND 100.0 * o.settlement_known_origin / s.settlement_people >= c.min_origin_coverage_pct
  AND o.settlement_known_origin >= c.min_recorded_origin_people
  AND o.people >= c.min_origin_group_people
ORDER BY 1.0 * o.people * o.all_known_origin
    / (o.settlement_known_origin * o.origin_people_all) DESC,
    o.people DESC, o.district, o.settlement, o.origin_place;

-- Extended analysis 4: Origin diversity and dominant origin by settlement.
-- Distinct origins count recorded labels, including On Sakhalin.
-- Dominant-origin share uses recorded origins only; ties resolve alphabetically.
-- Settlements with no recorded origins remain in the output.
WITH settlement_totals AS (
    SELECT district, settlement, COUNT(*) AS people,
        COUNT(origin_place) AS recorded_origin_people,
        COUNT(DISTINCT origin_place) AS distinct_origins
    FROM sakhalin_1890_en
    GROUP BY district, settlement
),
ranked_origins AS (
    SELECT district, settlement, origin_place, COUNT(*) AS origin_people,
        ROW_NUMBER() OVER (
            PARTITION BY district, settlement
            ORDER BY COUNT(*) DESC, origin_place
        ) AS origin_rank
    FROM sakhalin_1890_en
    WHERE origin_place IS NOT NULL
    GROUP BY district, settlement, origin_place
)
SELECT s.district, s.settlement, s.people, s.distinct_origins,
    s.recorded_origin_people, s.people - s.recorded_origin_people AS origin_not_recorded,
    ROUND(100.0 * s.recorded_origin_people / s.people, 1) AS origin_completion_pct,
    r.origin_place AS dominant_origin, r.origin_people AS dominant_origin_people,
    ROUND(100.0 * r.origin_people / NULLIF(s.recorded_origin_people, 0), 1) AS dominant_origin_pct
FROM settlement_totals s
LEFT JOIN ranked_origins r
    ON s.district = r.district AND s.settlement = r.settlement AND r.origin_rank = 1
ORDER BY s.distinct_origins DESC, s.people DESC, s.district, s.settlement;

-- Extended analysis 5: Private households with recorded lodgers, by settlement.
-- Only private-household records with a populated household ID are grouped.
-- A missing household role cannot establish whether someone is a lodger.
WITH household_lodgers AS (
    SELECT district, settlement, household_id, COUNT(*) AS household_size,
        SUM(CASE WHEN family_status = 'Lodger' THEN 1 ELSE 0 END) AS lodgers,
        SUM(CASE WHEN family_status IS NULL THEN 1 ELSE 0 END) AS role_not_recorded
    FROM sakhalin_1890_en
    WHERE household_type = 'Private household' AND household_id IS NOT NULL
    GROUP BY district, settlement, household_id
)
SELECT district, settlement, COUNT(*) AS private_households,
    SUM(household_size) AS people,
    SUM(CASE WHEN lodgers > 0 THEN 1 ELSE 0 END) AS households_with_recorded_lodgers,
    SUM(lodgers) AS recorded_lodgers,
    SUM(role_not_recorded) AS people_with_role_not_recorded,
    ROUND(100.0 * SUM(CASE WHEN lodgers > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS households_with_lodgers_pct,
    ROUND(AVG(CASE WHEN lodgers > 0 THEN household_size END), 1) AS avg_size_with_recorded_lodgers,
    ROUND(AVG(CASE WHEN lodgers = 0 THEN household_size END), 1) AS avg_size_without_recorded_lodgers
FROM household_lodgers
GROUP BY district, settlement
ORDER BY households_with_lodgers_pct DESC, private_households DESC, district, settlement;

-- Extended analysis 6: Private households containing multiple non-child legal statuses.
-- Child of ... categories remain separate and do not inflate the status-diversity count.
-- Status labels are counted as recorded; non-child status does not imply adult age.
WITH household_statuses AS (
    SELECT district, settlement, household_id, COUNT(*) AS household_size,
        COUNT(DISTINCT CASE WHEN legal_status NOT LIKE 'Child of %' THEN legal_status END) AS distinct_non_child_statuses,
        SUM(CASE WHEN legal_status LIKE 'Child of %' THEN 1 ELSE 0 END) AS child_status_people,
        SUM(CASE WHEN legal_status IS NULL THEN 1 ELSE 0 END) AS legal_status_not_recorded,
        SUM(CASE WHEN legal_status = 'Penal convict' THEN 1 ELSE 0 END) AS penal_convicts,
        SUM(CASE WHEN legal_status = 'Free-status person' THEN 1 ELSE 0 END) AS free_status_people
    FROM sakhalin_1890_en
    WHERE household_type = 'Private household' AND household_id IS NOT NULL
    GROUP BY district, settlement, household_id
)
SELECT district, settlement, household_id, household_size,
    distinct_non_child_statuses, child_status_people, legal_status_not_recorded,
    penal_convicts, free_status_people,
    CASE WHEN penal_convicts > 0 AND free_status_people > 0 THEN 1 ELSE 0 END AS has_convict_and_free_status
FROM household_statuses
WHERE distinct_non_child_statuses >= 2
ORDER BY distinct_non_child_statuses DESC, household_size DESC,
    district, settlement, household_id;

-- Extended analysis 7: Recorded Sakhalin marriage by arrival cohort, adult age band, and sex.
-- Age is age in 1890, not age at arrival or at marriage.
-- Includes compound Sakhalin-marriage labels, even if also widowed.
-- Missing age or arrival year is excluded; missing marital status is reported.
-- Cohorts are calendar-aligned five-year groups; the final group is partial.
WITH marriage_cohorts AS (
    SELECT FLOOR(arrival_year / 5.0) * 5 AS cohort_start, sex, marital_status,
        CASE
            WHEN age < 25 THEN '16-24'
            WHEN age < 35 THEN '25-34'
            WHEN age < 45 THEN '35-44'
            WHEN age < 55 THEN '45-54'
            ELSE '55+'
        END AS age_band,
        CASE WHEN marital_status IN (
            'Married on Sakhalin', 'Married on Sakhalin; Widowed',
            'Married in homeland and on Sakhalin'
        ) THEN 1 ELSE 0 END AS sakhalin_marriage
    FROM sakhalin_1890_en
    WHERE arrival_year IS NOT NULL AND age >= 16
)
SELECT cohort_start, CONCAT(cohort_start, '-', cohort_start + 4) AS arrival_cohort,
    age_band, sex, COUNT(*) AS people,
    SUM(sakhalin_marriage) AS recorded_sakhalin_marriages,
    SUM(CASE WHEN marital_status IS NULL THEN 1 ELSE 0 END) AS marital_status_not_recorded,
    ROUND(100.0 * SUM(sakhalin_marriage) / COUNT(*), 1) AS sakhalin_marriage_pct_all,
    ROUND(100.0 * SUM(sakhalin_marriage) / NULLIF(COUNT(marital_status), 0), 1) AS sakhalin_marriage_pct_recorded
FROM marriage_cohorts
GROUP BY cohort_start, age_band, sex
ORDER BY age_band, sex, cohort_start;

-- Extended analysis 8: Literacy among people in each recorded occupation.
-- Literate and Educated remain separate categories.
-- Literacy percentages use known literacy only; missing literacy is shown separately.
-- Non-employment and compound occupation labels are retained as recorded.
WITH occupation_literacy AS (
    SELECT occupation, COUNT(*) AS people, COUNT(literacy) AS recorded_literacy,
        SUM(CASE WHEN literacy = 'Literate' THEN 1 ELSE 0 END) AS literate_people,
        SUM(CASE WHEN literacy = 'Educated' THEN 1 ELSE 0 END) AS educated_people,
        SUM(CASE WHEN literacy = 'Illiterate' THEN 1 ELSE 0 END) AS illiterate_people
    FROM sakhalin_1890_en
    WHERE occupation IS NOT NULL
    GROUP BY occupation
)
SELECT occupation, people, recorded_literacy,
    people - recorded_literacy AS literacy_not_recorded,
    ROUND(100.0 * (people - recorded_literacy) / people, 1) AS literacy_not_recorded_pct,
    literate_people, educated_people, illiterate_people,
    ROUND(100.0 * literate_people / NULLIF(recorded_literacy, 0), 1) AS literate_pct_recorded,
    ROUND(100.0 * educated_people / NULLIF(recorded_literacy, 0), 1) AS educated_pct_recorded,
    ROUND(100.0 * illiterate_people / NULLIF(recorded_literacy, 0), 1) AS illiterate_pct_recorded
FROM occupation_literacy
ORDER BY literate_pct_recorded DESC, recorded_literacy DESC, occupation;

-- Settlements with people originating from the Kingdom of Poland (1890 boundaries).
-- Scope: ten governorates plus the general Kingdom of Poland label.
-- Geographic origin does not establish ethnicity or modern citizenship.
-- Mapping: docs/reference/origin_place_reference_1890.md, Polish governorates, 1890.
-- Historical reference: https://tonik-libra.pl/wp-content/uploads/2019/07/Russian-Governors.pdf
-- Every settlement with a matching record is included; no size/coverage filter applies.
WITH kingdom_of_poland_records AS (
    SELECT district, settlement, origin_place,
        CASE WHEN origin_place IN (
            'Kingdom of Poland',
            'Warsaw Governorate',
            'Kalisz Governorate',
            'Kielce Governorate',
            'Lomza Governorate',
            'Lublin Governorate',
            'Piotrkow Governorate',
            'Plock Governorate',
            'Radom Governorate',
            'Siedlce Governorate',
            'Suwalki Governorate'
        ) THEN 1 ELSE 0 END AS from_kingdom_of_poland
    FROM sakhalin_1890_en
)
SELECT district, settlement,
    COUNT(*) AS settlement_people,
    SUM(from_kingdom_of_poland) AS kingdom_of_poland_people,
    ROUND(100.0 * SUM(from_kingdom_of_poland) / COUNT(*), 1) AS settlement_share_pct,
    SUM(CASE WHEN origin_place IS NULL THEN 1 ELSE 0 END) AS origin_not_recorded,
    ROUND(100.0 * COUNT(origin_place) / COUNT(*), 1) AS origin_coverage_pct
FROM kingdom_of_poland_records
GROUP BY district, settlement
HAVING SUM(from_kingdom_of_poland) > 0
ORDER BY kingdom_of_poland_people DESC, district, settlement;
