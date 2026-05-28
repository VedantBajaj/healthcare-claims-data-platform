# Healthcare Claims Data Platform

A production-style healthcare claims data platform built using CMS SynPUF data, Python, PostgreSQL, Docker, dbt, and Apache Airflow.

This project simulates how raw healthcare claims files move through a modern data engineering pipeline: ingestion, validation, transformation, testing, orchestration, documentation, audit logging, and analytics-ready marts.

## Project Goal

The goal of this project is to build a realistic healthcare claims platform that demonstrates how data engineering teams process healthcare claims data from raw source files into trusted analytics tables.

This project currently includes:

- Batch ingestion of CMS SynPUF claims files
- Bronze, Silver, and Gold warehouse architecture
- Python-based ingestion and validation
- PostgreSQL warehouse running locally with Docker
- dbt transformations, tests, documentation, and lineage
- Apache Airflow orchestration
- Daily synthetic claims feed generation
- Latest-feed-only daily incremental loading
- Pipeline audit logging
- Claims analytics marts for volume, payments, provider performance, daily feed quality, and pipeline run monitoring

## Dataset

This project uses the **CMS DE-SynPUF Sample 1** dataset.

CMS DE-SynPUF is a synthetic Medicare claims dataset designed to resemble real Medicare claims data while protecting beneficiary privacy. It is useful for learning healthcare data engineering patterns such as claims ingestion, member modeling, provider analysis, and payment analytics.

Current historical files used in this project:

- 2008 Beneficiary Summary
- 2009 Beneficiary Summary
- 2010 Beneficiary Summary
- 2008–2010 Inpatient Claims
- 2008–2010 Outpatient Claims

The raw CSV files are **not committed to GitHub** because they are large. After downloading the files from CMS, place them locally under:

```text
data/external/cms_synpuf/sample_1/
```

Expected local files:

```text
DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv
DE1_0_2009_Beneficiary_Summary_File_Sample_1.csv
DE1_0_2010_Beneficiary_Summary_File_Sample_1.csv
DE1_0_2008_to_2010_Inpatient_Claims_Sample_1.csv
DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.csv
```

## Architecture

The platform follows a medallion-style architecture with Bronze, Silver, and Gold layers.

```text
CMS SynPUF Historical Files
        ↓
Python Historical Ingestion
        ↓
PostgreSQL Bronze Tables
        ↓
dbt Staging Views
        ↓
dbt Silver Tables
        ↓
dbt Gold Marts
        ↓
Analytics / Monitoring


Daily Synthetic Claims Feed
        ↓
Daily Bronze Loader
        ↓
Daily Bronze Validation
        ↓
dbt Silver + Gold Refresh
        ↓
Daily Feed Quality + Audit Marts
```

### Data Flow

| Layer | Purpose | Examples |
|---|---|---|
| Source | Raw CMS SynPUF CSV files and generated daily files | Beneficiary, inpatient claims, outpatient claims, daily claims |
| Bronze | Raw loaded data with minimal changes | `bronze.beneficiary_summary`, `bronze.inpatient_claims`, `bronze.outpatient_claims`, `bronze.daily_inpatient_claims`, `bronze.daily_outpatient_claims` |
| Staging | Light cleanup and standardization | `stg_beneficiary_summary`, `stg_inpatient_claims`, `stg_outpatient_claims`, `stg_daily_inpatient_claims`, `stg_daily_outpatient_claims` |
| Silver | Trusted standardized tables | `silver_beneficiaries`, `silver_claims` |
| Gold | Analytics-ready marts | `mart_claim_volume`, `mart_claim_payments`, `mart_provider_performance`, `mart_daily_claim_feed_quality`, `mart_pipeline_run_audit` |
| Audit | Pipeline execution tracking | `audit.pipeline_run_log` |

## Tech Stack

| Component | Tool |
|---|---|
| Data Source | CMS DE-SynPUF |
| Programming Language | Python |
| Database / Warehouse | PostgreSQL |
| Containerization | Docker Compose |
| Transformations | dbt Core |
| Orchestration | Apache Airflow |
| Data Testing | Python validation scripts + dbt tests |
| Documentation | dbt Docs |
| Version Control | Git and GitHub |

## Why These Tools Were Used

