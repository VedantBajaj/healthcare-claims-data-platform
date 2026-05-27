import os
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


DATA_DIR = Path("data/external/cms_synpuf/sample_1")
CHUNK_SIZE = 50_000


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
    df.columns = [col.strip().lower() for col in df.columns]
    return df


def extract_year_from_filename(file_name: str) -> int | None:
    match = re.search(r"20\d{2}", file_name)

    if match:
        return int(match.group())

    return None


def identify_target_table(file_name: str) -> str | None:
    lower_name = file_name.lower()

    if "beneficiary_summary" in lower_name:
        return "beneficiary_summary"

    if "inpatient_claims" in lower_name:
        return "inpatient_claims"

    if "outpatient_claims" in lower_name:
        return "outpatient_claims"

    return None


def truncate_bronze_tables(engine) -> None:
    tables = [
        "bronze.beneficiary_summary",
        "bronze.inpatient_claims",
        "bronze.outpatient_claims",
    ]

    logger.info("Starting truncate for Bronze tables")

    with engine.begin() as conn:
        for table in tables:
            logger.info("Truncating table: %s", table)
            conn.execute(text(f"TRUNCATE TABLE {table};"))

    logger.info("Finished truncating Bronze tables")

def load_csv_to_bronze(file_path: Path, engine) -> None:
    table_name = identify_target_table(file_path.name)

    if table_name is None:
        logger.warning("Skipping unsupported file: %s", file_path.name)
        return

    source_year = extract_year_from_filename(file_path.name)

    logger.info("=" * 80)
    logger.info("Starting Bronze load")
    logger.info("Source file: %s", file_path.name)
    logger.info("Target table: bronze.%s", table_name)
    logger.info("Detected source year: %s", source_year)
    logger.info("Read chunk size: %s rows", CHUNK_SIZE)

    start_time = time.time()
    total_rows = 0
    chunk_number = 0

    for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE, dtype=str):
        chunk_number += 1
        chunk_start_time = time.time()

        logger.info(
            "Processing chunk %s for %s with %s rows",
            chunk_number,
            file_path.name,
            len(chunk),
        )

        chunk = clean_column_names(chunk)

        logger.info(
            "Cleaned column names for chunk %s. Column count=%s",
            chunk_number,
            len(chunk.columns),
        )

        chunk["source_file_name"] = file_path.name

        if table_name == "beneficiary_summary":
            chunk["source_year"] = source_year
            logger.info(
                "Added source_year=%s metadata for beneficiary file",
                source_year,
            )

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
        chunk_duration = round(time.time() - chunk_start_time, 2)

        logger.info(
            "Loaded chunk %s successfully. chunk_rows=%s total_rows_loaded=%s duration_seconds=%s",
            chunk_number,
            len(chunk),
            total_rows,
            chunk_duration,
        )

    total_duration = round(time.time() - start_time, 2)

    logger.info(
        "Finished loading file=%s target_table=bronze.%s total_rows=%s total_duration_seconds=%s",
        file_path.name,
        table_name,
        total_rows,
        total_duration,
    )
    logger.info("=" * 80)

def main() -> None:
    logger.info("Starting CMS SynPUF Bronze ingestion pipeline")
    logger.info("Looking for CSV files in: %s", DATA_DIR)

    if not DATA_DIR.exists():
        logger.error("Data directory does not exist: %s", DATA_DIR)
        raise FileNotFoundError(f"Data directory does not exist: {DATA_DIR}")

    csv_files = sorted(DATA_DIR.glob("*.csv"))

    if not csv_files:
        logger.error("No CSV files found in: %s", DATA_DIR)
        raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")

    logger.info("Found %s CSV files", len(csv_files))

    for file_path in csv_files:
        logger.info("Discovered source file: %s", file_path.name)

    engine = get_engine()

    logger.info("Database connection engine created successfully")

    truncate_bronze_tables(engine)

    for file_path in csv_files:
        load_csv_to_bronze(file_path, engine)

    logger.info("Bronze load completed successfully for all supported files")

    logger.info("\nBronze load completed successfully")


if __name__ == "__main__":
    main()