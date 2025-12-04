"""Chart tools for SRAG data visualization."""

from typing import Annotated

from langchain_core.tools import tool

from charts.charts import figure_to_json, plot_daily_cases, plot_monthly_cases
from elt.load import load_srag_data
from tools.location_utils import determine_location_filter


@tool
def get_daily_chart_json(
    uf: Annotated[str | None, "State code (e.g., 'SP'). None for national."] = None,
    days: Annotated[int, "Days to display (default: 30)."] = 30,
) -> str:
    """Generate daily SRAG cases chart as JSON. Use for daily trends, recent progression."""
    df = load_srag_data()
    location_col, location_value = determine_location_filter(uf, None)
    fig = plot_daily_cases(
        df, location_col=location_col, location_value=location_value, days=days
    )
    return figure_to_json(fig)


@tool
def get_monthly_chart_json(
    uf: Annotated[str | None, "State code (e.g., 'SP'). None for national."] = None,
    months: Annotated[int, "Months to display (default: 12)."] = 12,
) -> str:
    """Generate monthly SRAG cases chart as JSON. Use for long-term trends."""
    df = load_srag_data()
    location_col, location_value = determine_location_filter(uf, None)
    fig = plot_monthly_cases(
        df, location_col=location_col, location_value=location_value, months=months
    )
    return figure_to_json(fig)
