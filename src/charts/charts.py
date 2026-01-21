"""Chart generation module for SRAG data visualization."""

from datetime import timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.io as pio
from plotly.graph_objects import Figure

from common.config import (
    CHART_ANNOTATION_FONT_SIZE,
    CHART_BAR_GAP,
    CHART_COLOR,
    CHART_FONT_SIZE,
    CHART_LINE_WIDTH,
    CHART_MARGIN,
    CHART_MARKER_SIZE,
    CHART_TITLE_FONT_SIZE,
    DEFAULT_CHART_HEIGHT,
    DEFAULT_CHART_WIDTH,
    DEFAULT_DAYS,
    DEFAULT_MONTHS,
)
from common.logging import logger


def figure_to_json(fig: Figure) -> str:
    """Convert Plotly Figure to JSON string."""
    return fig.to_json()


def figure_to_image_file(
    fig: Figure,
    file_path: Path,
    width: int = DEFAULT_CHART_WIDTH,
    height: int = DEFAULT_CHART_HEIGHT,
) -> Path:
    """
    Save Plotly figure as PNG image file.

    Args:
        fig: Plotly Figure object
        file_path: Path where to save the image
        width: Image width in pixels (default: 1200)
        height: Image height in pixels (default: 600)

    Returns:
        Path to saved image file

    """
    try:
        pio.write_image(fig, str(file_path), format="png", width=width, height=height)
    except Exception as e:
        logger.warning("Failed to export chart as PNG: %s", e)
        raise RuntimeError(
            "Failed to export chart as PNG. Ensure 'kaleido' is installed "
            "(pip install kaleido) and system dependencies are correct."
        ) from e
    return file_path


