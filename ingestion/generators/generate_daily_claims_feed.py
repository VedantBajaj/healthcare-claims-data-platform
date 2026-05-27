import logging
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


SOURCE_DIR = Path("data/external/cms_synpuf/sample_1")
OUTPUT_DIR = Path("data/landing/daily_claims")

INPATIENT_SOURCE_FILE = "DE1_0_2008_to_2010_Inpatient_Claims_Sample_1.csv"
OUTPATIENT_SOURCE_FILE = "DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.csv"

RANDOM_SEED = 42


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [column.strip() for column in df.columns]
    return df


def create_daily_claim_id(original_claim_id: str, run_date: date, row_number: int) -> str:
    return f"DAILY_{run_date.strftime('%Y%m%d')}_{original_claim_id}_{row_number}"


def shift_claim_dates(df: pd.DataFrame, run_date: date) -> pd.DataFrame:
    df = df.copy()

    service_start_date = run_date - timedelta(days=1)
    service_end_date = run_date

    if "CLM_FROM_DT" in df.columns:
        df["CLM_FROM_DT"] = service_start_date.strftime("%Y-%m-%d")

    if "CLM_THRU_DT" in df.columns:
        df["CLM_THRU_DT"] = service_end_date.strftime("%Y-%m-%d")

    if "CLM_ADMSN_DT" in df.columns:
        df["CLM_ADMSN_DT"] = service_start_date.strftime("%Y-%m-%d")

    if "NCH_BENE_DSCHRG_DT" in df.columns:
        df["NCH_BENE_DSCHRG_DT"] = service_end_date.strftime("%Y-%m-%d")

    return df


def adjust_payment_amounts(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "CLM_PMT_AMT" not in df.columns:
        return df

    payment_amounts = pd.to_numeric(df["CLM_PMT_AMT"], errors="coerce").fillna(0)

    adjustment_factors = [
        random.uniform(0.85, 1.15)
        for _ in range(len(payment_amounts))
    ]

    adjusted_amounts = [
        round(amount * factor, 2)
        for amount, factor in zip(payment_amounts, adjustment_factors)
    ]

    df["CLM_PMT_AMT"] = adjusted_amounts

    return df


def assign_daily_claim_ids(df: pd.DataFrame, run_date: date) -> pd.DataFrame:
    df = df.copy()

    if "CLM_ID" not in df.columns:
        raise ValueError("Expected CLM_ID column was not found")

    df["CLM_ID"] = [
        create_daily_claim_id(original_claim_id, run_date, index + 1)
        for index, original_claim_id in enumerate(df["CLM_ID"].astype(str))
    ]

    return df


def inject_bad_records(df: pd.DataFrame, claim_type: str) -> pd.DataFrame:
    df = df.copy()

    if len(df) < 10:
        return df

    logger.info("Injecting controlled bad records for %s feed", claim_type)

    # 1. Missing claim ID
    df.loc[df.index[0], "CLM_ID"] = ""

    # 2. Missing beneficiary ID
    df.loc[df.index[1], "DESYNPUF_ID"] = ""

    # 3. Negative payment
    if "CLM_PMT_AMT" in df.columns:
        df.loc[df.index[2], "CLM_PMT_AMT"] = -999.99

    # 4. Missing claim start date
    if "CLM_FROM_DT" in df.columns:
        df.loc[df.index[3], "CLM_FROM_DT"] = ""

    return df


def generate_daily_file(
    source_file_name: str,
    claim_type: str,
    run_date: date,
    sample_size: int,
) -> Path:
    source_path = SOURCE_DIR / source_file_name

    if not source_path.exists():
        raise FileNotFoundError(f"Source file does not exist: {source_path}")

    logger.info("Reading source file: %s", source_path)

    source_df = pd.read_csv(source_path, dtype=str)
    source_df = clean_column_names(source_df)

    logger.info("Source rows available for %s: %s", claim_type, len(source_df))

    sample_df = source_df.sample(
        n=min(sample_size, len(source_df)),
        random_state=RANDOM_SEED,
    ).reset_index(drop=True)

    logger.info("Sampled %s rows for %s daily feed", len(sample_df), claim_type)

    sample_df = assign_daily_claim_ids(sample_df, run_date)
    sample_df = shift_claim_dates(sample_df, run_date)
    sample_df = adjust_payment_amounts(sample_df)
    sample_df = inject_bad_records(sample_df, claim_type)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file_name = f"daily_{claim_type}_claims_{run_date.strftime('%Y_%m_%d')}.csv"
    output_path = OUTPUT_DIR / output_file_name

    sample_df.to_csv(output_path, index=False)

    logger.info("Created daily %s claims file: %s", claim_type, output_path)
    logger.info("Rows written: %s", len(sample_df))

    return output_path


def main() -> None:
    run_date = date.today()

    logger.info("Starting daily claims feed generation")
    logger.info("Run date: %s", run_date)

    inpatient_output = generate_daily_file(
        source_file_name=INPATIENT_SOURCE_FILE,
        claim_type="inpatient",
        run_date=run_date,
        sample_size=500,
    )

    outpatient_output = generate_daily_file(
        source_file_name=OUTPATIENT_SOURCE_FILE,
        claim_type="outpatient",
        run_date=run_date,
        sample_size=1000,
    )

    logger.info("Daily claims feed generation completed")
    logger.info("Generated file: %s", inpatient_output)
    logger.info("Generated file: %s", outpatient_output)


if __name__ == "__main__":
    main()