"""Fuzzy matching algorithms and utilities for Charfinder.

Provides consistent wrappers for multiple fuzzy string similarity algorithms,
as well as a hybrid strategy combining multiple scores.

Uses:
    - difflib.SequenceMatcher
    - rapidfuzz.fuzz.ratio
    - Levenshtein.ratio
    - custom simple and normalized ratio algorithms

Public API:
    compute_similarity(): Main function to compute similarity between two strings.
    In addition to SUPPORTED_ALGORITHMS, it supports the following built-in algorithms:
        - 'sequencematcher' (uses difflib.SequenceMatcher)
        - 'rapidfuzz' (uses rapidfuzz.fuzz.ratio)
        - 'levenshtein' (uses Levenshtein.ratio)

Internal algorithms:
    simple_ratio(): Matching character ratio in order.
    normalized_ratio(): Ratio after Unicode normalization and uppercasing.
    levenshtein_ratio(): Levenshtein similarity ratio.
    hybrid_score(): Combine multiple algorithm scores using an aggregation function.

Constants:
    SUPPORTED_ALGORITHMS: Dict of algorithm names to implementations.
    VALID_FUZZY_ALGOS: Allowed algorithm names (from constants.py).
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
from typing import TYPE_CHECKING

import Levenshtein
from rapidfuzz.fuzz import ratio as rapidfuzz_ratio

from charfinder.constants import (
    DEFAULT_NORMALIZATION_FORM,
    VALID_FUZZY_ALGOS,
    VALID_FUZZY_MATCH_MODES,
    VALID_HYBRID_AGG_FUNCS,
    FuzzyAlgorithm,
    MatchMode,
)

if TYPE_CHECKING:
    from charfinder.types import AlgorithmFn

# ---------------------------------------------------------------------
# Algorithms
# ---------------------------------------------------------------------


def simple_ratio(a: str, b: str) -> float:
    """Compute the ratio of matching characters in order.

    Args:
        a: First string.
        b: Second string.

    Returns:
        float: Similarity score in the range [0.0, 1.0].
    """
    matches = sum(1 for c1, c2 in zip(a, b, strict=False) if c1 == c2)
    return matches / max(len(a), len(b)) if max(len(a), len(b)) > 0 else 0.0


def normalized_ratio(a: str, b: str) -> float:
    """Compute ratio after Unicode normalization and uppercasing.

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
    """Compute Levenshtein similarity ratio.

    Args:
        a: First string.
        b: Second string.

    Returns:
        Similarity score in the range [0.0, 1.0].
    """
    return float(Levenshtein.ratio(a, b))


def hybrid_score(a: str, b: str, agg_fn: VALID_HYBRID_AGG_FUNCS = "mean") -> float:
    """Hybrid score combining multiple algorithms with a chosen aggregate function.

    Args:
        a: First string.
        b: Second string.
        agg_fn: Aggregation function to combine scores ("mean", "median", "max", "min").

    Returns:
        Hybrid similarity score in the range [0.0, 1.0].

    Raises:
        ValueError: If agg_fn is not supported.
    """
    scores = [
        simple_ratio(a, b),
        normalized_ratio(a, b),
        levenshtein_ratio(a, b),
    ]

    if agg_fn == "mean":
        return sum(scores) / len(scores)
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

SUPPORTED_ALGORITHMS: dict[str, AlgorithmFn] = {
    "simple_ratio": simple_ratio,
    "normalized_ratio": normalized_ratio,
    "levenshtein_ratio": levenshtein_ratio,
    # Provide hybrid_score with agg_fn="mean" by default for compatibility with AlgorithmFn
    "hybrid_score": functools.partial(hybrid_score, agg_fn="mean"),
}

# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

__all__ = [
    "compute_similarity",
]


def get_supported_algorithms() -> list[str]:
    """Return a list of supported algorithm names.

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
        mode: 'single' (default) to use one algorithm, or 'hybrid' to use `hybrid_score`
            (supports configurable aggregation).
        agg_fn: Aggregation function to aggregate the scores.

    Returns:
        float: Similarity score in the range [0.0, 1.0].

    Raises:
        ValueError: If algorithm or mode is invalid.
        RuntimeError:
            If an unexpected algorithm is passed (should not occur if validation is correct).
    """
    if algorithm not in VALID_FUZZY_ALGOS:
        message = (
            f"Unsupported algorithm: '{algorithm}'. "
            f"Expected one of: {', '.join(VALID_FUZZY_ALGOS)}."
        )
        raise ValueError(message)

    if mode not in VALID_FUZZY_MATCH_MODES:
        message = (
            f"Unsupported match mode: '{mode}'. "
            f"Expected one of: {', '.join(VALID_FUZZY_MATCH_MODES)}."
        )
        raise ValueError(message)

    # Normalize case and spacing
    s1 = s1.strip().upper()
    s2 = s2.strip().upper()

    if s1 == s2:
        return 1.0

    if mode == "hybrid":
        # Use our unified hybrid_score function
        return hybrid_score(s1, s2, agg_fn=agg_fn)
    if algorithm == "sequencematcher":
        return SequenceMatcher(None, s1, s2).ratio()
    if algorithm == "rapidfuzz":
        return float(rapidfuzz_ratio(s1, s2)) / 100.0
    if algorithm == "levenshtein":
        return levenshtein_ratio(s1, s2)

    # Should never reach here
    message = f"Unexpected algorithm: {algorithm}"
    raise RuntimeError(message)
