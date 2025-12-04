"""Metrics calculation module for SRAG data analysis."""

from datetime import timedelta
from typing import Any

import pandas as pd


def _filter_by_location(
    df: pd.DataFrame,
    location_col: str | None = None,
    location_value: str | None = None,
) -> pd.DataFrame:
    """
    Filter DataFrame by location if specified.

    Args:
        df: DataFrame to filter
        location_col: Optional location column name (e.g., "SG_UF_NOT", "CO_MUN_NOT")
        location_value: Optional location value to filter

    Returns:
        Filtered DataFrame.
    """
    if location_col and location_value:
        if location_col not in df.columns:
            return df
        return df[df[location_col] == location_value].copy()
    return df.copy()


def _get_date_column(df: pd.DataFrame, preferred: str = "DT_SIN_PRI") -> str | None:
    """
    Get available date column, preferring DT_SIN_PRI over DT_NOTIFIC.

    Args:
        df: DataFrame to check
        preferred: Preferred date column name

    Returns:
        Column name if available, None otherwise.
    """
    if preferred in df.columns and df[preferred].notna().any():
        return preferred
    if "DT_NOTIFIC" in df.columns and df["DT_NOTIFIC"].notna().any():
        return "DT_NOTIFIC"
    return None


def calculate_case_increase_rate(
    df: pd.DataFrame,
    period_days: int = 7,
    location_col: str | None = None,
    location_value: str | None = None,
    date_col: str | None = None,
) -> dict[str, Any]:
    """
    Calculate case increase rate comparing current period vs previous period.

    Args:
        df: DataFrame with case data
        period_days: Number of days for each period (default: 7)
        location_col: Optional location column name for filtering
        location_value: Optional location value to filter
        date_col: Optional date column name (auto-detected if None)

    Returns:
        Dictionary with:
        - rate: Percentage increase (float or None)
        - current_period_cases: Number of cases in current period
        - previous_period_cases: Number of cases in previous period
        - current_period_start: Start date of current period
        - current_period_end: End date of current period
        - previous_period_start: Start date of previous period
        - previous_period_end: End date of previous period
        - metadata: Additional information
    """
    df = _filter_by_location(df, location_col, location_value)

    if date_col is None:
        date_col = _get_date_column(df)
        if date_col is None:
            return {
                "rate": None,
                "current_period_cases": 0,
                "previous_period_cases": 0,
                "current_period_start": None,
                "current_period_end": None,
                "previous_period_start": None,
                "previous_period_end": None,
                "metadata": {"error": "No valid date column found"},
            }

    df = df[[date_col]].copy()
    df = df.dropna(subset=[date_col])
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])

    if len(df) == 0:
        return {
            "rate": None,
            "current_period_cases": 0,
            "previous_period_cases": 0,
            "current_period_start": None,
            "current_period_end": None,
            "previous_period_start": None,
            "previous_period_end": None,
            "metadata": {"error": "No valid date records found"},
        }

    end_date = df[date_col].max().normalize()
    current_start = end_date - timedelta(days=period_days - 1)
    previous_end = current_start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=period_days - 1)

    current_mask = (df[date_col] >= current_start) & (df[date_col] <= end_date)
    previous_mask = (df[date_col] >= previous_start) & (df[date_col] <= previous_end)

    current_cases = current_mask.sum()
    previous_cases = previous_mask.sum()

    if previous_cases == 0:
        rate = None
        metadata = {"warning": "Previous period has no cases, cannot calculate rate"}
    else:
        rate = ((current_cases - previous_cases) / previous_cases) * 100
        metadata = {}

    return {
        "rate": rate,
        "current_period_cases": int(current_cases),
        "previous_period_cases": int(previous_cases),
        "current_period_start": current_start.isoformat(),
        "current_period_end": end_date.isoformat(),
        "previous_period_start": previous_start.isoformat(),
        "previous_period_end": previous_end.isoformat(),
        "metadata": metadata,
    }


