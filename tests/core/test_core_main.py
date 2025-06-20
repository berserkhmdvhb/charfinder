"""Tests for public API functions in charfinder.core.core_main."""

from unittest.mock import MagicMock, patch

import pytest
from typing import Any, cast
from charfinder.core.core_main import (
    find_chars,
    find_chars_raw,
    find_chars_with_info,
)


@pytest.mark.parametrize(
    "fuzzy, threshold, prefer_fuzzy",
    [
        (False, 1.0, False),
        (True, 0.85, False),
        (True, 0.9, True),
    ],
)
@patch("charfinder.core.core_main._find_chars_impl")
def test_find_chars_delegation(
    mock_impl: MagicMock,
    fuzzy: bool,
    threshold: float,
    prefer_fuzzy: bool,
) -> None:
    query = "heart"
    find_chars(query, fuzzy=fuzzy, threshold=threshold, prefer_fuzzy=prefer_fuzzy)
    mock_impl.assert_called_once()
    _, kwargs = mock_impl.call_args
    config = kwargs["config"]
    assert config.fuzzy == fuzzy
    assert config.threshold == threshold
    assert config.prefer_fuzzy == prefer_fuzzy


@patch("charfinder.core.core_main._find_chars_raw_impl")
def test_find_chars_raw_returns_match_list(mock_impl: MagicMock) -> None:
    query = "smile"
    mock_impl.return_value = [{"char": "☺", "name": "WHITE SMILING FACE"}]
    results = find_chars_raw(query)
    assert isinstance(results, list)
    assert results[0]["char"] == "☺"
    mock_impl.assert_called_once()


@patch("charfinder.core.core_main._find_chars_info_impl")
def test_find_chars_with_info_returns_tuple(mock_impl: MagicMock) -> None:
    query = "check"
    mock_impl.return_value = ([{"char": "✓", "name": "CHECK MARK"}], True)
    matches, used_fuzzy = find_chars_with_info(query)
    assert isinstance(matches, list)
    assert used_fuzzy is True
    assert any("✓" in str(item["char"]) for item in matches)
    mock_impl.assert_called_once()


@patch("charfinder.core.core_main._find_chars_impl")
def test_find_chars_empty_query(mock_impl: MagicMock) -> None:
    find_chars("")
    mock_impl.assert_called_once()
    _, kwargs = mock_impl.call_args
    assert kwargs["query"] == ""



@patch("charfinder.core.core_main._find_chars_impl")
def test_find_chars_invalid_threshold_capped(mock_impl: MagicMock) -> None:
    with pytest.raises(ValueError):
        find_chars("abc", threshold=1.7)


@patch("charfinder.core.core_main._find_chars_impl")
def test_find_chars_invalid_fuzzy_algo_fallback(mock_impl: MagicMock) -> None:
    with pytest.raises(ValueError):
        find_chars("abc", fuzzy_algo=cast(Any, "bad_algo"))


@patch("charfinder.core.core_main._find_chars_impl")
def validate_prefer_fuzzy(value: Any) -> bool:
    if not isinstance(value, bool):
        raise TypeError("prefer_fuzzy must be a boolean")
    return value
