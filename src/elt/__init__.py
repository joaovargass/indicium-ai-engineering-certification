"""ELT module for SRAG data processing."""

from elt.azure import get_client
from elt.cache import NoDataAvailableError, load_srag_data
from elt.deltas import (
    download_unprocessed_deltas,
    get_unprocessed_deltas,
    mark_deltas_processed,
    upload_frozen_delta,
    upload_live_delta,
)
from elt.dw import read_from_dw, save_to_dw
from elt.reset import reset_all_state
from elt.state import (
    get_extraction_date,
    load_dw_state,
    load_raw_state,
    save_dw_state,
    save_raw_state,
    update_extraction_date,
)

__all__ = [
    # Azure client
    "get_client",
    # Cache/data loading
    "NoDataAvailableError",
    "load_srag_data",
    # State management
    "load_raw_state",
    "save_raw_state",
    "load_dw_state",
    "save_dw_state",
    "get_extraction_date",
    "update_extraction_date",
    # Delta operations
    "upload_frozen_delta",
    "upload_live_delta",
    "get_unprocessed_deltas",
    "download_unprocessed_deltas",
    "mark_deltas_processed",
    # DW operations
    "read_from_dw",
    "save_to_dw",
    # Reset
    "reset_all_state",
]