- **Python** handles file ingestion, synthetic feed generation, chunked CSV loading, and validation.
- **PostgreSQL** acts as the local analytics warehouse.
- **Docker Compose** makes the database and Airflow environment reproducible.
- **dbt** manages SQL transformations, tests, documentation, and lineage.
- **Apache Airflow** orchestrates historical and daily workflows.
- **GitHub** tracks project history and makes the project portfolio-ready.

## Repository Structure

```text
healthcare-claims-data-platform/
│
├── airflow/
│   └── dags/
│       ├── healthcare_claims_historical_bootstrap.py
│       └── healthcare_claims_daily_incremental.py
│
├── data/
│   ├── external/              # Raw CMS files, ignored by Git
│   ├── landing/               # Generated daily files, ignored by Git
│   └── raw/
│
├── ingestion/
│   ├── generators/
│   │   └── generate_daily_claims_feed.py
│   ├── loaders/
│   │   ├── load_bronze.py
│   │   └── load_daily_bronze.py
│   └── validators/
│       ├── validate_bronze.py
│       └── validate_daily_bronze.py
│
├── warehouse/
│   ├── init.sql
│   ├── daily_tables.sql
│   └── audit_tables.sql
│
├── dbt/
│   └── healthcare_claims/
│       ├── models/
│       │   ├── staging/
│       │   ├── silver/
│       │   └── marts/
│       ├── tests/
│       ├── dbt_project.yml
│       ├── packages.yml
│       └── profiles.yml
│
├── Dockerfile.airflow
├── docker-compose.yml
├── requirements.txt
├── requirements-airflow.txt
├── .gitignore
└── README.md
```

### Main Components

- `warehouse/init.sql` creates the Bronze schema and historical raw tables.
- `warehouse/daily_tables.sql` creates daily Bronze claim tables.
- `warehouse/audit_tables.sql` creates the pipeline audit schema and table.
- `ingestion/loaders/load_bronze.py` loads historical CMS CSV files into PostgreSQL.
- `ingestion/loaders/load_daily_bronze.py` loads only the latest generated daily claims feed into Bronze.
- `ingestion/generators/generate_daily_claims_feed.py` creates synthetic daily inpatient and outpatient claims files.
- `ingestion/validators/validate_bronze.py` runs historical Bronze validation checks.
- `ingestion/validators/validate_daily_bronze.py` runs daily Bronze validation checks.
- `airflow/dags/` contains historical and daily Airflow DAGs.
- `dbt/healthcare_claims/models/staging/` contains cleaned staging views.
- `dbt/healthcare_claims/models/silver/` contains trusted Silver tables.
- `dbt/healthcare_claims/models/marts/` contains analytics-ready Gold marts.
- `dbt/healthcare_claims/tests/` contains custom dbt data tests.

## Data Pipeline Layers

### Bronze Layer

The Bronze layer stores raw CMS SynPUF data and daily synthetic feed data with minimal transformation.

Bronze tables:

- `bronze.beneficiary_summary`
- `bronze.inpatient_claims`
- `bronze.outpatient_claims`
- `bronze.daily_inpatient_claims`
- `bronze.daily_outpatient_claims`

The Python ingestion scripts load CSV files into PostgreSQL, add metadata columns, and preserve the source structure.

Metadata columns include:

- `source_file_name`
- `source_year`
- `feed_date`
- `ingested_at`

### Staging Layer

The Staging layer is built with dbt views. It performs light cleanup and standardization on top of Bronze tables.

Staging models:

- `stg_beneficiary_summary`
- `stg_inpatient_claims`
- `stg_outpatient_claims`
- `stg_daily_inpatient_claims`
- `stg_daily_outpatient_claims`

Staging logic includes:

- Renaming CMS columns into readable names
- Casting date fields
- Casting numeric fields
- Adding claim type labels
- Adding source system labels
- Keeping source metadata for traceability

### Silver Layer

The Silver layer contains trusted, standardized dbt tables.

Silver models:

- `silver_beneficiaries`
- `silver_claims`

Silver logic includes:

