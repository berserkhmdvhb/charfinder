"""
Tests for charfinder.core.unicode_data_loader.

Covers validation, download fallback, file loading, and parsing logic for UnicodeData.txt.
"""

import pytest
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.error import URLError
from _pytest.monkeypatch import MonkeyPatch
from unittest.mock import MagicMock
from charfinder.core.unicode_data_loader import (
    load_alternate_names,
    validate_files_and_url,
    download_and_cache_unicode_data,
    load_unicode_data_from_file,
    parse_unicode_data,
)
from charfinder.config.constants import (
    ALT_NAME_INDEX,
    EXPECTED_MIN_FIELDS,
)


# ---------------------------------------------------------------------
# validate_files_and_url
# ---------------------------------------------------------------------

def test_validate_files_and_url_valid(tmp_path: Path) -> None:
    """It should return None when URL and path are valid."""
    url = "https://example.com/unicode.txt"
    file_path = tmp_path / "file.txt"
    file_path.touch()
    result = validate_files_and_url(url, file_path, show=False)
    assert result is None


def test_validate_files_and_url_invalid_url(tmp_path: Path) -> None:
    """It should return a message if the URL is invalid or has a bad scheme."""
    url = "ftp://invalid.com"  # Disallowed scheme
    file_path = tmp_path / "file.txt"
    file_path.touch()
    result = validate_files_and_url(url, file_path, show=False)
    assert result is not None
    assert "Validation failed" in result or "Unsupported URL scheme" in result


# ---------------------------------------------------------------------
# download_and_cache_unicode_data
# ---------------------------------------------------------------------

def test_download_and_cache_unicode_data_success(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """It should download, write, and return True on success."""

    mock_response = MagicMock()
    mock_response.read.return_value = b"0041;LATIN CAPITAL LETTER A;;;;"
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = None

    monkeypatch.setattr("charfinder.core.unicode_data_loader.urlopen", lambda url, timeout=5: mock_response)

    file_path = tmp_path / "UnicodeData.txt"
    url = "https://example.com/unicode.txt"
    success = download_and_cache_unicode_data(url, file_path, show=False, use_color=False)

    assert success is True
    assert file_path.read_text("utf-8").startswith("0041;")


def test_download_and_cache_unicode_data_failure(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """It should return False on URLError or IOError."""

    def fake_urlopen_fail(url: str, timeout: int = 5) -> Any:
        raise URLError("Simulated failure")

    monkeypatch.setattr("charfinder.core.unicode_data_loader.urlopen", fake_urlopen_fail)

    file_path = tmp_path / "UnicodeData.txt"
    url = "https://example.com/unicode.txt"
    success = download_and_cache_unicode_data(url, file_path, show=False, use_color=False)

    assert success is False
    assert not file_path.exists()


def test_download_and_cache_unicode_data_invalid_scheme(tmp_path: Path) -> None:
    """It should raise ValueError on invalid URL scheme."""
    file_path = tmp_path / "UnicodeData.txt"
    with pytest.raises(ValueError, match=r"Invalid URL scheme.*Only HTTP/HTTPS are allowed"):
        download_and_cache_unicode_data("ftp://example.com/file", file_path)


# ---------------------------------------------------------------------
# load_unicode_data_from_file
# ---------------------------------------------------------------------

def test_load_unicode_data_from_file_success(tmp_path: Path) -> None:
    """It should return content if file exists and is readable."""
    file_path = tmp_path / "unicode.txt"
    file_path.write_text("0041;LATIN CAPITAL LETTER A;;;;")
    result = load_unicode_data_from_file(file_path, show=False)
    assert isinstance(result, str)
    assert "LATIN CAPITAL" in result


def test_load_unicode_data_from_file_failure(tmp_path: Path) -> None:
    """It should return None on read error."""
    file_path = tmp_path / "missing.txt"
    result = load_unicode_data_from_file(file_path, show=False)
    assert result is None


# ---------------------------------------------------------------------
# parse_unicode_data
# ---------------------------------------------------------------------


def test_parse_unicode_data_valid() -> None:
    """It should return a dictionary mapping character to alternate name."""
    code_point = "0041"
    name = "LATIN CAPITAL LETTER A"

    # Create the field list with enough fields and name at the correct index
    fields = [""] * max(EXPECTED_MIN_FIELDS, ALT_NAME_INDEX + 1)
    fields[0] = code_point
    fields[ALT_NAME_INDEX] = name
    line = ";".join(fields)

    result = parse_unicode_data(line, show=False)
    expected = {chr(int(code_point, 16)): name}
    assert result == expected, f"Expected {expected}, got {result}"

# ---------------------------------------------------------------------
# load_alternate_names (integration-style)
# ---------------------------------------------------------------------

def test_load_alternate_names_local(
    monkeypatch: MonkeyPatch,
    setup_test_root: Callable[[], Path],
    load_fresh_settings: None,
) -> None:
    """It should return parsed dict if local file exists."""
    # 10 fields
    fields = [""] * 19
    fields[0] = "0041"
    fields[10] = "LATIN CAPITAL LETTER A"
    test_data = ";".join(fields) + "\n"
    print(test_data.count(";"))
    root = setup_test_root()
    unicode_file = root / "UnicodeData.txt"
    unicode_file.write_text(test_data)

    monkeypatch.setattr("charfinder.core.unicode_data_loader.get_unicode_data_file", lambda: unicode_file)
    monkeypatch.setattr("charfinder.core.unicode_data_loader.get_unicode_data_url", lambda: "https://example.com/unicode.txt")

    result = load_alternate_names(show=False, use_color=False)
    assert result == {"A": "LATIN CAPITAL LETTER A"}
