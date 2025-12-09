"""ICU bed data fetcher from CNES (Cadastro Nacional de Estabelecimentos de Saúde)."""

import json
import unicodedata
from datetime import datetime, timedelta
from io import StringIO

import pandas as pd
import requests

from common.config import (
    CACHE_DIR,
    CNES_LEITOS_URL_TEMPLATE,
    FALLBACK_BRAZIL_TOTAL,
    FALLBACK_ICU_BEDS,
    IBGE_STATE_TO_UF,
    ICU_BEDS_CACHE_PATH,
    ICU_BEDS_CACHE_TTL_DAYS,
    ICU_BEDS_REQUEST_TIMEOUT_SECONDS,
)


def _normalize_city_name(name: str) -> str:
    """
    Normalize city name to match CNES format (uppercase, no accents).

    Args:
        name: City name (e.g., "São Paulo")

    Returns:
        Normalized name (e.g., "SAO PAULO")

    """
    nfd = unicodedata.normalize("NFD", name)
    without_accents = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return without_accents.upper().strip()


def _load_cache() -> dict | None:
    """Load cached ICU bed data if valid."""
    if not ICU_BEDS_CACHE_PATH.exists():
        return None

    try:
        with open(ICU_BEDS_CACHE_PATH) as f:
            cache = json.load(f)

        cached_at = datetime.fromisoformat(cache.get("cached_at", ""))
        if datetime.now() - cached_at > timedelta(days=ICU_BEDS_CACHE_TTL_DAYS):
            return None

        # Convert string keys back to tuples
        icu_beds_by_city_str = cache.get("icu_beds_by_city", {})
        icu_beds_by_city = {
            tuple(key.split("|")): beds for key, beds in icu_beds_by_city_str.items()
        }
        cache["icu_beds_by_city"] = icu_beds_by_city

        return cache
    except Exception:
        return None


def _save_cache(data: dict) -> None:
    """Save ICU bed data to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Convert tuple keys to strings for JSON serialization
    icu_beds_by_city = data.get("icu_beds_by_city", {})
    icu_beds_by_city_str = {
        f"{uf}|{city}": beds for (uf, city), beds in icu_beds_by_city.items()
    }

    cache = {
        "cached_at": datetime.now().isoformat(),
        "competency": data.get("competency"),
        "icu_beds_by_uf": data.get("icu_beds_by_uf"),
        "icu_beds_by_city": icu_beds_by_city_str,
        "brazil_total": data.get("brazil_total"),
    }

    with open(ICU_BEDS_CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def _fetch_from_api(year: int | None = None) -> dict | None:
    """Fetch ICU bed data from CNES API."""
    if year is None:
        year = datetime.now().year

    url = CNES_LEITOS_URL_TEMPLATE.format(year=year)

    try:
        response = requests.get(url, timeout=ICU_BEDS_REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()

        df = pd.read_csv(
            StringIO(response.text),
            sep=",",
            quotechar='"',
            on_bad_lines="skip",
            dtype=str,
        )

        for col in ["UTI_TOTAL_EXIST", "COMP"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        latest_comp = df["COMP"].max()
        df_latest = df[df["COMP"] == latest_comp]

        icu_by_uf = df_latest.groupby("UF")["UTI_TOTAL_EXIST"].sum().to_dict()
        brazil_total = int(df_latest["UTI_TOTAL_EXIST"].sum())
        icu_by_uf = {k: int(v) for k, v in icu_by_uf.items()}
        city_beds = (
            df_latest.groupby(["UF", "MUNICIPIO"])["UTI_TOTAL_EXIST"]
            .sum()
            .reset_index()
        )
        icu_by_city = {}
        for _, row in city_beds.iterrows():
            uf = row["UF"]
            city_name = _normalize_city_name(str(row["MUNICIPIO"]))
            key = (uf, city_name)
            icu_by_city[key] = int(row["UTI_TOTAL_EXIST"])

        return {
            "competency": int(latest_comp),
            "icu_beds_by_uf": icu_by_uf,
            "icu_beds_by_city": icu_by_city,
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
        - icu_beds_by_city: Dict mapping (UF, city_name) -> ICU bed count
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
        "icu_beds_by_city": {},
        "brazil_total": FALLBACK_BRAZIL_TOTAL,
        "source": "fallback",
    }


def get_location_icu_beds(
    uf: str | None = None,
    city_code: str | None = None,
) -> tuple[int | None, str]:
    """
    Get ICU bed count for a specific location.

    Args:
        uf: State code (e.g., "SP", "RJ") or None for Brazil total.
        city_code: IBGE city code (6 digits). Converts to city name for lookup.

    Returns:
        Tuple of (bed_count, source_description).
        bed_count is None if location not found.

    """
    data = get_icu_beds_data()
    source = f"CNES {data.get('competency', 'N/A')} ({data.get('source', 'unknown')})"

    if city_code:
        from tools.location_utils import resolve_city_name

        city_name = resolve_city_name(city_code)
        if not city_name:
            return None, "city not found"

        normalized_city = _normalize_city_name(city_name)
        state_code = str(city_code)[:2]
        uf_from_code = IBGE_STATE_TO_UF.get(state_code)
        if not uf_from_code:
            return None, "invalid city code"

        city_key = (uf_from_code, normalized_city)
        beds = data.get("icu_beds_by_city", {}).get(city_key)
        if beds is not None:
            return beds, source

        return None, "city-level ICU data not found in CNES"

    if uf:
        uf_upper = uf.upper()
        beds = data.get("icu_beds_by_uf", {}).get(uf_upper)
        return beds, source

    # National total
    return data.get("brazil_total"), source