- Selecting the latest beneficiary record across available years
- Combining historical inpatient, historical outpatient, daily inpatient, and daily outpatient claims into one unified claims table
- Creating a claim surrogate key
- Preserving claim type as `inpatient` or `outpatient`
- Preserving source system as `cms_historical` or `daily_synthetic`
- Filtering invalid daily records before trusted analytics
- Validating relationships between claims and beneficiaries

### Gold Layer

The Gold layer contains analytics-ready marts for reporting, monitoring, and dashboarding.

Gold marts:

- `mart_claim_volume`
- `mart_claim_payments`
- `mart_provider_performance`
- `mart_claims_by_source_system`
- `mart_daily_claim_feed_quality`
- `mart_pipeline_run_audit`

Gold marts support analysis of:

- Claim volume by claim type
- Total and average payment amounts
- Provider-level claim performance
- Claims by source system
- Daily feed quality
- Rejected daily rows between Bronze and Silver
- Pipeline run duration and row-load audit history

## Orchestration and Daily Incremental Pipeline

This project uses Apache Airflow to orchestrate both historical and daily claims workflows.

### Airflow DAGs

The project includes two Airflow DAGs:

| DAG | Purpose | When to Run |
|---|---|---|
| `healthcare_claims_historical_bootstrap` | Loads historical CMS SynPUF files into Bronze, validates Bronze, and refreshes dbt models | Run manually when rebuilding the warehouse |
| `healthcare_claims_daily_incremental` | Generates daily synthetic claims, loads daily Bronze tables, validates the daily feed, and refreshes dbt models | Run daily or manually for incremental processing |

### Historical Bootstrap Flow

```text
CMS SynPUF Historical Files
        ↓
Load Historical Bronze Tables
        ↓
Validate Historical Bronze
        ↓
dbt Run
        ↓
dbt Test
        ↓
Silver and Gold Tables
```

### Daily Incremental Flow

```text
Generate Daily Synthetic Claims
        ↓
Load Latest Daily Feed into Bronze
        ↓
Validate Daily Bronze Feed
        ↓
dbt Run
        ↓
dbt Test
        ↓
Updated Silver and Gold Tables
```

The daily pipeline avoids reloading the large historical outpatient claims file. Instead, it processes only the latest daily synthetic feed from:

```text
data/landing/daily_claims/
```

Daily files follow this naming pattern:

```text
daily_inpatient_claims_YYYY_MM_DD.csv
daily_outpatient_claims_YYYY_MM_DD.csv
```

## Daily Synthetic Claims Feed

The project includes a synthetic daily feed generator:

```text
ingestion/generators/generate_daily_claims_feed.py
```

The generator samples from the CMS SynPUF claims files and creates small daily inbound files for testing incremental processing.

Generated daily files include:

- New daily claim IDs
- Shifted claim dates
- Adjusted payment amounts
- Controlled bad records for data quality testing

The generator intentionally injects records with:

- Missing claim IDs
- Missing beneficiary IDs
- Negative payment amounts
- Missing claim start dates

These records are kept in Bronze and Staging for traceability, detected during validation, and filtered out before the trusted Silver layer.

## Daily Bronze Validation

Daily Bronze validation is handled by:

```text
ingestion/validators/validate_daily_bronze.py
```

The validation checks include:

```text
- Daily inpatient and outpatient tables contain rows
- Feed date is not null
- Missing claim IDs are tracked as warnings
- Missing beneficiary IDs are tracked as warnings
- Negative payments are tracked as warnings
- Missing claim start dates are tracked as warnings
```

Warnings do not stop the pipeline because they represent controlled data quality issues used for testing and monitoring.

## Pipeline Audit Logging

The project includes an audit table to track daily Bronze load execution:

```text
audit.pipeline_run_log
```

Each daily load records:

```text
pipeline_name
run_id
feed_date
source_file_name
target_table
rows_loaded
status
error_message
started_at
ended_at
```

This makes the pipeline observable and helps answer:

- Which feed date was processed?
- Which files were loaded?
- How many rows were loaded?
- Did the load succeed or fail?
- How long did the load take?

A dbt Gold mart summarizes audit records:

```text
silver_marts.mart_pipeline_run_audit
```

Example audit mart output:

| Pipeline | Feed Date | Files Processed | Rows Loaded | Status |
|---|---:|---:|---:|---|
| daily_claims_bronze_load | 2026-05-28 | 2 | 1,500 | success |

