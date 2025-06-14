"""
Unit tests for charfinder.settings.

Covers:
- Environment detection and helpers
- Test mode logic
- .env loading and diagnostics
- Logging and config defaults
- Filesystem path logic
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
from collections.abc import Callable

import pytest

import charfinder.settings as settings


# ---------------------------------------------------------------------
# Environment detection
# ---------------------------------------------------------------------

@pytest.mark.parametrize(
    "env_value,expected",
    [
        ("dev", "DEV"),
        ("UAT", "UAT"),
        ("PROD", "PROD"),
        ("unexpected", "UNEXPECTED"),
        ("", "DEV"),
        (None, "DEV"),
    ],
)
def test_get_environment(monkeypatch: pytest.MonkeyPatch, env_value: str | None, expected: str) -> None:
    if env_value is None:
        monkeypatch.delenv("CHARFINDER_ENV", raising=False)
    else:
        monkeypatch.setenv("CHARFINDER_ENV", env_value)
    assert settings.get_environment() == expected


def test_env_helpers(patch_env: Callable[[str], None]) -> None:
    patch_env("DEV")
    assert settings.is_dev()
    assert not settings.is_uat()
    assert not settings.is_prod()

    patch_env("UAT")
    assert settings.is_uat()

    patch_env("PROD")
    assert settings.is_prod()


# ---------------------------------------------------------------------
# Test mode detection
# ---------------------------------------------------------------------

def test_is_test(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHARFINDER_ENV", "TEST")
    assert settings.is_test()

    monkeypatch.setenv("CHARFINDER_ENV", "DEV")
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "yes")
    assert settings.is_test()


def test_is_test_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHARFINDER_ENV", "TEST")
    assert settings.is_test_mode()

    monkeypatch.setenv("CHARFINDER_ENV", "DEV")
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "yes")
    assert not settings.is_test_mode()


# ---------------------------------------------------------------------
# .env loading and diagnostics
# ---------------------------------------------------------------------

def test_load_settings(load_fresh_settings: Callable[[Path | None], ModuleType], tmp_path: Path) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text("CHARFINDER_ENV=UAT\nCHARFINDER_LOG_MAX_BYTES=12345\n")

    sett = load_fresh_settings(dotenv)
    assert dotenv in sett.resolve_loaded_dotenv_paths()
    assert sett.get_environment() == "UAT"
    assert sett.get_log_max_bytes() == 12345


def test_load_settings_none(load_fresh_settings: Callable[[Path | None], ModuleType]) -> None:
    sett = load_fresh_settings(None)
    assert sett.load_settings() == []


def test_resolve_loaded_dotenv_paths(
    load_fresh_settings: Callable[[Path | None], ModuleType],
    tmp_path: Path,
) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text("CHARFINDER_ENV=DEV\n")
    sett = load_fresh_settings(dotenv)
    assert sett.resolve_loaded_dotenv_paths() == [dotenv]


# ---------------------------------------------------------------------
# Safe int and config fallback
# ---------------------------------------------------------------------

@pytest.mark.parametrize(
    "envval,default,expected",
    [("123", 5, 123), ("bad", 5, 5), (None, 7, 7)],
)
def test_safe_int(monkeypatch: pytest.MonkeyPatch, envval: str | None, default: int, expected: int) -> None:
    key = "CHARFINDER_LOG_MAX_BYTES"
    if envval is None:
        monkeypatch.delenv(key, raising=False)
    else:
        monkeypatch.setenv(key, envval)
    assert settings.safe_int(key, default) == expected


def test_get_log_defaults() -> None:
    assert isinstance(settings.get_log_max_bytes(), int)
    assert isinstance(settings.get_log_backup_count(), int)


# ---------------------------------------------------------------------
# Path functions
# ---------------------------------------------------------------------

def test_get_root_dir() -> None:
    root = settings.get_root_dir()
    assert isinstance(root, Path)
    assert root.exists()


def test_get_log_dir(temp_log_dir: Path) -> None:
    path = settings.get_log_dir()
    assert str(path) == str(temp_log_dir)


def test_get_cache_file(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CHARFINDER_CACHE_FILE_PATH", raising=False)
    path = settings.get_cache_file()
    assert path.name.endswith("unicode_name_cache.json")


def test_get_unicode_data_file(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CHARFINDER_UNICODE_DATA_FILE_PATH", raising=False)
    path = settings.get_unicode_data_file()
    assert path.name == "UnicodeData.txt"


def test_get_unicode_data_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UNICODE_DATA_URL", raising=False)
    url = settings.get_unicode_data_url()
    assert url.startswith("https://")
