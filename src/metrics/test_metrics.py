"""Test file for metrics calculation functions.

This file demonstrates how to use each metric function with proper data cleaning.
Each metric function filters and cleans data specific to its needs.
"""

import sys
from pathlib import Path

# Add src to path for direct execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import pandas as pd
from metrics.core import (
    calculate_case_increase_rate,
    calculate_icu_occupancy_rate,
    calculate_mortality_rate,
    calculate_vaccination_rate,
)


def load_test_data() -> pd.DataFrame:
    """
    Load test data from cleaned parquet file or create sample data.

    Returns:
        DataFrame with SRAG case data.
    """
    try:
        df = pd.read_parquet("data/cleaned/dash_cache.parquet")
        print(f"Loaded {len(df):,} rows from cleaned data")
        return df
    except FileNotFoundError:
        print("Cleaned data file not found, creating sample data...")
        return _create_sample_data()


def _create_sample_data() -> pd.DataFrame:
    """Create sample SRAG data for testing."""
    import numpy as np
    from datetime import datetime, timedelta

    np.random.seed(42)
    n_samples = 1000

    base_date = datetime(2024, 1, 1)
    dates = [base_date + timedelta(days=x) for x in range(n_samples)]

    data = {
        "NU_NOTIFIC": range(1, n_samples + 1),
        "DT_NOTIFIC": dates,
        "DT_SIN_PRI": [d - timedelta(days=np.random.randint(0, 7)) for d in dates],
        "EVOLUCAO": np.random.choice(["1", "2", "3", "9", None], n_samples, p=[0.6, 0.15, 0.05, 0.1, 0.1]),
        "UTI": np.random.choice(["1", "2", "9", None], n_samples, p=[0.2, 0.6, 0.1, 0.1]),
        "DT_ENTUTI": [None] * n_samples,
        "DT_SAIDUTI": [None] * n_samples,
        "VACINA_COV": np.random.choice(["1", "2", "9", None], n_samples, p=[0.7, 0.15, 0.05, 0.1]),
        "VACINA": np.random.choice(["1", "2", "9", None], n_samples, p=[0.5, 0.3, 0.1, 0.1]),
        "SG_UF_NOT": np.random.choice(["SP", "RJ", "MG", "RS"], n_samples),
        "CO_MUN_NOT": np.random.choice(["3550308", "3304557", "3106200"], n_samples),
    }

    for i in range(n_samples):
        if data["UTI"][i] == "1":
            entry_date = data["DT_SIN_PRI"][i] + timedelta(days=np.random.randint(0, 5))
            data["DT_ENTUTI"][i] = entry_date
            if np.random.random() > 0.3:
                exit_date = entry_date + timedelta(days=np.random.randint(1, 20))
                data["DT_SAIDUTI"][i] = exit_date

    df = pd.DataFrame(data)
    return df


def test_case_increase_rate(df: pd.DataFrame) -> None:
    """
    Test case increase rate calculation.

    This function:
    1. Filters rows that have date information (DT_SIN_PRI or DT_NOTIFIC)
    2. Removes nulls only from date columns
    3. Calls the metric function
    """
    print("\n" + "=" * 60)
    print("TEST: Case Increase Rate")
    print("=" * 60)

    required_cols = ["DT_SIN_PRI", "DT_NOTIFIC"]
    available_cols = [col for col in required_cols if col in df.columns]

    if not available_cols:
        print("ERROR: No date columns found")
        return

    print(f"Original data: {len(df):,} rows")
    print(f"Available date columns: {available_cols}")

    result = calculate_case_increase_rate(df, period_days=7)
    print(f"\nResult:")
    print(f"  Rate: {result['rate']:.2f}%" if result['rate'] is not None else "  Rate: N/A")
    print(f"  Current period cases: {result['current_period_cases']:,}")
    print(f"  Previous period cases: {result['previous_period_cases']:,}")
    print(f"  Current period: {result['current_period_start']} to {result['current_period_end']}")
    print(f"  Previous period: {result['previous_period_start']} to {result['previous_period_end']}")

    if result.get("metadata", {}).get("error"):
        print(f"  Error: {result['metadata']['error']}")
    elif result.get("metadata", {}).get("warning"):
        print(f"  Warning: {result['metadata']['warning']}")

    result_sp = calculate_case_increase_rate(df, period_days=7, location_col="SG_UF_NOT", location_value="SP")
    print(f"\nResult for SP:")
    print(f"  Rate: {result_sp['rate']:.2f}%" if result_sp['rate'] is not None else "  Rate: N/A")
    print(f"  Current period cases: {result_sp['current_period_cases']:,}")
    print(f"  Previous period cases: {result_sp['previous_period_cases']:,}")


