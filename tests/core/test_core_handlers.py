"""
Tests for charfinder.core.handlers.
Validates query input, config building, match coordination, and logging.
"""

from __future__ import annotations

from io import StringIO
import logging
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from charfinder.config.types import MatchTuple, SearchConfig
from charfinder.core import handlers as H
from charfinder.config.messages import MSG_DEBUG_REMOVED_DUPLICATE_FUZZY


# ---------------------------------------------------------------------
# _validate_query
# ---------------------------------------------------------------------

def test_validate_query_rejects_non_string() -> None:
    """_validate_query raises TypeError if query is not a string."""
    config = SearchConfig(
        fuzzy=False,
        threshold=1.0,
        name_cache=None,
        verbose=False,
        debug=False,
        use_color=False,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="single",
        exact_match_mode="substring",
        agg_fn="mean",
        prefer_fuzzy=False,
        normalization_profile="aggressive",
    )
    with pytest.raises(TypeError, match="Query must be a string"):
        H._validate_query(cast(Any, 123), config=config)


def test_validate_query_rejects_empty_string() -> None:
    """_validate_query raises ValueError if query is empty."""
    config = SearchConfig(
        fuzzy=True,
        threshold=0.9,
        name_cache=None,
        verbose=True,
        debug=False,
        use_color=True,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="single",
        exact_match_mode="substring",
        agg_fn="max",
        prefer_fuzzy=False,
        normalization_profile="aggressive",
    )
    with pytest.raises(ValueError, match="Query string must not be empty"):
        H._validate_query("   ", config=config)


# ---------------------------------------------------------------------
# build_search_config
# ---------------------------------------------------------------------

def test_build_search_config_valid_threshold() -> None:
    """SearchConfig builds correctly for valid inputs."""
    cfg = H.build_search_config(
        fuzzy=True,
        threshold=0.9,
        name_cache=None,
        verbose=False,
        debug=False,
        use_color=False,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="hybrid",
        exact_match_mode="substring",
        agg_fn="mean",
        prefer_fuzzy=True,
        normalization_profile="aggressive",
    )
    assert isinstance(cfg, SearchConfig)
    assert cfg.threshold == 0.9
    assert cfg.fuzzy_algo == "token_sort_ratio"
    assert cfg.normalization_profile == "aggressive"


def test_build_search_config_invalid_threshold() -> None:
    """Invalid threshold raises ValueError during validation."""
    with pytest.raises(ValueError, match="Invalid threshold"):
        H.build_search_config(
            fuzzy=True,
            threshold=2.5,
            name_cache=None,
            verbose=True,
            debug=False,
            use_color=True,
            fuzzy_algo="simple_ratio",
            fuzzy_match_mode="hybrid",
            exact_match_mode="substring",
            agg_fn="max",
            prefer_fuzzy=False,
            normalization_profile="aggressive",
        )


# ---------------------------------------------------------------------
# _resolve_matches
# ---------------------------------------------------------------------

