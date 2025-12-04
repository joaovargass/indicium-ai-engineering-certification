"""Comprehensive test suite for metrics calculation functions."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import pandas as pd

from metrics.calculators import (
    calculate_case_increase_rate,
    calculate_icu_occupancy_rate,
    calculate_mortality_rate,
    calculate_vaccination_rate,
)


def load_test_data() -> pd.DataFrame:
    """Load test data from cache or create sample data."""
    cache_path = PROJECT_ROOT / "data" / "cleaned" / "dash_cache.parquet"
    if cache_path.exists():
        df = pd.read_parquet(cache_path)
        print(f"Loaded {len(df):,} rows from cache")
        return df

    print("Cache not found, creating sample data...")
    return _create_sample_data()


def _create_sample_data() -> pd.DataFrame:
    """Create sample SRAG data for testing."""
    from datetime import datetime, timedelta

    import numpy as np

    rng = np.random.default_rng(42)
    n_samples = 1000

    base_date = datetime(2024, 1, 1)
    dates = [base_date + timedelta(days=x) for x in range(n_samples)]

    data = {
        "NU_NOTIFIC": range(1, n_samples + 1),
        "DT_NOTIFIC": dates,
        "DT_SIN_PRI": [d - timedelta(days=rng.integers(0, 7)) for d in dates],
        "EVOLUCAO": rng.choice(
            ["1", "2", "3", "9", None], n_samples, p=[0.6, 0.15, 0.05, 0.1, 0.1]
        ),
        "UTI": rng.choice(["1", "2", "9", None], n_samples, p=[0.2, 0.6, 0.1, 0.1]),
        "DT_ENTUTI": [None] * n_samples,
        "DT_SAIDUTI": [None] * n_samples,
        "VACINA_COV": rng.choice(
            ["1", "2", "9", None], n_samples, p=[0.7, 0.15, 0.05, 0.1]
        ),
        "VACINA": rng.choice(["1", "2", "9", None], n_samples, p=[0.5, 0.3, 0.1, 0.1]),
        "SG_UF_NOT": rng.choice(["SP", "RJ", "MG", "RS"], n_samples),
        "CO_MUN_NOT": rng.choice(["3550308", "3304557", "3106200"], n_samples),
    }

    for i in range(n_samples):
        if data["UTI"][i] == "1":
            entry_date = data["DT_SIN_PRI"][i] + timedelta(days=rng.integers(0, 5))
            data["DT_ENTUTI"][i] = entry_date
            if rng.random() > 0.3:
                exit_date = entry_date + timedelta(days=rng.integers(1, 20))
                data["DT_SAIDUTI"][i] = exit_date

    return pd.DataFrame(data)


def test_case_increase_rate_national(df: pd.DataFrame):
    """Test case increase rate - national data."""
    print("\n" + "=" * 70)
    print("TEST: Case Increase Rate - National")
    print("=" * 70)

    print(f"\nData: {len(df):,} rows")

    # Default period (7 days)
    print("\n1. Default period (7 days)")
    result = calculate_case_increase_rate(df, period_days=7)
    _print_case_increase_result(result)

    # Custom period (14 days)
    print("\n2. Custom period (14 days)")
    result = calculate_case_increase_rate(df, period_days=14)
    _print_case_increase_result(result)

    # Custom reporting lag
    print("\n3. Custom reporting lag (3 days)")
    result = calculate_case_increase_rate(df, period_days=7, reporting_lag_days=3)
    _print_case_increase_result(result)


def test_case_increase_rate_filtered(df: pd.DataFrame):
    """Test case increase rate - with filters."""
    print("\n" + "=" * 70)
    print("TEST: Case Increase Rate - Filtered")
    print("=" * 70)

    # State filter
    print("\n1. State filter (SP)")
    result = calculate_case_increase_rate(
        df, period_days=7, location_col="SG_UF_NOT", location_value="SP"
    )
    _print_case_increase_result(result)

    # City filter (6-digit IBGE code: 355030 = Sao Paulo)
    print("\n2. City filter (355030 - Sao Paulo)")
    result = calculate_case_increase_rate(
        df, period_days=7, location_col="CO_MUN_NOT", location_value="355030"
    )
    _print_case_increase_result(result)

    # Multiple states comparison
    print("\n3. Multiple states comparison")
    for uf in ["SP", "RJ", "MG"]:
        result = calculate_case_increase_rate(
            df, period_days=7, location_col="SG_UF_NOT", location_value=uf
        )
        rate = f"{result['rate']:.1f}%" if result["rate"] is not None else "N/A"
        print(f"   {uf}: {rate} ({result['current_period_cases']} current)")


def _print_case_increase_result(result: dict) -> None:
    """Print case increase result."""
    if result["rate"] is not None:
        print(f"   [OK] Rate: {result['rate']:.2f}%")
    else:
        print("   [OK] Rate: N/A")
    print(
        f"   Current: {result['current_period_cases']:,}, Previous: {result['previous_period_cases']:,}"
    )
    print(
        f"   Period: {result['current_period_start']} to {result['current_period_end']}"
    )
    if result.get("metadata", {}).get("warning"):
        print(f"   Warning: {result['metadata']['warning']}")


def test_mortality_rate_national(df: pd.DataFrame):
    """Test mortality rate - national data."""
    print("\n" + "=" * 70)
    print("TEST: Mortality Rate - National")
    print("=" * 70)

    print(f"\nData: {len(df):,} rows")
    print(f"Rows with EVOLUCAO: {df['EVOLUCAO'].notna().sum():,}")

    result = calculate_mortality_rate(df)
    _print_mortality_result(result)


def test_mortality_rate_filtered(df: pd.DataFrame):
    """Test mortality rate - with filters."""
    print("\n" + "=" * 70)
    print("TEST: Mortality Rate - Filtered")
    print("=" * 70)

    # State filter
    print("\n1. State filter (SP)")
    result = calculate_mortality_rate(df, location_col="SG_UF_NOT", location_value="SP")
    _print_mortality_result(result)

    # State filter (RJ)
    print("\n2. State filter (RJ)")
    result = calculate_mortality_rate(df, location_col="SG_UF_NOT", location_value="RJ")
    _print_mortality_result(result)

    # City filter (6-digit IBGE code: 330455 = Rio de Janeiro)
    print("\n3. City filter (330455 - Rio de Janeiro)")
    result = calculate_mortality_rate(
        df, location_col="CO_MUN_NOT", location_value="330455"
    )
    _print_mortality_result(result)

    # All states comparison
    print("\n4. All states comparison")
    for uf in ["SP", "RJ", "MG", "RS"]:
        result = calculate_mortality_rate(
            df, location_col="SG_UF_NOT", location_value=uf
        )
        rate = f"{result['rate']:.2f}%" if result["rate"] is not None else "N/A"
        print(f"   {uf}: {rate} ({result['total_deaths']} deaths)")


def _print_mortality_result(result: dict) -> None:
    """Print mortality result."""
    if result["rate"] is not None:
        print(f"   [OK] Rate: {result['rate']:.2f}%")
    else:
        print("   [OK] Rate: N/A")
    print(f"   Deaths: {result['total_deaths']:,}, Cases: {result['total_cases']:,}")
    if result.get("metadata", {}).get("ignored_cases"):
        print(f"   Ignored (EVOLUCAO=9): {result['metadata']['ignored_cases']:,}")


def test_icu_occupancy_national(df: pd.DataFrame):
    """Test ICU occupancy rate - national data."""
    print("\n" + "=" * 70)
    print("TEST: ICU Occupancy Rate - National")
    print("=" * 70)

    print(f"\nData: {len(df):,} rows")
    print(f"Rows with UTI=1: {(df['UTI'] == '1').sum():,}")

    # Default lookback (90 days)
    print("\n1. Default lookback (90 days)")
    result = calculate_icu_occupancy_rate(df, lookback_days=90)
    _print_icu_result(result)

    # Short lookback (30 days)
    print("\n2. Short lookback (30 days)")
    result = calculate_icu_occupancy_rate(df, lookback_days=30)
    _print_icu_result(result)

    # With provided bed count
    print("\n3. With provided bed count (1000)")
    result = calculate_icu_occupancy_rate(df, total_icu_beds=1000)
    _print_icu_result(result)


def test_icu_occupancy_filtered(df: pd.DataFrame):
    """Test ICU occupancy rate - with filters."""
    print("\n" + "=" * 70)
    print("TEST: ICU Occupancy Rate - Filtered")
    print("=" * 70)

    # State filter
    print("\n1. State filter (SP)")
    result = calculate_icu_occupancy_rate(
        df, location_col="SG_UF_NOT", location_value="SP"
    )
    _print_icu_result(result)

    # State filter (RJ)
    print("\n2. State filter (RJ)")
    result = calculate_icu_occupancy_rate(
        df, location_col="SG_UF_NOT", location_value="RJ"
    )
    _print_icu_result(result)

    # All states comparison
    print("\n3. All states comparison")
    for uf in ["SP", "RJ", "MG", "RS"]:
        result = calculate_icu_occupancy_rate(
            df, location_col="SG_UF_NOT", location_value=uf
        )
        rate = (
            f"{result['occupancy_rate']:.2f}%"
            if result["occupancy_rate"] is not None
            else "N/A"
        )
        print(f"   {uf}: {rate} ({result['patients_in_icu']} patients)")


def _print_icu_result(result: dict) -> None:
    """Print ICU occupancy result."""
    if result["occupancy_rate"] is not None:
        print(f"   [OK] Occupancy: {result['occupancy_rate']:.2f}%")
    else:
        print("   [OK] Occupancy: N/A")
    print(f"   Patients in ICU: {result['patients_in_icu']:,}")
    print(f"   Total beds: {result['total_icu_beds']}")
    print(f"   Data source: {result.get('data_source', 'N/A')}")


def test_vaccination_rate_national(df: pd.DataFrame):
    """Test vaccination rate - national data."""
    print("\n" + "=" * 70)
    print("TEST: Vaccination Rate - National")
    print("=" * 70)

    print(f"\nData: {len(df):,} rows")

    # Both vaccines
    print("\n1. Both vaccines")
    result = calculate_vaccination_rate(df, vaccine_type="both")
    _print_vaccination_result(result, "both")

    # COVID only
    print("\n2. COVID-19 only")
    result = calculate_vaccination_rate(df, vaccine_type="covid")
    _print_vaccination_result(result, "covid")

    # Flu only
    print("\n3. Flu only")
    result = calculate_vaccination_rate(df, vaccine_type="flu")
    _print_vaccination_result(result, "flu")


def test_vaccination_rate_filtered(df: pd.DataFrame):
    """Test vaccination rate - with filters."""
    print("\n" + "=" * 70)
    print("TEST: Vaccination Rate - Filtered")
    print("=" * 70)

    # State filter - both vaccines
    print("\n1. State filter (SP) - both vaccines")
    result = calculate_vaccination_rate(
        df, vaccine_type="both", location_col="SG_UF_NOT", location_value="SP"
    )
    _print_vaccination_result(result, "both")

    # State filter - COVID only
    print("\n2. State filter (RJ) - COVID only")
    result = calculate_vaccination_rate(
        df, vaccine_type="covid", location_col="SG_UF_NOT", location_value="RJ"
    )
    _print_vaccination_result(result, "covid")

    # All states comparison
    print("\n3. All states COVID vaccination comparison")
    for uf in ["SP", "RJ", "MG", "RS"]:
        result = calculate_vaccination_rate(
            df, vaccine_type="covid", location_col="SG_UF_NOT", location_value=uf
        )
        rate = (
            f"{result['covid_rate']:.2f}%"
            if result["covid_rate"] is not None
            else "N/A"
        )
        print(f"   {uf}: {rate} ({result['covid_vaccinated']:,} vaccinated)")


def _print_vaccination_result(result: dict, vaccine_type: str) -> None:
    """Print vaccination result."""
    if vaccine_type in ("both", "covid"):
        if result["covid_rate"] is not None:
            print(f"   [OK] COVID rate: {result['covid_rate']:.2f}%")
        else:
            print("   [OK] COVID rate: N/A")
        print(f"   COVID vaccinated: {result['covid_vaccinated']:,}")

    if vaccine_type in ("both", "flu"):
        if result["flu_rate"] is not None:
            print(f"   [OK] Flu rate: {result['flu_rate']:.2f}%")
        else:
            print("   [OK] Flu rate: N/A")
        print(f"   Flu vaccinated: {result['flu_vaccinated']:,}")

    print(f"   Total cases: {result['total_cases']:,}")


def test_edge_cases():
    """Test edge cases with empty/invalid data."""
    print("\n" + "=" * 70)
    print("TEST: Edge Cases")
    print("=" * 70)

    # Empty DataFrame
    print("\n1. Empty DataFrame")
    empty_df = pd.DataFrame(columns=["DT_SIN_PRI", "EVOLUCAO", "UTI", "VACINA_COV"])

    result = calculate_case_increase_rate(empty_df)
    print(
        f"   Case increase: rate={result['rate']}, cases={result['current_period_cases']}"
    )

    result = calculate_mortality_rate(empty_df)
    print(f"   Mortality: rate={result['rate']}, deaths={result['total_deaths']}")

    result = calculate_icu_occupancy_rate(empty_df)
    print(
        f"   ICU: rate={result['occupancy_rate']}, patients={result['patients_in_icu']}"
    )

    result = calculate_vaccination_rate(empty_df)
    print(f"   Vaccination: covid={result['covid_rate']}, flu={result['flu_rate']}")

    # Missing columns
    print("\n2. Missing required columns")
    minimal_df = pd.DataFrame({"NU_NOTIFIC": [1, 2, 3]})

    result = calculate_case_increase_rate(minimal_df)
    print(
        f"   Case increase (no date): {result.get('metadata', {}).get('error', 'OK')}"
    )

    result = calculate_mortality_rate(minimal_df)
    print(
        f"   Mortality (no EVOLUCAO): {result.get('metadata', {}).get('error', 'OK')}"
    )

    # Invalid location filter
    print("\n3. Invalid location filter")
    df = load_test_data()
    result = calculate_mortality_rate(df, location_col="SG_UF_NOT", location_value="XX")
    print(
        f"   Non-existent state: deaths={result['total_deaths']}, cases={result['total_cases']}"
    )


def main():
    """Run all metric tests."""
    print("\n" + "=" * 70)
    print("METRICS CALCULATION - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    df = load_test_data()

    tests = [
        ("Case Increase - National", lambda: test_case_increase_rate_national(df)),
        ("Case Increase - Filtered", lambda: test_case_increase_rate_filtered(df)),
        ("Mortality - National", lambda: test_mortality_rate_national(df)),
        ("Mortality - Filtered", lambda: test_mortality_rate_filtered(df)),
        ("ICU Occupancy - National", lambda: test_icu_occupancy_national(df)),
        ("ICU Occupancy - Filtered", lambda: test_icu_occupancy_filtered(df)),
        ("Vaccination - National", lambda: test_vaccination_rate_national(df)),
        ("Vaccination - Filtered", lambda: test_vaccination_rate_filtered(df)),
        ("Edge Cases", test_edge_cases),
    ]

    failed = []
    for name, test_fn in tests:
        try:
            test_fn()
        except Exception as e:
            print(f"\n[ERROR] {name} failed: {e}")
            failed.append(name)
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"\nTotal test groups: {len(tests)}")
    print(f"Passed: {len(tests) - len(failed)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print(f"\nFailed tests: {failed}")
    else:
        print("\n[OK] All tests completed successfully!")


if __name__ == "__main__":
    main()
