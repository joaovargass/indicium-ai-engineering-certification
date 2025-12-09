"""Common module - shared configuration and utilities."""

from common.config import (
    CACHE_DIR,
    DASH_CACHE_PATH,
    DATA_DIR,
    # Defaults
    DEFAULT_DAYS,
    DEFAULT_MODEL_NAME,
    DEFAULT_MONTHS,
    DEFAULT_TEMPERATURE,
    MAX_NEWS_ARTICLES,
    NO_DATA_MESSAGE_CHARTS,
    # Error messages
    NO_DATA_MESSAGE_METRICS,
    # Paths
    PROJECT_ROOT,
    REPORTS_DIR,
    SRC_PATH,
)

__all__ = [
    "PROJECT_ROOT",
    "SRC_PATH",
    "DATA_DIR",
    "CACHE_DIR",
    "REPORTS_DIR",
    "DASH_CACHE_PATH",
    "DEFAULT_DAYS",
    "DEFAULT_MONTHS",
    "MAX_NEWS_ARTICLES",
    "DEFAULT_MODEL_NAME",
    "DEFAULT_TEMPERATURE",
    "NO_DATA_MESSAGE_METRICS",
    "NO_DATA_MESSAGE_CHARTS",
]