## Current Data Volumes

| Layer / Table | Row Count |
|---|---:|
| Bronze Beneficiary Summary | 343,644 |
| Bronze Inpatient Claims | 66,773 |
| Bronze Outpatient Claims | 790,790 |
| Bronze Daily Inpatient Claims | 500 |
| Bronze Daily Outpatient Claims | 1,000 |
| Silver Beneficiaries | 116,352 |
| Silver Claims with Daily Feed | 859,059 |
| Provider Performance Mart | 8,969 |
| Pipeline Run Audit Mart | 2+ |

## Gold Mart Results

### Claim Volume

| Claim Type | Total Claims | Unique Beneficiaries | Unique Providers | Missing Start Date | Negative Payments |
|---|---:|---:|---:|---:|---:|
| inpatient | 67,271 | 37,780+ | 2,675+ | 69+ | 56+ |
| outpatient | 791,788 | 85,272+ | 6,294+ | 11,254+ | 2,566+ |

### Claim Payments

| Claim Type | Historical Total Claims | Historical Total Claim Payment | Historical Average Payment |
|---|---:|---:|---:|
| inpatient | 66,773 | 639,260,180.00 | 9,573.63 |
| outpatient | 790,790 | 224,524,710.00 | 283.92 |

### Daily Feed Quality

| Feed Date | Claim Type | Bronze Rows | Silver Rows | Rejected Rows |
|---|---|---:|---:|---:|
| 2026-05-28 | inpatient | 500 | 498 | 2 |
| 2026-05-28 | outpatient | 1,000 | 998 | 2 |

## Data Quality and Testing

This project includes validation at multiple stages of the pipeline.

### Historical Bronze Validation

Historical Bronze validation is handled with a Python script:

```text
ingestion/validators/validate_bronze.py
```

The Bronze validation checks include:

```text
- Source tables contain data
- Beneficiary IDs are not null
- Claim IDs are not null
- Inpatient and outpatient claims connect to beneficiaries
- Duplicate claim IDs are tracked as warnings
- Negative payment amounts are tracked as warnings
```

Duplicate claim IDs and negative payment values are treated as warnings because raw healthcare claims data can contain claim segments, adjustments, reversals, and reprocessed payments.

### Daily Bronze Validation

Daily Bronze validation is handled with:

```text
ingestion/validators/validate_daily_bronze.py
```

Daily validation checks include:

```text
- Daily files loaded into Bronze
- Feed date is populated
- Missing claim IDs are tracked as warnings
- Missing beneficiary IDs are tracked as warnings
- Negative payment amounts are tracked as warnings
- Missing claim start dates are tracked as warnings
```

### dbt Tests

dbt tests validate the Staging, Silver, and Gold layers.

Current dbt tests include:

```text
- Not-null checks for important identifiers
- Unique checks for surrogate keys
- Accepted values for claim types and source systems
- Relationship checks between claims and beneficiaries
- Gold mart completeness checks
- Custom uniqueness checks for provider, claim type, source system, feed date, and audit run combinations
```

### Current Test Results

Recent dbt test result:

```text
PASS=39 WARN=0 ERROR=0 TOTAL=39
```

## dbt Documentation and Lineage

This project uses dbt Docs to generate model documentation and lineage graphs.

dbt Docs helps show how data flows from raw Bronze sources into Staging views, Silver tables, and Gold marts.

### Generate dbt Docs

```powershell
cd dbt/healthcare_claims
dbt docs generate --profiles-dir .
dbt docs serve --port 8081
```

Then open:

```text
http://localhost:8081
```

### Example Lineage

```text
bronze.beneficiary_summary
        ↓
stg_beneficiary_summary
        ↓
silver_beneficiaries
```

Claims lineage:

```text
bronze.inpatient_claims
bronze.outpatient_claims
bronze.daily_inpatient_claims
bronze.daily_outpatient_claims
        ↓
stg_inpatient_claims
stg_outpatient_claims
stg_daily_inpatient_claims
stg_daily_outpatient_claims
        ↓
silver_claims
        ↓
mart_claim_volume
mart_claim_payments
mart_provider_performance
mart_claims_by_source_system
mart_daily_claim_feed_quality
```

Audit lineage:

