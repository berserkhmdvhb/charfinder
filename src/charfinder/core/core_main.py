"""
Core logic for charfinder.

This module provides the core processing functions for Unicode character search
with fuzzy matching and name normalization.

It is intentionally kept free of any CLI-specific or I/O code to maximize
testability and reusability.

Functions in this module:
- `normalize`: Normalize Unicode names for comparison.
- `build_name_cache`: Build and cache Unicode character name mappings.
- `find_chars`: Search Unicode characters by exact or fuzzy name match.

This module adheres to clean-code principles and is part of the library
interface exposed via `__all__`.
"""

from __future__ import annotations

from collections.abc import Generator

from charfinder.constants import (
    DEFAULT_THRESHOLD,
    VALID_FUZZY_ALGOS,
    VALID_FUZZY_MATCH_MODES,
    FuzzyAlgorithm,
    MatchMode,
)
from charfinder.core.matching import find_exact_matches, find_fuzzy_matches
from charfinder.core.name_cache import build_name_cache
from charfinder.types import CharMatch, FuzzyMatchContext
from charfinder.utils.formatter import echo, format_result_header, format_result_row
from charfinder.utils.logger_styles import format_info
from charfinder.utils.normalizer import normalize

__all__ = [
    "find_chars",
    "find_chars_raw",
]


def find_chars(
    query: str,
    *,
    fuzzy: bool = False,
    threshold: float = DEFAULT_THRESHOLD,
    name_cache: dict[str, dict[str, str]] | None = None,
    verbose: bool = True,
    use_color: bool = True,
    fuzzy_algo: FuzzyAlgorithm = "sequencematcher",
    fuzzy_match_mode: MatchMode = "single",
    exact_match_mode: str = "word-subset",
) -> Generator[str, None, None]:
    """
    Search for Unicode characters by name using exact or fuzzy matching.

    Args:
        query: Input query string.
        fuzzy: Whether to enable fuzzy matching.
        threshold: Fuzzy match threshold.
        name_cache: Optional prebuilt Unicode name cache.
        verbose: Whether to log progress.
        use_color: Whether to colorize log output.
        fuzzy_algo: Algorithm to use for fuzzy scoring.
        fuzzy_match_mode: 'single' or 'hybrid'.
        exact_match_mode: 'substring' or 'word-subset'.

    Yields:
        Each line to be printed for the result table (header first, then matching rows).
    """
    if fuzzy_algo not in VALID_FUZZY_ALGOS:
        valid_algos = ", ".join(VALID_FUZZY_ALGOS)
        msg = f"Invalid fuzzy algorithm: '{fuzzy_algo}'. Must be one of: {valid_algos}"
        raise ValueError(msg)

    if fuzzy_match_mode not in VALID_FUZZY_MATCH_MODES:
        msg = f"Invalid fuzzy match mode: '{fuzzy_match_mode}'. Must be 'single' or 'hybrid'."
        raise ValueError(msg)

    if not isinstance(query, str):
        msg = "Query must be a string."
        raise TypeError(msg)

    if not query.strip():
        msg = "Query string must not be empty."
        raise ValueError(msg)

    if name_cache is None:
        name_cache = build_name_cache(verbose=verbose, use_color=use_color)

    norm_query = normalize(query)
    matches: list[tuple[int, str, str, float | None]] = find_exact_matches(
        norm_query, name_cache, exact_match_mode
    )

    if not matches and fuzzy:
        context = FuzzyMatchContext(
            threshold=threshold,
            fuzzy_algo=fuzzy_algo,
            match_mode=fuzzy_match_mode,
            verbose=verbose,
            use_color=use_color,
            query=query,
        )
        matches.extend(find_fuzzy_matches(norm_query, name_cache, context))

    match_info = f"Found {len(matches)} match(es)" if matches else "No matches found"
    message = f"{match_info} for query: '{query}'"
    echo(
        message,
        style=lambda m: format_info(m, use_color=use_color),
        show=verbose,
        log=True,
        log_method="info",
    )

    if not matches:
        return

    yield from format_result_header(has_score=(matches[0][3] is not None))

    for code, char, name, score in matches:
        yield format_result_row(code, char, name, score)


def find_chars_raw(
    query: str,
    *,
    fuzzy: bool = False,
    threshold: float = DEFAULT_THRESHOLD,
    name_cache: dict[str, dict[str, str]] | None = None,
    verbose: bool = True,
    fuzzy_algo: FuzzyAlgorithm = "sequencematcher",
    fuzzy_match_mode: MatchMode = "single",
    exact_match_mode: str = "word-subset",
) -> list[CharMatch]:
    """
    Search for Unicode characters and return raw results for JSON output.

    Args:
        query: Input query string.
        fuzzy: Whether to enable fuzzy matching.
        threshold: Fuzzy match threshold.
        name_cache: Optional prebuilt Unicode name cache.
        verbose: Whether to log progress.
        fuzzy_algo: Algorithm to use for fuzzy scoring.
        fuzzy_match_mode: 'single' or 'hybrid'.
        exact_match_mode: 'substring' or 'word-subset'.

    Returns:
        List of dicts: [{code, char, name, (score)}]
    """
    if name_cache is None:
        name_cache = build_name_cache(verbose=verbose, use_color=True)

    norm_query = normalize(query)
    matches: list[tuple[int, str, str, float | None]] = find_exact_matches(
        norm_query, name_cache, exact_match_mode
    )

    if not matches and fuzzy:
        context = FuzzyMatchContext(
            threshold=threshold,
            fuzzy_algo=fuzzy_algo,
            match_mode=fuzzy_match_mode,
            verbose=verbose,
            use_color=False,  # no color needed for raw output
            query=query,
        )
        matches.extend(find_fuzzy_matches(norm_query, name_cache, context))

    match_info = f"Found {len(matches)} match(es)" if matches else "No matches found"
    message = f"{match_info} for query: '{query}'"
    echo(
        message,
        format_info,
        show=verbose,
        log=True,
        log_method="info",
    )

    results: list[CharMatch] = []
    for code, char, name, score in matches:
        item: CharMatch = {
            "code": f"U+{code:04X}",
            "char": char,
            "name": f"{name}  (\\u{code:04x})",
        }
        if score is not None:
            item["score"] = round(score, 3)
        results.append(item)

    return results
