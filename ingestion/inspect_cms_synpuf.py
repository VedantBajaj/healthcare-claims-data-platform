from pathlib import Path
import pandas as pd


DATA_DIR = Path("D:\healthcare-claims-data-platform\data\external\cms_synpuf\sample_1")
OUTPUT_DIR = Path("docs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def inspect_csv(file_path: Path) -> dict:
    print(f"\nInspecting: {file_path.name}")

    df_sample = pd.read_csv(file_path, nrows=1000)

    row_count = sum(1 for _ in open(file_path, encoding="utf-8")) - 1
    column_count = len(df_sample.columns)

    print(f"Rows: {row_count}")
    print(f"Columns: {column_count}")
    print("Column names:")
    for col in df_sample.columns:
        print(f"  - {col}")

    return {
        "file_name": file_path.name,
        "row_count": row_count,
        "column_count": column_count,
        "columns": ", ".join(df_sample.columns),
    }


def main() -> None:
    csv_files = sorted(DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")

    results = []

    for file_path in csv_files:
        results.append(inspect_csv(file_path))

    summary_df = pd.DataFrame(results)
    output_path = OUTPUT_DIR / "cms_synpuf_file_summary.csv"
    summary_df.to_csv(output_path, index=False)

    print(f"\nSaved summary to: {output_path}")


if __name__ == "__main__":
    main()