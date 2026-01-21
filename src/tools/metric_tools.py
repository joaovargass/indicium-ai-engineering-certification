"""Metric tools for SRAG data analysis."""

from typing import Annotated, Any

from langchain_core.tools import tool

from common.config import (
    DEFAULT_LOOKBACK_DAYS,
    DEFAULT_MONTHS,
    DEFAULT_PERIOD_DAYS,
    NO_DATA_MESSAGE_METRICS,
)
from elt.load import NoDataAvailableError, load_srag_data
from metrics.calculators import (
    calculate_case_growth,
    calculate_icu_occupancy_rate,
    calculate_mortality_rate,
    calculate_vaccination_rate,
)
from tools.location_utils import determine_location_filter, get_location_description


def _with_location(uf: str | None, city_code: str | None, result: dict) -> dict:
    """Add location description to result dict."""
    return {"location": get_location_description(uf, city_code), **result}


@tool
def get_case_increase_rate(
    uf: Annotated[str | None, "State code (e.g., 'SP'). None for national."] = None,
    city_code: Annotated[str | None, "IBGE city code. Overrides UF."] = None,
    period_days: Annotated[int, "Days per period (default: 7)."] = DEFAULT_PERIOD_DAYS,
) -> dict[str, Any]:
    """Calculate case increase rate vs previous period. Use for trends, growth analysis."""
    try:
        df = load_srag_data()
    except NoDataAvailableError:
        return {"error": NO_DATA_MESSAGE_METRICS}
    location_col, location_value = determine_location_filter(uf, city_code)
    result = calculate_case_growth(
        df,
        period_days=period_days,
        location_col=location_col,
        location_value=location_value,
    )
    return _with_location(uf, city_code, result)


@tool
def get_mortality_rate(
    uf: Annotated[str | None, "State code (e.g., 'SP'). None for national."] = None,
    city_code: Annotated[str | None, "IBGE city code. Overrides UF."] = None,
    lookback_months: Annotated[
        int | None, "Number of months to look back (default: 12). None for all data."
    ] = DEFAULT_MONTHS,
) -> dict[str, Any]:
    """Calculate mortality rate (deaths/cases). Use for fatality, death rate queries."""
    try:
        df = load_srag_data()
    except NoDataAvailableError:
        return {"error": NO_DATA_MESSAGE_METRICS}
    location_col, location_value = determine_location_filter(uf, city_code)
    result = calculate_mortality_rate(
        df,
        location_col=location_col,
        location_value=location_value,
        lookback_months=lookback_months,
    )
    return _with_location(uf, city_code, result)


@tool
def get_icu_occupancy_rate(
    uf: Annotated[str | None, "State code (e.g., 'SP'). None for national."] = None,
    city_code: Annotated[str | None, "IBGE city code. Overrides UF."] = None,
    lookback_days: Annotated[
        int, "Days to look back (default: 30)."
    ] = DEFAULT_LOOKBACK_DAYS,
) -> dict[str, Any]:
    """Calculate ICU occupancy rate. Use for hospital capacity queries. Apenas casos SRAG. Taxa = pacientes-dia / leitos-dia. Fontes: OpenDataSUS (SRAG) para pacientes-dia, CNES para leitos."""
    try:
        df = load_srag_data()
    except NoDataAvailableError:
        return {"error": NO_DATA_MESSAGE_METRICS}
    location_col, location_value = determine_location_filter(uf, city_code)
    result = calculate_icu_occupancy_rate(
        df,
        location_col=location_col,
        location_value=location_value,
        lookback_days=lookback_days,
    )
    return _with_location(uf, city_code, result)


@tool
def get_vaccination_rate(
    uf: Annotated[str | None, "State code (e.g., 'SP'). None for national."] = None,
    city_code: Annotated[str | None, "IBGE city code. Overrides UF."] = None,
    vaccine_type: Annotated[str, "'covid', 'flu', or 'both' (default)."] = "both",
    lookback_months: Annotated[
        int | None, "Number of months to look back (default: 12). None for all data."
    ] = DEFAULT_MONTHS,
) -> dict[str, Any]:
    """Calculate vaccination rates. Use for vaccine coverage queries."""
    try:
        df = load_srag_data()
    except NoDataAvailableError:
        return {"error": NO_DATA_MESSAGE_METRICS}
    location_col, location_value = determine_location_filter(uf, city_code)
    result = calculate_vaccination_rate(
        df,
        vaccine_type=vaccine_type,
        location_col=location_col,
        location_value=location_value,
        lookback_months=lookback_months,
    )
    return _with_location(uf, city_code, result)
