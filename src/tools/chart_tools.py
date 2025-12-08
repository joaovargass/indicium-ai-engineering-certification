"""Chart tools for SRAG data visualization."""

from typing import Annotated

from langchain_core.tools import tool

from charts.charts import figure_to_json, plot_daily_cases, plot_monthly_cases
from elt.load import load_srag_data
from tools.location_utils import determine_location_filter


@tool
def get_daily_chart_json(
    uf: Annotated[str | None, "State code (e.g., 'SP'). None for national."] = None,
    city_code: Annotated[str | None, "IBGE city code. Overrides UF."] = None,
    days: Annotated[int, "Days to display (default: 30)."] = 30,
    title: Annotated[str | None, "Chart title in user's language (e.g., 'Daily Cases' or 'Casos Diários')."] = None,
    x_axis_label: Annotated[str | None, "X-axis label in user's language (e.g., 'Date' or 'Data')."] = None,
    y_axis_label: Annotated[str | None, "Y-axis label in user's language (e.g., 'Number of Cases' or 'Número de Casos')."] = None,
) -> str:
    """Generate daily SRAG cases chart as JSON. Use for daily trends, recent progression. Provide title and axis labels in the user's language."""
    df = load_srag_data()
    location_col, location_value = determine_location_filter(uf, city_code)
    fig = plot_daily_cases(
        df, location_col=location_col, location_value=location_value, days=days,
        title=title, x_axis_label=x_axis_label, y_axis_label=y_axis_label
    )
    return figure_to_json(fig)


@tool
def get_monthly_chart_json(
    uf: Annotated[str | None, "State code (e.g., 'SP'). None for national."] = None,
    city_code: Annotated[str | None, "IBGE city code. Overrides UF."] = None,
    months: Annotated[int, "Months to display (default: 12)."] = 12,
    title: Annotated[str | None, "Chart title in user's language (e.g., 'Monthly Cases' or 'Casos Mensais')."] = None,
    x_axis_label: Annotated[str | None, "X-axis label in user's language (e.g., 'Month' or 'Mês')."] = None,
    y_axis_label: Annotated[str | None, "Y-axis label in user's language (e.g., 'Number of Cases' or 'Número de Casos')."] = None,
) -> str:
    """Generate monthly SRAG cases chart as JSON. Use for long-term trends. Provide title and axis labels in the user's language."""
    df = load_srag_data()
    location_col, location_value = determine_location_filter(uf, city_code)
    fig = plot_monthly_cases(
        df, location_col=location_col, location_value=location_value, months=months,
        title=title, x_axis_label=x_axis_label, y_axis_label=y_axis_label
    )
    return figure_to_json(fig)
