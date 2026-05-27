import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

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


CHECKS = [
    {
        "check_name": "beneficiary_summary_has_rows",
        "severity": "error",
        "sql": """
            SELECT COUNT(*) AS failed_count
            FROM bronze.beneficiary_summary
            HAVING COUNT(*) = 0;
        """,
    },
    {
        "check_name": "inpatient_claims_has_rows",
        "severity": "error",
        "sql": """
            SELECT COUNT(*) AS failed_count
            FROM bronze.inpatient_claims
            HAVING COUNT(*) = 0;
        """,
    },
    {
        "check_name": "outpatient_claims_has_rows",
        "severity": "error",
        "sql": """
            SELECT COUNT(*) AS failed_count
            FROM bronze.outpatient_claims
            HAVING COUNT(*) = 0;
        """,
    },
    {
        "check_name": "beneficiary_id_not_null",
        "severity": "error",
        "sql": """
            SELECT COUNT(*) AS failed_count
            FROM bronze.beneficiary_summary
            WHERE desynpuf_id IS NULL OR TRIM(desynpuf_id) = '';
        """,
    },
    {
        "check_name": "inpatient_claim_id_not_null",
        "severity": "error",
        "sql": """
            SELECT COUNT(*) AS failed_count
            FROM bronze.inpatient_claims
            WHERE clm_id IS NULL OR TRIM(clm_id) = '';
        """,
    },
    {
        "check_name": "outpatient_claim_id_not_null",
        "severity": "error",
        "sql": """
            SELECT COUNT(*) AS failed_count
            FROM bronze.outpatient_claims
            WHERE clm_id IS NULL OR TRIM(clm_id) = '';
        """,
    },
    {
        "check_name": "inpatient_claims_missing_beneficiary",
        "severity": "error",
        "sql": """
            SELECT COUNT(*) AS failed_count
            FROM bronze.inpatient_claims c
            LEFT JOIN bronze.beneficiary_summary b
                ON c.desynpuf_id = b.desynpuf_id
            WHERE b.desynpuf_id IS NULL;
        """,
    },
    {
        "check_name": "outpatient_claims_missing_beneficiary",
        "severity": "error",
        "sql": """
            SELECT COUNT(*) AS failed_count
            FROM bronze.outpatient_claims c
            LEFT JOIN bronze.beneficiary_summary b
                ON c.desynpuf_id = b.desynpuf_id
            WHERE b.desynpuf_id IS NULL;
        """,
    },
    {
        "check_name": "inpatient_duplicate_claim_ids_warning",
        "severity": "warning",
        "sql": """
            SELECT COUNT(*) AS failed_count
            FROM (
                SELECT clm_id
                FROM bronze.inpatient_claims
                GROUP BY clm_id
                HAVING COUNT(*) > 1
            ) duplicate_claims;
        """,
    },
    {
        "check_name": "outpatient_duplicate_claim_ids_warning",
        "severity": "warning",
        "sql": """
            SELECT COUNT(*) AS failed_count
            FROM (
                SELECT clm_id
                FROM bronze.outpatient_claims
                GROUP BY clm_id
                HAVING COUNT(*) > 1
            ) duplicate_claims;
        """,
    },
    {
        "check_name": "inpatient_negative_payment_amounts_warning",
        "severity": "warning",
        "sql": """
            SELECT COUNT(*) AS failed_count
            FROM bronze.inpatient_claims
            WHERE clm_pmt_amt < 0;
        """,
    },
    {
        "check_name": "outpatient_negative_payment_amounts_warning",
        "severity": "warning",
        "sql": """
            SELECT COUNT(*) AS failed_count
            FROM bronze.outpatient_claims
            WHERE clm_pmt_amt < 0;
        """,
    },
]


def run_check(engine, check: dict) -> dict:
    with engine.connect() as conn:
        result = conn.execute(text(check["sql"])).fetchone()

    failed_count = 0 if result is None else int(result[0])

    if failed_count == 0:
        status = "PASS"
    elif check["severity"] == "warning":
        status = "WARN"
    else:
        status = "FAIL"

    return {
        "check_name": check["check_name"],
        "severity": check["severity"],
        "status": status,
        "failed_count": failed_count,
    }


def main() -> None:
    engine = get_engine()

    logger.info("Starting Bronze data quality validation")

    results = []

    for check in CHECKS:
        result = run_check(engine, check)
        results.append(result)

        log_message = (
            f"{result['status']:4} | "
            f"{result['check_name']:45} | "
            f"severity={result['severity']} | "
            f"failed_count={result['failed_count']}"
        )

        if result["status"] == "FAIL":
            logger.error(log_message)
        elif result["status"] == "WARN":
            logger.warning(log_message)
        else:
            logger.info(log_message)

    failed_checks = [result for result in results if result["status"] == "FAIL"]
    warning_checks = [result for result in results if result["status"] == "WARN"]

    logger.info("Validation summary")
    logger.info("Total checks: %s", len(results))
    logger.info("Passed: %s", len([r for r in results if r["status"] == "PASS"]))
    logger.info("Warnings: %s", len(warning_checks))
    logger.info("Failed: %s", len(failed_checks))

    if failed_checks:
        raise SystemExit("Bronze validation failed")

    print("\nBronze validation completed successfully with warnings allowed")


if __name__ == "__main__":
    main()