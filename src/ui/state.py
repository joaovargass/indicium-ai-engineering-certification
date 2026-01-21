"""ELT status state management."""

from datetime import datetime

import diskcache

from common.logging import logger
from common.config import ELT_STATUS_CACHE_DIR, ELT_STATUS_TIMEOUT_SECONDS

# Initialize server-side cache
ELT_STATUS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_elt_status_cache = diskcache.Cache(str(ELT_STATUS_CACHE_DIR))


def get_elt_running_status() -> bool:
    """Check if ELT is currently running. Auto-resets if stuck too long."""
    status = _elt_status_cache.get("elt_status", {})

    if not isinstance(status, dict):
        _elt_status_cache.delete("elt_status")
        return False

    if not status.get("running"):
        return False

    # Check if stuck
    started_at = status.get("started_at")
    if started_at:
        try:
            started_time = datetime.fromisoformat(started_at)
            elapsed = (datetime.now() - started_time).total_seconds()
            if elapsed > ELT_STATUS_TIMEOUT_SECONDS:
                logger.warning(f"ELT status auto-reset: stuck for {elapsed / 60:.1f} minutes")
                set_elt_running_status(False)
                return False
        except (ValueError, TypeError) as e:
            logger.warning("started_at inválido em elt_status: %s", e)

    return True


def set_elt_running_status(running: bool) -> None:
    """Set ELT running status with timestamp."""
    if running:
        _elt_status_cache.set(
            "elt_status",
            {"running": True, "started_at": datetime.now().isoformat()},
        )
    else:
        _elt_status_cache.set("elt_status", {"running": False})