def test_mortality_rate(df: pd.DataFrame) -> None:
    """
    Test mortality rate calculation.

    This function:
    1. Filters rows that have EVOLUCAO information
    2. Removes nulls only from EVOLUCAO column
    3. Calls the metric function
    """
    print("\n" + "=" * 60)
    print("TEST: Mortality Rate")
    print("=" * 60)

    if "EVOLUCAO" not in df.columns:
        print("ERROR: EVOLUCAO column not found")
        return

    print(f"Original data: {len(df):,} rows")
    print(f"Rows with EVOLUCAO: {df['EVOLUCAO'].notna().sum():,}")

    result = calculate_mortality_rate(df)
    print(f"\nResult:")
    print(f"  Rate: {result['rate']:.2f}%" if result['rate'] is not None else "  Rate: N/A")
    print(f"  Total deaths: {result['total_deaths']:,}")
    print(f"  Total cases (with evolution): {result['total_cases']:,}")

    if result.get("metadata", {}).get("ignored_cases"):
        print(f"  Ignored cases (EVOLUCAO=9): {result['metadata']['ignored_cases']:,}")

    if result.get("metadata", {}).get("error"):
        print(f"  Error: {result['metadata']['error']}")
    elif result.get("metadata", {}).get("warning"):
        print(f"  Warning: {result['metadata']['warning']}")

    result_sp = calculate_mortality_rate(df, location_col="SG_UF_NOT", location_value="SP")
    print(f"\nResult for SP:")
    print(f"  Rate: {result_sp['rate']:.2f}%" if result_sp['rate'] is not None else "  Rate: N/A")
    print(f"  Total deaths: {result_sp['total_deaths']:,}")
    print(f"  Total cases: {result_sp['total_cases']:,}")


def test_icu_occupancy_rate(df: pd.DataFrame) -> None:
    """
    Test ICU occupancy rate calculation.

    This function:
    1. Filters rows that have UTI information
    2. Removes nulls only from UTI and related date columns
    3. Calls the metric function
    """
    print("\n" + "=" * 60)
    print("TEST: ICU Occupancy Rate")
    print("=" * 60)

    required_cols = ["UTI", "DT_ENTUTI"]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        print(f"ERROR: Missing required columns: {missing_cols}")
        return

    print(f"Original data: {len(df):,} rows")
    print(f"Rows with UTI info: {df['UTI'].notna().sum():,}")
    print(f"Rows with UTI=1: {(df['UTI'] == '1').sum():,}")

    result = calculate_icu_occupancy_rate(df, use_mock_data=True)
    print(f"\nResult (with mock data):")
    print(f"  Occupancy rate: {result['occupancy_rate']:.2f}%" if result['occupancy_rate'] is not None else "  Occupancy rate: N/A")
    print(f"  Patients in ICU: {result['patients_in_icu']:,}")
    print(f"  Total ICU beds: {result['total_icu_beds']:,}")
    print(f"  Data source: {result['metadata'].get('data_source', 'unknown')}")

    if result.get("metadata", {}).get("note"):
        print(f"  Note: {result['metadata']['note']}")

    result_absolute = calculate_icu_occupancy_rate(df, use_mock_data=False)
    print(f"\nResult (absolute only, no external data):")
    print(f"  Patients in ICU: {result_absolute['patients_in_icu']:,}")
    print(f"  Occupancy rate: {result_absolute['occupancy_rate']}" if result_absolute['occupancy_rate'] is not None else "  Occupancy rate: N/A (no bed data)")

    result_sp = calculate_icu_occupancy_rate(df, location_col="SG_UF_NOT", location_value="SP", use_mock_data=True)
    print(f"\nResult for SP (with mock data):")
    print(f"  Occupancy rate: {result_sp['occupancy_rate']:.2f}%" if result_sp['occupancy_rate'] is not None else "  Occupancy rate: N/A")
    print(f"  Patients in ICU: {result_sp['patients_in_icu']:,}")
    print(f"  Total ICU beds: {result_sp['total_icu_beds']:,}")


