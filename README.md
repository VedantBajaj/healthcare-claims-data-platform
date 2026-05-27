# Healthcare Claims Data Platform

A production-style healthcare claims data platform built using CMS SynPUF data, Python, PostgreSQL, Docker, and dbt.

This project simulates how raw healthcare claims files move through a modern data engineering pipeline: ingestion, validation, transformation, testing, documentation, and analytics-ready marts.

## Project Goal

The goal of this project is to build a realistic healthcare claims platform that demonstrates how data engineering teams process healthcare claims data from raw source files into trusted analytics tables.

This project currently includes:

- Batch ingestion of CMS SynPUF claims files
- Bronze, Silver, and Gold warehouse architecture
- Python-based ingestion and validation
- PostgreSQL warehouse running locally with Docker
- dbt transformations, tests, and documentation
- Claims analytics marts for volume, payments, and provider performance

## Dataset

This project uses the **CMS DE-SynPUF Sample 1** dataset.

CMS DE-SynPUF is a synthetic Medicare claims dataset designed to resemble real Medicare claims data while protecting beneficiary privacy. It is useful for learning healthcare data engineering patterns such as claims ingestion, member modeling, provider analysis, and payment analytics.

Current files used in this project:

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
CMS SynPUF CSV Files
        ↓
Python Ingestion
        ↓
PostgreSQL Bronze Tables
        ↓
dbt Staging Views
        ↓
dbt Silver Tables
        ↓
dbt Gold Marts
        ↓
Analytics / Dashboards
```

### Data Flow

| Layer | Purpose | Examples |
|---|---|---|
| Source | Raw CMS SynPUF CSV files | Beneficiary, inpatient claims, outpatient claims |
| Bronze | Raw loaded data with minimal changes | `bronze.beneficiary_summary`, `bronze.inpatient_claims`, `bronze.outpatient_claims` |
| Staging | Light cleanup and standardization | `stg_beneficiary_summary`, `stg_inpatient_claims`, `stg_outpatient_claims` |
| Silver | Trusted standardized tables | `silver_beneficiaries`, `silver_claims` |
| Gold | Analytics-ready marts | `mart_claim_volume`, `mart_claim_payments`, `mart_provider_performance` |

## Tech Stack

| Component | Tool |
|---|---|
| Data Source | CMS DE-SynPUF |
| Programming Language | Python |
| Database / Warehouse | PostgreSQL |
| Containerization | Docker Compose |
| Transformations | dbt Core |
| Data Testing | Python validation scripts + dbt tests |
| Documentation | dbt Docs |
| Version Control | Git and GitHub |

## Why These Tools Were Used

- **Python** handles file ingestion, chunked CSV loading, and Bronze validation.
- **PostgreSQL** acts as the local analytics warehouse.
- **Docker Compose** makes the database environment reproducible.
- **dbt** manages SQL transformations, tests, documentation, and lineage.
- **GitHub** tracks project history and makes the project portfolio-ready.

## Repository Structure

```text
healthcare-claims-data-platform/
│
├── data/
│   ├── external/              # Raw CMS files, ignored by Git
│   ├── raw/
│   └── landing/
│
├── ingestion/
│   ├── loaders/
│   │   └── load_bronze.py
│   └── validators/
│       └── validate_bronze.py
│
├── warehouse/
│   └── init.sql
│
├── dbt/
│   └── healthcare_claims/
│       ├── models/
│       │   ├── staging/
│       │   ├── silver/
│       │   └── marts/
│       ├── tests/
│       ├── dbt_project.yml
│       └── packages.yml
│
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

### Main Components

- `warehouse/init.sql` creates the Bronze schema and raw tables.
- `ingestion/loaders/load_bronze.py` loads CMS CSV files into PostgreSQL.
- `ingestion/validators/validate_bronze.py` runs Bronze-level validation checks.
- `dbt/healthcare_claims/models/staging/` contains cleaned staging views.
- `dbt/healthcare_claims/models/silver/` contains trusted Silver tables.
- `dbt/healthcare_claims/models/marts/` contains analytics-ready Gold marts.
- `dbt/healthcare_claims/tests/` contains custom dbt data tests.

## Data Pipeline Layers

### Bronze Layer

The Bronze layer stores raw CMS SynPUF data with minimal transformation.

Bronze tables:

- `bronze.beneficiary_summary`
- `bronze.inpatient_claims`
- `bronze.outpatient_claims`

The Python ingestion script loads large CSV files into PostgreSQL in chunks, adds metadata columns, and preserves the raw CMS-style structure.

Metadata columns include:

- `source_file_name`
- `source_year`
- `ingested_at`

### Staging Layer

The Staging layer is built with dbt views. It performs light cleanup and standardization on top of Bronze tables.

Staging models:

- `stg_beneficiary_summary`
- `stg_inpatient_claims`
- `stg_outpatient_claims`

Staging logic includes:

- Renaming CMS columns into readable names
- Casting date fields
- Casting numeric fields
- Adding claim type labels
- Keeping source metadata for traceability

