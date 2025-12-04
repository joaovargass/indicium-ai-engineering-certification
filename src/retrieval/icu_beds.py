"""ICU bed data fetcher from CNES (Cadastro Nacional de Estabelecimentos de Saúde)."""

import json
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

# Cache configuration
CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "cleaned"
CACHE_FILE = CACHE_DIR / "icu_beds_cache.json"
CACHE_TTL_DAYS = 7

# CNES API URLs
CNES_LEITOS_URL_TEMPLATE = (
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/Leitos_SUS/Leitos_{year}.csv"
)

# Fallback static data (Dec 2024) - used if API unavailable
FALLBACK_ICU_BEDS = {
    "SP": 15695,
    "RJ": 8456,
    "MG": 5894,
    "PR": 3731,
    "BA": 3299,
    "RS": 2996,
    "PE": 2917,
    "GO": 2156,
    "DF": 2089,
    "SC": 1942,
    "CE": 1833,
    "ES": 1724,
    "PA": 1622,
    "MA": 1234,
    "MT": 1185,
    "PB": 1009,
    "RN": 834,
    "AM": 808,
    "MS": 761,
    "AL": 697,
    "RO": 640,
    "PI": 564,
    "SE": 491,
    "TO": 428,
    "AP": 185,
    "AC": 106,
    "RR": 105,
}
FALLBACK_BRAZIL_TOTAL = 63401


def _load_cache() -> dict | None:
    """Load cached ICU bed data if valid."""
    if not CACHE_FILE.exists():
        return None

    try:
        with open(CACHE_FILE) as f:
            cache = json.load(f)

        cached_at = datetime.fromisoformat(cache.get("cached_at", ""))
        if datetime.now() - cached_at > timedelta(days=CACHE_TTL_DAYS):
            return None

        return cache
    except Exception:
        return None


def _save_cache(data: dict) -> None:
    """Save ICU bed data to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache = {
        "cached_at": datetime.now().isoformat(),
        "competency": data.get("competency"),
        "icu_beds_by_uf": data.get("icu_beds_by_uf"),
        "brazil_total": data.get("brazil_total"),
    }

    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def _fetch_from_api(year: int | None = None) -> dict | None:
    """Fetch ICU bed data from CNES API."""
    if year is None:
        year = datetime.now().year

    url = CNES_LEITOS_URL_TEMPLATE.format(year=year)

    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()

        df = pd.read_csv(
            StringIO(response.text),
            sep=",",
            quotechar='"',
            on_bad_lines="skip",
            dtype=str,
        )

        # Convert numeric columns
        numeric_cols = ["UTI_TOTAL_EXIST", "UTI_TOTAL_SUS", "COMP"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Get latest competency
        latest_comp = df["COMP"].max()
        df_latest = df[df["COMP"] == latest_comp]

        # Aggregate by UF
        icu_by_uf = df_latest.groupby("UF")["UTI_TOTAL_EXIST"].sum().to_dict()
        brazil_total = int(df_latest["UTI_TOTAL_EXIST"].sum())

        # Convert to int
        icu_by_uf = {k: int(v) for k, v in icu_by_uf.items()}

        return {
            "competency": int(latest_comp),
            "icu_beds_by_uf": icu_by_uf,
            "brazil_total": brazil_total,
            "source": "cnes_api",
        }

    except Exception as e:
        print(f"Warning: Could not fetch ICU beds from API: {e}")
        return None


def get_icu_beds_data(force_refresh: bool = False) -> dict:
    """
    Get ICU bed data by state.

    Uses cache if available and valid, otherwise fetches from CNES API.
    Falls back to static data if API unavailable.

    Args:
        force_refresh: If True, bypasses cache and fetches fresh data.

    Returns:
        Dictionary with:
        - competency: Data period (YYYYMM)
        - icu_beds_by_uf: Dict mapping UF -> ICU bed count
        - brazil_total: Total ICU beds in Brazil
        - source: "cache", "cnes_api", or "fallback"

    """
    if not force_refresh:
        cache = _load_cache()
        if cache:
            cache["source"] = "cache"
            return cache

    api_data = _fetch_from_api()
    if api_data:
        _save_cache(api_data)
        return api_data

    # Fallback to static data
    return {
        "competency": 202412,
        "icu_beds_by_uf": FALLBACK_ICU_BEDS.copy(),
        "brazil_total": FALLBACK_BRAZIL_TOTAL,
        "source": "fallback",
    }


def get_icu_beds_for_location(
    uf: str | None = None,
    city_code: str | None = None,
) -> tuple[int | None, str]:
    """
    Get ICU bed count for a specific location.

    Args:
        uf: State code (e.g., "SP", "RJ") or None for Brazil total.
        city_code: IBGE city code (not supported yet, uses state data).

    Returns:
        Tuple of (bed_count, source_description).
        bed_count is None if location not found.

    """
    data = get_icu_beds_data()
    source = f"CNES {data.get('competency', 'N/A')} ({data.get('source', 'unknown')})"

    if city_code:
        # City-level data not available in this API
        # Fall back to state data if we can determine the state
        # For now, return None with explanation
        return None, "city-level ICU data not available"

    if uf:
        uf_upper = uf.upper()
        beds = data.get("icu_beds_by_uf", {}).get(uf_upper)
        return beds, source

    # National total
    return data.get("brazil_total"), source


def clear_cache() -> bool:
    """Clear the ICU beds cache file."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
        return True
    return False
