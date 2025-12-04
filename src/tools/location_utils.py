"""Location filter utilities."""


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
        return f"Código IBGE {city_code}"
    if uf:
        return uf.upper()
    return "Brasil (todos os estados)"
