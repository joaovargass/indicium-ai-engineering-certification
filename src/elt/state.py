"""ELT state: raw_state (deltas, processed_years, last_live_date) and dw_state (processed_deltas, last_max_notific) in Azure."""

import concurrent.futures

import diskcache
from azure.storage.filedatalake import FileSystemClient

from common.logging import logger
from common.config import DW_STATE_PATH, ELT_STATUS_CACHE_DIR, RAW_STATE_PATH
from elt.azure import _read_json, _write_json, get_client

_EXTRACTION_DATE_CACHE = diskcache.Cache(str(ELT_STATUS_CACHE_DIR))


def _get_default_raw_state() -> dict:
    """Return default raw state structure."""
    return {
        "processed_years": [],
        "current_year": None,
        "last_live_date": None,
        "last_extraction_date": None,
        "deltas": [],
    }


def _get_default_dw_state() -> dict:
    """Return default DW state structure."""
    return {
        "last_max_notific": 0,
        "processed_deltas": [],
        "last_upload_timestamp": None,
        "total_rows": 0,
    }


def load_raw_state(client: FileSystemClient) -> dict:
    """Load raw data state from Azure."""
    state = _read_json(client, RAW_STATE_PATH)
    if state is None:
        return _get_default_raw_state()
    return state


def save_raw_state(client: FileSystemClient, state: dict) -> None:
    """Save raw data state to Azure."""
    _write_json(client, RAW_STATE_PATH, state)
    logger.info(f"Raw state saved: {len(state.get('deltas', []))} deltas tracked")


def update_extraction_date(client: FileSystemClient, extraction_date: str) -> None:
    """Update last extraction date in raw state."""
    state = load_raw_state(client)
    state["last_extraction_date"] = extraction_date
    save_raw_state(client, state)


def _fetch_extraction_date_from_azure() -> str | None:
    """Fetch last extraction date from Azure. Used in a thread with timeout."""
    client = get_client()
    state = load_raw_state(client)
    return state.get("last_extraction_date")


def cache_extraction_date_local(extraction_date: str) -> None:
    """Store extraction date locally to avoid Azure on page load when ELT is busy."""
    _EXTRACTION_DATE_CACHE.set("last_extraction_date", extraction_date)


def get_extraction_date() -> str | None:
    """Get last extraction date: local cache first, then Azure with 5s timeout."""
    local = _EXTRACTION_DATE_CACHE.get("last_extraction_date")
    if local is not None:
        return local
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            f = ex.submit(_fetch_extraction_date_from_azure)
            res = f.result(timeout=5)
        if res is not None:
            _EXTRACTION_DATE_CACHE.set("last_extraction_date", res)
        return res
    except Exception:
        return _EXTRACTION_DATE_CACHE.get("last_extraction_date")


def _fetch_last_live_date_from_azure() -> str | None:
    """Fetch last live date (vivo) from Azure raw_state. Used in a thread with timeout."""
    client = get_client()
    state = load_raw_state(client)
    return state.get("last_live_date")


def get_last_live_date() -> str | None:
    """Get last live date (vivo) from raw_state: Azure with 5s timeout. Format dd-mm-yyyy."""
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            f = ex.submit(_fetch_last_live_date_from_azure)
            return f.result(timeout=5)
    except Exception:
        return None


def load_dw_state(client: FileSystemClient) -> dict:
    """Load DW state from Azure."""
    state = _read_json(client, DW_STATE_PATH)
    if state is None:
        return _get_default_dw_state()
    return state


def save_dw_state(client: FileSystemClient, state: dict) -> None:
    """Save DW state to Azure."""
    _write_json(client, DW_STATE_PATH, state)
    logger.info(f"DW state saved: last_max_notific={state.get('last_max_notific')}")
