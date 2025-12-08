"""State management for ELT pipeline."""

from azure.storage.filedatalake import FileSystemClient

from common.config import DW_STATE_PATH, RAW_STATE_PATH
from elt.azure import _read_json, _write_json, get_client


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
    print(f"Raw state saved: {len(state.get('deltas', []))} deltas tracked")


def update_extraction_date(client: FileSystemClient, extraction_date: str) -> None:
    """Update last extraction date in raw state."""
    state = load_raw_state(client)
    state["last_extraction_date"] = extraction_date
    save_raw_state(client, state)


def get_extraction_date() -> str | None:
    """Get last extraction date from raw state."""
    client = get_client()
    state = load_raw_state(client)
    return state.get("last_extraction_date")


def load_dw_state(client: FileSystemClient) -> dict:
    """Load DW state from Azure."""
    state = _read_json(client, DW_STATE_PATH)
    if state is None:
        return _get_default_dw_state()
    return state


def save_dw_state(client: FileSystemClient, state: dict) -> None:
    """Save DW state to Azure."""
    _write_json(client, DW_STATE_PATH, state)
    print(f"DW state saved: last_max_notific={state.get('last_max_notific')}")
