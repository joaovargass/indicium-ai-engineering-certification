"""Unified logging via loguru: console (stderr) and logs/app.log with rotation. Import logger from common.logging."""

import sys

from loguru import logger

from common.config import PROJECT_ROOT

LOGS_DIR = PROJECT_ROOT / "logs"


def setup_logging(
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
) -> None:
    """
    Configure loguru for the application.

    Args:
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
        log_to_file: Enable file logging
        log_to_console: Enable console logging

    """
    # Remove default handler
    logger.remove()

    # Console handler with colored output
    if log_to_console:
        logger.add(
            sys.stderr,
            level=level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            colorize=True,
        )

    # File handler with rotation
    if log_to_file:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        logger.add(
            LOGS_DIR / "app.log",
            level=level,
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | "
                "{level: <8} | "
                "{name}:{function}:{line} | "
                "{message}"
            ),
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            encoding="utf-8",
        )


# Initialize logging on import
setup_logging()

# Re-export logger for use in other modules
__all__ = ["logger", "setup_logging"]
