from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


PROJECT_DIR = "/opt/airflow/project"
DAILY_CLAIMS_DIR = Path(f"{PROJECT_DIR}/data/landing/daily_claims")


def check_daily_claims_directory() -> None:
    if not DAILY_CLAIMS_DIR.exists():
        raise FileNotFoundError(
            f"Daily claims landing directory does not exist: {DAILY_CLAIMS_DIR}"
        )

    print(f"Daily claims landing directory exists: {DAILY_CLAIMS_DIR}")


default_args = {
    "owner": "vedant",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="healthcare_claims_daily_incremental",
    description="Generates daily synthetic claims, loads daily Bronze tables, and refreshes dbt Silver/Gold models.",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["healthcare", "claims", "daily", "dbt", "postgres"],
) as dag:

    check_landing_directory = PythonOperator(
        task_id="check_daily_claims_landing_directory",
        python_callable=check_daily_claims_directory,
    )

    generate_daily_claims = BashOperator(
        task_id="generate_daily_claims_feed",
        bash_command="""
        echo "Starting daily synthetic claims generation"
        cd /opt/airflow/project
        python ingestion/generators/generate_daily_claims_feed.py
        echo "Finished daily synthetic claims generation"
        """,
    )

    load_daily_bronze = BashOperator(
        task_id="load_daily_bronze_tables",
        bash_command="""
        echo "Starting daily Bronze ingestion"
        cd /opt/airflow/project
        python ingestion/loaders/load_daily_bronze.py
        echo "Finished daily Bronze ingestion"
        """,
    )

    validate_daily_bronze = BashOperator(
    task_id="validate_daily_bronze_tables",
    bash_command="""
    echo "Starting daily Bronze validation"
    cd /opt/airflow/project
    python ingestion/validators/validate_daily_bronze.py
    echo "Finished daily Bronze validation"
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
        echo "Starting dbt run for daily incremental pipeline"
        cd /opt/airflow/project/dbt/healthcare_claims
        dbt run --profiles-dir .
        echo "Finished dbt run"
        """,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="""
        echo "Starting dbt test for daily incremental pipeline"
        cd /opt/airflow/project/dbt/healthcare_claims
        dbt test --profiles-dir .
        echo "Finished dbt test"
        """,
    )

    (
        check_landing_directory
        >> generate_daily_claims
        >> load_daily_bronze
        >> validate_daily_bronze
        >> dbt_deps
        >> dbt_run
        >> dbt_test
    )