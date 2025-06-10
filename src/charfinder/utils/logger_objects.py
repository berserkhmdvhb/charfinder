import contextlib
import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal

from charfinder.settings import get_environment


class EnvironmentFilter(logging.Filter):
    """Injects the current environment (e.g., DEV, UAT, PROD) into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.env = get_environment()
        return True


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
        if not hasattr(record, "env"):
            record.env = "UNKNOWN"
        return super().format(record)


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
