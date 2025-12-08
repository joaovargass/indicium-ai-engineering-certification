"""Test script for chart generation functions."""

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from charts.charts import plot_daily_cases, plot_monthly_cases  # noqa: E402
from elt.load import read_from_dw  # noqa: E402


def load_data() -> pd.DataFrame:
    """Load data from DW or local file."""
    try:
        print("Attempting to load data from Data Warehouse...")
        df = read_from_dw()
        return df
    except Exception as e:
        print(f"Could not load from DW: {e}")
        print("Trying local parquet file...")

        local_path = PROJECT_ROOT / "data" / "cleaned" / "srag_cleaned.parquet"
        if local_path.exists():
            df = pd.read_parquet(local_path)
            print(f"Loaded {len(df):,} rows from local file")
            return df
        else:
            raise FileNotFoundError(
                f"Data not found. Check DW connection or ensure {local_path} exists"
            ) from e


def test_general_charts(df: pd.DataFrame) -> None:
    """Test charts without location filtering."""
    print("\n" + "=" * 80)
    print("Testing General Charts (No Location Filter)")
    print("=" * 80)

    print("\n1. Daily Cases Chart (Last 30 Days)")
    fig_daily = plot_daily_cases(df)
    fig_daily.show()

    print("\n2. Monthly Cases Chart (Last 12 Months)")
    fig_monthly = plot_monthly_cases(df)
    fig_monthly.show()


def test_location_filtered_charts(df: pd.DataFrame) -> None:
    """Test charts with location filtering."""
    print("\n" + "=" * 80)
    print("Testing Location-Filtered Charts")
    print("=" * 80)

    if "SG_UF_NOT" not in df.columns:
        print("SG_UF_NOT column not found. Skipping location-filtered tests.")
        return

    available_ufs = df["SG_UF_NOT"].dropna().unique()[:3]
    print(f"\nTesting with UFs: {list(available_ufs)}")

    for uf in available_ufs:
        print(f"\n--- Testing with UF: {uf} ---")

        print(f"\n1. Daily Cases Chart - {uf}")
        fig_daily = plot_daily_cases(df, location_col="SG_UF_NOT", location_value=uf)
        fig_daily.show()

        print(f"\n2. Monthly Cases Chart - {uf}")
        fig_monthly = plot_monthly_cases(
            df, location_col="SG_UF_NOT", location_value=uf
        )
        fig_monthly.show()


def main() -> None:
    """Run chart tests."""
    print("=" * 80)
    print("CHART TESTING")
    print("=" * 80)

    df = load_data()
    print(f"\nLoaded dataset with {len(df):,} rows")

    if "DT_SIN_PRI" in df.columns:
        df["DT_SIN_PRI"] = pd.to_datetime(df["DT_SIN_PRI"], errors="coerce")
        valid_dates = df["DT_SIN_PRI"].notna().sum()
        print(f"Valid dates in DT_SIN_PRI: {valid_dates:,}")

    test_general_charts(df)
    test_location_filtered_charts(df)

    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
