"""Shared statistics helpers for chart data extraction."""

from datetime import timedelta
from typing import Any

import pandas as pd


def prepare_chart_data(
    df: pd.DataFrame,
    date_col: str,
    location_col: str | None,
    location_value: str | None,
) -> pd.DataFrame:
    """
    Prepare and filter data for chart generation.

    Args:
        df: Input DataFrame
        date_col: Name of the date column
        location_col: Name of the location column (optional)
        location_value: Value to filter location by (optional)

    Returns:
        Filtered DataFrame with parsed dates

    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    if location_col and location_value:
        df = df.dropna(subset=[date_col, location_col])
        df = df[df[location_col] == location_value]
    else:
        df = df.dropna(subset=[date_col])

    return df


def calculate_trend(
    counts: pd.DataFrame, value_col: str = "casos"
) -> tuple[str, float]:
    """
    Calculate trend direction and percentage change.

    Compares the average of the first half vs second half of the data.

    Args:
        counts: DataFrame with aggregated counts
        value_col: Name of the column containing values

    Returns:
        Tuple of (trend_direction, trend_percentage)
        - trend_direction: "increasing", "decreasing", or "stable"
        - trend_percentage: Absolute percentage change

    """
    if len(counts) < 2:
        return "stable", 0.0

    mid_point = len(counts) // 2
    if mid_point == 0:
        return "stable", 0.0

    first_half_avg = counts.iloc[:mid_point][value_col].mean()
    second_half_avg = counts.iloc[mid_point:][value_col].mean()

    if second_half_avg > first_half_avg:
        trend_direction = "increasing"
    elif second_half_avg < first_half_avg:
        trend_direction = "decreasing"
    else:
        trend_direction = "stable"

    trend_percentage = (
        abs((second_half_avg - first_half_avg) / first_half_avg * 100)
        if first_half_avg > 0
        else 0.0
    )

    return trend_direction, trend_percentage


def extract_daily_stats(
    df: pd.DataFrame,
    location_col: str | None,
    location_value: str | None,
    days: int,
    date_col: str = "DT_SIN_PRI",
) -> dict[str, Any] | None:
    """
    Extract statistics from daily chart data.

    Args:
        df: Input DataFrame
        location_col: Name of the location column
        location_value: Value to filter location by
        days: Number of days to include
        date_col: Name of the date column

    Returns:
        Dictionary with daily statistics or None if no data

    """
    df = prepare_chart_data(df, date_col, location_col, location_value)

    end_date = df[date_col].max()
    if pd.isna(end_date):
        return None

    start_date = end_date - timedelta(days=days)
    df_filtered = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)].copy()

    daily_counts = df_filtered.groupby(date_col).size().reset_index(name="casos")
    daily_counts = daily_counts.sort_values(date_col)

    if len(daily_counts) == 0:
        return None

    total_cases = daily_counts["casos"].sum()
    avg_daily = daily_counts["casos"].mean()
    max_daily = daily_counts["casos"].max()
    max_date = daily_counts.loc[daily_counts["casos"].idxmax(), date_col]
    min_daily = daily_counts["casos"].min()

    trend_direction, trend_percentage = calculate_trend(daily_counts)

    return {
        "chart_type": "daily",
        "start_date": daily_counts[date_col].min(),
        "end_date": daily_counts[date_col].max(),
        "total_cases": int(total_cases),
        "avg_daily": float(avg_daily),
        "max_daily": int(max_daily),
        "max_date": max_date,
        "min_daily": int(min_daily),
        "trend_direction": trend_direction,
        "trend_percentage": float(trend_percentage),
        "location": location_value or "Brasil (nacional)",
    }


def extract_monthly_stats(
    df: pd.DataFrame,
    location_col: str | None,
    location_value: str | None,
    months: int,
    date_col: str = "DT_SIN_PRI",
) -> dict[str, Any] | None:
    """
    Extract statistics from monthly chart data.

    Args:
        df: Input DataFrame
        location_col: Name of the location column
        location_value: Value to filter location by
        months: Number of months to include
        date_col: Name of the date column

    Returns:
        Dictionary with monthly statistics or None if no data

    """
    df = prepare_chart_data(df, date_col, location_col, location_value)

    end_date = df[date_col].max()
    if pd.isna(end_date):
        return None

    data_min_date = df[date_col].min()
    desired_start_date = end_date - pd.DateOffset(months=months)
    start_date = max(desired_start_date, data_min_date)

    df_filtered = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)].copy()

    df_filtered["ano_mes"] = df_filtered[date_col].dt.to_period("M")
    monthly_counts = df_filtered.groupby("ano_mes").size().reset_index(name="casos")
    monthly_counts["ano_mes"] = monthly_counts["ano_mes"].dt.to_timestamp()
    monthly_counts = monthly_counts.sort_values("ano_mes")

    if len(monthly_counts) == 0:
        return None

    total_cases = monthly_counts["casos"].sum()
    avg_monthly = monthly_counts["casos"].mean()
    max_monthly = monthly_counts["casos"].max()
    max_date = monthly_counts.loc[monthly_counts["casos"].idxmax(), "ano_mes"]
    min_monthly = monthly_counts["casos"].min()

    trend_direction, trend_percentage = calculate_trend(monthly_counts)

    # Check if period was limited by available data
    actual_months = len(monthly_counts)
    period_limited = actual_months < months or start_date > desired_start_date

    result = {
        "chart_type": "monthly",
        "start_date": monthly_counts["ano_mes"].min(),
        "end_date": monthly_counts["ano_mes"].max(),
        "total_cases": int(total_cases),
        "avg_monthly": float(avg_monthly),
        "max_monthly": int(max_monthly),
        "max_date": max_date,
        "min_monthly": int(min_monthly),
        "trend_direction": trend_direction,
        "trend_percentage": float(trend_percentage),
        "location": location_value or "Brasil (nacional)",
    }

    if period_limited:
        result["period_limited_by_data"] = True
        result["requested_months"] = months
        result["actual_months"] = actual_months
        result["data_max_date"] = (
            end_date.isoformat() if hasattr(end_date, "isoformat") else str(end_date)
        )
        result["data_min_date"] = (
            data_min_date.isoformat()
            if hasattr(data_min_date, "isoformat")
            else str(data_min_date)
        )

    return result
