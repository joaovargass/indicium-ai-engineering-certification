"""
Data loading module - backward compatibility facade.

This module re-exports public ELT functionality for backward compatibility.
New code should import directly from the appropriate submodules:
- elt.azure: Azure client operations
- elt.state: State management
- elt.deltas: Delta file operations
- elt.dw: Data warehouse operations
- elt.cache: Cache and data loading

Note: Private functions (prefixed with _) are not re-exported.
Import them directly from their source modules if needed.

"""

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
from elt.state import (
    cache_extraction_date_local,
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
    # State management
    "load_raw_state",
    "save_raw_state",
    "load_dw_state",
    "save_dw_state",
    "get_extraction_date",
    "update_extraction_date",
    "cache_extraction_date_local",
    # Delta operations
    "upload_frozen_delta",
    "upload_live_delta",
    "get_unprocessed_deltas",
    "download_unprocessed_deltas",
    "mark_deltas_processed",
    # DW operations
    "read_from_dw",
    "save_to_dw",
    # Cache
    "NoDataAvailableError",
    "load_srag_data",
]
