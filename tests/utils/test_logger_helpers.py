"""Unit tests for logger_helpers.py in charfinder.utils.

Covers:
- StreamFilter behavior for suppression flag
- suppress_console_logging context manager functionality
- EnvironmentFilter injecting environment into log records
- SafeFormatter handling missing or invalid attributes
- CustomRotatingFileHandler filename rotation, deletion, encoding, and rollover logic
"""

from __future__ import annotations

from collections.abc import Callable, Generator
import logging
from pathlib import Path
from unittest.mock import patch
import pytest
import time
from typing import ContextManager

from charfinder.utils import logger_helpers as lh
from charfinder.config.types import EchoFunc

# Optional marker for test categorization
pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------
# StreamFilter Tests
# ---------------------------------------------------------------------

def test_stream_filter_blocks_when_suppressed() -> None:
    """StreamFilter disables logging when suppression flag is set."""
    lh._SUPPRESS_CONSOLE_OUTPUT.value = True
    filt = lh.StreamFilter()
    record = logging.LogRecord("name", logging.INFO, "", 0, "msg", None, None)
    assert not filt.filter(record)


def test_stream_filter_allows_when_not_suppressed() -> None:
    """StreamFilter allows logging when suppression flag is not set."""
    lh._SUPPRESS_CONSOLE_OUTPUT.value = False
    filt = lh.StreamFilter()
    record = logging.LogRecord("name", logging.INFO, "", 0, "msg", None, None)
    assert filt.filter(record)


# ---------------------------------------------------------------------
# suppress_console_logging Tests
# ---------------------------------------------------------------------

def test_suppress_console_logging_context_restores_flag() -> None:
    """suppress_console_logging restores flag after context."""
    old_value = getattr(lh._SUPPRESS_CONSOLE_OUTPUT, "value", False)
    with lh.suppress_console_logging():
        assert lh._SUPPRESS_CONSOLE_OUTPUT.value is True
    assert lh._SUPPRESS_CONSOLE_OUTPUT.value == old_value


# ---------------------------------------------------------------------
# EnvironmentFilter Tests
# ---------------------------------------------------------------------

def test_environment_filter_sets_env(patch_env: Callable[[str], None]) -> None:
    """EnvironmentFilter adds `env` to the log record."""
    record = logging.LogRecord("name", logging.INFO, "", 0, "msg", None, None)
    env_filter = lh.EnvironmentFilter()
    patch_env("TEST_ENV")  # Use fixture to patch environment
    assert env_filter.filter(record) is True
    assert getattr(record, "env", None) == "TEST_ENV"


# ---------------------------------------------------------------------
# SafeFormatter Tests
# ---------------------------------------------------------------------

def test_safe_formatter_adds_env_if_missing() -> None:
    """SafeFormatter sets 'env' to 'UNKNOWN' if missing."""
    formatter = lh.SafeFormatter(fmt="%(env)s - %(msg)s")
    record = logging.LogRecord("name", logging.INFO, "", 0, "hello", None, None)
    formatted = formatter.format(record)
    assert formatted.startswith("UNKNOWN")


def test_safe_formatter_uses_existing_env() -> None:
    """SafeFormatter uses existing 'env' if present."""
    formatter = lh.SafeFormatter(fmt="%(env)s - %(msg)s")
    record = logging.LogRecord("name", logging.INFO, "", 0, "hello", None, None)
    record.env = "EXISTING_ENV"
    formatted = formatter.format(record)
    assert formatted.startswith("EXISTING_ENV")


def test_safe_formatter_handles_non_string_env() -> None:
    """SafeFormatter falls back if 'env' is not a string."""
    formatter = lh.SafeFormatter(fmt="%(env)s - %(msg)s")
    record = logging.LogRecord("name", logging.INFO, "", 0, "hello", None, None)
    record.env = 12345
    formatted = formatter.format(record)
    assert formatted.startswith("UNKNOWN")


# ---------------------------------------------------------------------
# CustomRotatingFileHandler Tests
# ---------------------------------------------------------------------

@pytest.fixture
def temp_log_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Creates a temporary log file."""
    f = tmp_path / "charfinder.log"
    f.write_text("initial log content", encoding="utf-8")
    yield f


def test_rotation_filename_standard_and_custom(tmp_path: Path) -> None:
    """rotation_filename handles standard and custom .log rotations."""
    handler = lh.CustomRotatingFileHandler(tmp_path / "charfinder.log")
    assert handler.rotation_filename("charfinder.log") == "charfinder.log"
    assert handler.rotation_filename("charfinder.log.1") == "charfinder_1.log"
    assert handler.rotation_filename("randomfile.txt") == "randomfile.txt"


import time

def test_get_files_to_delete(tmp_path: Path) -> None:
    """get_files_to_delete returns old files beyond backup count."""
    base_file = tmp_path / "charfinder.log"
    base_file.write_text("base", encoding="utf-8")

    files = []
    for i in range(5):
        f = tmp_path / f"charfinder_{i+1}.log"
        f.write_text(f"content {i}", encoding="utf-8")
        files.append(f)
        # Ensure unique mtime across platforms
        time.sleep(0.01)  

    handler = lh.CustomRotatingFileHandler(base_file, backupCount=3)
    to_delete = handler.get_files_to_delete()

    # Sort files by mtime to align with implementation logic
    expected = sorted(files, key=lambda p: p.stat().st_mtime)[:2]
    assert set(to_delete) == set(expected)


def test_do_rollover_renames_files(tmp_path: Path) -> None:
    """do_rollover renames files and rotates correctly."""
    base_file = tmp_path / "charfinder.log"
    base_file.write_text("base content", encoding="utf-8")

    for i in range(1, 3):
        f = tmp_path / f"charfinder_{i}.log"
        f.write_text(f"old content {i}", encoding="utf-8")

    handler = lh.CustomRotatingFileHandler(str(base_file), backupCount=3, delay=False)
    handler.stream = handler._open()
    handler.do_rollover()

    assert base_file.exists()
    assert (tmp_path / "charfinder_1.log").exists()
    assert (tmp_path / "charfinder_3.log").exists()
    handler.stream.close()


def test_do_rollover_closes_and_opens_stream(tmp_path: Path) -> None:
    """do_rollover closes old stream and reopens new one."""
    base_file = tmp_path / "charfinder.log"
    handler = lh.CustomRotatingFileHandler(str(base_file), backupCount=1, delay=False)
    handler.stream = handler._open()
    old_stream = handler.stream
    handler.do_rollover()
    assert old_stream.closed
    assert handler.stream is not None
    assert not handler.stream.closed
    handler.stream.close()


def test_do_rollover_logs_warning_on_delete_failure(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    fail_unlink_for: Callable[[Path], ContextManager[None]],
) -> None:
    """do_rollover logs a warning when a log file can't be deleted."""
    base_file = tmp_path / "charfinder.log"
    base_file.write_text("main log", encoding="utf-8")

    file_to_fail = tmp_path / "charfinder_1.log"
    file_to_fail.write_text("locked", encoding="utf-8")

    handler = lh.CustomRotatingFileHandler(str(base_file), backupCount=1, delay=False)

    with patch.object(handler, "get_files_to_delete", return_value=[file_to_fail]):
        with fail_unlink_for(file_to_fail):
            caplog.set_level(logging.WARNING)
            handler.do_rollover()

    expected_message = f"Failed to delete old log file: {file_to_fail}"
    assert any(expected_message in r.message for r in caplog.records)