def calculate_mortality_rate(
    df: pd.DataFrame,
    location_col: str | None = None,
    location_value: str | None = None,
) -> dict[str, Any]:
    """
    Calculate mortality rate (percentage of cases that resulted in death).

    Args:
        df: DataFrame with case data
        location_col: Optional location column name for filtering
        location_value: Optional location value to filter

    Returns:
        Dictionary with:
        - rate: Mortality percentage (float or None)
        - total_deaths: Number of deaths (EVOLUCAO = 2 or 3)
        - total_cases: Total cases with defined evolution (excluding ignored)
        - metadata: Additional information
    """
    df = _filter_by_location(df, location_col, location_value)

    if "EVOLUCAO" not in df.columns:
        return {
            "rate": None,
            "total_deaths": 0,
            "total_cases": 0,
            "metadata": {"error": "EVOLUCAO column not found"},
        }

    df = df[["EVOLUCAO"]].copy()
    df = df.dropna(subset=["EVOLUCAO"])

    if len(df) == 0:
        return {
            "rate": None,
            "total_deaths": 0,
            "total_cases": 0,
            "metadata": {"error": "No records with evolution data"},
        }

    df["EVOLUCAO"] = df["EVOLUCAO"].astype(str).str.strip()

    deaths = df[df["EVOLUCAO"].isin(["2", "3"])]
    total_cases = df[~df["EVOLUCAO"].isin(["9"])]

    total_deaths = len(deaths)
    total_with_evolution = len(total_cases)

    if total_with_evolution == 0:
        rate = None
        metadata = {"warning": "No cases with valid evolution data"}
    else:
        rate = (total_deaths / total_with_evolution) * 100
        metadata = {
            "ignored_cases": int((df["EVOLUCAO"] == "9").sum()),
        }

    return {
        "rate": rate,
        "total_deaths": int(total_deaths),
        "total_cases": int(total_with_evolution),
        "metadata": metadata,
    }


