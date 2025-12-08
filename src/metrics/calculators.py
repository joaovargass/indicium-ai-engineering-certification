"""Metrics calculation module for SRAG data analysis."""

from datetime import datetime, timedelta
from typing import Any

import pandas as pd

from common.config import DEFAULT_LOOKBACK_DAYS


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


def calculate_case_growth(
    df: pd.DataFrame,
    period_days: int = 7,
    location_col: str | None = None,
    location_value: str | None = None,
    date_col: str | None = None,
    reporting_lag_days: int = 7,
) -> dict[str, Any]:
    """
    Calculate case increase rate comparing current period vs previous period.

    Args:
        df: DataFrame with case data
        period_days: Number of days for each period (default: 7)
        location_col: Optional location column name for filtering
        location_value: Optional location value to filter
        date_col: Optional date column name (auto-detected if None)
        reporting_lag_days: Days to exclude from end to account for reporting lag (default: 7)

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
    df = df.dropna(subset=[date_col]).copy()
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

    data_max_date = df[date_col].max().normalize()
    end_date = data_max_date - timedelta(days=reporting_lag_days)
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

    period_start = previous_start
    period_end = end_date

    return {
        "rate": rate,
        "current_period_cases": int(current_cases),
        "previous_period_cases": int(previous_cases),
        "current_period_start": current_start.isoformat(),
        "current_period_end": end_date.isoformat(),
        "previous_period_start": previous_start.isoformat(),
        "previous_period_end": previous_end.isoformat(),
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "metadata": metadata,
    }


def calculate_mortality_rate(
    df: pd.DataFrame,
    location_col: str | None = None,
    location_value: str | None = None,
    lookback_months: int | None = None,
) -> dict[str, Any]:
    """
    Calculate mortality rate (percentage of cases that resulted in death).

    Args:
        df: DataFrame with case data
        location_col: Optional location column name for filtering
        location_value: Optional location value to filter
        lookback_months: Optional number of months to look back (default: None = all data)

    Returns:
        Dictionary with:
        - rate: Mortality percentage (float or None)
        - total_deaths: Number of deaths (EVOLUCAO = 2 or 3)
        - total_cases: Total cases with defined evolution (excluding ignored)
        - period_start: Start date of data period used
        - period_end: End date of data period used
        - metadata: Additional information

    """
    df = _filter_by_location(df, location_col, location_value)

    if "EVOLUCAO" not in df.columns:
        return {
            "rate": None,
            "total_deaths": 0,
            "total_cases": 0,
            "period_start": None,
            "period_end": None,
            "metadata": {"error": "EVOLUCAO column not found"},
        }

    date_col = _get_date_column(df)
    period_start = None
    period_end = None

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col, "EVOLUCAO"])

        if len(df) > 0:
            data_max_date = df[date_col].max().normalize()
            data_min_date = df[date_col].min().normalize()

            # Filter by lookback_months if specified
            if lookback_months is not None:
                current_date = datetime.now().date()
                period_end_date = min(data_max_date.date(), current_date)
                period_start_date = period_end_date - timedelta(
                    days=lookback_months * 30
                )
                period_start_date = max(period_start_date, data_min_date.date())

                df = df[
                    (df[date_col].dt.date >= period_start_date)
                    & (df[date_col].dt.date <= period_end_date)
                ]

                period_start = pd.Timestamp(period_start_date).normalize()
                period_end = pd.Timestamp(period_end_date).normalize()
            else:
                period_start = data_min_date
                period_end = data_max_date
        else:
            period_start = None
            period_end = None
    else:
        df = df.dropna(subset=["EVOLUCAO"])

    df = df[["EVOLUCAO"]].copy()
    df = df.dropna(subset=["EVOLUCAO"])

    if len(df) == 0:
        return {
            "rate": None,
            "total_deaths": 0,
            "total_cases": 0,
            "period_start": period_start.isoformat() if period_start else None,
            "period_end": period_end.isoformat() if period_end else None,
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
        "period_start": period_start.isoformat() if period_start else None,
        "period_end": period_end.isoformat() if period_end else None,
        "metadata": metadata,
    }


def _prepare_icu_patients(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare and filter ICU patients from DataFrame."""
    df = df.dropna(subset=["UTI"]).copy()
    df["UTI"] = df["UTI"].astype(str).str.strip()
    icu_patients = df[df["UTI"] == "1"].copy()

    if "DT_ENTUTI" in icu_patients.columns:
        icu_patients["DT_ENTUTI"] = pd.to_datetime(
            icu_patients["DT_ENTUTI"], errors="coerce"
        )
        icu_patients = icu_patients.dropna(subset=["DT_ENTUTI"])

    if "DT_SAIDUTI" in icu_patients.columns:
        icu_patients["DT_SAIDUTI"] = pd.to_datetime(
            icu_patients["DT_SAIDUTI"], errors="coerce"
        )

    return icu_patients


