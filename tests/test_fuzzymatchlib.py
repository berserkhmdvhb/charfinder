"""Tests for fuzzymatchlib.py – all algorithms, modes, and combinations."""

import re
import pytest

from charfinder.fuzzymatchlib import (
    compute_similarity,
    get_fuzzy_algorithm_registry,
    resolve_algorithm_name,
    simple_ratio,
    normalized_ratio,
    levenshtein_ratio,
    token_sort_ratio_score,
    hybrid_score,
    FUZZY_ALGORITHM_REGISTRY,
)
from charfinder.config.constants import (
    VALID_FUZZY_MATCH_MODES,
    VALID_HYBRID_AGG_FUNCS,
    FUZZY_ALGO_ALIASES,
)
from charfinder.config.aliases import (
    FuzzyAlgorithm,
    FuzzyMatchMode,
    HybridAggFunc,
)
from charfinder.config.messages import (
    MSG_ERROR_UNSUPPORTED_ALGO_INPUT,
    MSG_ERROR_INVALID_FUZZY_MATCH_MODE,
    MSG_ERROR_ALGO_NOT_FOUND
)

# ---------------------------------------------------------------------
# Parametrized Combinations
# ---------------------------------------------------------------------

@pytest.mark.parametrize(
    "algorithm,mode,agg_fn",
    [
        *[(algo, "single", None) for algo in FUZZY_ALGORITHM_REGISTRY],
        *[(algo, "hybrid", agg_fn) for algo in FUZZY_ALGORITHM_REGISTRY
          if algo == "hybrid_score"
          for agg_fn in VALID_HYBRID_AGG_FUNCS],
    ],
)
def test_compute_similarity_combinations(
    algorithm: FuzzyAlgorithm,
    mode: FuzzyMatchMode,
    agg_fn: HybridAggFunc | None,
) -> None:
    """Test all algorithm × mode × agg_fn combinations."""
    score = compute_similarity("abc", "abc", algorithm=algorithm, mode=mode, agg_fn=agg_fn or "mean")
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0

# ---------------------------------------------------------------------
# Individual Algorithm Tests
# ---------------------------------------------------------------------

def test_simple_ratio_exact_and_partial() -> None:
    assert simple_ratio("abc", "abc") == 1.0
    assert simple_ratio("abc", "axc") == 2 / 3
    assert simple_ratio("", "") == 0.0


def test_normalized_ratio_with_case_and_accents() -> None:
    assert normalized_ratio("CAFÉ", "CAFE") < 1.0
    assert normalized_ratio("café", "café") == 1.0
    assert normalized_ratio("CAFÉ", "CAFÉ") == 1.0
    assert normalized_ratio("Café", "café") == 1.0


def test_levenshtein_ratio_basic() -> None:
    assert levenshtein_ratio("kitten", "sitting") < 1.0
    assert levenshtein_ratio("abc", "abc") == 1.0


def test_token_sort_ratio_score_disorder() -> None:
    assert token_sort_ratio_score("a b c", "c b a") == 1.0
    assert 0.0 <= token_sort_ratio_score("abc", "xyz") <= 1.0


@pytest.mark.parametrize("agg_fn", sorted(VALID_HYBRID_AGG_FUNCS))
def test_hybrid_score_agg_functions(agg_fn: HybridAggFunc) -> None:
    score = hybrid_score("hello", "hxlxo", agg_fn=agg_fn)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0

# ---------------------------------------------------------------------
# Resolver Tests
# ---------------------------------------------------------------------

@pytest.mark.parametrize("alias,expected", sorted(FUZZY_ALGO_ALIASES.items()))
def test_resolve_algorithm_name_aliases(alias: str, expected: FuzzyAlgorithm) -> None:
    resolved = resolve_algorithm_name(alias)
    assert resolved == expected


def test_resolve_algorithm_name_known_registry_name() -> None:
    for algo in FUZZY_ALGORITHM_REGISTRY:
        resolved = resolve_algorithm_name(algo)
        assert resolved == algo


def test_resolve_algorithm_name_invalid() -> None:
    """It should raise ValueError for unsupported algorithm name."""
    invalid_name = "foo"
    valid_options = sorted(set(FUZZY_ALGO_ALIASES) | set(FUZZY_ALGORITHM_REGISTRY))
    expected_msg = MSG_ERROR_UNSUPPORTED_ALGO_INPUT.format(
        name=invalid_name,
        valid_options=valid_options,
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        resolve_algorithm_name(invalid_name)
# ---------------------------------------------------------------------
# Registry Access
# ---------------------------------------------------------------------

def test_get_fuzzy_algorithm_registry_contains_expected() -> None:
    registry = get_fuzzy_algorithm_registry()
    assert isinstance(registry, list)
    assert "levenshtein_ratio" in registry
    assert set(registry) == set(FUZZY_ALGORITHM_REGISTRY.keys())

# ---------------------------------------------------------------------
# Error Handling
# ---------------------------------------------------------------------

def test_compute_similarity_with_invalid_mode() -> None:
    """It should raise ValueError for invalid fuzzy match mode."""
    invalid_mode = "invalid"
    expected_msg = MSG_ERROR_INVALID_FUZZY_MATCH_MODE.format(
        value=invalid_mode,
        valid_options=", ".join(sorted(VALID_FUZZY_MATCH_MODES)),
    )
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        compute_similarity("a", "b", algorithm="simple_ratio", mode=invalid_mode)  # type: ignore


def test_compute_similarity_with_unregistered_algorithm() -> None:
    """It should raise ValueError if the algorithm is not in the registry."""
    algorithm = "unknown"
    expected_msg = MSG_ERROR_ALGO_NOT_FOUND.format(algorithm=algorithm)
    with pytest.raises(ValueError, match=re.escape(expected_msg)):
        compute_similarity("a", "b", algorithm=algorithm)  # type: ignore