def _prepare_data(
    df: pd.DataFrame,
    date_col: str,
    location_col: str | None = None,
    location_value: str | None = None,
) -> pd.DataFrame:
    """
    Prepare and filter data for charting.

    Args:
        df: DataFrame with case data
        date_col: Name of date column
        location_col: Optional location column name
        location_value: Optional location value to filter

    Returns:
        Filtered DataFrame with date column converted to datetime.

    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    if location_col and location_value:
        df = df.dropna(subset=[date_col, location_col])
        df = df[df[location_col] == location_value]
    else:
        df = df.dropna(subset=[date_col])

    return df


def _filter_by_date_range(
    df: pd.DataFrame,
    date_col: str,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    """
    Filter DataFrame by date range.

    Args:
        df: DataFrame with date column
        date_col: Name of date column
        start_date: Start date (inclusive)
        end_date: End date (inclusive)

    Returns:
        Filtered DataFrame.

    """
    return df[(df[date_col] >= start_date) & (df[date_col] <= end_date)].copy()


def _aggregate_daily(
    df: pd.DataFrame,
    date_col: str,
) -> pd.DataFrame:
    """
    Aggregate data by day.

    Args:
        df: DataFrame with date column
        date_col: Name of date column

    Returns:
        DataFrame with daily counts.

    """
    daily_counts = df.groupby(date_col).size().reset_index(name="casos")
    return daily_counts.sort_values(date_col)


def _aggregate_monthly(
    df: pd.DataFrame,
    date_col: str,
) -> pd.DataFrame:
    """
    Aggregate data by month.

    Args:
        df: DataFrame with date column
        date_col: Name of date column

    Returns:
        DataFrame with monthly counts.

    """
    df = df.copy()
    df["ano_mes"] = df[date_col].dt.to_period("M")
    monthly_counts = df.groupby("ano_mes").size().reset_index(name="casos")
    monthly_counts["ano_mes"] = monthly_counts["ano_mes"].dt.to_timestamp()
    return monthly_counts.sort_values("ano_mes")


def _create_line_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    x_axis_label: str | None = None,
    y_axis_label: str | None = None,
) -> Figure:
    """
    Create a line chart with standard styling.

    Args:
        data: DataFrame with chart data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Chart title
        x_axis_label: Optional custom x-axis label
        y_axis_label: Optional custom y-axis label

    Returns:
        Plotly figure object.

    """
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
        color_discrete_sequence=[CHART_COLOR],
        template="plotly_white",
        title=title,
    )

    fig.update_traces(
        line=dict(width=CHART_LINE_WIDTH),
        marker=dict(size=CHART_MARKER_SIZE, line=dict(width=1, color="white")),
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>%{y:,.0f}<extra></extra>",
    )

    fig.update_layout(
        xaxis_title=x_axis_label or "Data",
        yaxis_title=y_axis_label or "Número de Casos",
        height=DEFAULT_CHART_HEIGHT,
        margin=CHART_MARGIN,
        title_font=dict(size=CHART_TITLE_FONT_SIZE),
        font=dict(size=CHART_FONT_SIZE),
        hovermode="x unified",
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
            tickformat="%d/%m",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
            tickformat=",.0f",
        ),
    )

    return fig


def _create_bar_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    x_axis_label: str | None = None,
    y_axis_label: str | None = None,
) -> Figure:
    """
    Create a bar chart with standard styling.

    Args:
        data: DataFrame with chart data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Chart title
        x_axis_label: Optional custom x-axis label
        y_axis_label: Optional custom y-axis label

    Returns:
        Plotly figure object.

    """
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        color_discrete_sequence=[CHART_COLOR],
        template="plotly_white",
        title=title,
    )

    fig.update_traces(
        hovertemplate="<b>%{x|%b/%Y}</b><br>%{y:,.0f}<extra></extra>",
        marker=dict(line=dict(width=0)),
    )

    fig.update_layout(
        xaxis_title=x_axis_label or "Mês",
        yaxis_title=y_axis_label or "Número de Casos",
        height=DEFAULT_CHART_HEIGHT,
        margin=CHART_MARGIN,
        title_font=dict(size=CHART_TITLE_FONT_SIZE),
        font=dict(size=CHART_FONT_SIZE),
        hovermode="x unified",
        bargap=CHART_BAR_GAP,
        xaxis=dict(
            showgrid=False,
            tickformat="%b/%Y",
            tickangle=-45,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
            tickformat=",.0f",
        ),
    )

    return fig


def _create_empty_chart(base_title: str, location_value: str | None = None) -> Figure:
    """Create empty chart with 'no data' message."""
    fig = Figure()
    title = _build_title(base_title, location_value)
    fig.update_layout(
        title=title,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[
            dict(
                text="Dados não disponíveis",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=CHART_ANNOTATION_FONT_SIZE),
            )
        ],
    )
    return fig


def _build_title(
    base_title: str,
    location_value: str | None = None,
) -> str:
    """
    Build chart title with optional location suffix.

    Args:
        base_title: Base title text
        location_value: Optional location value to append

    Returns:
        Complete title string.

    """
    if location_value:
        return f"{base_title} - {location_value}"
    return base_title


def plot_daily_cases(
    df: pd.DataFrame,
    date_col: str = "DT_SIN_PRI",
    location_col: str | None = None,
    location_value: str | None = None,
    days: int = DEFAULT_DAYS,
    title: str | None = None,
    x_axis_label: str | None = None,
    y_axis_label: str | None = None,
) -> Figure:
    """
    Generate daily cases chart for specified number of days.

    Args:
        df: DataFrame with case data
        date_col: Name of date column (default: "DT_SIN_PRI")
        location_col: Optional location column name (e.g., "SG_UF_NOT")
        location_value: Optional location value to filter
        days: Number of days to display (default: 30)
        title: Optional custom chart title
        x_axis_label: Optional custom x-axis label
        y_axis_label: Optional custom y-axis label

    Returns:
        Plotly figure object.

    """
    df = _prepare_data(df, date_col, location_col, location_value)

    end_date = df[date_col].max()
    if pd.isna(end_date):
        default_title = title or f"Casos Diários - Últimos {days} Dias"
        return _create_empty_chart(default_title, location_value)

    start_date = end_date - timedelta(days=days)
    df_filtered = _filter_by_date_range(df, date_col, start_date, end_date)

    daily_counts = _aggregate_daily(df_filtered, date_col)
    chart_title = title or f"Casos Diários - Últimos {days} Dias"
    chart_title = _build_title(chart_title, location_value)

    return _create_line_chart(
        daily_counts, date_col, "casos", chart_title, x_axis_label, y_axis_label
    )


def plot_monthly_cases(
    df: pd.DataFrame,
    date_col: str = "DT_SIN_PRI",
    location_col: str | None = None,
    location_value: str | None = None,
    months: int = DEFAULT_MONTHS,
    title: str | None = None,
    x_axis_label: str | None = None,
    y_axis_label: str | None = None,
) -> Figure:
    """
    Generate monthly cases chart for specified number of months.

    Args:
        df: DataFrame with case data
        date_col: Name of date column (default: "DT_SIN_PRI")
        location_col: Optional location column name (e.g., "SG_UF_NOT")
        location_value: Optional location value to filter
        months: Number of months to display (default: 12)
        title: Optional custom chart title
        x_axis_label: Optional custom x-axis label
        y_axis_label: Optional custom y-axis label

    Returns:
        Plotly figure object.

    """
    df = _prepare_data(df, date_col, location_col, location_value)

    end_date = df[date_col].max()
    if pd.isna(end_date):
        default_title = title or f"Casos Mensais - Últimos {months} Meses"
        return _create_empty_chart(default_title, location_value)

    data_min_date = df[date_col].min()
    desired_start_date = end_date - pd.DateOffset(months=months)
    start_date = max(desired_start_date, data_min_date)

    df_filtered = _filter_by_date_range(df, date_col, start_date, end_date)

    monthly_counts = _aggregate_monthly(df_filtered, date_col)
    chart_title = title or f"Casos Mensais - Últimos {months} Meses"
    chart_title = _build_title(chart_title, location_value)

    return _create_bar_chart(
        monthly_counts, "ano_mes", "casos", chart_title, x_axis_label, y_axis_label
    )
