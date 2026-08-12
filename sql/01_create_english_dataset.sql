-- Sakhalin 1890 compact English dataset — MySQL 8.0+
-- Run inside the target database before loading the CSV.

CREATE TABLE IF NOT EXISTS sakhalin_1890_en (
    person_id              CHAR(7)             NOT NULL,
    source_position_id     CHAR(13)            NOT NULL,
    district               VARCHAR(32)         NOT NULL,
    settlement             VARCHAR(64)         NOT NULL,
    person_seq             SMALLINT UNSIGNED   NOT NULL,
    household_id           VARCHAR(16)         NULL,
    household_type         VARCHAR(64)         NULL,
    legal_status           VARCHAR(100)        NULL,
    full_name              VARCHAR(128)        NOT NULL,
    sex                    VARCHAR(10)         NOT NULL,
    family_status          VARCHAR(64)         NULL,
    age                    TINYINT UNSIGNED    NULL,
    age_months             TINYINT UNSIGNED    NULL,
    religion               VARCHAR(64)         NULL,
    origin_place           VARCHAR(128)        NULL,
    arrival_year           SMALLINT UNSIGNED   NULL,
    occupation             VARCHAR(128)        NULL,
    literacy               VARCHAR(32)         NULL,
    marital_status         VARCHAR(64)         NULL,
    living_alone_status    VARCHAR(32)         NULL,
    allowance_status       BOOLEAN             NULL,
    illness                VARCHAR(128)        NULL,
    archive_code           VARCHAR(32)         NULL,

    PRIMARY KEY (person_id),
    UNIQUE KEY uq_sakhalin_1890_source_position (source_position_id),
    KEY ix_sakhalin_1890_district_settlement (district, settlement),
    KEY ix_sakhalin_1890_household (district, settlement, household_id),
    KEY ix_sakhalin_1890_legal_status (legal_status),
    KEY ix_sakhalin_1890_origin_place (origin_place),
    KEY ix_sakhalin_1890_occupation (occupation),
    KEY ix_sakhalin_1890_age (age),

    CONSTRAINT chk_sakhalin_1890_allowance
        CHECK (allowance_status IS NULL OR allowance_status IN (0, 1))
) ENGINE=InnoDB
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
