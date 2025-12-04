"""
Test file for all tools modules.

This file will be deleted later - it's only for development testing.
"""

import sys
from pathlib import Path

# Add src to path for direct execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from agent.tools.charts import get_daily_chart_json, get_monthly_chart_json
from agent.tools.metrics import (
    get_case_increase_rate,
    get_icu_occupancy_rate,
    get_mortality_rate,
    get_vaccination_rate,
)
from agent.tools.news import search_srag_news_tool
from agent.tools.reports import (
    generate_full_report_for_chat,
    generate_full_report_for_download,
)

from agent.tools import get_tools


def test_helpers() -> None:
    """Test helper functions."""
    print("=" * 60)
    print("Test: Helper Functions")
    print("=" * 60)

    from agent.tools.helpers import (
        determine_location_filter,
        get_location_description,
        load_srag_data,
    )

    # Test data loading
    print("\n1. Testing load_srag_data()...")
    try:
        df = load_srag_data()
        print(f"   ✅ Loaded {len(df):,} rows")
        print(f"   Columns: {len(df.columns)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test location filter
    print("\n2. Testing determine_location_filter()...")
    col, val = determine_location_filter("SP", None)
    print(f"   UF='SP' → ({col}, {val})")
    col, val = determine_location_filter(None, "3550308")
    print(f"   city_code='3550308' → ({col}, {val})")
    col, val = determine_location_filter(None, None)
    print(f"   None → ({col}, {val})")

    # Test location description
    print("\n3. Testing get_location_description()...")
    desc = get_location_description("SP", None)
    print(f"   UF='SP' → '{desc}'")
    desc = get_location_description(None, "3550308")
    print(f"   city_code='3550308' → '{desc}'")
    desc = get_location_description(None, None)
    print(f"   None → '{desc}'")


def test_metric_tools() -> None:
    """Test individual metric tools."""
    print("\n" + "=" * 60)
    print("Test: Individual Metric Tools")
    print("=" * 60)

    # Test case increase rate
    print("\n1. Testing get_case_increase_rate()...")
    try:
        result = get_case_increase_rate.invoke({"uf": "SP", "period_days": 7})
        print(f"   ✅ Location: {result.get('location')}")
        print(f"   Rate: {result.get('rate')}%")
        print(f"   Current cases: {result.get('current_period_cases')}")
        print(f"   Previous cases: {result.get('previous_period_cases')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test mortality rate
    print("\n2. Testing get_mortality_rate()...")
    try:
        result = get_mortality_rate.invoke({"uf": "SP"})
        print(f"   ✅ Location: {result.get('location')}")
        print(f"   Rate: {result.get('rate')}%")
        print(f"   Deaths: {result.get('total_deaths')}")
        print(f"   Total cases: {result.get('total_cases')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test ICU occupancy rate
    print("\n3. Testing get_icu_occupancy_rate()...")
    try:
        result = get_icu_occupancy_rate.invoke({"uf": "SP"})
        print(f"   ✅ Location: {result.get('location')}")
        print(f"   Occupancy rate: {result.get('occupancy_rate')}%")
        print(f"   Patients in ICU: {result.get('patients_in_icu')}")
        print(f"   Total beds: {result.get('total_icu_beds')}")
        print(f"   Data source: {result.get('data_source')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test vaccination rate
    print("\n4. Testing get_vaccination_rate()...")
    try:
        result = get_vaccination_rate.invoke({"uf": "SP", "vaccine_type": "both"})
        print(f"   ✅ Location: {result.get('location')}")
        print(f"   COVID rate: {result.get('covid_rate')}%")
        print(f"   Flu rate: {result.get('flu_rate')}%")
        print(f"   COVID vaccinated: {result.get('covid_vaccinated')}")
        print(f"   Flu vaccinated: {result.get('flu_vaccinated')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def test_chart_tools() -> None:
    """Test individual chart tools."""
    print("\n" + "=" * 60)
    print("Test: Individual Chart Tools")
    print("=" * 60)

    # Test daily chart
    print("\n1. Testing get_daily_chart_json()...")
    try:
        chart_json = get_daily_chart_json.invoke({"uf": "SP", "days": 30})
        print(f"   ✅ Chart JSON length: {len(chart_json):,} characters")
        print(f"   First 100 chars: {chart_json[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test monthly chart
    print("\n2. Testing get_monthly_chart_json()...")
    try:
        chart_json = get_monthly_chart_json.invoke({"uf": "SP", "months": 12})
        print(f"   ✅ Chart JSON length: {len(chart_json):,} characters")
        print(f"   First 100 chars: {chart_json[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def test_news_tool() -> None:
    """Test news search tool (skipped - API calls are paid)."""
    print("\n" + "=" * 60)
    print("Test: News Search Tool")
    print("=" * 60)

    print("\n1. Testing search_srag_news_tool()...")
    print(
        "   ⚠️  Skipped - Tavily API calls are paid. Tool is available but not executed."
    )
    print(f"   ✅ Tool name: {search_srag_news_tool.name}")
    print(f"   ✅ Tool description: {search_srag_news_tool.description[:80]}...")


def test_report_tools() -> None:
    """Test report generation tools."""
    print("\n" + "=" * 60)
    print("Test: Report Generation Tools")
    print("=" * 60)

    # Test download report (without news to avoid API costs)
    print("\n1. Testing generate_full_report_for_download()...")
    try:
        report = generate_full_report_for_download.invoke(
            {"uf": "SP", "days": 30, "months": 12, "include_news": False}
        )
        print(f"   ✅ Report length: {len(report):,} characters")
        print(f"   First 500 chars:\n{report[:500]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test chat report (without news to avoid API costs)
    print("\n2. Testing generate_full_report_for_chat()...")
    try:
        report_dict = generate_full_report_for_chat.invoke(
            {"uf": "SP", "days": 30, "months": 12, "include_news": False}
        )
        print(
            f"   ✅ Report text length: {len(report_dict.get('report_text', '')):,} chars"
        )
        print(
            f"   Daily chart JSON length: {len(report_dict.get('daily_chart_json', '')):,} chars"
        )
        print(
            f"   Monthly chart JSON length: {len(report_dict.get('monthly_chart_json', '')):,} chars"
        )
        print(
            f"   News articles: {len(report_dict.get('news', []))} (skipped - API is paid)"
        )
        print(
            f"\n   Report text preview:\n{report_dict.get('report_text', '')[:300]}..."
        )
    except Exception as e:
        print(f"   ❌ Error: {e}")


def test_all_tools_export() -> None:
    """Test that all tools are properly exported."""
    print("\n" + "=" * 60)
    print("Test: Tools Export")
    print("=" * 60)

    tools = get_tools()
    print(f"\n✅ Total tools exported: {len(tools)}")
    print("\nTools list:")
    for i, tool in enumerate(tools, 1):
        print(f"   {i}. {tool.name}")


def test_national_data() -> None:
    """Test tools with national data (no UF filter)."""
    print("\n" + "=" * 60)
    print("Test: National Data (All States)")
    print("=" * 60)

    print("\n1. Testing metrics with national data...")
    try:
        result = get_mortality_rate.invoke({"uf": None})
        print(f"   ✅ National mortality rate: {result.get('rate')}%")
        print(f"   Total deaths: {result.get('total_deaths'):,}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n2. Testing charts with national data...")
    try:
        chart_json = get_daily_chart_json.invoke({"uf": None, "days": 30})
        print(f"   ✅ National daily chart JSON length: {len(chart_json):,} chars")
    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SRAG AGENT TOOLS TEST SUITE")
    print("=" * 60)

    try:
        # Run all tests
        test_helpers()
        test_metric_tools()
        test_chart_tools()
        test_news_tool()
        test_report_tools()
        test_all_tools_export()
        test_national_data()

        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
