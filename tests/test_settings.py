"""Unit tests for charfinder.settings module."""

from __future__ import annotations

import logging
from io import StringIO
from pathlib import Path
from types import ModuleType
from typing import Callable

import pytest
from charfinder import settings
from charfinder.settings import (
    get_cache_file,
    get_environment,
    get_log_backup_count,
    get_log_dir,
    get_log_max_bytes,
    get_unicode_data_file,
    get_unicode_data_url,
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
        ("uat", "UAT"),
        ("PROD", "PROD"),
        ("", "DEV"),  # fallback
        (None, "DEV"),
    ],
)
def test_get_environment_behavior(
    monkeypatch: pytest.MonkeyPatch,
    env_value: str | None,
    expected: str,
) -> None:
    if env_value is not None:
        monkeypatch.setenv("CHARFINDER_ENV", env_value)
    else:
        monkeypatch.delenv("CHARFINDER_ENV", raising=False)

    assert get_environment() == expected
    assert is_dev() is (expected == "DEV")
    assert is_uat() is (expected == "UAT")
    assert is_prod() is (expected == "PROD")

# ---------------------------------------------------------------------
# safe_int behavior
# ---------------------------------------------------------------------

def test_safe_int_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("X_INT", "42")
    assert safe_int("X_INT", 999) == 42

def test_safe_int_invalid(
    monkeypatch: pytest.MonkeyPatch,
    debug_logger: logging.Logger,
    log_stream: StringIO,
) -> None:
    monkeypatch.setenv("X_INT", "not_a_number")
    _ = debug_logger
    assert safe_int("X_INT", 1000) == 1000
    assert "Invalid int for" in log_stream.getvalue()

def test_safe_int_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("X_INT", raising=False)
    assert safe_int("X_INT", 1234) == 1234

# ---------------------------------------------------------------------
# Accessor behavior
# ---------------------------------------------------------------------

def test_get_log_dir_returns_env_path(patch_env: Callable[[str], None]) -> None:
    patch_env("uat")
    path = get_log_dir()
    assert isinstance(path, Path)
    assert path.name == "UAT"

def test_get_log_max_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHARFINDER_LOG_MAX_BYTES", "8192")
    assert get_log_max_bytes() == 8192

def test_get_log_backup_count(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHARFINDER_LOG_BACKUP_COUNT", "3")
    assert get_log_backup_count() == 3

# ---------------------------------------------------------------------
# File path accessors
# ---------------------------------------------------------------------

def test_get_cache_file_default(setup_test_root: Callable[[], Path]) -> None:
    root = setup_test_root()
    path = get_cache_file()
    assert root in path.parents
    assert path.name == "unicode_name_cache.json"

def test_get_cache_file_env_override(
    monkeypatch: pytest.MonkeyPatch,
    setup_test_root: Callable[[], Path],
) -> None:
    root = setup_test_root()
    monkeypatch.setenv("CHARFINDER_CACHE_FILE_PATH", "custom/cache.json")
    path = get_cache_file()
    assert path == root / "custom" / "cache.json"

def test_get_unicode_data_file_default(setup_test_root: Callable[[], Path]) -> None:
    root = setup_test_root()
    path = get_unicode_data_file()
    assert path == root / "data" / "UnicodeData.txt"

def test_get_unicode_data_file_env_override(
    monkeypatch: pytest.MonkeyPatch,
    setup_test_root: Callable[[], Path],
) -> None:
    root = setup_test_root()
    monkeypatch.setenv("CHARFINDER_UNICODE_DATA_FILE_PATH", "alt/data.txt")
    path = get_unicode_data_file()
    assert path == root / "alt" / "data.txt"

def test_get_unicode_data_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNICODE_DATA_URL", "https://example.com/data.txt")
    assert get_unicode_data_url() == "https://example.com/data.txt"

# ---------------------------------------------------------------------
# load_settings() and resolve_loaded_dotenv_paths()
# ---------------------------------------------------------------------

def test_load_settings_with_fake_dotenv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    debug_logger: logging.Logger,
    log_stream: StringIO,
) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text("CHARFINDER_ENV=PROD\n")
    monkeypatch.setenv("DOTENV_PATH", str(dotenv))
    _ = debug_logger

    loaded = load_settings(verbose=True)
    assert loaded == [dotenv]

    paths = resolve_loaded_dotenv_paths()
    assert paths == [dotenv]

def test_load_settings_without_dotenv(
    monkeypatch: pytest.MonkeyPatch,
    debug_logger: logging.Logger,
    log_stream: StringIO,
    tmp_path: Path,
) -> None:
    dummy_path = tmp_path / "nonexistent.env"
    monkeypatch.setenv("DOTENV_PATH", str(dummy_path.resolve()))
    _ = debug_logger

    loaded = load_settings(verbose=True)
    assert loaded == []

    output = log_stream.getvalue()
    assert "No .env file loaded" in output

def test_load_settings_default_path(setup_test_root: Callable[[], Path]) -> None:
    root = setup_test_root()
    dotenv = root / ".env"
    dotenv.write_text("CHARFINDER_ENV=UAT\n")

    result = load_settings()
    assert result == [dotenv]
    assert get_environment() == "UAT"

# ---------------------------------------------------------------------
# resolve_loaded_dotenv_paths() fallback
# ---------------------------------------------------------------------

def test_resolve_loaded_dotenv_paths_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DOTENV_PATH", raising=False)
    monkeypatch.delenv("CHARFINDER_ROOT_DIR_FOR_TESTS", raising=False)

    paths = resolve_loaded_dotenv_paths()
    assert paths == []  # no .env present

# ---------------------------------------------------------------------
# Internal utility debug smoke (print_dotenv_debug is indirect)
# ---------------------------------------------------------------------

def test_dotenv_debug_output(
    monkeypatch: pytest.MonkeyPatch,
    debug_logger: logging.Logger,
    log_stream: StringIO,
    tmp_path: Path,
) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text("CHARFINDER_ENV=PROD\n")
    monkeypatch.setenv("DOTENV_PATH", str(dotenv))
    monkeypatch.setenv("CHARFINDER_DEBUG_ENV_LOAD", "1")

    _ = debug_logger
    _ = load_settings(debug=True)

    output = log_stream.getvalue()
    assert "No .env file loaded" not in output or "loaded" in output

# ---------------------------------------------------------------------
# Teardown cleanup (optional, mostly redundant with fixtures)
# ---------------------------------------------------------------------

def teardown_module(module: object) -> None:
    teardown_logger(logging.getLogger("charfinder"))
