"""Location filter utilities."""

import json

import requests

from common.config import (
    CITY_MAPPING_PATH,
    IBGE_MUNICIPIOS_ID_KEY,
    IBGE_MUNICIPIOS_NOME_KEY,
    IBGE_MUNICIPIOS_URL,
    LOCATION_REQUEST_TIMEOUT_SECONDS,
)
from common.logging import logger


def resolve_city_name(city_code: str) -> str | None:
    """
    Get city name from 6-digit IBGE code using cached API data.

    Args:
        city_code: 6-digit IBGE city code

    Returns:
        City name if found, None otherwise

    """
    if CITY_MAPPING_PATH.exists():
        try:
            with open(CITY_MAPPING_PATH, encoding="utf-8") as f:
                mapping = json.load(f)
            return mapping.get(str(city_code))
        except Exception as e:
            logger.warning(
                "Error loading city mapping cache %s: %s", CITY_MAPPING_PATH, e
            )

    try:
        response = requests.get(
            IBGE_MUNICIPIOS_URL,
            timeout=LOCATION_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()

        mapping = {}
        for city in data:
            raw_id = city.get(IBGE_MUNICIPIOS_ID_KEY)
            raw_nome = city.get(IBGE_MUNICIPIOS_NOME_KEY)
            if raw_id is not None and raw_nome is not None:
                code_6digit = str(raw_id)[:6]
                if code_6digit not in mapping:
                    mapping[code_6digit] = str(raw_nome)

        CITY_MAPPING_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CITY_MAPPING_PATH, "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)

        return mapping.get(str(city_code))
    except Exception as e:
        logger.warning("Error fetching municipalities from IBGE API: %s", e)
        return None


def determine_location_filter(
    uf: str | None = None, city_code: str | None = None
) -> tuple[str | None, str | None]:
    """Return (column, value) tuple for location filtering."""
    if city_code:
        return "CO_MUN_NOT", city_code
    if uf:
        return "SG_UF_NOT", uf.upper()
    return None, None


def get_location_description(
    uf: str | None = None, city_code: str | None = None
) -> str:
    """Return human-readable location description."""
    if city_code:
        city_name = resolve_city_name(city_code)
        if city_name:
            return city_name
        return f"Cidade código {city_code}"
    if uf:
        return uf.upper()
    return "Brasil (nacional)"
