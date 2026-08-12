-- Expected result: every row in validation_summary has status PASS.

SELECT 'record_count' AS control_name,
       CAST(COUNT(*) AS CHAR) AS actual_value,
       '7446' AS expected_value,
       IF(COUNT(*) = 7446, 'PASS', 'FAIL') AS status
FROM sakhalin_1890_en
UNION ALL
SELECT 'unique_person_id', CAST(COUNT(DISTINCT person_id) AS CHAR), '7446',
       IF(COUNT(DISTINCT person_id) = 7446, 'PASS', 'FAIL')
FROM sakhalin_1890_en
UNION ALL
SELECT 'unique_source_position_id', CAST(COUNT(DISTINCT source_position_id) AS CHAR), '7446',
       IF(COUNT(DISTINCT source_position_id) = 7446, 'PASS', 'FAIL')
FROM sakhalin_1890_en
UNION ALL
SELECT 'populated_household_groups',
       CAST(COUNT(DISTINCT CASE WHEN household_id IS NOT NULL
            THEN CONCAT_WS('|', district, settlement, household_id) END) AS CHAR),
       '2796',
       IF(COUNT(DISTINCT CASE WHEN household_id IS NOT NULL
            THEN CONCAT_WS('|', district, settlement, household_id) END) = 2796, 'PASS', 'FAIL')
FROM sakhalin_1890_en
UNION ALL
SELECT 'blank_household_id', CAST(SUM(household_id IS NULL) AS CHAR), '246',
       IF(SUM(household_id IS NULL) = 246, 'PASS', 'FAIL')
FROM sakhalin_1890_en
UNION ALL
SELECT 'age_zero', CAST(SUM(age = 0) AS CHAR), '204',
       IF(SUM(age = 0) = 204, 'PASS', 'FAIL')
FROM sakhalin_1890_en
UNION ALL
SELECT 'blank_age', CAST(SUM(age IS NULL) AS CHAR), '147',
       IF(SUM(age IS NULL) = 147, 'PASS', 'FAIL')
FROM sakhalin_1890_en
UNION ALL
SELECT 'allowance_true', CAST(SUM(allowance_status = 1) AS CHAR), '2550',
       IF(SUM(allowance_status = 1) = 2550, 'PASS', 'FAIL')
FROM sakhalin_1890_en
UNION ALL
SELECT 'allowance_false', CAST(SUM(allowance_status = 0) AS CHAR), '4328',
       IF(SUM(allowance_status = 0) = 4328, 'PASS', 'FAIL')
FROM sakhalin_1890_en
UNION ALL
SELECT 'allowance_null', CAST(SUM(allowance_status IS NULL) AS CHAR), '568',
       IF(SUM(allowance_status IS NULL) = 568, 'PASS', 'FAIL')
FROM sakhalin_1890_en
UNION ALL
SELECT 'rgb_archive_codes', CAST(SUM(archive_code LIKE 'RGB %') AS CHAR), '7223',
       IF(SUM(archive_code LIKE 'RGB %') = 7223, 'PASS', 'FAIL')
FROM sakhalin_1890_en
UNION ALL
SELECT 'rgali_archive_codes', CAST(SUM(archive_code LIKE 'RGALI %') AS CHAR), '222',
       IF(SUM(archive_code LIKE 'RGALI %') = 222, 'PASS', 'FAIL')
FROM sakhalin_1890_en
UNION ALL
SELECT 'dmch_archive_codes', CAST(SUM(archive_code LIKE 'DMCh %') AS CHAR), '1',
       IF(SUM(archive_code LIKE 'DMCh %') = 1, 'PASS', 'FAIL')
FROM sakhalin_1890_en
UNION ALL
SELECT 'blank_archive_code', CAST(SUM(archive_code IS NULL) AS CHAR), '0',
       IF(SUM(archive_code IS NULL) = 0, 'PASS', 'FAIL')
FROM sakhalin_1890_en;

-- Expected: zero rows.
SELECT district, settlement, person_seq, COUNT(*) AS duplicate_count
FROM sakhalin_1890_en
GROUP BY district, settlement, person_seq
HAVING COUNT(*) > 1;

-- Expected: zero rows. This scans every English text field for Cyrillic.
SELECT person_id
FROM sakhalin_1890_en
WHERE CONCAT_WS('|', district, settlement, household_type, legal_status,
      full_name, sex, family_status, religion, origin_place, occupation,
      literacy, marital_status, living_alone_status, illness, archive_code)
      REGEXP '[А-Яа-яЁё]';

-- Expected district totals.
SELECT district, COUNT(*) AS records
FROM sakhalin_1890_en
GROUP BY district
ORDER BY records DESC;

-- Field-level NULL profile for reconciliation with the CSV QA report.
SELECT
    SUM(household_id IS NULL) AS household_id_nulls,
    SUM(household_type IS NULL) AS household_type_nulls,
    SUM(legal_status IS NULL) AS legal_status_nulls,
    SUM(family_status IS NULL) AS family_status_nulls,
    SUM(age IS NULL) AS age_nulls,
    SUM(age_months IS NULL) AS age_months_nulls,
    SUM(religion IS NULL) AS religion_nulls,
    SUM(origin_place IS NULL) AS origin_place_nulls,
    SUM(arrival_year IS NULL) AS arrival_year_nulls,
    SUM(occupation IS NULL) AS occupation_nulls,
    SUM(literacy IS NULL) AS literacy_nulls,
    SUM(marital_status IS NULL) AS marital_status_nulls,
    SUM(living_alone_status IS NULL) AS living_alone_status_nulls,
    SUM(allowance_status IS NULL) AS allowance_status_nulls,
    SUM(illness IS NULL) AS illness_nulls,
    SUM(archive_code IS NULL) AS archive_code_nulls
FROM sakhalin_1890_en;
