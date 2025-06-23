"""Unit tests for charfinder.utils.logger_helpers.

Covers:
- StreamFilter behavior
- suppress_console_logging context manager
- EnvironmentFilter enrichment
- SafeFormatter robustness
- CustomRotatingFileHandler rotation logic and failure cases
"""

from __future__ import annotations

from io import StringIO
import logging
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager

import pytest
from unittest.mock import patch

from charfinder.utils import logger_helpers as lh
from charfinder.config.types import EchoFunc
from charfinder.config.messages import MSG_WARNING_DELETE_ROLLOVER_TARGET_FAILED
from charfinder.utils.formatter import log_optionally_echo
from charfinder.utils.logger_styles import format_warning

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------
# StreamFilter Tests
# ---------------------------------------------------------------------

def test_stream_filter_blocks_when_suppressed() -> None:
    """StreamFilter disables logging when suppression flag is set."""
    lh._SUPPRESS_CONSOLE_OUTPUT.value = True
    filt = lh.StreamFilter()
    record = logging.LogRecord("x", logging.INFO, "", 0, "msg", None, None)
    assert not filt.filter(record)


def test_stream_filter_allows_when_not_suppressed() -> None:
    """StreamFilter allows logging when suppression flag is not set."""
    lh._SUPPRESS_CONSOLE_OUTPUT.value = False
    filt = lh.StreamFilter()
    record = logging.LogRecord("x", logging.INFO, "", 0, "msg", None, None)
    assert filt.filter(record)


# ---------------------------------------------------------------------
# suppress_console_logging Tests
# ---------------------------------------------------------------------

def test_suppress_console_logging_restores_state() -> None:
    """suppress_console_logging restores the flag after context exit."""
    old_value = getattr(lh._SUPPRESS_CONSOLE_OUTPUT, "value", False)
    with lh.suppress_console_logging():
        assert lh._SUPPRESS_CONSOLE_OUTPUT.value is True
    assert lh._SUPPRESS_CONSOLE_OUTPUT.value == old_value


# ---------------------------------------------------------------------
# EnvironmentFilter Tests
# ---------------------------------------------------------------------

def test_environment_filter_adds_env(patch_env_name: Callable[[str], None]) -> None:
    """EnvironmentFilter adds the environment field to log records."""
    record = logging.LogRecord("x", logging.INFO, "", 0, "msg", None, None)
    env_filter = lh.EnvironmentFilter()
    patch_env_name("DEV_TEST")
    assert env_filter.filter(record)
    assert getattr(record, "env", None) == "DEV_TEST"


# ---------------------------------------------------------------------
# SafeFormatter Tests
# ---------------------------------------------------------------------

def test_safe_formatter_sets_unknown_if_missing() -> None:
    """SafeFormatter sets env=UNKNOWN if not found on record."""
    fmt = lh.SafeFormatter("%(env)s - %(message)s")
    record = logging.LogRecord("x", logging.INFO, "", 0, "hello", None, None)
    assert fmt.format(record).startswith("UNKNOWN")


def test_safe_formatter_preserves_existing_env() -> None:
    """SafeFormatter uses the provided env value if present."""
    fmt = lh.SafeFormatter("%(env)s - %(message)s")
    record = logging.LogRecord("x", logging.INFO, "", 0, "hello", None, None)
    record.env = "PROD"
    assert fmt.format(record).startswith("PROD")


def test_safe_formatter_handles_non_str_env() -> None:
    """SafeFormatter sets UNKNOWN if env is not a string."""
    fmt = lh.SafeFormatter("%(env)s - %(message)s")
    record = logging.LogRecord("x", logging.INFO, "", 0, "hello", None, None)
    record.env = 12345
    assert fmt.format(record).startswith("UNKNOWN")


# ---------------------------------------------------------------------
# CustomRotatingFileHandler Tests
# ---------------------------------------------------------------------

