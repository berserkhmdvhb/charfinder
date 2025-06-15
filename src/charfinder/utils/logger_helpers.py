"""Logger helpers and custom classes for CharFinder.

Provides helpers for advanced logging behavior in CharFinder.

Classes:
    EnvironmentFilter: Injects current environment into log records.
    SafeFormatter: Formatter that handles missing LogRecord attributes safely.
    CustomRotatingFileHandler: Rotating file handler with custom filename scheme:
        charfinder.log → charfinder_1.log, charfinder_2.log, etc.
    StreamFilter: Filter that disables StreamHandler output when suppression is active.

Functions:
    suppress_console_logging():
        Context manager to temporarily suppress StreamHandler (console) output.
"""

from __future__ import annotations

import logging
import re
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from io import TextIOWrapper
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal, cast

from charfinder.utils.logger_styles import format_warning

__all__ = [
    "CustomRotatingFileHandler",
    "EnvironmentFilter",
    "SafeFormatter",
    "StreamFilter",
    "suppress_console_logging",
]

logger = logging.getLogger("charfinder.logger")

# ---------------------------------------------------------------------
# Console Output Suppression
# ---------------------------------------------------------------------

_SUPPRESS_CONSOLE_OUTPUT = threading.local()
_SUPPRESS_CONSOLE_OUTPUT.value = False


class StreamFilter(logging.Filter):
    """Filter that disables StreamHandler output if suppression is active."""

    def filter(self, _record: logging.LogRecord) -> bool:
        return not getattr(_SUPPRESS_CONSOLE_OUTPUT, "value", False)


@contextmanager
def suppress_console_logging() -> Iterator[None]:
    """
    Context manager to temporarily suppress StreamHandler (console) output.
    Thread-safe version using global flag + StreamFilter.
    """
    old_value = getattr(_SUPPRESS_CONSOLE_OUTPUT, "value", False)
    _SUPPRESS_CONSOLE_OUTPUT.value = True
    try:
        yield
    finally:
        _SUPPRESS_CONSOLE_OUTPUT.value = old_value


# ---------------------------------------------------------------------
# Log Record Filters
# ---------------------------------------------------------------------


class EnvironmentFilter(logging.Filter):
    """Injects the current environment (e.g., DEV, UAT, PROD) into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        from charfinder.settings import get_environment

        record.env = get_environment()
        return True


# ---------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------


class SafeFormatter(logging.Formatter):
    """Formatter that substitutes missing LogRecord attributes with defaults."""

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
    ) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "env") or not isinstance(record.env, str):
            record.env = "UNKNOWN"
        return super().format(record)


# ---------------------------------------------------------------------
# Custom File Handlers
# ---------------------------------------------------------------------


class CustomRotatingFileHandler(RotatingFileHandler):
    """
    Rotating file handler with custom filename scheme.

    Behavior:
        charfinder.log → charfinder_1.log, charfinder_2.log, ...
    """

    def rotation_filename(self, default_name: str) -> str:
        if default_name.endswith(".log"):
            return default_name
        if ".log." in default_name:
            base, suffix = default_name.rsplit(".log.", maxsplit=1)
            return f"{base}_{suffix}.log"
        return default_name

    def do_rollover(self) -> None:
        self._close_stream()

        if self.backupCount > 0:
            self._delete_old_logs()
            self._rotate_existing_logs()

        if not self.delay:
            self.stream = self._open()

    def _close_stream(self) -> None:
        if self.stream:
            self.stream.close()
            self.stream = None  # type: ignore[assignment]

    def _delete_old_logs(self) -> None:
        for path in self.get_files_to_delete():
            try:
                path.unlink()
            except OSError:  # noqa: PERF203
                from charfinder.utils.formatter import log_optionally_echo

                message = f"Failed to delete old log file: {path}"
                log_optionally_echo(
                    message,
                    level="warning",
                    show=False,
                    style=format_warning,
                )

    def _rotate_existing_logs(self) -> None:
        from charfinder.utils.formatter import log_optionally_echo

        for i in range(self.backupCount - 1, 0, -1):
            src = Path(self.rotation_filename(f"{self.baseFilename}.{i}"))
            dst = Path(self.rotation_filename(f"{self.baseFilename}.{i + 1}"))
            if src.exists():
                if dst.exists():
                    try:
                        dst.unlink()
                    except OSError:
                        message = f"Failed to delete rollover target: {dst}"
                        log_optionally_echo(
                            message,
                            level="warning",
                            show=False,
                            style=format_warning,
                        )
                        continue
                src.rename(dst)

        rollover_path = Path(self.rotation_filename(f"{self.baseFilename}.1"))
        current_log = Path(self.baseFilename)
        if current_log.exists():
            if rollover_path.exists():
                try:
                    rollover_path.unlink()
                except OSError:
                    message = f"Failed to delete existing rollover log: {rollover_path}"
                    log_optionally_echo(
                        message,
                        level="warning",
                        show=False,
                        style=format_warning,
                    )
                    return
            current_log.rename(rollover_path)

    def _open(self) -> TextIOWrapper:
        """Open log file using UTF-8 encoding to ensure consistent Unicode support."""
        return cast("TextIOWrapper", Path(self.baseFilename).open(self.mode, encoding="utf-8"))

    def get_files_to_delete(self) -> list[Path]:
        base_path = Path(self.baseFilename)
        prefix = base_path.stem
        ext = base_path.suffix
        pattern = re.compile(rf"^{re.escape(prefix)}_(\d+){re.escape(ext)}$")

        return sorted(
            [p for p in base_path.parent.iterdir() if pattern.match(p.name)],
            key=lambda p: p.stat().st_mtime,
        )[: -self.backupCount]