def _calculate_icu_period(
    icu_patients: pd.DataFrame, lookback_days: int
) -> tuple[pd.Timestamp, pd.Timestamp, bool]:
    """Calculate period dates for ICU occupancy calculation."""
    current_date = pd.Timestamp.now().normalize()

    if len(icu_patients) > 0 and "DT_ENTUTI" in icu_patients.columns:
        data_max_date = icu_patients["DT_ENTUTI"].max().normalize()
        data_min_date = icu_patients["DT_ENTUTI"].min().normalize()
        period_end = min(data_max_date, current_date)
        desired_period_start = period_end - timedelta(days=lookback_days - 1)
        period_start = max(desired_period_start, data_min_date)
        period_limited = (
            period_end < current_date or period_start > desired_period_start
        )
        return period_start, period_end, period_limited

    period_end = current_date
    period_start = current_date - timedelta(days=lookback_days - 1)
    return period_start, period_end, False


def _filter_current_icu_patients(
    icu_patients: pd.DataFrame, period_start: pd.Timestamp
) -> pd.DataFrame:
    """Filter patients currently in ICU within the period."""
    current_date = pd.Timestamp.now().normalize()

    if "DT_SAIDUTI" in icu_patients.columns:
        return icu_patients[
            (
                (icu_patients["DT_SAIDUTI"].isna())
                | (icu_patients["DT_SAIDUTI"] > current_date)
            )
            & (icu_patients["DT_ENTUTI"] >= period_start)
        ]

    return icu_patients[icu_patients["DT_ENTUTI"] >= period_start]


def _build_icu_metadata(
    total_icu_beds: int | None,
    data_source: str | None,
    period_limited: bool,
    period_start: pd.Timestamp,
    period_end: pd.Timestamp,
    lookback_days: int,
) -> dict[str, Any]:
    """Build metadata dictionary for ICU occupancy result."""
    if total_icu_beds is not None:
        metadata = {"data_source": data_source or "provided"}
    else:
        metadata = {
            "data_source": "none",
            "note": "ICU bed data not available for this location.",
        }

    if period_limited:
        current_date = pd.Timestamp.now().normalize()
        actual_days = (period_end - period_start).days + 1
        metadata["period_limited_by_data"] = True
        metadata["requested_lookback_days"] = lookback_days
        metadata["actual_period_days"] = actual_days
        metadata["data_max_date"] = period_end.isoformat()
        metadata["current_date"] = current_date.isoformat()

    return metadata


