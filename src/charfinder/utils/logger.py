"""
Custom logging setup utilities for CharFinder.

- Centralized `charfinder` logger with consistent format and handlers
- Rotating file logging (charfinder.log + rotated backups)
- Console logging:
    - WARNING+ by default (prevents terminal duplication)
    - DEBUG if `log_level=logging.DEBUG` passed (for --debug flag)
- Environment name (e.g., DEV, UAT, PROD) injected into each log record

Typical Usage:
    from charfinder.utils.logger import setup_logging
    setup_logging()

Exports:
    - LOGGER_NAME: Central logger identifier
    - setup_logging: Attach console/file handlers
    - teardown_logger: Cleanly detach all logging handlers
    - EnvironmentFilter: Injects `record.env` into each log message
    - CustomRotatingFileHandler: Renames rotated logs as `charfinder_1.log`, etc.
"""

from __future__ import annotations

import contextlib
import logging
from pathlib import Path

from charfinder import constants as const
from charfinder.settings import (
    get_log_backup_count,
    get_log_dir,
    get_log_max_bytes,
)
from charfinder.utils.logger_objects import (
    CustomRotatingFileHandler,
    EnvironmentFilter,
    SafeFormatter,
)

__all__ = [
    "CustomRotatingFileHandler",
    "EnvironmentFilter",
    "get_default_formatter",
    "setup_logging",
    "teardown_logger",
]

LOGGER_NAME = "charfinder"


def get_logger() -> logging.Logger:
    """Return the central project logger."""
    return logging.getLogger(LOGGER_NAME)


def ensure_filter(handler: logging.Handler, filt: logging.Filter) -> None:
    """Ensure the filter is applied only once to a handler."""
    if not any(isinstance(existing, type(filt)) for existing in handler.filters):
        handler.addFilter(filt)


def get_default_formatter() -> logging.Formatter:
    """Return default log formatter."""
    return SafeFormatter(const.LOG_FORMAT)


def setup_logging(
    log_dir: Path | None = None,
    log_level: int | None = None,
    *,
    reset: bool = False,
    return_handlers: bool = False,
) -> list[logging.Handler] | None:
    """
    Set up logging to both console and file.

    Console handler:
        - WARNING+ by default to avoid terminal duplication
        - DEBUG if `log_level=logging.DEBUG` passed (for --debug flag)

    File handler:
        - Always DEBUG+

    Args:
        log_dir: Optional directory to store the log file.
        log_level: Optional log level for console output (for --debug).
        reset: If True, clears existing handlers before reconfiguring.
        return_handlers: If True, returns the list of attached handlers.

    Returns:
        List of handlers if return_handlers is True; otherwise None.
    """
    logger = get_logger()
    if reset:
        teardown_logger(logger)

    # Idempotent protection:
    # Check if already correctly configured
    existing_handler_types = {type(h) for h in logger.handlers}
    expected_handler_types = {logging.StreamHandler, CustomRotatingFileHandler}

    if existing_handler_types == expected_handler_types and not reset:
        return None  # Already configured — skip re-setup

    # Clean existing if partial config detected
    if logger.hasHandlers():
        teardown_logger(logger)

    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    resolved_dir = log_dir or get_log_dir()
    resolved_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = resolved_dir / const.LOG_FILE_NAME

    formatter = get_default_formatter()
    env_filter = EnvironmentFilter()

    # Console handler — WARNING+ by default, DEBUG if log_level param passed
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    ensure_filter(stream_handler, env_filter)

    console_level = logging.INFO
    if log_level is not None:
        console_level = log_level

    stream_handler.setLevel(console_level)
    logger.addHandler(stream_handler)

    # Custom rotating file handler — always DEBUG
    custom_file_handler = CustomRotatingFileHandler(
        filename=str(log_file_path),
        mode="a",
        maxBytes=get_log_max_bytes(),
        backupCount=get_log_backup_count(),
        encoding=const.DEFAULT_ENCODING,
        delay=True,
    )
    custom_file_handler.setFormatter(formatter)
    ensure_filter(custom_file_handler, env_filter)
    custom_file_handler.setLevel(logging.DEBUG)
    logger.addHandler(custom_file_handler)

    # Final confirmation log after all handlers are attached — avoid using debug()
    mb, bc = get_log_max_bytes(), get_log_backup_count()
    message = f"Logging initialized. Log file: {log_file_path} (maxBytes={mb}, backupCount={bc})"
    logger.info(message)
    return [stream_handler, custom_file_handler] if return_handlers else None


def teardown_logger(logger: logging.Logger | None = None) -> None:
    """
    Cleanly detach all handlers from the logger.

    Args:
        logger: Target logger to tear down. Defaults to project logger.
    """
    logger = get_logger()
    for handler in logger.handlers[:]:
        with contextlib.suppress(Exception):
            handler.flush()
        with contextlib.suppress(Exception):
            handler.close()
        logger.removeHandler(handler)
