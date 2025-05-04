from difflib import SequenceMatcher
from rapidfuzz.fuzz import ratio as rapidfuzz_ratio
from Levenshtein import ratio as levenshtein_ratio
from typing import Literal

FuzzyAlgorithm = Literal["sequencematcher", "rapidfuzz", "levenshtein"]
MatchMode = Literal["single", "hybrid"]

def compute_similarity(
    s1: str,
    s2: str,
    algorithm: FuzzyAlgorithm = "sequencematcher",
    mode: MatchMode = "single"
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
    """
    # Normalize case and spacing
    s1 = s1.strip().upper()
    s2 = s2.strip().upper()

    if s1 == s2:
        return 1.0

    if mode == "hybrid":
        return sum([
            SequenceMatcher(None, s1, s2).ratio(),
            rapidfuzz_ratio(s1, s2) / 100.0,
            levenshtein_ratio(s1, s2)
        ]) / 3

    if algorithm == "sequencematcher":
        return SequenceMatcher(None, s1, s2).ratio()
    if algorithm == "rapidfuzz":
        return rapidfuzz_ratio(s1, s2) / 100.0
    if algorithm == "levenshtein":
        return levenshtein_ratio(s1, s2)

    raise ValueError(
        f"Unsupported algorithm: '{algorithm}'. "
        "Expected one of: 'sequencematcher', 'rapidfuzz', 'levenshtein'."
    )