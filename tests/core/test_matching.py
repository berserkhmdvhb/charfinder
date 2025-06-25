"""
Unit tests for charfinder.core.matching.

Covers:
- find_exact_matches (substring, word-subset, verbose, invalid mode)
- find_fuzzy_matches (threshold, alt name scoring, verbose logging, skip scoring)
"""

from __future__ import annotations

from io import StringIO
import logging
import pytest
import re

from charfinder.config.types import FuzzyMatchContext
from charfinder.core.matching import find_exact_matches, find_fuzzy_matches
from charfinder.config.constants import DEFAULT_THRESHOLD, VALID_EXACT_MATCH_MODES
from charfinder.config.messages import (
    MSG_EXACT_CHECKING,
    MSG_ERROR_INVALID_EXACT_MATCH_MODE,
    MSG_SUBSET_CHECKING,
)

# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def sample_name_cache() -> dict[str, dict[str, str]]:
    return {
        "✓": {

            "original": "CHECK MARK",
            "normalized": "check mark",
            "alternate_normalized": "tick",
        },
        "✗": {
            "original": "BALLOT X",
            "normalized": "ballot x",
        },
    }


@pytest.fixture
def fuzzy_context() -> FuzzyMatchContext:
    return FuzzyMatchContext(
        query="check",
        threshold=DEFAULT_THRESHOLD,
        fuzzy_algo="simple_ratio",
        match_mode="single",
        agg_fn="mean",
        verbose=False,
        debug=False,
        use_color=False,
    )


# ---------------------------------------------------------------------
# find_exact_matches
# ---------------------------------------------------------------------

def test_exact_match_substring(sample_name_cache: dict[str, dict[str, str]]) -> None:
    matches = find_exact_matches("check", sample_name_cache, "substring")
    assert len(matches) == 1
    assert matches[0].char == "✓"


def test_exact_match_word_subset(sample_name_cache: dict[str, dict[str, str]]) -> None:
    matches = find_exact_matches("ballot", sample_name_cache, "word-subset")
    assert len(matches) == 1
    assert matches[0].char == "✗"


def test_exact_match_invalid_mode(sample_name_cache: dict[str, dict[str, str]]) -> None:
    with pytest.raises(ValueError):
        find_exact_matches("check", sample_name_cache, "unsupported-mode")


def test_exact_match_verbose_output(sample_name_cache: dict[str, dict[str, str]]) -> None:
    # Should not raise with verbose logging enabled
    result = find_exact_matches("check", sample_name_cache, "substring", verbose=True)
    assert any(match.char == "✓" for match in result)


# ---------------------------------------------------------------------
# find_fuzzy_matches
# ---------------------------------------------------------------------

def test_fuzzy_match_single_score(fuzzy_context: FuzzyMatchContext, sample_name_cache: dict[str, dict[str, str]]) -> None:
    fuzzy_context.fuzzy_algo = "token_sort_ratio"
    fuzzy_context.threshold = 0.65
    results = find_fuzzy_matches("check", sample_name_cache, fuzzy_context)
    assert isinstance(results, list)
    assert results
    assert results[0].char == "✓"
    assert results[0].name == "CHECK MARK"


def test_fuzzy_match_alt_name_scoring(fuzzy_context: FuzzyMatchContext) -> None:
    name_cache = {
        "✔": {
            "original": "HEAVY CHECK MARK",
            "normalized": "irrelevant",
            "alternate_normalized": "check",
        }
    }
    results = find_fuzzy_matches("check", name_cache, fuzzy_context)
    assert len(results) == 1
    assert results[0].char == "✔"
    assert results[0].score == pytest.approx(1.0)


def test_fuzzy_match_skip_when_no_score(fuzzy_context: FuzzyMatchContext) -> None:
    name_cache = {
        "✘": {
            "original": "HEAVY BALLOT X",
            "normalized": "",
            "alternate_normalized": "",
        }
    }
    results = find_fuzzy_matches("check", name_cache, fuzzy_context)
    assert results == []


def test_fuzzy_match_verbose_logging(
    fuzzy_context: FuzzyMatchContext,
    sample_name_cache: dict[str, dict[str, str]],
    debug_logger: logging.Logger,
    log_stream: StringIO,
) -> None:
    """Fuzzy match emits verbose logs when verbose=True."""
    fuzzy_context.verbose = True
    fuzzy_context.debug = False
    fuzzy_context.query = "check"
    fuzzy_context.threshold = 0.5
    fuzzy_context.fuzzy_algo = "token_sort_ratio"

    results = find_fuzzy_matches("check", sample_name_cache, fuzzy_context)
    output = log_stream.getvalue()

    assert results
    assert "trying fuzzy" in output
    assert "threshold=0.5" in output

def test_fuzzy_match_verbose__debug_logging(
    fuzzy_context: FuzzyMatchContext,
    sample_name_cache: dict[str, dict[str, str]],
    debug_logger: logging.Logger,
    log_stream: StringIO,
) -> None:
    """Fuzzy match emits verbose logs when verbose=True."""
    fuzzy_context.verbose = True
    fuzzy_context.debug = True
    fuzzy_context.query = "check"
    fuzzy_context.threshold = 0.5
    fuzzy_context.fuzzy_algo = "token_sort_ratio"

    results = find_fuzzy_matches("check", sample_name_cache, fuzzy_context)
    output = log_stream.getvalue()

    assert results
    assert "trying fuzzy" in output
    assert "threshold=0.5" in output
    assert "Skipped char" in output


def test_find_exact_matches_logs_when_verbose(
    log_stream: StringIO,
    debug_logger: logging.Logger,  # ensures logger is wired to log_stream
) -> None:
    """Should log exact checking details when verbose=True."""
    name_cache = {
        "✓": {"original": "CHECK MARK", "normalized": "check mark"},
    }

    result = find_exact_matches(
        "check",
        name_cache,
        exact_match_mode="substring",
        verbose=True,
    )

    assert result

    expected_msg = MSG_EXACT_CHECKING.format(
        code=0x2713,
        name="check mark",
        alt="",
    )

    log_output = log_stream.getvalue()
    assert expected_msg in log_output


def test_find_exact_matches_raises_on_invalid_mode() -> None:
    """Should raise if an unsupported exact match mode is given."""
    name_cache = {
        "✓": {"original": "CHECK MARK", "normalized": "check mark"},
    }
    expected_msg = MSG_ERROR_INVALID_EXACT_MATCH_MODE.format(
        value="invalid",
        valid_options=", ".join(sorted(VALID_EXACT_MATCH_MODES)),
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        find_exact_matches("check", name_cache, exact_match_mode="invalid", verbose=False)


def test_word_subset_logs_when_verbose(
    sample_name_cache: dict[str, dict[str, str]],
    log_stream: StringIO,
    debug_logger: logging.Logger,
) -> None:
    """Should log subset matching details when verbose=True in word-subset mode."""
    result = find_exact_matches(
        "ballot",
        sample_name_cache,
        exact_match_mode="word-subset",
        verbose=True,
    )
    assert result

    expected_1 = MSG_SUBSET_CHECKING.format(
        query=set(["ballot"]),
        name=set(["check", "mark", "tick"]),
    )
    expected_2 = MSG_SUBSET_CHECKING.format(
        query=set(["ballot"]),
        name=set(["ballot", "x"]),
    )

    log_output = log_stream.getvalue()
    assert expected_1 in log_output
    assert expected_2 in log_output
