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
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path

from charfinder import constants as const
from charfinder.settings import (
    get_environment,
    get_log_backup_count,
    get_log_dir,
    get_log_max_bytes,
)

LOGGER_NAME = "charfinder"

__all__ = [
    "LOGGER_NAME",
    "CustomRotatingFileHandler",
    "EnvironmentFilter",
    "get_default_formatter",
    "setup_logging",
    "teardown_logger",
]


class CustomRotatingFileHandler(RotatingFileHandler):
    """Custom handler with renamed rotated logs:
    charfinder.log, charfinder_1.log, charfinder_2.log."""

    def rotation_filename(self, default_name: str) -> str:
        """Rename rotated files: charfinder.log.1 → charfinder_1.log"""
        if default_name.endswith(".log"):
            return default_name
        if ".log." in default_name:
            base, suffix = default_name.rsplit(".log.", maxsplit=1)
            return f"{base}_{suffix}.log"
        return default_name

    def do_rollover(self) -> None:
        """Override base class to support custom filename logic."""
        if self.stream:
            self.stream.close()
            self.stream = None  # type: ignore[assignment]

        if self.backupCount > 0:
            for path in self.get_files_to_delete():
                with contextlib.suppress(OSError):
                    path.unlink()

            for i in range(self.backupCount - 1, 0, -1):
                src = Path(self.rotation_filename(f"{self.baseFilename}.{i}"))
                dst = Path(self.rotation_filename(f"{self.baseFilename}.{i + 1}"))
                if src.exists():
                    if dst.exists():
                        dst.unlink()
                    src.rename(dst)

            rollover_path = Path(self.rotation_filename(f"{self.baseFilename}.1"))
            current_log = Path(self.baseFilename)
            if current_log.exists():
                current_log.rename(rollover_path)

        if not self.delay:
            self.stream = self._open()

    def get_files_to_delete(self) -> list[Path]:
        """Return rotated log files to delete to enforce backup count."""
        base_path = Path(self.baseFilename)
        prefix = base_path.stem
        ext = base_path.suffix
        pattern = re.compile(rf"^{re.escape(prefix)}_(\d+){re.escape(ext)}$")

        return sorted(
            [p for p in base_path.parent.iterdir() if pattern.match(p.name)],
            key=lambda p: p.stat().st_mtime,
        )[: -self.backupCount]


class EnvironmentFilter(logging.Filter):
    """Injects the current environment (e.g., DEV, UAT, PROD) into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.env = get_environment()
        return True


def ensure_filter(handler: logging.Handler, filt: logging.Filter) -> None:
    """Ensure the filter is applied only once to a handler."""
    if not any(isinstance(existing, type(filt)) for existing in handler.filters):
        handler.addFilter(filt)


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
    logger = logging.getLogger(LOGGER_NAME)

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

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    resolved_dir = log_dir or get_log_dir()
    resolved_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = resolved_dir / const.LOG_FILE_NAME

    formatter = get_default_formatter()
    env_filter = EnvironmentFilter()

    # Console handler — WARNING+ by default, DEBUG if log_level param passed
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    ensure_filter(stream_handler, env_filter)

    console_level = logging.WARNING  # default
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
    logger.info(
        "Logging initialized. Log file: %s (maxBytes=%d, backupCount=%d)",
        log_file_path,
        get_log_max_bytes(),
        get_log_backup_count(),
    )

    return [stream_handler, custom_file_handler] if return_handlers else None


def teardown_logger(logger: logging.Logger | None = None) -> None:
    """
    Cleanly detach all handlers from the logger.

    Args:
        logger: Target logger to tear down. Defaults to project logger.
    """
    logger = logger or logging.getLogger(LOGGER_NAME)
    for handler in logger.handlers[:]:
        with contextlib.suppress(Exception):
            handler.flush()
        with contextlib.suppress(Exception):
            handler.close()
        logger.removeHandler(handler)
