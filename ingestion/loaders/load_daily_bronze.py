import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


DATA_DIR = Path("data/landing/daily_claims")
CHUNK_SIZE = 25_000


def get_engine():
    load_dotenv()

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")

    if not all([user, password, host, port, db]):
        raise ValueError("Missing one or more Postgres environment variables in .env")

    connection_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(connection_url)


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [column.strip().lower() for column in df.columns]
    return df


def identify_target_table(file_name: str) -> str | None:
    lower_name = file_name.lower()

    if "daily_inpatient_claims" in lower_name:
        return "daily_inpatient_claims"

    if "daily_outpatient_claims" in lower_name:
        return "daily_outpatient_claims"

    return None


def extract_feed_date(file_name: str):
    match = re.search(r"(\d{4})_(\d{2})_(\d{2})", file_name)

    if not match:
        raise ValueError(f"Could not extract feed date from file name: {file_name}")

    year, month, day = match.groups()
    return f"{year}-{month}-{day}"

def get_latest_daily_files(daily_files: list[Path]) -> list[Path]:
    files_by_feed_date = {}

    for file_path in daily_files:
        feed_date = extract_feed_date(file_path.name)
        files_by_feed_date.setdefault(feed_date, []).append(file_path)

    latest_feed_date = max(files_by_feed_date.keys())

    latest_files = files_by_feed_date[latest_feed_date]

    logger.info("Latest feed date detected: %s", latest_feed_date)
    logger.info("Files selected for latest feed date: %s", len(latest_files))

    for file_path in latest_files:
        logger.info("Selected latest feed file: %s", file_path.name)

    return sorted(latest_files)


def truncate_daily_tables(engine) -> None:
    tables = [
        "bronze.daily_inpatient_claims",
        "bronze.daily_outpatient_claims",
    ]

    logger.info("Truncating daily Bronze tables")

    with engine.begin() as conn:
        for table in tables:
            logger.info("Truncating table: %s", table)
            conn.execute(text(f"TRUNCATE TABLE {table};"))

    logger.info("Daily Bronze tables truncated successfully")

def write_audit_log(
    engine,
    pipeline_name: str,
    run_id: str,
    feed_date: str | None,
    source_file_name: str | None,
    target_table: str | None,
    rows_loaded: int,
    status: str,
    error_message: str | None,
    started_at: datetime,
    ended_at: datetime,
) -> None:
    sql = text(
        """
        INSERT INTO audit.pipeline_run_log (
            pipeline_name,
            run_id,
            feed_date,
            source_file_name,
            target_table,
            rows_loaded,
            status,
            error_message,
            started_at,
            ended_at
        )
        VALUES (
            :pipeline_name,
            :run_id,
            :feed_date,
            :source_file_name,
            :target_table,
            :rows_loaded,
            :status,
            :error_message,
            :started_at,
            :ended_at
        );
        """
    )

    with engine.begin() as conn:
        conn.execute(
            sql,
            {
                "pipeline_name": pipeline_name,
                "run_id": run_id,
                "feed_date": feed_date,
                "source_file_name": source_file_name,
                "target_table": target_table,
                "rows_loaded": rows_loaded,
                "status": status,
                "error_message": error_message,
                "started_at": started_at,
                "ended_at": ended_at,
            },
        )

    logger.info(
        "Audit log written | pipeline=%s run_id=%s file=%s table=%s rows=%s status=%s",
        pipeline_name,
        run_id,
        source_file_name,
        target_table,
        rows_loaded,
        status,
    )

def load_daily_file(file_path: Path, engine, run_id: str) -> None:
    table_name = identify_target_table(file_path.name)

    if table_name is None:
        logger.warning("Skipping unsupported daily file: %s", file_path.name)
        return

    feed_date = extract_feed_date(file_path.name)
    target_table = f"bronze.{table_name}"
    started_at = datetime.now()
    total_rows = 0

    logger.info("=" * 80)
    logger.info("Starting daily Bronze load")
    logger.info("Run ID: %s", run_id)
    logger.info("Source file: %s", file_path.name)
    logger.info("Target table: %s", target_table)
    logger.info("Feed date: %s", feed_date)

    try:
        for chunk_number, chunk in enumerate(
            pd.read_csv(file_path, chunksize=CHUNK_SIZE, dtype=str),
            start=1,
        ):
            logger.info(
                "Processing chunk=%s file=%s rows=%s",
                chunk_number,
                file_path.name,
                len(chunk),
            )

            chunk = clean_column_names(chunk)
            chunk["feed_date"] = feed_date
            chunk["source_file_name"] = file_path.name

            chunk.to_sql(
                name=table_name,
                con=engine,
                schema="bronze",
                if_exists="append",
                index=False,
                method="multi",
                chunksize=5_000,
            )

            total_rows += len(chunk)

            logger.info(
                "Loaded chunk=%s total_rows_loaded=%s",
                chunk_number,
                total_rows,
            )

        ended_at = datetime.now()

        write_audit_log(
            engine=engine,
            pipeline_name="daily_claims_bronze_load",
            run_id=run_id,
            feed_date=feed_date,
            source_file_name=file_path.name,
            target_table=target_table,
            rows_loaded=total_rows,
            status="success",
            error_message=None,
            started_at=started_at,
            ended_at=ended_at,
        )

        logger.info(
            "Finished daily load file=%s table=%s total_rows=%s",
            file_path.name,
            target_table,
            total_rows,
        )

    except Exception as exc:
        ended_at = datetime.now()

        write_audit_log(
            engine=engine,
            pipeline_name="daily_claims_bronze_load",
            run_id=run_id,
            feed_date=feed_date,
            source_file_name=file_path.name,
            target_table=target_table,
            rows_loaded=total_rows,
            status="failed",
            error_message=str(exc),
            started_at=started_at,
            ended_at=ended_at,
        )

        logger.exception("Failed daily load for file=%s", file_path.name)
        raise

    finally:
        logger.info("=" * 80)


def main() -> None:
    logger.info("Starting daily claims Bronze ingestion")
    logger.info("Looking for daily files in: %s", DATA_DIR)

    daily_files = sorted(DATA_DIR.glob("daily_*_claims_*.csv"))

    if not daily_files:
        raise FileNotFoundError(f"No daily claims files found in {DATA_DIR}")

    logger.info("Found %s total daily claim files", len(daily_files))

    for file_path in daily_files:
        logger.info("Discovered daily file: %s", file_path.name)

    latest_daily_files = get_latest_daily_files(daily_files)

    engine = get_engine()

    run_id = str(uuid.uuid4())
    logger.info("Daily Bronze load run_id=%s", run_id)

    truncate_daily_tables(engine)

    for file_path in latest_daily_files:
        load_daily_file(file_path, engine, run_id)

    logger.info("Daily claims Bronze ingestion completed successfully")


if __name__ == "__main__":
    main()