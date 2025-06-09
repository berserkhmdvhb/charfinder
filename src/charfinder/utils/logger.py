"""
Custom logging setup utilities for CharFinder.

- Centralized `charfinder` logger with consistent format and handlers
- Rotating file logging (charfinder.log + rotated backups)
- Console logging with DEBUG/INFO level
- Optional debug logging of .env file and settings

Typical Usage:
    from charfinder.cli.utils_logger import setup_logging
    setup_logging()

Exports:
    - LOGGER_NAME: Central logger identifier
    - setup_logging: Attach console/file handlers
    - teardown_logger: Cleanly detach all logging handlers
"""

from __future__ import annotations

import contextlib
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from charfinder import constants as const
from charfinder.settings import load_settings, safe_int
from charfinder.utils.formatter import format_debug

LOGGER_NAME = "charfinder"

__all__ = [
    "LOGGER_NAME",
    "setup_logging",
    "teardown_logger",
]


class EnvironmentFilter(logging.Filter):
    """Injects the current environment (e.g., DEV, UAT, PROD) into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        from charfinder.settings import get_environment

        record.env = get_environment()
        return True


def get_default_formatter() -> logging.Formatter:
    """Return default log formatter."""
    return logging.Formatter(const.LOG_FORMAT)


def setup_logging(
    log_dir: Path | None = None,
    log_level: int | None = None,
    *,
    reset: bool = False,
    return_handlers: bool = False,
) -> list[logging.Handler] | None:
    """
    Set up logging to both console and file.

    Args:
        log_dir: Optional directory to store the log file.
        log_level: Optional log level for console output.
        reset: If True, clears existing handlers before reconfiguring.
        return_handlers: If True, returns the list of attached handlers.

    Returns:
        List of handlers if return_handlers is True; otherwise None.
    """
    load_settings()  # Ensure .env is loaded

    logger = logging.getLogger("charfinder")

    if logger.hasHandlers() and not reset:
        return None

    if reset:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    resolved_dir = log_dir or const.DEFAULT_LOG_ROOT
    resolved_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = resolved_dir / const.LOG_FILE_NAME

    formatter = get_default_formatter()
    env_filter = EnvironmentFilter()
    # Console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(env_filter)
    stream_handler.setLevel(
        log_level
        if log_level is not None
        else (logging.DEBUG if _is_debug_mode() else logging.INFO)
    )
    logger.addHandler(stream_handler)

    # Rotating file handler
    file_handler = RotatingFileHandler(
        filename=str(log_file_path),
        mode="a",
        maxBytes=safe_int(const.ENV_LOG_MAX_BYTES, 1_000_000),
        backupCount=safe_int(const.ENV_LOG_BACKUP_COUNT, 5),
        encoding=const.DEFAULT_ENCODING,
        delay=True,
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(env_filter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    if _is_debug_mode():
        message = f"Logging initialized in %s with level DEBUG, {resolved_dir}"
        sys.stdout.write(format_debug(message) + "\n")

    return [stream_handler, file_handler] if return_handlers else None


def teardown_logger(logger: logging.Logger | None = None) -> None:
    """
    Cleanly detach all handlers from the logger.

    Args:
        logger: Target logger to tear down. Defaults to project logger.
    """
    logger = logger or logging.getLogger("charfinder")
    for handler in logger.handlers[:]:
        with contextlib.suppress(Exception):
            handler.flush()
        with contextlib.suppress(Exception):
            handler.close()
        logger.removeHandler(handler)


def _is_debug_mode() -> bool:
    """Return True if CHARFINDER_DEBUG_ENV_LOAD=1."""
    return os.getenv(const.ENV_DEBUG_ENV_LOAD) == "1"