@patch("charfinder.core.handlers.find_fuzzy_matches")
@patch("charfinder.core.handlers.find_exact_matches")
@patch("charfinder.core.handlers.build_name_cache")
def test_resolve_matches_exact_only(
    mock_cache: MagicMock,
    mock_exact: MagicMock,
    mock_fuzzy: MagicMock,
    log_stream: StringIO,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test exact match path with no fuzzy fallback."""
    mock_exact.return_value = [
        MatchTuple(0x1F600, "😀", "GRINNING FACE", None, False)
    ]
    mock_cache.return_value = {}
    config = H.build_search_config(
        fuzzy=True,
        threshold=0.8,
        name_cache=None,
        verbose=True,
        debug=False,
        use_color=False,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="single",
        exact_match_mode="substring",
        agg_fn="max",
        prefer_fuzzy=False,
        normalization_profile="aggressive",
    )
    matches, used_fuzzy = H._resolve_matches("grin", config=config)
    assert not used_fuzzy
    assert matches[0].name == "GRINNING FACE"


@patch("charfinder.core.handlers.find_fuzzy_matches")
@patch("charfinder.core.handlers.find_exact_matches")
@patch("charfinder.core.handlers.build_name_cache")
def test_resolve_matches_fuzzy_added(
    mock_cache: MagicMock,
    mock_exact: MagicMock,
    mock_fuzzy: MagicMock,
) -> None:
    """Fuzzy results are included and deduped."""
    mock_exact.return_value = []
    mock_fuzzy.return_value = [
        MatchTuple(0x2713, "✓", "CHECK MARK", 0.98, True),
        MatchTuple(0x2714, "✔", "HEAVY CHECK MARK", 0.85, True),
    ]
    mock_cache.return_value = {}
    config = H.build_search_config(
        fuzzy=True,
        threshold=0.7,
        name_cache=None,
        verbose=False,
        debug=False,
        use_color=False,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="hybrid",
        exact_match_mode="substring",
        agg_fn="mean",
        prefer_fuzzy=True,
        normalization_profile="aggressive",
    )
    matches, used_fuzzy = H._resolve_matches("check", config=config)
    assert used_fuzzy is True
    assert len(matches) == 2
    assert matches[0].char == "✓"


@patch("charfinder.core.handlers.build_name_cache")
def test_resolve_matches_invalid_algo(mock_cache: MagicMock) -> None:
    """resolve_algorithm_name failure raises friendly ValueError."""
    mock_cache.return_value = {}
    config = SearchConfig(
        fuzzy=True,
        threshold=0.8,
        name_cache=None,
        verbose=True,
        debug=False,
        use_color=True,
        fuzzy_algo=cast(Any, "invalid_algo"),
        fuzzy_match_mode="hybrid",
        exact_match_mode="substring",
        agg_fn="mean",
        prefer_fuzzy=False,
        normalization_profile="aggressive",
    )
    with pytest.raises(ValueError, match="Invalid fuzzy algorithm"):
        H._resolve_matches("abc", config=config)

@patch("charfinder.core.handlers.find_fuzzy_matches")
@patch("charfinder.core.handlers.find_exact_matches")
@patch("charfinder.core.handlers.build_name_cache")
def test_resolve_matches_logs_removed_duplicates(
    mock_cache: MagicMock,
    mock_exact: MagicMock,
    mock_fuzzy: MagicMock,
    log_stream: StringIO,
    debug_logger: logging.Logger,  # required to route logs to log_stream
) -> None:
    """Debug log is printed when fuzzy matches are deduplicated due to exact matches."""

    mock_exact.return_value = [
        MatchTuple(0x2713, "✓", "CHECK MARK", None, False)
    ]
    mock_fuzzy.return_value = [
        MatchTuple(0x2713, "✓", "CHECK MARK", 1.0, True),   # Duplicate of exact
        MatchTuple(0x2714, "✔", "HEAVY CHECK MARK", 0.9, True),
    ]
    mock_cache.return_value = {}

    config = H.build_search_config(
        fuzzy=True,
        threshold=0.7,
        name_cache=None,
        verbose=True,  # Required to trigger echo and log
        debug=False,
        use_color=False,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="single",
        exact_match_mode="substring",
        agg_fn="mean",
        prefer_fuzzy=True,
        normalization_profile="aggressive",
    )
    matches, used_fuzzy = H._resolve_matches("check", config=config)
    assert used_fuzzy is True
    assert len(matches) == 2

    expected_message = MSG_DEBUG_REMOVED_DUPLICATE_FUZZY.format(removed_count=1)
    log_output = log_stream.getvalue()
    assert expected_message in log_output

# ---------------------------------------------------------------------
# _normalize_and_build_config
# ---------------------------------------------------------------------

def test_normalize_and_build_config_normalizes_and_returns_config() -> None:
    """Query is normalized and returned with SearchConfig."""
    norm, cfg = H._normalize_and_build_config(
        query=" café ",
        fuzzy=True,
        threshold=0.85,
        name_cache=None,
        verbose=False,
        debug=False,
        use_color=True,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="single",
        exact_match_mode="substring",
        agg_fn="mean",
        prefer_fuzzy=False,
        normalization_profile="medium",
    )
    assert isinstance(norm, str)
    assert "CAFE" in norm.upper()
    assert isinstance(cfg, SearchConfig)