def calculate_icu_occupancy_rate(
    df: pd.DataFrame,
    location_col: str | None = None,
    location_value: str | None = None,
    total_icu_beds: int | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> dict[str, Any]:
    """
    Calculate ICU occupancy rate.

    Args:
        df: DataFrame with case data
        location_col: Optional location column name for filtering
        location_value: Optional location value to filter
        total_icu_beds: Optional total ICU beds (if None, fetches from CNES)
        lookback_days: Number of days to look back for ICU admissions (default: DEFAULT_LOOKBACK_DAYS)

    Returns:
        Dictionary with:
        - occupancy_rate: Percentage of ICU beds occupied (float or None)
        - patients_in_icu: Number of patients currently in ICU
        - total_icu_beds: Total ICU beds (from parameter or CNES)
        - data_source: Source of ICU bed data
        - metadata: Additional information

    """
    df = _filter_by_location(df, location_col, location_value)

    required_cols = ["UTI", "DT_ENTUTI"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return {
            "occupancy_rate": None,
            "patients_in_icu": 0,
            "total_icu_beds": None,
            "data_source": None,
            "metadata": {"error": f"Missing required columns: {missing_cols}"},
        }

    df = df[
        required_cols + (["DT_SAIDUTI"] if "DT_SAIDUTI" in df.columns else [])
    ].copy()

    icu_patients = _prepare_icu_patients(df)

    if len(icu_patients) == 0:
        return {
            "occupancy_rate": None,
            "patients_in_icu": 0,
            "total_icu_beds": total_icu_beds,
            "data_source": None,
            "metadata": {"warning": "No ICU patients found"},
        }

    period_start, period_end, period_limited = _calculate_icu_period(
        icu_patients, lookback_days
    )
    currently_in_icu = _filter_current_icu_patients(icu_patients, period_start)
    patients_count = len(currently_in_icu)

    data_source = None
    if total_icu_beds is None:
        total_icu_beds, data_source = _fetch_cnes_beds(location_col, location_value)

    metadata = _build_icu_metadata(
        total_icu_beds,
        data_source,
        period_limited,
        period_start,
        period_end,
        lookback_days,
    )

    occupancy_rate = None
    if total_icu_beds is not None and total_icu_beds > 0:
        occupancy_rate = (patients_count / total_icu_beds) * 100

    return {
        "occupancy_rate": occupancy_rate,
        "patients_in_icu": int(patients_count),
        "total_icu_beds": total_icu_beds,
        "lookback_days": lookback_days,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "data_source": data_source,
        "metadata": metadata,
    }


def _fetch_cnes_beds(
    location_col: str | None,
    location_value: str | None,
) -> tuple[int | None, str | None]:
    """
    Get ICU bed count from CNES data.

    Args:
        location_col: Location column name (SG_UF_NOT or CO_MUN_NOT)
        location_value: Location value (UF code or city code)

    Returns:
        Tuple of (bed_count, source_description).

    """
    try:
        from retrieval.icu_beds import get_location_icu_beds

        if location_col == "SG_UF_NOT":
            return get_location_icu_beds(uf=location_value)
        elif location_col == "CO_MUN_NOT":
            return get_location_icu_beds(city_code=location_value)
        else:
            # National data
            return get_location_icu_beds()
    except Exception as e:
        print(f"Warning: Could not get ICU beds from CNES: {e}")
        return None, None


def _prepare_vaccination_data(
    df: pd.DataFrame,
    calculate_covid: bool,
    calculate_flu: bool,
    lookback_months: int | None,
) -> tuple[pd.DataFrame, pd.Timestamp | None, pd.Timestamp | None]:
    """Prepare vaccination data and calculate period."""
    date_col = _get_date_column(df)
    period_start = None
    period_end = None

    if not date_col:
        return df, period_start, period_end

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])

    if calculate_covid and "VACINA_COV" in df.columns:
        df = df.dropna(subset=["VACINA_COV"])
    if calculate_flu and "VACINA" in df.columns:
        df = df.dropna(subset=["VACINA"])

    if len(df) == 0:
        return df, period_start, period_end

    data_max_date = df[date_col].max().normalize()
    data_min_date = df[date_col].min().normalize()

    if lookback_months is not None:
        current_date = datetime.now().date()
        period_end_date = min(data_max_date.date(), current_date)
        period_start_date = period_end_date - timedelta(days=lookback_months * 30)
        period_start_date = max(period_start_date, data_min_date.date())

        df = df[
            (df[date_col].dt.date >= period_start_date)
            & (df[date_col].dt.date <= period_end_date)
        ]

        period_start = pd.Timestamp(period_start_date).normalize()
        period_end = pd.Timestamp(period_end_date).normalize()
    else:
        period_start = data_min_date
        period_end = data_max_date

    return df, period_start, period_end


