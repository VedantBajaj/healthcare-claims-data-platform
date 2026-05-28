from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


PROJECT_DIR = "/opt/airflow/project"
DATA_DIR = Path(f"{PROJECT_DIR}/data/external/cms_synpuf/sample_1")


REQUIRED_FILES = [
    "DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv",
    "DE1_0_2009_Beneficiary_Summary_File_Sample_1.csv",
    "DE1_0_2010_Beneficiary_Summary_File_Sample_1.csv",
    "DE1_0_2008_to_2010_Inpatient_Claims_Sample_1.csv",
    "DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.csv",
]


def check_source_files() -> None:
    missing_files = []

    for file_name in REQUIRED_FILES:
        file_path = DATA_DIR / file_name

        if not file_path.exists():
            missing_files.append(str(file_path))

    if missing_files:
        raise FileNotFoundError(
            "Missing required CMS SynPUF files:\n" + "\n".join(missing_files)
        )

    print("All required CMS SynPUF source files are present.")


default_args = {
    "owner": "vedant",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="healthcare_claims_historical_bootstrap",
    description="Loads historical CMS SynPUF files into Bronze, validates data, and refreshes dbt models.",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["healthcare", "claims", "historical", "bootstrap", "dbt"],
) as dag:

    check_files = PythonOperator(
        task_id="check_historical_source_files",
        python_callable=check_source_files,
    )

    load_bronze = BashOperator(
        task_id="load_historical_bronze_tables",
        bash_command="""
        echo "Starting historical Bronze ingestion"
        cd /opt/airflow/project
        python ingestion/loaders/load_bronze.py
        echo "Finished historical Bronze ingestion"
        """,
    )

    validate_bronze = BashOperator(
        task_id="validate_historical_bronze_tables",
        bash_command="""
        echo "Starting historical Bronze validation"
        cd /opt/airflow/project
        python ingestion/validators/validate_bronze.py
        echo "Finished historical Bronze validation"
        """,
    )

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command="""
        echo "Starting dbt deps"
        cd /opt/airflow/project/dbt/healthcare_claims
        dbt deps --profiles-dir .
        echo "Finished dbt deps"
        """,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="""
        echo "Starting dbt run for historical bootstrap"
        cd /opt/airflow/project/dbt/healthcare_claims
        dbt run --profiles-dir .
        echo "Finished dbt run"
        """,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="""
        echo "Starting dbt test for historical bootstrap"
        cd /opt/airflow/project/dbt/healthcare_claims
        dbt test --profiles-dir .
        echo "Finished dbt test"
        """,
    )

    check_files >> load_bronze >> validate_bronze >> dbt_deps >> dbt_run >> dbt_test