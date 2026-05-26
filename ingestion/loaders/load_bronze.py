import os
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


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

    with engine.begin() as conn:
        for table in tables:
            conn.execute(text(f"TRUNCATE TABLE {table};"))

    print("Truncated Bronze tables")


def load_csv_to_bronze(file_path: Path, engine) -> None:
    table_name = identify_target_table(file_path.name)

    if table_name is None:
        print(f"Skipping unsupported file: {file_path.name}")
        return

    source_year = extract_year_from_filename(file_path.name)

    print(f"\nLoading {file_path.name} into bronze.{table_name}")

    total_rows = 0

    for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE, dtype=str):
        chunk = clean_column_names(chunk)

        chunk["source_file_name"] = file_path.name

        if table_name == "beneficiary_summary":
            chunk["source_year"] = source_year

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
        print(f"Loaded {total_rows} rows so far...")

    print(f"Finished loading {file_path.name}: {total_rows} rows")


def main() -> None:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data directory does not exist: {DATA_DIR}")

    csv_files = sorted(DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")

    engine = get_engine()

    truncate_bronze_tables(engine)

    for file_path in csv_files:
        load_csv_to_bronze(file_path, engine)

    print("\nBronze load completed successfully")


if __name__ == "__main__":
    main()