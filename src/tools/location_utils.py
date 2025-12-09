"""Location filter utilities."""

import json

import requests

from common.config import CITY_MAPPING_PATH, LOCATION_REQUEST_TIMEOUT_SECONDS


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
        except Exception:
            pass

    try:
        response = requests.get(
            "https://servicodados.ibge.gov.br/api/v1/localidades/municipios",
            timeout=LOCATION_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()

        mapping = {}
        for city in data:
            code_6digit = str(city["id"])[:6]
            if code_6digit not in mapping:
                mapping[code_6digit] = city["nome"]

        CITY_MAPPING_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CITY_MAPPING_PATH, "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)

        return mapping.get(str(city_code))
    except Exception:
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