@pytest.fixture
def temp_log_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Fixture to create a dummy log file."""
    f = tmp_path / "charfinder.log"
    f.write_text("initial\n", encoding="utf-8")
    yield f


def test_rotation_filename_variants(tmp_path: Path) -> None:
    """rotation_filename transforms .log.N into charfinder_N.log."""
    handler = lh.CustomRotatingFileHandler(tmp_path / "charfinder.log")
    assert handler.rotation_filename("charfinder.log") == "charfinder.log"
    assert handler.rotation_filename("charfinder.log.1") == "charfinder_1.log"
    assert handler.rotation_filename("other.txt") == "other.txt"


def test_get_files_to_delete_respects_backup_count(tmp_path: Path) -> None:
    """get_files_to_delete returns old rotated files beyond limit."""
    base_file = tmp_path / "charfinder.log"
    base_file.write_text("base", encoding="utf-8")
    files = []

    for i in range(5):
        rotated = tmp_path / f"charfinder_{i+1}.log"
        rotated.write_text(f"log {i}", encoding="utf-8")
        files.append(rotated)
        time.sleep(0.01)  # Ensure mtime order

    handler = lh.CustomRotatingFileHandler(base_file, backupCount=3)
    to_delete = handler.get_files_to_delete()
    expected = sorted(files, key=lambda f: f.stat().st_mtime)[:2]
    assert set(to_delete) == set(expected)


def test_do_rollover_renames_rotated_files(tmp_path: Path) -> None:
    """do_rollover rotates base log and older files correctly."""
    base_file = tmp_path / "charfinder.log"
    base_file.write_text("log content", encoding="utf-8")

    for i in range(1, 3):
        rotated = tmp_path / f"charfinder_{i}.log"
        rotated.write_text(f"old {i}", encoding="utf-8")

    handler = lh.CustomRotatingFileHandler(str(base_file), backupCount=3, delay=False)
    handler.stream = handler._open()
    handler.do_rollover()

    assert base_file.exists()
    assert (tmp_path / "charfinder_1.log").exists()
    assert (tmp_path / "charfinder_3.log").exists()
    handler.stream.close()


def test_do_rollover_opens_new_stream(tmp_path: Path) -> None:
    """do_rollover closes current stream and opens new one."""
    base_file = tmp_path / "charfinder.log"
    handler = lh.CustomRotatingFileHandler(str(base_file), backupCount=1, delay=False)
    handler.stream = handler._open()
    old_stream = handler.stream
    handler.do_rollover()
    assert old_stream.closed
    assert handler.stream is not None
    assert not handler.stream.closed
    handler.stream.close()


# tests/utils/test_logger_helpers.py

# ---------------------------------------------------------------------
# Rollover Behavior
# ---------------------------------------------------------------------

def test_do_rollover_warns_on_unlink_fail(
    tmp_path: Path,
    fail_unlink_for: Callable[[Path], ContextManager[None]],
    debug_logger: logging.Logger,
    log_stream: StringIO,
) -> None:
    """do_rollover logs a warning if a file cannot be deleted."""
    base_file = tmp_path / "charfinder.log"
    base_file.write_text("main", encoding="utf-8")
    failing_file = tmp_path / "charfinder_1.log"
    failing_file.write_text("locked", encoding="utf-8")

    handler = lh.CustomRotatingFileHandler(str(base_file), backupCount=1, delay=False)

    with patch.object(handler, "get_files_to_delete", return_value=[failing_file]):
        with fail_unlink_for(failing_file):
            handler.do_rollover()

    logs = log_stream.getvalue()
    assert "Failed to delete old log file" in logs
    assert str(failing_file) in logs






def test_do_rollover_warns_on_unlink_of_rollover_target(
    tmp_path: Path,
    log_stream: StringIO,
    debug_logger: logging.Logger,
) -> None:
    """do_rollover logs warning if rollover target cannot be deleted."""
    base_file = tmp_path / "charfinder.log"
    base_file.write_text("main", encoding="utf-8")

    handler = lh.CustomRotatingFileHandler(str(base_file), backupCount=3, delay=False)

    # Create rotated files
    log1 = Path(handler.rotation_filename(f"{base_file}.1"))
    log2 = Path(handler.rotation_filename(f"{base_file}.2"))
    log3 = Path(handler.rotation_filename(f"{base_file}.3"))
    log1.write_text("rotate me", encoding="utf-8")
    log2.write_text("also rotate", encoding="utf-8")
    log3.write_text("block me", encoding="utf-8")
    target = log3.resolve()

    print(f"[DEBUG] Target to fail unlink: {target}")

    original_unlink = Path.unlink

    def unlink_side_effect(self: Path, *args: object, **kwargs: object) -> None:
        print(f"[DEBUG] Attempting unlink: {self}")
        if self.resolve() == target:
            print(f"[DEBUG] Simulating unlink failure for: {self}")
            raise OSError("Simulated failure")
        return original_unlink(self)

    with patch("pathlib.Path.unlink", new=unlink_side_effect):
        handler.do_rollover()

    logs = log_stream.getvalue()
    print("[DEBUG] Captured logs:\n", logs)

    assert "Failed to delete rollover target" in logs
    assert str(target) in logs
