"""
Fuzzy matching utilities for charfinder.

This module provides a unified interface to compute string similarity
using different fuzzy matching algorithms:

- SequenceMatcher (difflib)
- RapidFuzz
- Levenshtein

It supports both single algorithm mode and hybrid mode (averaging results).

Functions:
- compute_similarity: Compute similarity score between two strings.
"""

from __future__ import annotations

from difflib import SequenceMatcher

from Levenshtein import ratio as levenshtein_ratio
from rapidfuzz.fuzz import ratio as rapidfuzz_ratio

from charfinder.constants import (
    VALID_FUZZY_ALGOS,
    VALID_FUZZY_MATCH_MODES,
    FuzzyAlgorithm,
    MatchMode,
)

__all__ = [
    "compute_similarity",
]


def compute_similarity(
    s1: str,
    s2: str,
    algorithm: FuzzyAlgorithm = "sequencematcher",
    mode: MatchMode = "single",
) -> float:
    """
    Compute similarity between two strings using a specified fuzzy algorithm
    or a hybrid strategy.

    Args:
        s1: First string (e.g., query).
        s2: Second string (e.g., candidate).
        algorithm: One of 'sequencematcher', 'rapidfuzz', or 'levenshtein'.
        mode: 'single' (default) to use one algorithm, or 'hybrid' to average all.

    Returns:
        Similarity score in the range [0.0, 1.0].

    Raises:
        ValueError: If algorithm or mode is invalid.
    """
    if algorithm not in VALID_FUZZY_ALGOS:
        msg = (
            f"Unsupported algorithm: '{algorithm}'. "
            f"Expected one of: {', '.join(VALID_FUZZY_ALGOS)}."
        )
        raise ValueError(msg)

    if mode not in VALID_FUZZY_MATCH_MODES:
        msg = (
            f"Unsupported match mode: '{mode}'. "
            f"Expected one of: {', '.join(VALID_FUZZY_MATCH_MODES)}."
        )
        raise ValueError(msg)

    # Normalize case and spacing
    s1 = s1.strip().upper()
    s2 = s2.strip().upper()

    if s1 == s2:
        return 1.0

    if mode == "hybrid":
        scores = [
            SequenceMatcher(None, s1, s2).ratio(),
            rapidfuzz_ratio(s1, s2) / 100.0,
            levenshtein_ratio(s1, s2),
        ]
        return sum(scores) / len(scores)

    if algorithm == "sequencematcher":
        return SequenceMatcher(None, s1, s2).ratio()
    if algorithm == "rapidfuzz":
        return rapidfuzz_ratio(s1, s2) / 100.0
    if algorithm == "levenshtein":
        return levenshtein_ratio(s1, s2)

    # Should never reach here
    msg = f"Unexpected algorithm: {algorithm}"
    raise RuntimeError(msg)
