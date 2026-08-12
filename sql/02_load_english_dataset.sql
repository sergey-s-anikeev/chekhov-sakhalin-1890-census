-- Load the compact English CSV into an empty sakhalin_1890_en table.
-- Requires the mysql client option --local-infile=1 and server permission
-- local_infile=ON. Change the path if the repository is moved.
-- Rerunning this file against a populated table intentionally fails on the
-- primary key instead of silently deleting or duplicating existing data.

LOAD DATA LOCAL INFILE
    'C:/Users/User/Documents/Work/sakhalin_1890/data/analytical/sakhalin_1890_en_v1.csv'
INTO TABLE sakhalin_1890_en
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
       OPTIONALLY ENCLOSED BY '"'
       ESCAPED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(
    person_id,
    source_position_id,
    district,
    settlement,
    @person_seq,
    @household_id,
    @household_type,
    @legal_status,
    full_name,
    sex,
    @family_status,
    @age,
    @age_months,
    @religion,
    @origin_place,
    @arrival_year,
    @occupation,
    @literacy,
    @marital_status,
    @living_alone_status,
    @allowance_status,
    @illness,
    @archive_code
)
SET
    person_seq          = CAST(@person_seq AS UNSIGNED),
    household_id        = NULLIF(@household_id, ''),
    household_type      = NULLIF(@household_type, ''),
    legal_status        = NULLIF(@legal_status, ''),
    family_status       = NULLIF(@family_status, ''),
    age                 = CAST(NULLIF(@age, '') AS UNSIGNED),
    age_months          = CAST(NULLIF(@age_months, '') AS UNSIGNED),
    religion            = NULLIF(@religion, ''),
    origin_place        = NULLIF(@origin_place, ''),
    arrival_year        = CAST(NULLIF(@arrival_year, '') AS UNSIGNED),
    occupation          = NULLIF(@occupation, ''),
    literacy            = NULLIF(@literacy, ''),
    marital_status      = NULLIF(@marital_status, ''),
    living_alone_status = NULLIF(@living_alone_status, ''),
    allowance_status    = CASE
                            WHEN @allowance_status = '' THEN NULL
                            WHEN @allowance_status = 'TRUE' THEN 1
                            WHEN @allowance_status = 'FALSE' THEN 0
                          END,
    illness             = NULLIF(@illness, ''),
    archive_code        = NULLIF(@archive_code, '');

SHOW WARNINGS;
SELECT COUNT(*) AS loaded_records FROM sakhalin_1890_en;
