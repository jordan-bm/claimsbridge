-- migrations/001_create_claims_table.sql

CREATE TABLE IF NOT EXISTS claims (
    id                  VARCHAR(64) PRIMARY KEY,
    source_message_id   VARCHAR(64) NOT NULL,
    status              VARCHAR(16) NOT NULL,
    patient_id          VARCHAR(64) NOT NULL,
    patient_name        VARCHAR(128) NOT NULL,
    birth_date          VARCHAR(16) NOT NULL,
    member_id           VARCHAR(64) NOT NULL,
    insurer             VARCHAR(64) NOT NULL,
    diagnosis_code      VARCHAR(32) NOT NULL,
    total_charge        NUMERIC(10, 2) NOT NULL,
    admission_date      VARCHAR(16) NOT NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);