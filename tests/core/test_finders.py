"""
Unit tests for charfinder.core.finders.

Covers:
- find_chars (CLI formatted output)
- find_chars_raw (JSON-style match dicts)
- find_chars_with_info (result + fuzzy flag)
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from charfinder.config.types import MatchTuple, SearchConfig
from charfinder.core import finders as F


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def sample_config() -> SearchConfig:
    """Return a basic SearchConfig with fuzzy disabled."""
    return SearchConfig(
        fuzzy=False,
        threshold=1.0,
        name_cache=None,
        verbose=False,
        use_color=False,
        fuzzy_algo="simple_ratio",
        fuzzy_match_mode="single",
        exact_match_mode="substring",
        agg_fn="mean",
        prefer_fuzzy=False,
        normalization_profile="aggressive",
    )


# ---------------------------------------------------------------------
# find_chars
# ---------------------------------------------------------------------

@patch("charfinder.core.finders._resolve_matches")
def test_find_chars_yields_formatted_lines(mock_resolve: MagicMock, sample_config: SearchConfig) -> None:
    """find_chars yields header + formatted result rows."""
    mock_resolve.return_value = (
        [
            MatchTuple(0x1F600, "😀", "GRINNING FACE", 1.0, False),
            MatchTuple(0x1F609, "😉", "WINKING FACE", 0.93, True),
        ],
        True,
    )
    output = list(F.find_chars(query="face", config=sample_config))
    assert output
    assert "CODE" in output[0]  # header
    assert any("GRINNING" in line for line in output)
    assert any("WINKING" in line for line in output)


# ---------------------------------------------------------------------
# find_chars_raw
# ---------------------------------------------------------------------

@patch("charfinder.core.finders._resolve_matches")
def test_find_chars_raw_returns_dicts(mock_resolve: MagicMock, sample_config: SearchConfig) -> None:
    """find_chars_raw returns list of match dictionaries."""
    mock_resolve.return_value = (
        [
            MatchTuple(0x2713, "✓", "CHECK MARK", 0.98, True),
        ],
        True,
    )
    results = F.find_chars_raw(query="check", config=sample_config)
    assert isinstance(results, list)
    assert isinstance(results[0], dict)
    assert results[0]["char"] == "✓"
    assert results[0]["name"] == "CHECK MARK"


# ---------------------------------------------------------------------
# find_chars_with_info
# ---------------------------------------------------------------------

@patch("charfinder.core.finders._resolve_matches")
def test_find_chars_with_info_returns_both(mock_resolve: MagicMock, sample_config: SearchConfig) -> None:
    """find_chars_with_info returns (results, fuzzy_used)"""
    mock_resolve.return_value = (
        [
            MatchTuple(0x2665, "♥", "BLACK HEART SUIT", 0.92, True),
        ],
        True,
    )
    matches, fuzzy_used = F.find_chars_with_info(query="heart", config=sample_config)
    assert isinstance(matches, list)
    assert matches[0]["char"] == "♥"
    assert fuzzy_used is True
