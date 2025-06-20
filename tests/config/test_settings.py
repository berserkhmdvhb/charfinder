"""
Unit tests for charfinder.config.settings.

Tests environment detection, mode helpers, .env loading,
config defaults, and path retrieval functions.
"""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
from collections.abc import Callable
from io import StringIO

import pytest


import charfinder.config.settings as settings
from charfinder.config.constants import (
    DEFAULT_LOG_ROOT,
    ENV_ENVIRONMENT,
    ENV_LOG_MAX_BYTES,
)    

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
        monkeypatch.delenv(ENV_ENVIRONMENT, raising=False)
    else:
        monkeypatch.setenv(ENV_ENVIRONMENT, env_value)
    assert settings.get_environment() == expected


def test_env_helpers(patch_env: Callable[[str], None], monkeypatch: pytest.MonkeyPatch) -> None:
    # DEV case – unset PYTEST_CURRENT_TEST to allow is_test() to be False
    patch_env("DEV")
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    assert settings.is_dev()
    assert not settings.is_uat()
    assert not settings.is_prod()
    assert not settings.is_test_mode()
    assert not settings.is_test()

    # UAT
    patch_env("UAT")
    assert settings.is_uat()

    # PROD
    patch_env("PROD")
    assert settings.is_prod()

    # TEST
    patch_env("TEST")
    assert settings.is_test_mode()
    assert settings.is_test()



def test_is_test_with_pytest_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_ENVIRONMENT, raising=False)
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "somevalue")
    assert settings.is_test()


def test_safe_int(monkeypatch: pytest.MonkeyPatch) -> None:
    key = ENV_LOG_MAX_BYTES

    monkeypatch.setenv(key, "12345")
    assert settings.safe_int(key, 5) == 12345

    monkeypatch.setenv(key, "not-an-int")
    assert settings.safe_int(key, 5) == 5

    monkeypatch.delenv(key, raising=False)
    assert settings.safe_int(key, 7) == 7


def test_get_log_defaults() -> None:
    assert isinstance(settings.get_log_max_bytes(), int)
    assert isinstance(settings.get_log_backup_count(), int)
    assert settings.get_log_max_bytes() > 0
    assert settings.get_log_backup_count() > 0


def test_get_root_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Without override: should point to project root (at least 3 parents above this file)
    monkeypatch.delenv("CHARFINDER_ROOT_DIR_FOR_TESTS", raising=False)
    root_dir = settings.get_root_dir()
    assert root_dir.exists()
    assert root_dir.is_dir()

    # With override
    monkeypatch.setenv("CHARFINDER_ROOT_DIR_FOR_TESTS", str(tmp_path))
    assert settings.get_root_dir() == tmp_path.resolve()

def test_resolve_dotenv_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CHARFINDER_ROOT_DIR_FOR_TESTS", str(tmp_path))

    assert settings.resolve_dotenv_path() is None

    env_file = tmp_path / ".env"
    env_file.write_text("DUMMY=1\n")
    assert settings.resolve_dotenv_path() == env_file

    fake_path = tmp_path / "nonexistent.env"
    monkeypatch.setenv("DOTENV_PATH", str(fake_path))
    monkeypatch.setenv("CHARFINDER_DEBUG_ENV_LOAD", "1")

    stream = StringIO()
    result = settings.resolve_dotenv_path(stream=stream)
    assert result == fake_path
    assert "DOTENV_PATH is set to" in stream.getvalue()

def test_load_settings_loads_dotenv_file(
    load_fresh_settings: Callable[[Path | None, Path | None], ModuleType],
    tmp_path: Path,
) -> None:
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("CHARFINDER_ENV=UAT\nCHARFINDER_LOG_MAX_BYTES=123\n")

    sett = load_fresh_settings(dotenv_path, tmp_path)
    loaded = sett.load_settings()
    assert dotenv_path in loaded
    assert sett.get_environment() == "UAT"
    assert sett.get_log_max_bytes() == 123


def test_load_settings_no_dotenv(
    load_fresh_settings: Callable[[Path | None, Path | None], ModuleType],
    tmp_path: Path,
) -> None:
    sett = load_fresh_settings(None, tmp_path)
    loaded = sett.load_settings()
    assert loaded == []


def test_resolve_loaded_dotenv_paths(
    load_fresh_settings: Callable[[Path | None, Path | None], ModuleType],
    tmp_path: Path,
) -> None:
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("CHARFINDER_ENV=DEV\n")

    sett = load_fresh_settings(dotenv_path, tmp_path)
    resolved = sett.resolve_loaded_dotenv_paths()
    assert isinstance(resolved, list)
    assert dotenv_path in resolved


def test_get_cache_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("CHARFINDER_CACHE_FILE_PATH", raising=False)
    path_default = settings.get_cache_file()
    assert path_default.name == "unicode_name_cache.json"

    monkeypatch.setenv("CHARFINDER_CACHE_FILE_PATH", "custom_cache.json")
    expected_path = tmp_path / "custom_cache.json"
    monkeypatch.setenv("CHARFINDER_ROOT_DIR_FOR_TESTS", str(tmp_path))
    path_custom = settings.get_cache_file()
    # Should combine root_dir and env var path
    assert path_custom.name == "custom_cache.json"
    assert path_custom == expected_path


def test_get_unicode_data_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("CHARFINDER_UNICODE_DATA_FILE_PATH", raising=False)
    path_default = settings.get_unicode_data_file()
    assert path_default.name == "UnicodeData.txt"

    monkeypatch.setenv("CHARFINDER_UNICODE_DATA_FILE_PATH", "custom_data.txt")
    expected_path = tmp_path / "custom_data.txt"
    monkeypatch.setenv("CHARFINDER_ROOT_DIR_FOR_TESTS", str(tmp_path))
    path_custom = settings.get_unicode_data_file()
    assert path_custom.name == "custom_data.txt"
    assert path_custom == expected_path


def test_get_unicode_data_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UNICODE_DATA_URL", raising=False)
    url_default = settings.get_unicode_data_url()
    assert url_default.startswith("https://")

    monkeypatch.setenv("UNICODE_DATA_URL", "https://custom.url/path")
    url_custom = settings.get_unicode_data_url()
    assert url_custom == "https://custom.url/path"


def test_get_log_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CHARFINDER_ENV", "TEST")
    monkeypatch.setenv("CHARFINDER_ROOT_DIR_FOR_TESTS", str(tmp_path))
    import importlib, charfinder.config.settings as sett

    importlib.reload(sett)
    path = sett.get_log_dir()
    assert path == DEFAULT_LOG_ROOT / "TEST"
