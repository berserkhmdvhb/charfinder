"""Fuzzy matching algorithms and utilities for Charfinder.

Provides consistent wrappers for multiple fuzzy string similarity algorithms,
as well as a hybrid strategy combining multiple scores.

Uses:
    - difflib.SequenceMatcher
    - rapidfuzz.fuzz.ratio
    - Levenshtein.ratio
    - rapidfuzz.fuzz.token_sort_ratio
    - custom simple and normalized ratio algorithms

Functions:
    compute_similarity(): Main function to compute similarity between two strings.
    In addition to SUPPORTED_ALGORITHMS, it supports the following built-in algorithms:
        - 'sequencematcher' (uses difflib.SequenceMatcher)
        - 'rapidfuzz' (uses rapidfuzz.fuzz.ratio)
        - 'levenshtein' (uses Levenshtein.ratio)
        - 'token_sort_ratio' (uses rapidfuzz.fuzz.token_sort_ratio)

Internal algorithms:
    simple_ratio(): Matching character ratio in order.
    normalized_ratio(): Ratio after Unicode normalization and uppercasing.
    levenshtein_ratio(): Levenshtein similarity ratio.
    token_sort_ratio_score(): Word-order-agnostic similarity via token sort.
    hybrid_score():
        Combine multiple algorithm scores using an aggregation function or weighted mean.

Constants:
    SUPPORTED_ALGORITHMS: Dict of algorithm names to implementations.
    VALID_FUZZY_MATCH_MODES: Allowed match modes ("single", "hybrid").
    VALID_HYBRID_AGG_FUNCS: Allowed hybrid aggregation functions ("mean", "median", "max", "min").
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from __future__ import annotations

import functools
import statistics
import unicodedata
from difflib import SequenceMatcher
from typing import TYPE_CHECKING, cast

import Levenshtein
from rapidfuzz.fuzz import ratio as rapidfuzz_ratio
from rapidfuzz.fuzz import token_sort_ratio

from charfinder.constants import (
    DEFAULT_NORMALIZATION_FORM,
    FUZZY_ALGO_ALIASES,
    FUZZY_HYBRID_WEIGHTS,
    VALID_FUZZY_MATCH_MODES,
    VALID_HYBRID_AGG_FUNCS,
    FuzzyAlgorithm,
    MatchMode,
)

if TYPE_CHECKING:
    from charfinder.types import AlgorithmFn

__all__ = ["compute_similarity", "resolve_algorithm_name"]

# ---------------------------------------------------------------------
# Algorithms
# ---------------------------------------------------------------------


def simple_ratio(a: str, b: str) -> float:
    """
    Compute the ratio of matching characters in order.

    Args:
        a: First string.
        b: Second string.

    Returns:
        float: Similarity score in the range [0.0, 1.0].
    """
    matches = sum(1 for c1, c2 in zip(a, b, strict=False) if c1 == c2)
    return matches / max(len(a), len(b)) if max(len(a), len(b)) > 0 else 0.0


def normalized_ratio(a: str, b: str) -> float:
    """
    Compute ratio after Unicode normalization and uppercasing.

    Args:
        a: First string.
        b: Second string.

    Returns:
        float: Similarity score in the range [0.0, 1.0].
    """
    norm_a = unicodedata.normalize(DEFAULT_NORMALIZATION_FORM, a).upper()
    norm_b = unicodedata.normalize(DEFAULT_NORMALIZATION_FORM, b).upper()
    matches = sum(1 for c1, c2 in zip(norm_a, norm_b, strict=False) if c1 == c2)
    return matches / max(len(norm_a), len(norm_b)) if max(len(norm_a), len(norm_b)) > 0 else 0.0


def levenshtein_ratio(a: str, b: str) -> float:
    """
    Compute Levenshtein similarity ratio.

    Args:
        a: First string.
        b: Second string.

    Returns:
        float: Similarity score in the range [0.0, 1.0].
    """
    return float(Levenshtein.ratio(a, b))


def token_sort_ratio_score(a: str, b: str) -> float:
    """
    Token-sort fuzzy ratio using RapidFuzz (handles word reordering and partial matches).

    Args:
        a: First string.
        b: Second string.

    Returns:
        float: Similarity score in the range [0.0, 1.0].
    """
    return token_sort_ratio(a, b) / 100.0


def hybrid_score(a: str, b: str, agg_fn: VALID_HYBRID_AGG_FUNCS = "mean") -> float:
    """
    Hybrid score combining multiple algorithms with a chosen aggregate function.

    Args:
        a: First string.
        b: Second string.
        agg_fn: Aggregation function to combine scores ("mean", "median", "max", "min").

    Returns:
        float: Hybrid similarity score in the range [0.0, 1.0].

    Raises:
        ValueError: If agg_fn is not supported.
    """
    components = {
        "simple_ratio": simple_ratio(a, b),
        "normalized_ratio": normalized_ratio(a, b),
        "levenshtein_ratio": levenshtein_ratio(a, b),
        "token_sort_ratio": token_sort_ratio_score(a, b),
    }

    if agg_fn == "mean":
        return sum(
            components[name] * FUZZY_HYBRID_WEIGHTS.get(name, 0.0) for name in FUZZY_HYBRID_WEIGHTS
        )

    scores = list(components.values())

    if agg_fn == "median":
        return statistics.median(scores)
    if agg_fn == "max":
        return max(scores)
    if agg_fn == "min":
        return min(scores)

    message = f"Unsupported agg_fn: {agg_fn!r}"
    raise ValueError(message)


# ---------------------------------------------------------------------
# Supported Algorithms
# ---------------------------------------------------------------------

SUPPORTED_ALGORITHMS: dict[FuzzyAlgorithm, AlgorithmFn] = {
    "simple_ratio": simple_ratio,
    "normalized_ratio": normalized_ratio,
    "levenshtein_ratio": levenshtein_ratio,
    "token_sort_ratio": token_sort_ratio_score,
    "hybrid_score": functools.partial(hybrid_score, agg_fn="mean"),
}


def resolve_algorithm_name(name: str) -> FuzzyAlgorithm:
    """
    Normalize user-specified algorithm name to internal name.

    Args:
        name: Algorithm name from user input.

    Returns:
        FuzzyAlgorithm: Validated internal algorithm name.

    Raises:
        ValueError: If the name is unknown.
    """
    folded = name.casefold()

    if folded in SUPPORTED_ALGORITHMS:
        return cast("FuzzyAlgorithm", folded)
    if folded in FUZZY_ALGO_ALIASES:
        return cast("FuzzyAlgorithm", FUZZY_ALGO_ALIASES[folded])

    message = (
        f"Unknown fuzzy algorithm: '{name}'. "
        f"Expected one of: {', '.join(sorted(FUZZY_ALGO_ALIASES.keys()))}."
    )
    raise ValueError(message)


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def get_supported_algorithms() -> list[str]:
    """
    Return a list of supported algorithm names.

    Returns:
        list[str]: List of supported algorithm names.
    """
    return list(SUPPORTED_ALGORITHMS.keys())


def compute_similarity(
    s1: str,
    s2: str,
    algorithm: FuzzyAlgorithm = "sequencematcher",
    mode: MatchMode = "single",
    agg_fn: VALID_HYBRID_AGG_FUNCS = "mean",
) -> float:
    """
    Compute similarity between two strings using a specified fuzzy algorithm
    or a hybrid strategy.

    Args:
        s1: First string (e.g., query).
        s2: Second string (e.g., candidate).
        algorithm: One of 'sequencematcher', 'rapidfuzz', or 'levenshtein'.
        mode: 'single' (default) to use one algorithm, or 'hybrid' to use hybrid_score
            (supports configurable aggregation).
        agg_fn: Aggregation function to aggregate the scores.

    Returns:
        float: Similarity score in the range [0.0, 1.0].

    Raises:
        ValueError: If match mode is invalid.
        RuntimeError: If an unexpected algorithm is passed.
    """
    resolved_algo = resolve_algorithm_name(algorithm)

    if mode not in VALID_FUZZY_MATCH_MODES:
        message = (
            f"Unsupported match mode: '{mode}'. "
            f"Expected one of: {', '.join(VALID_FUZZY_MATCH_MODES)}."
        )
        raise ValueError(message)

    s1 = s1.strip().upper()
    s2 = s2.strip().upper()

    if s1 == s2:
        return 1.0

    if mode == "hybrid":
        return hybrid_score(s1, s2, agg_fn=agg_fn)

    if resolved_algo == "sequencematcher":
        return SequenceMatcher(None, s1, s2).ratio()
    if resolved_algo == "rapidfuzz":
        return float(rapidfuzz_ratio(s1, s2)) / 100.0

    return SUPPORTED_ALGORITHMS[resolved_algo](s1, s2)
