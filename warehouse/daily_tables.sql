CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.daily_inpatient_claims (
    LIKE bronze.inpatient_claims INCLUDING DEFAULTS
);

ALTER TABLE bronze.daily_inpatient_claims
ADD COLUMN IF NOT EXISTS feed_date DATE;

CREATE TABLE IF NOT EXISTS bronze.daily_outpatient_claims (
    LIKE bronze.outpatient_claims INCLUDING DEFAULTS
);

ALTER TABLE bronze.daily_outpatient_claims
ADD COLUMN IF NOT EXISTS feed_date DATE;