### Silver Layer

The Silver layer contains trusted, standardized dbt tables.

Silver models:

- `silver_beneficiaries`
- `silver_claims`

Silver logic includes:

- Selecting the latest beneficiary record across available years
- Combining inpatient and outpatient claims into one unified claims table
- Creating a claim surrogate key
- Preserving claim type as `inpatient` or `outpatient`
- Validating relationships between claims and beneficiaries

### Gold Layer

The Gold layer contains analytics-ready marts for reporting and dashboarding.

Gold marts:

- `mart_claim_volume`
- `mart_claim_payments`
- `mart_provider_performance`

Gold marts support analysis of:

- Claim volume by claim type
- Total and average payment amounts
- Provider-level claim performance
- Missing claim dates
- Negative payment adjustments

## Current Data Volumes

| Layer / Table | Row Count |
|---|---:|
| Bronze Beneficiary Summary | 343,644 |
| Bronze Inpatient Claims | 66,773 |
| Bronze Outpatient Claims | 790,790 |
| Silver Beneficiaries | 116,352 |
| Silver Claims | 857,563 |
| Provider Performance Mart | 8,969 |

## Gold Mart Results

### Claim Volume

| Claim Type | Total Claims | Unique Beneficiaries | Unique Providers | Missing Start Date | Negative Payments |
|---|---:|---:|---:|---:|---:|
| inpatient | 66,773 | 37,780 | 2,675 | 68 | 55 |
| outpatient | 790,790 | 85,272 | 6,294 | 11,253 | 2,566 |

### Claim Payments

| Claim Type | Total Claims | Total Claim Payment | Average Payment | Min Payment | Max Payment |
|---|---:|---:|---:|---:|---:|
| inpatient | 66,773 | 639,260,180.00 | 9,573.63 | -8,000.00 | 57,000.00 |
| outpatient | 790,790 | 224,524,710.00 | 283.92 | -100.00 | 3,300.00 |

## Data Quality and Testing

This project includes validation at multiple stages of the pipeline.

### Bronze Validation

Bronze validation is handled with a Python script:

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

### dbt Tests

dbt tests validate the Staging, Silver, and Gold layers.

Current dbt tests include:

```text
- Not-null checks for important identifiers
- Unique checks for surrogate keys
- Accepted values for claim types
- Relationship checks between claims and beneficiaries
- Gold mart completeness checks
- Custom uniqueness checks for provider and claim type combinations
```

### Current Test Results

Staging tests:

```text
PASS=11 WARN=2 ERROR=0 TOTAL=13
```

Silver tests:

```text
PASS=11 WARN=1 ERROR=0 TOTAL=12
```

Gold mart tests:

```text
PASS=17 WARN=0 ERROR=0 TOTAL=17
```

## dbt Documentation and Lineage

This project uses dbt Docs to generate model documentation and lineage graphs.

dbt Docs helps show how data flows from raw Bronze sources into Staging views, Silver tables, and Gold marts.

### Generate dbt Docs

```powershell
cd dbt/healthcare_claims
dbt docs generate
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
        ↓
stg_inpatient_claims
stg_outpatient_claims
        ↓
silver_claims
        ↓
mart_claim_volume
mart_claim_payments
mart_provider_performance
```

The lineage graph makes it easy to understand how each analytics table is built from the original CMS SynPUF source files.

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

### 3. Start PostgreSQL with Docker

```powershell
docker compose up -d
```

Confirm the container is running:

```powershell
docker ps
```

Expected container:

```text
healthcare_claims_postgres
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

The raw data files are ignored by Git and must be added locally before running ingestion.

### 6. Load Bronze Data

```powershell
python ingestion/loaders/load_bronze.py
```

### 7. Run Bronze Validation

```powershell
python ingestion/validators/validate_bronze.py
```

### 8. Run dbt Models and Tests

```powershell
cd dbt/healthcare_claims
dbt deps
dbt run
dbt test
```

### 9. Generate and Serve dbt Docs

```powershell
dbt docs generate
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
- Separating ingestion logic from transformation logic
- Using dbt for SQL-based transformations, testing, documentation, and lineage
- Creating trusted Silver tables from raw healthcare claims data
- Building Gold marts for claim volume, payment, and provider performance analytics
- Handling real-world data quality issues such as duplicate claim IDs, missing dates, and negative payment adjustments
- Using Docker Compose for reproducible local development
- Keeping raw datasets out of GitHub using `.gitignore`

## Future Enhancements

Planned next steps for this project:

- Add Airflow orchestration for end-to-end pipeline scheduling
- Add daily synthetic claims file generation based on CMS SynPUF patterns
- Add incremental loading instead of full reloads
- Add Great Expectations for more advanced data quality validation
- Add Grafana dashboards for claim volume, payment trends, and provider performance
- Add GitHub Actions CI/CD to run Python checks and dbt tests automatically
- Add CMS Carrier Claims and Prescription Drug Events data
- Add cloud deployment using GCP, BigQuery, and Cloud Composer or Cloud Run