def calculate_icu_occupancy_rate(
    df: pd.DataFrame,
    location_col: str | None = None,
    location_value: str | None = None,
    total_icu_beds: int | None = None,
    use_mock_data: bool = True,
    lookback_days: int = 90,
) -> dict[str, Any]:
    """
    Calculate ICU occupancy rate.

    Args:
        df: DataFrame with case data
        location_col: Optional location column name for filtering
        location_value: Optional location value to filter
        total_icu_beds: Optional total ICU beds (if None and use_mock_data=True, uses mock)
        use_mock_data: If True and total_icu_beds is None, uses mock data
        lookback_days: Number of days to look back for ICU admissions (default: 90)

    Returns:
        Dictionary with:
        - occupancy_rate: Percentage of ICU beds occupied (float or None)
        - patients_in_icu: Number of patients currently in ICU
        - total_icu_beds: Total ICU beds (from parameter or mock)
        - metadata: Additional information including data source
    """
    df = _filter_by_location(df, location_col, location_value)

    required_cols = ["UTI", "DT_ENTUTI"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return {
            "occupancy_rate": None,
            "patients_in_icu": 0,
            "total_icu_beds": None,
            "metadata": {"error": f"Missing required columns: {missing_cols}"},
        }

    df = df[required_cols + (["DT_SAIDUTI"] if "DT_SAIDUTI" in df.columns else [])].copy()

    df = df.dropna(subset=["UTI"])
    df["UTI"] = df["UTI"].astype(str).str.strip()

    icu_patients = df[df["UTI"] == "1"].copy()

    if len(icu_patients) == 0:
        return {
            "occupancy_rate": None,
            "patients_in_icu": 0,
            "total_icu_beds": total_icu_beds if total_icu_beds is not None else None,
            "metadata": {"warning": "No ICU patients found"},
        }

    if "DT_ENTUTI" in icu_patients.columns:
        icu_patients["DT_ENTUTI"] = pd.to_datetime(icu_patients["DT_ENTUTI"], errors="coerce")
        icu_patients = icu_patients.dropna(subset=["DT_ENTUTI"])

    if "DT_SAIDUTI" in icu_patients.columns:
        icu_patients["DT_SAIDUTI"] = pd.to_datetime(icu_patients["DT_SAIDUTI"], errors="coerce")

    current_date = pd.Timestamp.now().normalize()
    cutoff_date = current_date - timedelta(days=lookback_days)

    if "DT_SAIDUTI" in icu_patients.columns:
        currently_in_icu = icu_patients[
            (
                (icu_patients["DT_SAIDUTI"].isna())
                | (icu_patients["DT_SAIDUTI"] > current_date)
            )
            & (icu_patients["DT_ENTUTI"] >= cutoff_date)
        ]
    else:
        currently_in_icu = icu_patients[icu_patients["DT_ENTUTI"] >= cutoff_date]

    patients_count = len(currently_in_icu)

    if total_icu_beds is None and use_mock_data:
        mock_beds = _get_mock_icu_beds(location_value)
        total_icu_beds = mock_beds
        metadata = {
            "data_source": "mock",
            "note": "Using mock ICU bed data. Replace with real data source.",
        }
    elif total_icu_beds is not None:
        metadata = {"data_source": "provided"}
    else:
        metadata = {
            "data_source": "none",
            "note": "No ICU bed data provided. Returning absolute count only.",
        }

    if total_icu_beds is not None and total_icu_beds > 0:
        occupancy_rate = (patients_count / total_icu_beds) * 100
    else:
        occupancy_rate = None

    return {
        "occupancy_rate": occupancy_rate,
        "patients_in_icu": int(patients_count),
        "total_icu_beds": total_icu_beds,
        "metadata": metadata,
    }


def _get_mock_icu_beds(location_value: str | None = None) -> int:
    """
    Get mock ICU bed count for testing purposes.

    Args:
        location_value: Optional location identifier

    Returns:
        Mock ICU bed count.
    """
    if location_value:
        return 500
    return 10000


def calculate_vaccination_rate(
    df: pd.DataFrame,
    vaccine_type: str = "both",
    location_col: str | None = None,
    location_value: str | None = None,
) -> dict[str, Any]:
    """
    Calculate vaccination rate for COVID-19 and/or flu.

    Args:
        df: DataFrame with case data
        vaccine_type: "covid", "flu", or "both" (default: "both")
        location_col: Optional location column name for filtering
        location_value: Optional location value to filter

    Returns:
        Dictionary with:
        - covid_rate: COVID-19 vaccination rate (float or None)
        - flu_rate: Flu vaccination rate (float or None)
        - covid_vaccinated: Number vaccinated against COVID-19
        - flu_vaccinated: Number vaccinated against flu
        - total_cases: Total cases analyzed
        - metadata: Additional information
    """
    df = _filter_by_location(df, location_col, location_value)

    calculate_covid = vaccine_type in ("covid", "both")
    calculate_flu = vaccine_type in ("flu", "both")

    cols_to_keep = []
    if calculate_covid and "VACINA_COV" in df.columns:
        cols_to_keep.append("VACINA_COV")
    if calculate_flu and "VACINA" in df.columns:
        cols_to_keep.append("VACINA")

    if not cols_to_keep:
        return {
            "covid_rate": None,
            "flu_rate": None,
            "covid_vaccinated": 0,
            "flu_vaccinated": 0,
            "total_cases": 0,
            "metadata": {"error": "No vaccination columns found"},
        }

    df = df[cols_to_keep].copy()

    covid_rate = None
    flu_rate = None
    covid_vaccinated = 0
    flu_vaccinated = 0
    metadata = {}

    if calculate_covid and "VACINA_COV" in df.columns:
        covid_df = df[["VACINA_COV"]].dropna()
        if len(covid_df) > 0:
            covid_df["VACINA_COV"] = covid_df["VACINA_COV"].astype(str).str.strip()
            covid_df = covid_df[~covid_df["VACINA_COV"].isin(["9"])]
            if len(covid_df) > 0:
                covid_vaccinated = (covid_df["VACINA_COV"] == "1").sum()
                total_covid = len(covid_df)
                covid_rate = (covid_vaccinated / total_covid) * 100
                metadata["covid_total"] = int(total_covid)
                metadata["covid_ignored"] = int((df["VACINA_COV"].astype(str).str.strip() == "9").sum())

    if calculate_flu and "VACINA" in df.columns:
        flu_df = df[["VACINA"]].dropna()
        if len(flu_df) > 0:
            flu_df["VACINA"] = flu_df["VACINA"].astype(str).str.strip()
            flu_df = flu_df[~flu_df["VACINA"].isin(["9"])]
            if len(flu_df) > 0:
                flu_vaccinated = (flu_df["VACINA"] == "1").sum()
                total_flu = len(flu_df)
                flu_rate = (flu_vaccinated / total_flu) * 100
                metadata["flu_total"] = int(total_flu)
                metadata["flu_ignored"] = int((df["VACINA"].astype(str).str.strip() == "9").sum())

    total_cases = max(
        metadata.get("covid_total", 0),
        metadata.get("flu_total", 0),
    )

    return {
        "covid_rate": covid_rate,
        "flu_rate": flu_rate,
        "covid_vaccinated": int(covid_vaccinated),
        "flu_vaccinated": int(flu_vaccinated),
        "total_cases": int(total_cases) if total_cases > 0 else 0,
        "metadata": metadata,
    }

