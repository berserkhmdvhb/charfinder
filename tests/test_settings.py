"""Unit tests for charfinder.settings."""

from __future__ import annotations

import logging
from io import StringIO
from pathlib import Path
from typing import Callable

import pytest
from charfinder.settings import (
    get_cache_file,
    get_environment,
    get_log_backup_count,
    get_log_dir,
    get_log_max_bytes,
    is_dev,
    is_prod,
    is_uat,
    load_settings,
    resolve_loaded_dotenv_paths,
    safe_int,
)
from charfinder.utils.logger_setup import teardown_logger

# ---------------------------------------------------------------------
# Basic environment accessors
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "env_value, expected",
    [
        ("DEV", "DEV"),
        ("dev", "DEV"),
        ("UAT", "UAT"),
        ("uat", "UAT"),
        ("PROD", "PROD"),
        ("prod", "PROD"),
        (None, "DEV"),  # default fallback
    ],
)
def test_get_environment(
    patch_env: Callable[[str], None],
    env_value: str | None,
    expected: str,
) -> None:
    """Test get_environment() and is_dev/is_uat/is_prod helpers."""
    if env_value is not None:
        patch_env(env_value)
    else:
        patch_env("")  # Clear

    assert get_environment() == expected
    assert is_dev() is (expected == "DEV")
    assert is_uat() is (expected == "UAT")
    assert is_prod() is (expected == "PROD")

# ---------------------------------------------------------------------
# safe_int utility
# ---------------------------------------------------------------------


def test_safe_int_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test safe_int() with valid integer env value."""
    monkeypatch.setenv("TEST_INT", "123")
    assert safe_int("TEST_INT", 999) == 123


def test_safe_int_invalid(
    monkeypatch: pytest.MonkeyPatch,
    log_stream: StringIO,
    debug_logger: logging.Logger,
) -> None:
    """Test safe_int() with invalid integer env value."""
    monkeypatch.setenv("TEST_INT", "abc")
    _ = debug_logger  # enable debug logger

    result = safe_int("TEST_INT", 999)
    assert result == 999

    log_output = log_stream.getvalue()
    assert "Invalid int for" in log_output
    assert "TEST_INT" in log_output


def test_safe_int_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test safe_int() fallback when env var is missing."""
    monkeypatch.delenv("TEST_INT", raising=False)
    assert safe_int("TEST_INT", 888) == 888

# ---------------------------------------------------------------------
# Log config accessors
# ---------------------------------------------------------------------


def test_get_log_max_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test get_log_max_bytes() accessor."""
    monkeypatch.setenv("CHARFINDER_LOG_MAX_BYTES", "2048")
    assert get_log_max_bytes() == 2048


def test_get_log_backup_count(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test get_log_backup_count() accessor."""
    monkeypatch.setenv("CHARFINDER_LOG_BACKUP_COUNT", "7")
    assert get_log_backup_count() == 7


def test_get_log_dir(patch_env: Callable[[str], None]) -> None:
    """Test get_log_dir() accessor."""
    patch_env("uat")
    log_dir = get_log_dir()
    assert isinstance(log_dir, Path)
    assert log_dir.name == "UAT"

# ---------------------------------------------------------------------
# Cache file accessor
# ---------------------------------------------------------------------


def test_get_cache_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test get_cache_file() accessor."""
    monkeypatch.setenv("CHARFINDER_CACHE", "custom_cache.json")
    assert get_cache_file() == "custom_cache.json"

    monkeypatch.delenv("CHARFINDER_CACHE", raising=False)
    assert get_cache_file() == "unicode_name_cache.json"

# ---------------------------------------------------------------------
# load_settings and resolve_loaded_dotenv_paths
# ---------------------------------------------------------------------


def test_load_settings_no_dotenv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    setup_test_root: Callable[[], Path],
    log_stream: StringIO,
    debug_logger: logging.Logger,
) -> None:
    """Test load_settings() and resolve_loaded_dotenv_paths() with no .env file."""
    _ = setup_test_root()

    # Force DOTENV_PATH to dummy empty file to isolate test
    dummy_env = tmp_path / ".env"
    dummy_env.write_text("")
    monkeypatch.setenv("DOTENV_PATH", str(dummy_env.resolve()))


    _ = debug_logger
    loaded = load_settings(verbose=True)
    assert isinstance(loaded, list)
    assert len(loaded) == 1
    assert loaded[0] == dummy_env

    paths = resolve_loaded_dotenv_paths()
    assert isinstance(paths, list)
    assert all(isinstance(p, Path) for p in paths)

# ---------------------------------------------------------------------
# print_dotenv_debug basic smoke test
# ---------------------------------------------------------------------



# ---------------------------------------------------------------------
# Teardown
# ---------------------------------------------------------------------


def teardown_module(module: object) -> None:
    """Ensure logger is clean after tests."""
    teardown_logger(logging.getLogger("charfinder"))