```text
audit.pipeline_run_log
        ↓
mart_pipeline_run_audit
```

The lineage graph makes it easy to understand how each analytics table is built from the original CMS SynPUF source files and daily synthetic feeds.

## How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/VedantBajaj/healthcare-claims-data-platform.git
cd healthcare-claims-data-platform
```

### 2. Create and Activate a Virtual Environment

For Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

### 3. Start PostgreSQL and Airflow with Docker

```powershell
docker compose up -d --build
```

Confirm the containers are running:

```powershell
docker ps
```

Expected containers include:

```text
healthcare_claims_postgres
healthcare_airflow_postgres
healthcare_airflow_webserver
healthcare_airflow_scheduler
```

### 4. Add Environment Variables

Create a `.env` file in the project root:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=claims_warehouse
POSTGRES_USER=claims_user
POSTGRES_PASSWORD=claims_password
```

### 5. Add CMS SynPUF Files Locally

Download the required CMS SynPUF Sample 1 files and place them under:

```text
data/external/cms_synpuf/sample_1/
```

The raw data files are ignored by Git and must be added locally before running historical ingestion.

### 6. Apply Daily and Audit Tables

```powershell
Get-Content warehouse/daily_tables.sql | docker exec -i healthcare_claims_postgres psql -U claims_user -d claims_warehouse
Get-Content warehouse/audit_tables.sql | docker exec -i healthcare_claims_postgres psql -U claims_user -d claims_warehouse
```

### 7. Run Historical Bootstrap Manually

```powershell
python ingestion/loaders/load_bronze.py
python ingestion/validators/validate_bronze.py
```

### 8. Run Daily Feed Manually

```powershell
python ingestion/generators/generate_daily_claims_feed.py
python ingestion/loaders/load_daily_bronze.py
python ingestion/validators/validate_daily_bronze.py
```

### 9. Run dbt Models and Tests

```powershell
cd dbt/healthcare_claims
dbt deps
dbt run --profiles-dir .
dbt test --profiles-dir .
```

### 10. Open Airflow

Open:

```text
http://localhost:8082
```

Login:

```text
username: admin
password: admin
```

Available DAGs:

```text
healthcare_claims_historical_bootstrap
healthcare_claims_daily_incremental
```

Recommended usage:

```text
1. Run healthcare_claims_historical_bootstrap only when rebuilding historical data.
2. Run healthcare_claims_daily_incremental for normal daily processing.
3. Do not run both DAGs at the same time.
```

### 11. Generate and Serve dbt Docs

```powershell
cd dbt/healthcare_claims
dbt docs generate --profiles-dir .
dbt docs serve --port 8081
```

Open:

```text
http://localhost:8081
```

## Key Learnings

This project demonstrates practical data engineering concepts, including:

- Building a medallion-style data platform using Bronze, Silver, and Gold layers
- Loading large healthcare CSV files into PostgreSQL using chunked Python ingestion
- Separating historical bootstrap processing from daily incremental processing
- Generating synthetic daily claims feeds from historical CMS patterns
- Loading only the latest daily feed to avoid reprocessing old files
- Preserving bad records in Bronze while filtering invalid records from trusted Silver models
- Using dbt for SQL-based transformations, testing, documentation, and lineage
- Creating trusted Silver tables from raw healthcare claims data
- Building Gold marts for claim volume, payment, provider performance, daily feed quality, and audit monitoring
- Using Airflow to orchestrate historical and daily workflows
- Adding audit logging for pipeline observability
- Handling real-world data quality issues such as duplicate claim IDs, missing dates, missing identifiers, and negative payment adjustments
- Using Docker Compose for reproducible local development
- Keeping raw datasets and generated files out of GitHub using `.gitignore`

## Future Enhancements

Planned next steps for this project:

- Add multi-day incremental history instead of latest-feed-only daily loading
- Add dashboarding on daily feed quality and pipeline audit marts
- Add Great Expectations for more advanced data quality validation
- Add Grafana dashboards for claim volume, payment trends, provider performance, and pipeline health
- Add GitHub Actions CI/CD to run Python checks and dbt parse/test checks automatically
- Add CMS Carrier Claims and Prescription Drug Events data
- Add cloud deployment using GCP, BigQuery, and Cloud Composer or Cloud Run