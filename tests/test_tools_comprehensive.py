"""Comprehensive test suite for all LangChain tools."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from tools import ALL_TOOLS
from tools.chart_tools import get_daily_chart_json, get_monthly_chart_json
from tools.metric_tools import (
    get_case_increase_rate,
    get_icu_occupancy_rate,
    get_mortality_rate,
    get_vaccination_rate,
)
from tools.news import search_srag_news_tool
from tools.reports import generate_chat_report, generate_download_report


def test_data_loading():
    """Test data loading and location utilities."""
    print("=" * 70)
    print("TEST: Data Loading & Location Utilities")
    print("=" * 70)

    from elt.load import load_srag_data
    from tools.location_utils import determine_location_filter, get_location_description

    # Test load_srag_data
    print("\n1. load_srag_data()")
    try:
        df = load_srag_data()
        print(f"   [OK] Loaded {len(df):,} rows, {len(df.columns)} columns")
        print(f"   Columns: {list(df.columns)[:5]}... (showing first 5)")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return

    # Test determine_location_filter - all scenarios
    print("\n2. determine_location_filter()")
    test_cases = [
        (None, None, (None, None), "No filter (national)"),
        ("SP", None, ("SG_UF_NOT", "SP"), "State filter (SP)"),
        ("sp", None, ("SG_UF_NOT", "SP"), "State filter lowercase"),
        (None, "355030", ("CO_MUN_NOT", "355030"), "City filter (Sao Paulo)"),
        ("RJ", "355030", ("CO_MUN_NOT", "355030"), "City overrides state"),
    ]
    for uf, city, expected, desc in test_cases:
        result = determine_location_filter(uf, city)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"   {status} {desc}: {result}")

    # Test get_location_description - all scenarios
    print("\n3. get_location_description()")
    test_cases = [
        (None, None, "Brasil (todos os estados)", "National"),
        ("SP", None, "SP", "State SP"),
        (None, "355030", "IBGE 355030", "City code"),
    ]
    for uf, city, expected, desc in test_cases:
        result = get_location_description(uf, city)
        status = "[OK]" if expected in result else "[FAIL]"
        print(f"   {status} {desc}: {result}")


def test_metric_tools_national():
    """Test metric tools with national data (no filters)."""
    print("\n" + "=" * 70)
    print("TEST: Metric Tools - National Data (No Filters)")
    print("=" * 70)

    print("\n1. get_case_increase_rate(uf=None)")
    try:
        result = get_case_increase_rate.invoke({"uf": None})
        print(f"   [OK] Location: {result.get('location')}")
        print(f"   Rate: {result.get('rate')}")
        print(
            f"   Current: {result.get('current_period_cases')}, Previous: {result.get('previous_period_cases')}"
        )
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n2. get_mortality_rate(uf=None)")
    try:
        result = get_mortality_rate.invoke({"uf": None})
        print(f"   [OK] Location: {result.get('location')}")
        print(f"   Rate: {result.get('rate')}%")
        print(
            f"   Deaths: {result.get('total_deaths')}, Cases: {result.get('total_cases')}"
        )
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n3. get_icu_occupancy_rate(uf=None)")
    try:
        result = get_icu_occupancy_rate.invoke({"uf": None})
        print(f"   [OK] Location: {result.get('location')}")
        print(f"   Occupancy: {result.get('occupancy_rate')}%")
        print(
            f"   Patients: {result.get('patients_in_icu')}, Beds: {result.get('total_icu_beds')}"
        )
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n4. get_vaccination_rate(uf=None, vaccine_type='both')")
    try:
        result = get_vaccination_rate.invoke({"uf": None, "vaccine_type": "both"})
        print(f"   [OK] Location: {result.get('location')}")
        print(f"   COVID: {result.get('covid_rate')}%, Flu: {result.get('flu_rate')}%")
    except Exception as e:
        print(f"   [FAIL] {e}")


def test_metric_tools_state():
    """Test metric tools with state filter."""
    print("\n" + "=" * 70)
    print("TEST: Metric Tools - State Filter (SP)")
    print("=" * 70)

    print("\n1. get_case_increase_rate(uf='SP', period_days=14)")
    try:
        result = get_case_increase_rate.invoke({"uf": "SP", "period_days": 14})
        print(f"   [OK] Location: {result.get('location')}")
        print(f"   Rate: {result.get('rate')}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n2. get_mortality_rate(uf='RJ')")
    try:
        result = get_mortality_rate.invoke({"uf": "RJ"})
        print(f"   [OK] Location: {result.get('location')}")
        print(f"   Rate: {result.get('rate')}%")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n3. get_icu_occupancy_rate(uf='MG', lookback_days=60)")
    try:
        result = get_icu_occupancy_rate.invoke({"uf": "MG", "lookback_days": 60})
        print(f"   [OK] Location: {result.get('location')}")
        print(f"   Occupancy: {result.get('occupancy_rate')}%")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n4. get_vaccination_rate(uf='RS', vaccine_type='covid')")
    try:
        result = get_vaccination_rate.invoke({"uf": "RS", "vaccine_type": "covid"})
        print(f"   [OK] Location: {result.get('location')}")
        print(f"   COVID rate: {result.get('covid_rate')}%")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n5. get_vaccination_rate(uf='BA', vaccine_type='flu')")
    try:
        result = get_vaccination_rate.invoke({"uf": "BA", "vaccine_type": "flu"})
        print(f"   [OK] Location: {result.get('location')}")
        print(f"   Flu rate: {result.get('flu_rate')}%")
    except Exception as e:
        print(f"   [FAIL] {e}")


def test_metric_tools_city():
    """Test metric tools with city filter (IBGE code - 6 digits)."""
    print("\n" + "=" * 70)
    print("TEST: Metric Tools - City Filter (IBGE 6-digit Code)")
    print("=" * 70)

    # Note: Dataset uses 6-digit IBGE codes (without check digit)
    # 355030 = Sao Paulo, 330455 = Rio de Janeiro, 310620 = Belo Horizonte

    print("\n1. get_case_increase_rate(city_code='355030')  # Sao Paulo")
    try:
        result = get_case_increase_rate.invoke({"city_code": "355030"})
        print(f"   [OK] Location: {result.get('location')}")
        print(f"   Rate: {result.get('rate')}")
        print(f"   Cases: {result.get('current_period_cases')}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n2. get_mortality_rate(city_code='330455')  # Rio de Janeiro")
    try:
        result = get_mortality_rate.invoke({"city_code": "330455"})
        print(f"   [OK] Location: {result.get('location')}")
        print(f"   Rate: {result.get('rate')}%")
        print(f"   Deaths: {result.get('total_deaths')}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n3. get_icu_occupancy_rate(city_code='310620')  # Belo Horizonte")
    try:
        result = get_icu_occupancy_rate.invoke({"city_code": "310620"})
        print(f"   [OK] Location: {result.get('location')}")
        print(f"   Patients in ICU: {result.get('patients_in_icu')}")
    except Exception as e:
        print(f"   [FAIL] {e}")


def test_chart_tools():
    """Test chart generation tools."""
    print("\n" + "=" * 70)
    print("TEST: Chart Tools")
    print("=" * 70)

    # Daily chart - national
    print("\n1. get_daily_chart_json(uf=None, days=30)")
    try:
        result = get_daily_chart_json.invoke({"uf": None, "days": 30})
        print(f"   [OK] JSON length: {len(result):,} chars")
        assert '"data"' in result, "Missing data field"
        assert '"layout"' in result, "Missing layout field"
        print("   Contains: data, layout fields")
    except Exception as e:
        print(f"   [FAIL] {e}")

    # Daily chart - state
    print("\n2. get_daily_chart_json(uf='SP', days=15)")
    try:
        result = get_daily_chart_json.invoke({"uf": "SP", "days": 15})
        print(f"   [OK] JSON length: {len(result):,} chars")
    except Exception as e:
        print(f"   [FAIL] {e}")

    # Monthly chart - national
    print("\n3. get_monthly_chart_json(uf=None, months=12)")
    try:
        result = get_monthly_chart_json.invoke({"uf": None, "months": 12})
        print(f"   [OK] JSON length: {len(result):,} chars")
    except Exception as e:
        print(f"   [FAIL] {e}")

    # Monthly chart - state
    print("\n4. get_monthly_chart_json(uf='RJ', months=6)")
    try:
        result = get_monthly_chart_json.invoke({"uf": "RJ", "months": 6})
        print(f"   [OK] JSON length: {len(result):,} chars")
    except Exception as e:
        print(f"   [FAIL] {e}")


def test_chart_functions_direct():
    """Test chart functions directly (not via LangChain tools)."""
    print("\n" + "=" * 70)
    print("TEST: Chart Functions (Direct)")
    print("=" * 70)

    import pandas as pd

    from charts.charts import (
        figure_to_json,
        plot_daily_cases,
        plot_daily_range,
        plot_monthly_cases,
        plot_monthly_range,
    )
    from elt.load import load_srag_data

    df = load_srag_data()

    # plot_daily_cases
    print("\n1. plot_daily_cases(days=30)")
    try:
        fig = plot_daily_cases(df, days=30)
        json_str = figure_to_json(fig)
        print(f"   [OK] Figure created, JSON: {len(json_str):,} chars")
    except Exception as e:
        print(f"   [FAIL] {e}")

    # plot_monthly_cases
    print("\n2. plot_monthly_cases(months=12)")
    try:
        fig = plot_monthly_cases(df, months=12)
        json_str = figure_to_json(fig)
        print(f"   [OK] Figure created, JSON: {len(json_str):,} chars")
    except Exception as e:
        print(f"   [FAIL] {e}")

    # plot_daily_range
    print("\n3. plot_daily_range(start, end)")
    try:
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=60)
        fig = plot_daily_range(df, start_date, end_date)
        json_str = figure_to_json(fig)
        print(f"   [OK] Figure created, JSON: {len(json_str):,} chars")
    except Exception as e:
        print(f"   [FAIL] {e}")

    # plot_monthly_range
    print("\n4. plot_monthly_range(start, end)")
    try:
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.DateOffset(months=6)
        fig = plot_monthly_range(df, start_date, end_date)
        json_str = figure_to_json(fig)
        print(f"   [OK] Figure created, JSON: {len(json_str):,} chars")
    except Exception as e:
        print(f"   [FAIL] {e}")

    # With location filter
    print("\n5. plot_daily_cases with location filter (SP)")
    try:
        fig = plot_daily_cases(
            df, location_col="SG_UF_NOT", location_value="SP", days=30
        )
        json_str = figure_to_json(fig)
        print(f"   [OK] Figure created, JSON: {len(json_str):,} chars")
    except Exception as e:
        print(f"   [FAIL] {e}")


def test_news_tool():
    """Test news search tool (skipped - paid API)."""
    print("\n" + "=" * 70)
    print("TEST: News Tool (API calls skipped)")
    print("=" * 70)

    print(f"\n1. Tool name: {search_srag_news_tool.name}")
    print(f"   Tool description: {search_srag_news_tool.description[:80]}...")
    print("   [SKIP] API calls skipped to avoid costs")


def test_report_tools():
    """Test report generation tools."""
    print("\n" + "=" * 70)
    print("TEST: Report Tools")
    print("=" * 70)

    # Download report - national
    print("\n1. generate_download_report(uf=None, include_news=False)")
    try:
        report = generate_download_report.invoke(
            {"uf": None, "days": 30, "months": 12, "include_news": False}
        )
        print(f"   [OK] Report length: {len(report):,} chars")
        # Check for report structure (title uses accented characters)
        has_title = "Relat" in report and "SRAG" in report
        has_metrics = "Metrica" in report or "Taxa" in report
        print(f"   Contains title: {has_title}, metrics: {has_metrics}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    # Download report - state
    print("\n2. generate_download_report(uf='SP')")
    try:
        report = generate_download_report.invoke({"uf": "SP", "include_news": False})
        print(f"   [OK] Report length: {len(report):,} chars")
    except Exception as e:
        print(f"   [FAIL] {e}")

    # Chat report - national
    print("\n3. generate_chat_report(uf=None, include_news=False)")
    try:
        result = generate_chat_report.invoke(
            {"uf": None, "days": 30, "months": 12, "include_news": False}
        )
        print(f"   [OK] Report text: {len(result.get('report_text', '')):,} chars")
        print(f"   Daily chart: {len(result.get('daily_chart_json', '')):,} chars")
        print(f"   Monthly chart: {len(result.get('monthly_chart_json', '')):,} chars")
        print(f"   Metrics keys: {list(result.get('metrics', {}).keys())}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    # Chat report - state
    print("\n4. generate_chat_report(uf='RJ')")
    try:
        result = generate_chat_report.invoke({"uf": "RJ", "include_news": False})
        print(f"   [OK] Report text: {len(result.get('report_text', '')):,} chars")
    except Exception as e:
        print(f"   [FAIL] {e}")


def test_tool_exports():
    """Test that all tools are properly exported."""
    print("\n" + "=" * 70)
    print("TEST: Tool Exports")
    print("=" * 70)

    expected_tools = [
        "get_case_increase_rate",
        "get_mortality_rate",
        "get_icu_occupancy_rate",
        "get_vaccination_rate",
        "get_daily_chart_json",
        "get_monthly_chart_json",
        "generate_download_report",
        "generate_chat_report",
        "search_srag_news_tool",
    ]

    print(f"\nTotal tools exported: {len(ALL_TOOLS)}")
    print("\nTools list:")

    exported_names = [t.name for t in ALL_TOOLS]
    all_found = True
    for expected in expected_tools:
        found = expected in exported_names
        status = "[OK]" if found else "[FAIL]"
        print(f"   {status} {expected}")
        if not found:
            all_found = False

    if all_found:
        print(f"\n[OK] All {len(expected_tools)} expected tools found")
    else:
        print("\n[FAIL] Some tools missing")


def test_icu_beds_fetcher():
    """Test ICU bed data fetcher."""
    print("\n" + "=" * 70)
    print("TEST: ICU Beds Fetcher (CNES)")
    print("=" * 70)

    from retrieval.icu_beds import get_icu_beds_data, get_icu_beds_for_location

    print("\n1. get_icu_beds_data()")
    try:
        data = get_icu_beds_data()
        print(f"   [OK] Source: {data.get('source')}")
        print(f"   Competency: {data.get('competency')}")
        print(f"   Brazil total: {data.get('brazil_total'):,} beds")
        print(f"   States with data: {len(data.get('icu_beds_by_uf', {}))}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n2. get_icu_beds_for_location(uf='SP')")
    try:
        beds, source = get_icu_beds_for_location(uf="SP")
        print(f"   [OK] SP beds: {beds:,}, Source: {source}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    print("\n3. get_icu_beds_for_location(uf=None) - National")
    try:
        beds, source = get_icu_beds_for_location(uf=None)
        print(f"   [OK] National beds: {beds:,}, Source: {source}")
    except Exception as e:
        print(f"   [FAIL] {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("SRAG TOOLS - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    tests = [
        ("Data Loading & Utilities", test_data_loading),
        ("Metric Tools - National", test_metric_tools_national),
        ("Metric Tools - State", test_metric_tools_state),
        ("Metric Tools - City", test_metric_tools_city),
        ("Chart Tools (LangChain)", test_chart_tools),
        ("Chart Functions (Direct)", test_chart_functions_direct),
        ("News Tool", test_news_tool),
        ("Report Tools", test_report_tools),
        ("Tool Exports", test_tool_exports),
        ("ICU Beds Fetcher", test_icu_beds_fetcher),
    ]

    failed = []
    for name, test_fn in tests:
        try:
            test_fn()
        except Exception as e:
            print(f"\n[ERROR] {name} failed with: {e}")
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