def _calculate_covid_rate(
    df: pd.DataFrame, calculate_covid: bool
) -> tuple[float | None, int, dict[str, Any]]:
    """Calculate COVID-19 vaccination rate."""
    if not calculate_covid or "VACINA_COV" not in df.columns:
        return None, 0, {}

    covid_df = df[["VACINA_COV"]].dropna()
    if len(covid_df) == 0:
        return None, 0, {}

    covid_df["VACINA_COV"] = covid_df["VACINA_COV"].astype(str).str.strip()
    covid_df = covid_df[~covid_df["VACINA_COV"].isin(["9"])]
    if len(covid_df) == 0:
        return None, 0, {}

    covid_vaccinated = (covid_df["VACINA_COV"] == "1").sum()
    total_covid = len(covid_df)
    covid_rate = (covid_vaccinated / total_covid) * 100

    metadata = {
        "covid_total": int(total_covid),
        "covid_ignored": int((df["VACINA_COV"].astype(str).str.strip() == "9").sum()),
    }

    return covid_rate, int(covid_vaccinated), metadata


def _calculate_flu_rate(
    df: pd.DataFrame, calculate_flu: bool
) -> tuple[float | None, int, dict[str, Any]]:
    """Calculate flu vaccination rate."""
    if not calculate_flu or "VACINA" not in df.columns:
        return None, 0, {}

    flu_df = df[["VACINA"]].dropna()
    if len(flu_df) == 0:
        return None, 0, {}

    flu_df["VACINA"] = flu_df["VACINA"].astype(str).str.strip()
    flu_df = flu_df[~flu_df["VACINA"].isin(["9"])]
    if len(flu_df) == 0:
        return None, 0, {}

    flu_vaccinated = (flu_df["VACINA"] == "1").sum()
    total_flu = len(flu_df)
    flu_rate = (flu_vaccinated / total_flu) * 100

    metadata = {
        "flu_total": int(total_flu),
        "flu_ignored": int((df["VACINA"].astype(str).str.strip() == "9").sum()),
    }

    return flu_rate, int(flu_vaccinated), metadata


def calculate_vaccination_rate(
    df: pd.DataFrame,
    vaccine_type: str = "both",
    location_col: str | None = None,
    location_value: str | None = None,
    lookback_months: int | None = None,
) -> dict[str, Any]:
    """
    Calculate vaccination rate for COVID-19 and/or flu.

    Args:
        df: DataFrame with case data
        vaccine_type: "covid", "flu", or "both" (default: "both")
        location_col: Optional location column name for filtering
        location_value: Optional location value to filter
        lookback_months: Optional number of months to look back (default: None = all data)

    Returns:
        Dictionary with:
        - covid_rate: COVID-19 vaccination rate (float or None)
        - flu_rate: Flu vaccination rate (float or None)
        - covid_vaccinated: Number vaccinated against COVID-19
        - flu_vaccinated: Number vaccinated against flu
        - total_cases: Total cases analyzed
        - period_start: Start date of data period used
        - period_end: End date of data period used
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
            "period_start": None,
            "period_end": None,
            "metadata": {"error": "No vaccination columns found"},
        }

    df, period_start, period_end = _prepare_vaccination_data(
        df, calculate_covid, calculate_flu, lookback_months
    )
    df = df[cols_to_keep].copy()

    covid_rate, covid_vaccinated, covid_metadata = _calculate_covid_rate(
        df, calculate_covid
    )
    flu_rate, flu_vaccinated, flu_metadata = _calculate_flu_rate(df, calculate_flu)

    metadata = {**covid_metadata, **flu_metadata}
    total_cases = max(
        metadata.get("covid_total", 0),
        metadata.get("flu_total", 0),
    )

    return {
        "covid_rate": covid_rate,
        "flu_rate": flu_rate,
        "covid_vaccinated": covid_vaccinated,
        "flu_vaccinated": flu_vaccinated,
        "total_cases": int(total_cases) if total_cases > 0 else 0,
        "period_start": period_start.isoformat() if period_start else None,
        "period_end": period_end.isoformat() if period_end else None,
        "metadata": metadata,
    }