def test_vaccination_rate(df: pd.DataFrame) -> None:
    """
    Test vaccination rate calculation.

    This function:
    1. Filters rows that have vaccination information (VACINA_COV or VACINA)
    2. Removes nulls only from vaccination columns
    3. Calls the metric function
    """
    print("\n" + "=" * 60)
    print("TEST: Vaccination Rate")
    print("=" * 60)

    has_covid = "VACINA_COV" in df.columns
    has_flu = "VACINA" in df.columns

    if not has_covid and not has_flu:
        print("ERROR: No vaccination columns found")
        return

    print(f"Original data: {len(df):,} rows")
    if has_covid:
        print(f"Rows with VACINA_COV: {df['VACINA_COV'].notna().sum():,}")
    if has_flu:
        print(f"Rows with VACINA: {df['VACINA'].notna().sum():,}")

    result = calculate_vaccination_rate(df, vaccine_type="both")
    print(f"\nResult (both vaccines):")
    print(f"  COVID-19 rate: {result['covid_rate']:.2f}%" if result['covid_rate'] is not None else "  COVID-19 rate: N/A")
    print(f"  Flu rate: {result['flu_rate']:.2f}%" if result['flu_rate'] is not None else "  Flu rate: N/A")
    print(f"  COVID-19 vaccinated: {result['covid_vaccinated']:,}")
    print(f"  Flu vaccinated: {result['flu_vaccinated']:,}")
    print(f"  Total cases: {result['total_cases']:,}")

    if result.get("metadata", {}).get("covid_ignored"):
        print(f"  COVID-19 ignored (VACINA_COV=9): {result['metadata']['covid_ignored']:,}")
    if result.get("metadata", {}).get("flu_ignored"):
        print(f"  Flu ignored (VACINA=9): {result['metadata']['flu_ignored']:,}")

    result_covid = calculate_vaccination_rate(df, vaccine_type="covid")
    print(f"\nResult (COVID-19 only):")
    print(f"  COVID-19 rate: {result_covid['covid_rate']:.2f}%" if result_covid['covid_rate'] is not None else "  COVID-19 rate: N/A")
    print(f"  COVID-19 vaccinated: {result_covid['covid_vaccinated']:,}")
    print(f"  Total cases: {result_covid['total_cases']:,}")

    result_sp = calculate_vaccination_rate(df, location_col="SG_UF_NOT", location_value="SP", vaccine_type="both")
    print(f"\nResult for SP (both vaccines):")
    print(f"  COVID-19 rate: {result_sp['covid_rate']:.2f}%" if result_sp['covid_rate'] is not None else "  COVID-19 rate: N/A")
    print(f"  Flu rate: {result_sp['flu_rate']:.2f}%" if result_sp['flu_rate'] is not None else "  Flu rate: N/A")
    print(f"  COVID-19 vaccinated: {result_sp['covid_vaccinated']:,}")
    print(f"  Flu vaccinated: {result_sp['flu_vaccinated']:,}")


def main() -> None:
    """Run all metric tests."""
    print("=" * 60)
    print("METRICS CALCULATION TESTS")
    print("=" * 60)
    print("\nThis test file demonstrates:")
    print("1. Loading and cleaning data specific to each metric")
    print("2. Filtering nulls only for relevant columns per metric")
    print("3. Calling each metric function with proper parameters")
    print("4. Testing location-based filtering (granularity)")

    df = load_test_data()

    test_case_increase_rate(df)
    test_mortality_rate(df)
    test_icu_occupancy_rate(df)
    test_vaccination_rate(df)

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()

