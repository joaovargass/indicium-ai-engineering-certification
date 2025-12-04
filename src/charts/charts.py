"""Chart generation module for SRAG data visualization."""

from datetime import timedelta

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

# Professional color palette (colorblind-friendly)
CHART_COLOR = "#2E86AB"


def figure_to_json(fig: Figure) -> str:
    """Convert Plotly Figure to JSON string."""
    return fig.to_json()


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
) -> Figure:
    """
    Create a line chart with standard styling.

    Args:
        data: DataFrame with chart data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Chart title

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
        line=dict(width=3),
        marker=dict(size=7, line=dict(width=1, color="white")),
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Cases: %{y:,.0f}<extra></extra>",
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Cases",
        height=600,
        margin=dict(l=60, r=40, t=80, b=60),
        title_font=dict(size=20),
        font=dict(size=12),
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
) -> Figure:
    """
    Create a bar chart with standard styling.

    Args:
        data: DataFrame with chart data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Chart title

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
        hovertemplate="<b>%{x|%b/%Y}</b><br>Cases: %{y:,.0f}<extra></extra>",
        marker=dict(line=dict(width=0)),
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Cases",
        height=600,
        margin=dict(l=60, r=40, t=80, b=60),
        title_font=dict(size=20),
        font=dict(size=12),
        hovermode="x unified",
        bargap=0.2,
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
                text="No data available",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16),
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
    days: int = 30,
) -> Figure:
    """
    Generate daily cases chart for specified number of days.

    Args:
        df: DataFrame with case data
        date_col: Name of date column (default: "DT_SIN_PRI")
        location_col: Optional location column name (e.g., "SG_UF_NOT")
        location_value: Optional location value to filter
        days: Number of days to display (default: 30)

    Returns:
        Plotly figure object.

    """
    df = _prepare_data(df, date_col, location_col, location_value)

    end_date = df[date_col].max()
    if pd.isna(end_date):
        return _create_empty_chart(f"Daily Cases - Last {days} Days", location_value)

    start_date = end_date - timedelta(days=days)
    df_filtered = _filter_by_date_range(df, date_col, start_date, end_date)

    daily_counts = _aggregate_daily(df_filtered, date_col)
    title = _build_title(f"Daily Cases - Last {days} Days", location_value)

    return _create_line_chart(daily_counts, date_col, "casos", title)


def plot_monthly_cases(
    df: pd.DataFrame,
    date_col: str = "DT_SIN_PRI",
    location_col: str | None = None,
    location_value: str | None = None,
    months: int = 12,
) -> Figure:
    """
    Generate monthly cases chart for specified number of months.

    Args:
        df: DataFrame with case data
        date_col: Name of date column (default: "DT_SIN_PRI")
        location_col: Optional location column name (e.g., "SG_UF_NOT")
        location_value: Optional location value to filter
        months: Number of months to display (default: 12)

    Returns:
        Plotly figure object.

    """
    df = _prepare_data(df, date_col, location_col, location_value)

    end_date = df[date_col].max()
    if pd.isna(end_date):
        return _create_empty_chart(
            f"Monthly Cases - Last {months} Months", location_value
        )

    start_date = end_date - pd.DateOffset(months=months)
    df_filtered = _filter_by_date_range(df, date_col, start_date, end_date)

    monthly_counts = _aggregate_monthly(df_filtered, date_col)
    title = _build_title(f"Monthly Cases - Last {months} Months", location_value)

    return _create_bar_chart(monthly_counts, "ano_mes", "casos", title)


def plot_daily_range(
    df: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    date_col: str = "DT_SIN_PRI",
    location_col: str | None = None,
    location_value: str | None = None,
) -> Figure:
    """
    Generate daily cases chart for a specific date range.

    Args:
        df: DataFrame with case data
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        date_col: Name of date column (default: "DT_SIN_PRI")
        location_col: Optional location column name (e.g., "SG_UF_NOT")
        location_value: Optional location value to filter

    Returns:
        Plotly figure object.

    """
    df = _prepare_data(df, date_col, location_col, location_value)
    df_filtered = _filter_by_date_range(df, date_col, start_date, end_date)

    daily_counts = _aggregate_daily(df_filtered, date_col)
    days = (end_date - start_date).days
    title = _build_title(
        f"Daily Cases - {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')} ({days} days)",
        location_value,
    )

    return _create_line_chart(daily_counts, date_col, "casos", title)


def plot_monthly_range(
    df: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    date_col: str = "DT_SIN_PRI",
    location_col: str | None = None,
    location_value: str | None = None,
) -> Figure:
    """
    Generate monthly cases chart for a specific date range.

    Args:
        df: DataFrame with case data
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        date_col: Name of date column (default: "DT_SIN_PRI")
        location_col: Optional location column name (e.g., "SG_UF_NOT")
        location_value: Optional location value to filter

    Returns:
        Plotly figure object.

    """
    df = _prepare_data(df, date_col, location_col, location_value)
    df_filtered = _filter_by_date_range(df, date_col, start_date, end_date)

    monthly_counts = _aggregate_monthly(df_filtered, date_col)

    month_names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    start_month_name = month_names[start_date.month - 1]
    end_month_name = month_names[end_date.month - 1]

    title = _build_title(
        f"Monthly Cases - {start_month_name}/{start_date.year} to {end_month_name}/{end_date.year}",
        location_value,
    )

    return _create_bar_chart(monthly_counts, "ano_mes", "casos", title)
