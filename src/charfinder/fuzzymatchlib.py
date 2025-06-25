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
    In addition to FUZZY_ALGORITHM_REGISTRY, it supports the following built-in algorithms:
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
    FUZZY_ALGORITHM_REGISTRY: Dict of algorithm names to implementations.
    VALID_FUZZY_MATCH_MODES: Allowed match modes ("single", "hybrid").
    VALID_HYBRID_AGG_FUNCS: Allowed hybrid aggregation functions ("mean", "median", "max", "min").
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from __future__ import annotations

import statistics
import unicodedata
from typing import TYPE_CHECKING, cast

import Levenshtein
from rapidfuzz import fuzz

from charfinder.config.constants import (
    DEFAULT_HYBRID_AGG_FUNC,
    DEFAULT_NORMALIZATION_FORM,
    FUZZY_ALGO_ALIASES,
)
from charfinder.config.messages import (
    MSG_ERROR_AGG_FN_UNEXPECTED,
    MSG_ERROR_UNSUPPORTED_ALGO_INPUT,
)
from charfinder.validators import (
    validate_fuzzy_algo,
    validate_fuzzy_hybrid_weights,
    validate_fuzzy_match_mode,
    validate_hybrid_agg_fn,
)

if TYPE_CHECKING:
    from charfinder.config.aliases import (
        FuzzyAlgorithm,
        HybridAggFunc,
        NormalizationForm,
    )
    from charfinder.config.types import AlgorithmFn, FuzzyMatchContext


__all__ = ["compute_similarity"]

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


def normalized_ratio(
    a: str,
    b: str,
    normalization_form: NormalizationForm = DEFAULT_NORMALIZATION_FORM,
) -> float:
    """
    Compute ratio after Unicode normalization and uppercasing.

    Args:
        a: First string.
        b: Second string.

    Returns:
        float: Similarity score in the range [0.0, 1.0].
    """
    norm_a = unicodedata.normalize(normalization_form, a).upper()
    norm_b = unicodedata.normalize(normalization_form, b).upper()
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
    return float(fuzz.token_sort_ratio(a, b)) / 100.0


def token_subset_ratio_score(a: str, b: str) -> float:
    """
    Compute a score based on whether tokens from 'a' are a fuzzy subset of tokens in 'b'.
    Each token in 'a' must have a good match in 'b'.

    Args:
        a: Normalized query string (already normalized externally).
        b: Normalized candidate string (already normalized externally).

    Returns:
        float: Similarity score in range [0.0, 1.0]
    """
    a_tokens = a.split()
    b_tokens = b.split()

    if not a_tokens or not b_tokens:
        return 0.0

    matched_scores = []
    for a_token in a_tokens:
        # Find best match for this query token in the candidate tokens
        best_score = max(fuzz.ratio(a_token, b_token) for b_token in b_tokens)
        matched_scores.append(best_score)

    # Final score = average normalized match quality of all query tokens
    return sum(matched_scores) / (100.0 * len(matched_scores))


def hybrid_score(
    a: str,
    b: str,
    agg_fn: HybridAggFunc = DEFAULT_HYBRID_AGG_FUNC,
    weights: dict[str, float] | None = None,
) -> float:
    """
    Hybrid score combining multiple algorithms with a chosen aggregate function.

    Args:
        a: First string.
        b: Second string.
        agg_fn: Aggregation function to combine scores ("mean", "median", "max", "min").
        weights: Optional dict of algorithm names to weights. If None, uses env/default.

    Returns:
        float: Hybrid similarity score in the range [0.0, 1.0].

    Raises:
        ValueError: If agg_fn is not supported or weights are invalid.
    """
    agg_fn = validate_hybrid_agg_fn(agg_fn)
    weights = validate_fuzzy_hybrid_weights(weights)

    components = {
        "simple_ratio": simple_ratio(a, b),
        "normalized_ratio": normalized_ratio(a, b),
        "levenshtein_ratio": levenshtein_ratio(a, b),
        "token_sort_ratio": token_sort_ratio_score(a, b),
        "token_subset_ratio": token_subset_ratio_score(a, b),
    }

    if agg_fn == "mean":
        return sum(components[name] * weights.get(name, 0.0) for name in weights)

    scores = list(components.values())

    if agg_fn == "median":
        return statistics.median(scores)
    if agg_fn == "max":
        return max(scores)
    if agg_fn == "min":
        return min(scores)

    raise RuntimeError(MSG_ERROR_AGG_FN_UNEXPECTED.format(agg_fn=agg_fn))


# ---------------------------------------------------------------------
# Supported Algorithms
# ---------------------------------------------------------------------

FUZZY_ALGORITHM_REGISTRY: dict[FuzzyAlgorithm, AlgorithmFn] = {
    "simple_ratio": simple_ratio,
    "normalized_ratio": normalized_ratio,
    "levenshtein_ratio": levenshtein_ratio,
    "token_sort_ratio": token_sort_ratio_score,
    "token_subset_ratio": token_subset_ratio_score,
    "hybrid_score": hybrid_score,
}


def resolve_algorithm_name(name: str) -> FuzzyAlgorithm:
    """
    Normalize and resolve a user-specified fuzzy algorithm name to its internal canonical name.

    Args:
        name (str): Algorithm name from user input.

    Returns:
        FuzzyAlgorithm: Validated canonical algorithm name.

    Raises:
        ValueError: If the name is unknown or unsupported.
    """
    normalized = name.strip().lower().replace("-", "_")

    if normalized in FUZZY_ALGO_ALIASES:
        return FUZZY_ALGO_ALIASES[normalized]
    if normalized in FUZZY_ALGORITHM_REGISTRY:
        return cast("FuzzyAlgorithm", normalized)

    valid_options = sorted(set(FUZZY_ALGO_ALIASES) | set(FUZZY_ALGORITHM_REGISTRY))
    raise ValueError(
        MSG_ERROR_UNSUPPORTED_ALGO_INPUT.format(name=name, valid_options=", ".join(valid_options))
    )


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def get_fuzzy_algorithm_registry() -> list[str]:
    """
    Return a list of supported algorithm names.

    Returns:
        list[str]: List of supported algorithm names.
    """
    return list(FUZZY_ALGORITHM_REGISTRY.keys())


def compute_similarity(
    s1: str,
    s2: str,
    context: FuzzyMatchContext,
) -> float:
    """
    Compute similarity between two strings using a specified fuzzy algorithm
    or a hybrid strategy.

    Args:
        s1: First string (e.g., query).
        s2: Second string (e.g., candidate).
        context: Match configuration (algorithm, mode, weights, agg_fn, etc.)

    Returns:
        float: Similarity score in the range [0.0, 1.0].

    Raises:
        ValueError: If match mode is invalid.
        RuntimeError: If an unexpected algorithm is passed.
    """
    algorithm = validate_fuzzy_algo(context.fuzzy_algo)
    mode = validate_fuzzy_match_mode(context.match_mode)

    if mode == "hybrid":
        return hybrid_score(s1, s2, agg_fn=context.agg_fn, weights=context.weights)

    resolved_algo = FUZZY_ALGORITHM_REGISTRY[algorithm]
    return resolved_algo(s1, s2)
