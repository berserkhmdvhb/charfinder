from difflib import SequenceMatcher

from Levenshtein import ratio as levenshtein_ratio
from rapidfuzz.fuzz import ratio as rapidfuzz_ratio

# constants and aliases
from .constants import VALID_FUZZY_ALGOS, VALID_MATCH_MODES, FuzzyAlgorithm, MatchMode


def compute_similarity(
    s1: str, s2: str, algorithm: FuzzyAlgorithm = "sequencematcher", mode: MatchMode = "single"
) -> float:
    """
    Compute similarity between two strings using a specified fuzzy algorithm
    or a hybrid strategy.

    Args:
        s1 (str): First string (e.g., query).
        s2 (str): Second string (e.g., candidate).
        algorithm (str): One of 'sequencematcher', 'rapidfuzz', 'levenshtein'.
        mode (str): 'single' (default) to use one algorithm, or 'hybrid' to average all.

    Returns:
        float: Similarity score in the range [0.0, 1.0].

    Raises:
        ValueError: If algorithm or mode is invalid.
    """
    if algorithm not in VALID_FUZZY_ALGOS:
        raise ValueError(
            f"Unsupported algorithm: '{algorithm}'. "
            f"Expected one of: {', '.join(VALID_FUZZY_ALGOS)}."
        )

    if mode not in VALID_MATCH_MODES:
        raise ValueError(
            f"Unsupported match mode: '{mode}'. "
            f"Expected one of: {', '.join(VALID_MATCH_MODES)}."
        )

    # Normalize case and spacing
    s1 = s1.strip().upper()
    s2 = s2.strip().upper()

    if s1 == s2:
        return 1.0

    if mode == "hybrid":
        return (
            sum(
                (
                    SequenceMatcher(None, s1, s2).ratio(),
                    rapidfuzz_ratio(s1, s2) / 100.0,
                    levenshtein_ratio(s1, s2),
                )
            )
            / 3
        )

    if algorithm == "sequencematcher":
        return SequenceMatcher(None, s1, s2).ratio()
    if algorithm == "rapidfuzz":
        return rapidfuzz_ratio(s1, s2) / 100.0
    return levenshtein_ratio(s1, s2)
