"""Test suite for core.name_cache."""

import json
import sys
from pathlib import Path
from typing import Any, IO
from unittest.mock import patch

import pytest

from charfinder.core.name_cache import (
    BuildCacheOptions,
    CacheIOOptions,
    build_name_cache,
    _save_cache_with_retries
)

# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture()
def dummy_cache_path(tmp_path: Path) -> Path:
    return tmp_path / "dummy_cache.json"


@pytest.fixture()
def valid_cache_content() -> dict[str, Any]:
    return {
        "✓": {"original": "CHECK MARK", "normalized": "check mark"},
        "✗": {"original": "BALLOT X", "normalized": "ballot x"},
    }


# ---------------------------------------------------------------------
# Cache Load Tests
# ---------------------------------------------------------------------


def test_load_existing_cache_success(
    dummy_cache_path: Path,
    valid_cache_content: dict[str, Any],
) -> None:
    dummy_cache_path.write_text(json.dumps(valid_cache_content, ensure_ascii=False), encoding="utf-8")

    options = CacheIOOptions(use_color=False, show=True, retry_attempts=1, retry_delay=0)
    from charfinder.core.name_cache import _load_existing_cache

    result = _load_existing_cache(dummy_cache_path, options=options)
    assert result == valid_cache_content


def test_load_existing_cache_invalid_json(dummy_cache_path: Path) -> None:
    dummy_cache_path.write_text("INVALID_JSON", encoding="utf-8")

    options = CacheIOOptions(use_color=False, show=False, retry_attempts=1, retry_delay=0)
    from charfinder.core.name_cache import _load_existing_cache

    with pytest.raises(ValueError, match="Failed to load cache from"):
        _load_existing_cache(dummy_cache_path, options=options)


# ---------------------------------------------------------------------
# Cache Save Tests
# ---------------------------------------------------------------------


def test_save_cache_success(tmp_path: Path) -> None:
    from charfinder.core.name_cache import _save_cache_with_retries

    path = tmp_path / "save_test.json"
    options = CacheIOOptions(use_color=False, show=False, retry_attempts=2, retry_delay=0)
    data = {"✔": {"original": "HEAVY CHECK MARK", "normalized": "heavy check mark"}}

    _save_cache_with_retries(data, path, options=options)
    assert path.exists()
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved == data



def test_save_cache_with_retries(tmp_path: Path) -> None:
    """Test that _save_cache_with_retries retries and raises if writing fails."""
    path = tmp_path / "retry.json"
    options = CacheIOOptions(use_color=False, show=False, retry_attempts=2, retry_delay=0.01)
    data = {"✘": {"original": "CROSS MARK", "normalized": "cross mark"}}

    original_open = Path.open

    def flaky_open(self: Path, mode: str = "r", buffering: int = -1,
                   encoding: str | None = None, errors: str | None = None,
                   newline: str | None = None) -> IO[str]:
        if "w" in mode:
            raise OSError("Simulated write failure")
        return original_open(self, mode, buffering, encoding, errors, newline)

    with patch("pathlib.Path.open", new=flaky_open):
        with pytest.raises(OSError, match="Failed to write cache to"):
            _save_cache_with_retries(data, path, options=options)

# ---------------------------------------------------------------------
# build_name_cache() Tests
# ---------------------------------------------------------------------


def test_build_name_cache_valid(tmp_path: Path) -> None:
    cache_path = tmp_path / "charfinder_cache.json"
    options = BuildCacheOptions(
        cache_file_path=cache_path,
        force_rebuild=True,
        show=False,
        use_color=False,
        retry_attempts=1,
        retry_delay=0,
    )
    result = build_name_cache(options=options)

    assert isinstance(result, dict)
    assert cache_path.exists()
    assert any("original" in v for v in result.values())
    assert all("normalized" in v for v in result.values())


def test_build_name_cache_invalid_path_type() -> None:
    bad_options = BuildCacheOptions(cache_file_path="not_a_path")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="cache_file_path must be a valid Path object"):
        build_name_cache(options=bad_options)


def test_build_name_cache_skips_rebuild(tmp_path: Path, valid_cache_content: dict[str, Any]) -> None:
    cache_file = tmp_path / "charfinder_cache.json"
    cache_file.write_text(json.dumps(valid_cache_content), encoding="utf-8")

    options = BuildCacheOptions(
        cache_file_path=cache_file,
        force_rebuild=False,
        show=False,
        use_color=False,
    )

    result = build_name_cache(options=options)
    assert result == valid_cache_content


# ---------------------------------------------------------------------
# Performance + Sanity
# ---------------------------------------------------------------------


def test_build_name_cache_small_unicode_subset(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Monkeypatch sys.maxunicode to limit test duration."""
    monkeypatch.setattr(sys, "maxunicode", 300)

    options = BuildCacheOptions(
        cache_file_path=tmp_path / "mini.json",
        force_rebuild=True,
        show=False,
        use_color=False,
    )

    result = build_name_cache(options=options)
    assert isinstance(result, dict)
    assert all("original" in v and "normalized" in v for v in result.values())
