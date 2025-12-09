"""
Chart rendering for UI display.

This module bridges agent tool calls to actual Plotly figure generation.
It handles:
- Converting tool call arguments to chart parameters
- Loading data and applying filters
- Generating figures with metadata for agent context

Used by response_parsing.py to render charts from tool outputs.

"""

import pandas as pd
from plotly.graph_objects import Figure

from common.config import DEFAULT_DAYS, DEFAULT_MONTHS
from elt.load import load_srag_data
from tools.location_utils import determine_location_filter
from ui.chart_data import (
    aggregate_daily,
    aggregate_monthly,
    build_daily_metadata,
    build_monthly_metadata,
    filter_by_days,
    filter_by_months,
    prepare_dataframe,
)


def render_tool_chart(
    tool_name: str, tool_args: dict
) -> tuple[Figure | None, dict | None]:
    """
    Generate a Plotly Figure from a chart tool call.

    Args:
        tool_name: Name of the chart tool (get_daily_chart_json or get_monthly_chart_json)
        tool_args: Tool arguments dict with uf, city_code, days/months, title, labels

    Returns:
        Tuple of (Figure, metadata_dict) or (None, None) on error

    """
    try:
        df = load_srag_data()
        location_col, location_value = determine_location_filter(
            tool_args.get("uf"), tool_args.get("city_code")
        )
        title = tool_args.get("title")
        x_label = tool_args.get("x_axis_label")
        y_label = tool_args.get("y_axis_label")

        if tool_name == "get_daily_chart_json":
            return render_daily_chart(
                df,
                location_col,
                location_value,
                tool_args.get("days", DEFAULT_DAYS),
                title,
                x_label,
                y_label,
            )
        elif tool_name == "get_monthly_chart_json":
            return render_monthly_chart(
                df,
                location_col,
                location_value,
                tool_args.get("months", DEFAULT_MONTHS),
                title,
                x_label,
                y_label,
            )
    except Exception as e:
        print(f"Warning: Chart generation failed for {tool_name}: {e}")
    return None, None


def render_daily_chart(
    df: pd.DataFrame,
    location_col: str | None,
    location_value: str | None,
    days: int,
    title: str | None,
    x_label: str | None,
    y_label: str | None,
) -> tuple[Figure, dict | None]:
    """
    Render daily cases line chart with metadata.

    Args:
        df: DataFrame with SRAG data
        location_col: Column name for location filter
        location_value: Value to filter by
        days: Number of days to show
        title: Custom chart title
        x_label: Custom x-axis label
        y_label: Custom y-axis label

    Returns:
        Tuple of (Figure, metadata_dict) - metadata may be None if no data

    """
    from charts.charts import _build_title, _create_empty_chart, _create_line_chart

    date_col = "DT_SIN_PRI"
    df = prepare_dataframe(df, date_col, location_col, location_value)

    if df.empty or pd.isna(df[date_col].max()):
        default_title = title or f"Casos Diários - Últimos {days} Dias"
        return _create_empty_chart(default_title, location_value), None

    df_filtered = filter_by_days(df, date_col, days)
    counts = aggregate_daily(df_filtered, date_col)

    if len(counts) == 0:
        default_title = title or f"Casos Diários - Últimos {days} Dias"
        return _create_empty_chart(default_title, location_value), None

    chart_title = _build_title(
        title or f"Casos Diários - Últimos {days} Dias", location_value
    )
    fig = _create_line_chart(counts, date_col, "casos", chart_title, x_label, y_label)
    metadata = build_daily_metadata(counts, date_col, location_value)

    return fig, metadata


def render_monthly_chart(
    df: pd.DataFrame,
    location_col: str | None,
    location_value: str | None,
    months: int,
    title: str | None,
    x_label: str | None,
    y_label: str | None,
) -> tuple[Figure, dict | None]:
    """
    Render monthly cases bar chart with metadata.

    Args:
        df: DataFrame with SRAG data
        location_col: Column name for location filter
        location_value: Value to filter by
        months: Number of months to show
        title: Custom chart title
        x_label: Custom x-axis label
        y_label: Custom y-axis label

    Returns:
        Tuple of (Figure, metadata_dict) - metadata may be None if no data

    """
    from charts.charts import _build_title, _create_bar_chart, _create_empty_chart

    date_col = "DT_SIN_PRI"
    df = prepare_dataframe(df, date_col, location_col, location_value)

    if df.empty or pd.isna(df[date_col].max()):
        default_title = title or f"Casos Mensais - Últimos {months} Meses"
        return _create_empty_chart(default_title, location_value), None

    end_date = df[date_col].max()
    min_date = df[date_col].min()
    df_filtered, is_limited, actual_months = filter_by_months(df, date_col, months)
    counts = aggregate_monthly(df_filtered, date_col)

    if len(counts) == 0:
        default_title = title or f"Casos Mensais - Últimos {months} Meses"
        return _create_empty_chart(default_title, location_value), None

    chart_title = _build_title(
        title or f"Casos Mensais - Últimos {months} Meses", location_value
    )
    fig = _create_bar_chart(counts, "ano_mes", "casos", chart_title, x_label, y_label)
    metadata = build_monthly_metadata(
        counts, location_value, is_limited, months, actual_months, end_date, min_date
    )

    return fig, metadata
