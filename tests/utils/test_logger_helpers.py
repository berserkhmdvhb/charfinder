"""
Unit tests for logger_helpers.py in charfinder.utils.

Covers:
- StreamFilter behavior for suppression flag
- suppress_console_logging context manager functionality
- EnvironmentFilter injecting environment into log records
- SafeFormatter handling missing attributes
- CustomRotatingFileHandler filename rotation and rollover logic
"""

from __future__ import annotations

import logging
import os
import tempfile
from contextlib import ExitStack
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from charfinder.utils import logger_helpers as lh


# ---------------------------------------------------------------------
# StreamFilter Tests
# ---------------------------------------------------------------------

def test_stream_filter_blocks_when_suppressed() -> None:
    """StreamFilter.filter returns False when suppression is active."""
    lh._SUPPRESS_CONSOLE_OUTPUT.value = True
    filt = lh.StreamFilter()
    record = logging.LogRecord("name", logging.INFO, "", 0, "msg", None, None)
    assert filt.filter(record) is False

def test_stream_filter_allows_when_not_suppressed() -> None:
    """StreamFilter.filter returns True when suppression is not active."""
    lh._SUPPRESS_CONSOLE_OUTPUT.value = False
    filt = lh.StreamFilter()
    record = logging.LogRecord("name", logging.INFO, "", 0, "msg", None, None)
    assert filt.filter(record) is True


# ---------------------------------------------------------------------
# suppress_console_logging Tests
# ---------------------------------------------------------------------

def test_suppress_console_logging_context_restores_flag() -> None:
    """Test suppression flag is set inside context and restored after."""
    old_value = getattr(lh._SUPPRESS_CONSOLE_OUTPUT, "value", False)
    with lh.suppress_console_logging():
        assert lh._SUPPRESS_CONSOLE_OUTPUT.value is True
    assert lh._SUPPRESS_CONSOLE_OUTPUT.value == old_value


# ---------------------------------------------------------------------
# EnvironmentFilter Tests
# ---------------------------------------------------------------------

def test_environment_filter_sets_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """EnvironmentFilter.filter injects environment from settings."""
    record = logging.LogRecord("name", logging.INFO, "", 0, "msg", None, None)
    monkeypatch.setattr("charfinder.utils.logger_helpers.get_environment", lambda: "TEST_ENV")
    env_filter = lh.EnvironmentFilter()
    result = env_filter.filter(record)
    assert result is True
    assert hasattr(record, "env")
    assert record.env == "TEST_ENV"


# ---------------------------------------------------------------------
# SafeFormatter Tests
# ---------------------------------------------------------------------

def test_safe_formatter_adds_env_if_missing() -> None:
    """SafeFormatter.format sets 'env' attribute if missing in record."""
    formatter = lh.SafeFormatter(fmt="%(env)s - %(msg)s")
    record = logging.LogRecord("name", logging.INFO, "", 0, "hello", None, None)
    if hasattr(record, "env"):
        delattr(record, "env")  # forcibly remove if present
    formatted = formatter.format(record)
    assert formatted.startswith("UNKNOWN")


def test_safe_formatter_uses_existing_env() -> None:
    """SafeFormatter.format uses existing 'env' attribute if present."""
    formatter = lh.SafeFormatter(fmt="%(env)s - %(msg)s")
    record = logging.LogRecord("name", logging.INFO, "", 0, "hello", None, None)
    record.env = "EXISTING_ENV"
    formatted = formatter.format(record)
    assert formatted.startswith("EXISTING_ENV")


# ---------------------------------------------------------------------
# CustomRotatingFileHandler Tests
# ---------------------------------------------------------------------

@pytest.fixture
def temp_log_file(tmp_path: Path) -> Path:
    """Create a temporary log file."""
    f = tmp_path / "charfinder.log"
    f.write_text("initial log content")
    return f

def test_rotation_filename_standard_and_custom(tmp_path: Path) -> None:
    """Test rotation_filename returns correct custom names."""
    handler = lh.CustomRotatingFileHandler(tmp_path / "charfinder.log")

    # Standard .log file remains unchanged
    assert handler.rotation_filename("charfinder.log") == "charfinder.log"

    # .log.1 style renamed to charfinder_1.log
    rotated = f"charfinder.log.1"
    expected = f"charfinder_1.log"
    assert handler.rotation_filename(rotated) == expected

    # Unknown pattern returns as-is
    assert handler.rotation_filename("randomfile.txt") == "randomfile.txt"

def test_get_files_to_delete(tmp_path: Path) -> None:
    """Test get_files_to_delete returns files beyond backupCount sorted by mtime."""
    base_file = tmp_path / "charfinder.log"
    base_file.write_text("base")
    files = []
    for i in range(5):
        f = tmp_path / f"charfinder_{i+1}.log"
        f.write_text(f"content {i}")
        files.append(f)

    handler = lh.CustomRotatingFileHandler(base_file, backupCount=3)
    to_delete = handler.get_files_to_delete()
    # Should return the oldest 2 files to delete (5 - 3)
    assert set(to_delete) == set(files[:2])

def test_do_rollover_renames_files(tmp_path: Path) -> None:
    """Test do_rollover renames files correctly with backupCount."""
    base_file = tmp_path / "charfinder.log"
    base_file.write_text("base content")

    # Create some rotated files
    for i in range(1, 3):
        f = tmp_path / f"charfinder_{i}.log"
        f.write_text(f"old content {i}")

    handler = lh.CustomRotatingFileHandler(str(base_file), backupCount=3, delay=False)
    handler.baseFilename = str(base_file)
    handler.backupCount = 3
    handler.stream = handler._open()

    handler.do_rollover()

    # After rollover, charfinder_2.log should be renamed to charfinder_3.log etc.
    assert (tmp_path / "charfinder_3.log").exists()
    assert (tmp_path / "charfinder_1.log").exists()
    # The base file renamed to charfinder_1.log
    assert not base_file.exists()


def test_do_rollover_closes_and_opens_stream(tmp_path: Path) -> None:
    """Test stream is closed before rollover and reopened after."""
    base_file = tmp_path / "charfinder.log"
    handler = lh.CustomRotatingFileHandler(str(base_file), backupCount=1, delay=False)
    handler.stream = handler._open()

    old_stream = handler.stream
    handler.do_rollover()
    assert old_stream.closed
    assert handler.stream is not None
    assert not handler.stream.closed
