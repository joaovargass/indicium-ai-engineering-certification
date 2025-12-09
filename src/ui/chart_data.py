"""
Chart data preparation and statistics calculation for UI.

This module provides UI-specific utilities for chart data handling.
Core data preparation functions are imported from charts.stats to avoid duplication.
"""

from datetime import datetime, timedelta

import pandas as pd

from charts.stats import calculate_trend, prepare_chart_data

# Re-export prepare_chart_data as prepare_dataframe for backward compatibility
prepare_dataframe = prepare_chart_data


def to_datetime(value: object) -> datetime | None:
    """
    Convert various date types to Python datetime.

    Args:
        value: Date value (pd.Timestamp, datetime, string, or None)

    Returns:
        Python datetime object or None if conversion fails

    """
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    if isinstance(value, datetime):
        return value
    try:
        return pd.to_datetime(value).to_pydatetime()
    except (ValueError, TypeError):
        return None


def filter_by_days(df: pd.DataFrame, date_col: str, days: int) -> pd.DataFrame:
    """
    Filter dataframe to last N days from the maximum date.

    Args:
        df: DataFrame with date column
        date_col: Name of date column
        days: Number of days to include

    Returns:
        Filtered DataFrame

    """
    end_date = df[date_col].max()
    if pd.isna(end_date):
        return df
    start_date = end_date - timedelta(days=days)
    return df[(df[date_col] >= start_date) & (df[date_col] <= end_date)].copy()


def filter_by_months(
    df: pd.DataFrame, date_col: str, months: int
) -> tuple[pd.DataFrame, bool, int]:
    """
    Filter dataframe to last N months from maximum date.

    Args:
        df: DataFrame with date column
        date_col: Name of date column
        months: Number of months to include

    Returns:
        Tuple of (filtered_df, is_period_limited, actual_months_count)

    """
    end_date = df[date_col].max()
    if pd.isna(end_date):
        return df, False, 0

    data_min_date = df[date_col].min()
    desired_start = end_date - pd.DateOffset(months=months)
    start_date = max(desired_start, data_min_date)

    filtered = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)].copy()
    actual_months = filtered[date_col].dt.to_period("M").nunique()
    is_limited = actual_months < months or start_date > desired_start

    return filtered, is_limited, actual_months


def aggregate_daily(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """
    Aggregate data by day, counting rows per date.

    Args:
        df: DataFrame with date column
        date_col: Name of date column

    Returns:
        DataFrame with date and 'casos' count columns, sorted by date

    """
    counts = df.groupby(date_col).size().reset_index(name="casos")
    return counts.sort_values(date_col)


def aggregate_monthly(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """
    Aggregate data by month, counting rows per month.

    Args:
        df: DataFrame with date column
        date_col: Name of date column

    Returns:
        DataFrame with 'ano_mes' timestamp and 'casos' count columns, sorted by month

    """
    df = df.copy()
    df["ano_mes"] = df[date_col].dt.to_period("M")
    counts = df.groupby("ano_mes").size().reset_index(name="casos")
    counts["ano_mes"] = counts["ano_mes"].dt.to_timestamp()
    return counts.sort_values("ano_mes")


def build_daily_metadata(
    counts: pd.DataFrame, date_col: str, location_value: str | None
) -> dict:
    """Build metadata dictionary for daily chart."""
    if len(counts) == 0:
        return {}

    trend_dir, trend_pct = calculate_trend(counts)

    return {
        "chart_type": "daily",
        "start_date": counts[date_col].min(),
        "end_date": counts[date_col].max(),
        "total_cases": int(counts["casos"].sum()),
        "avg_daily": float(counts["casos"].mean()),
        "max_daily": int(counts["casos"].max()),
        "max_date": counts.loc[counts["casos"].idxmax(), date_col],
        "min_daily": int(counts["casos"].min()),
        "trend_direction": trend_dir,
        "trend_percentage": float(trend_pct),
        "location": location_value or "Brasil (nacional)",
    }


def build_monthly_metadata(
    counts: pd.DataFrame,
    location_value: str | None,
    is_limited: bool = False,
    requested_months: int = 0,
    actual_months: int = 0,
    end_date: datetime | None = None,
    min_date: datetime | None = None,
) -> dict:
    """Build metadata dictionary for monthly chart."""
    if len(counts) == 0:
        return {}

    trend_dir, trend_pct = calculate_trend(counts)

    metadata = {
        "chart_type": "monthly",
        "start_date": counts["ano_mes"].min(),
        "end_date": counts["ano_mes"].max(),
        "total_cases": int(counts["casos"].sum()),
        "avg_monthly": float(counts["casos"].mean()),
        "max_monthly": int(counts["casos"].max()),
        "max_date": counts.loc[counts["casos"].idxmax(), "ano_mes"],
        "min_monthly": int(counts["casos"].min()),
        "trend_direction": trend_dir,
        "trend_percentage": float(trend_pct),
        "location": location_value or "Brasil (nacional)",
    }

    if is_limited:
        metadata["period_limited_by_data"] = True
        metadata["requested_months"] = requested_months
        metadata["actual_months"] = actual_months
        if end_date:
            metadata["data_max_date"] = (
                end_date.isoformat()
                if hasattr(end_date, "isoformat")
                else str(end_date)
            )
        if min_date:
            metadata["data_min_date"] = (
                min_date.isoformat()
                if hasattr(min_date, "isoformat")
                else str(min_date)
            )

    return metadata
