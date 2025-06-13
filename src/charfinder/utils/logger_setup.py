"""Custom logging setup utilities for CharFinder.

Features:
- Centralized `charfinder` logger with consistent format and handlers
- Rotating file logging (charfinder.log + rotated backups)
- Console logging:
    - WARNING+ by default (prevents terminal duplication)
    - DEBUG if `log_level=logging.DEBUG` passed (for --debug flag)
- Environment name (e.g., DEV, UAT, PROD) injected into each log record

Typical Usage:
    from charfinder.utils.logger_setup import setup_logging
    setup_logging()

Functions:
    get_logger(): Return the central project logger.
    setup_logging(): Attach console/file handlers.
    teardown_logger(): Cleanly detach all logging handlers.
    get_default_formatter(): Return default SafeFormatter instance.

Classes:
    EnvironmentFilter: Injects `record.env` into each log message.
    CustomRotatingFileHandler: Renames rotated logs as `charfinder_1.log`, etc.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

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
from charfinder.utils.formatter import echo
from charfinder.utils.logger_helpers import (
    CustomRotatingFileHandler,
    EnvironmentFilter,
    SafeFormatter,
    StreamFilter,
)
from charfinder.utils.logger_styles import format_settings

__all__ = [
    "CustomRotatingFileHandler",
    "EnvironmentFilter",
    "get_default_formatter",
    "get_logger",
    "setup_logging",
    "teardown_logger",
]

LOGGER_NAME = "charfinder"

# ---------------------------------------------------------------------
# Logger Access Functions
# ---------------------------------------------------------------------


def get_logger() -> logging.Logger:
    """Return the central project logger."""
    return logging.getLogger(LOGGER_NAME)


def ensure_filter(handler: logging.Handler, filt: logging.Filter) -> None:
    """Ensure the filter is applied only once to a handler."""
    if not any(isinstance(existing, type(filt)) for existing in handler.filters):
        handler.addFilter(filt)


def get_default_formatter() -> logging.Formatter:
    """Return default SafeFormatter instance."""
    return SafeFormatter(const.LOG_FORMAT)


# ---------------------------------------------------------------------
# Logging Setup Functions
# ---------------------------------------------------------------------


def setup_logging(  # noqa: PLR0913
    log_dir: Path | None = None,
    log_level: int | None = None,
    *,
    reset: bool = False,
    return_handlers: bool = False,
    suppress_echo: bool = False,
    use_color: bool = True,
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
        suppress_echo: If True, suppress terminal output showing.
        use_color: If True, shows color.

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
    stream_handler.addFilter(StreamFilter())

    console_level = logging.INFO
    if log_level is not None:
        console_level = log_level

    stream_handler.setLevel(console_level)
    logger.addHandler(stream_handler)

    # Custom rotating file handler — always DEBUG
    max_bytes = get_log_max_bytes()
    backup_count = get_log_backup_count()

    custom_file_handler = CustomRotatingFileHandler(
        filename=str(log_file_path),
        mode="a",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding=const.DEFAULT_ENCODING,
        delay=False,
    )
    custom_file_handler.setFormatter(formatter)
    ensure_filter(custom_file_handler, env_filter)
    custom_file_handler.setLevel(logging.DEBUG)
    logger.addHandler(custom_file_handler)

    # Final confirmation log after all handlers are attached
    if not suppress_echo:
        message = (
            f'Logging initialized. Log file: "{log_file_path}" '
            f"(maxBytes={max_bytes}, backupCount={backup_count})"
        )
        echo(
            msg=message,
            style=lambda m: format_settings(m, use_color=use_color),
            show=True,
            log=False,
            log_method="info",
        )

    return [stream_handler, custom_file_handler] if return_handlers else None


def teardown_logger(logger: logging.Logger | None = None) -> None:
    """
    Cleanly detach all handlers from the logger.

    Args:
        logger: Target logger to tear down. Defaults to project logger.
    """
    logger = logger or get_logger()

    for handler in logger.handlers[:]:
        with contextlib.suppress(Exception):
            handler.flush()
        with contextlib.suppress(Exception):
            handler.close()
        logger.removeHandler(handler)
