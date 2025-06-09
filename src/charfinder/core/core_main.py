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

import json
import logging
import sys
import unicodedata
from collections.abc import Generator
from pathlib import Path
from typing import cast

from charfinder.constants import (
    DEFAULT_THRESHOLD,
    VALID_FUZZY_ALGOS,
    VALID_FUZZY_MATCH_MODES,
    FuzzyAlgorithm,
    MatchMode,
)
from charfinder.fuzzymatchlib import compute_similarity
from charfinder.types import CharMatch, FuzzyMatchContext
from charfinder.utils.formatter import (
    echo,
    format_debug,
    format_error,
    format_info,
    format_result_header,
    format_result_row,
)

__all__ = [
    "build_name_cache",
    "find_chars",
    "find_chars_raw",
    "normalize",
]

logger = logging.getLogger(__name__)


def normalize(text: str) -> str:
    """
    Normalize the input text using Unicode NFKD normalization and convert to uppercase.

    Args:
        text: Input text.

    Returns:
        Normalized and uppercased text.
    """
    return unicodedata.normalize("NFKD", text).upper()


def build_name_cache(
    *,
    force_rebuild: bool = False,
    verbose: bool = True,
    use_color: bool = True,
    cache_file: str | None = None,
) -> dict[str, dict[str, str]]:
    """
    Build and return a cache dictionary of characters to original and normalized names.

    Args:
        force_rebuild: Force rebuilding even if cache file exists.
        verbose: Show logging messages.
        use_color: Colorize log output.
        cache_file: Path to the cache file.

    Returns:
        Character to name mapping.
    """
    if cache_file is None:
        from charfinder.settings import get_cache_file

        cache_file = get_cache_file()
    path = Path(cache_file)
    if not force_rebuild and path.exists():
        with path.open(encoding="utf-8") as f:
            cache = cast("dict[str, dict[str, str]]", json.load(f))
        message = f"Loaded Unicode name cache from: {cache_file}"
        logger.info(message)
        if verbose:
            echo(
                message,
                style=lambda m: format_info(m, use_color=use_color),
            )
            
        return cache

    message = "Rebuilding Unicode name cache. This may take a few seconds..."
    logger.info(message)
    if verbose:    
        echo(
            message,
            style=lambda m: format_info(m, use_color=use_color),
        )

    cache = {}
    for code in range(sys.maxunicode + 1):
        char = chr(code)
        name = unicodedata.name(char, "")
        if name:
            cache[char] = {"original": name, "normalized": normalize(name)}

    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)
        message = f"Cache written to: {cache_file}"
        logger.info(message)
        if verbose:
            echo(
                message,
                style=lambda m: format_info(m, use_color=use_color),
            )

    except Exception:
        message = "Failed to write cache."
        echo(message, style=lambda m: format_error(m, use_color=use_color))
        logger.exception(message)

    return cache


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
    matches: list[tuple[int, str, str, float | None]] = _find_exact_matches(
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
        matches.extend(_find_fuzzy_matches(norm_query, name_cache, context))

    match_info = f"Found {len(matches)} match(es)" if matches else "No matches found"
    message = f"{match_info} for query: '{query}'"
    logger.info(message)
    if verbose:
        echo(message, style=lambda m: format_info(m, use_color=use_color))

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
        name_cache = build_name_cache(verbose=verbose, use_color=False)

    norm_query = normalize(query)
    matches: list[tuple[int, str, str, float | None]] = _find_exact_matches(
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
        matches.extend(_find_fuzzy_matches(norm_query, name_cache, context))

    match_info = f"Found {len(matches)} match(es)" if matches else "No matches found"
    message = f"{match_info} for query: '{query}'"
    logger.info(message)
    if verbose:
        echo(message, style=lambda m: format_info(m, use_color=False))

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


def _find_exact_matches(
    norm_query: str, name_cache: dict[str, dict[str, str]], exact_match_mode: str
) -> list[tuple[int, str, str, float | None]]:
    """
    Internal helper to perform exact matching based on the chosen exact match mode.

    Args:
        norm_query: Normalized query.
        name_cache: Unicode name cache.
        exact_match_mode: Exact match mode to use.

    Returns:
        List of matches as (code point, character, name).
    """
    matches: list[tuple[int, str, str, float | None]] = []

    for char, names in name_cache.items():
        code_point = ord(char)
        original_name = names["original"]
        normalized_name = names["normalized"]

        if exact_match_mode == "substring":
            if norm_query in normalized_name:
                matches.append((code_point, char, original_name, None))
        elif exact_match_mode == "word-subset":
            query_words = set(norm_query.split())
            name_words = set(normalized_name.split())
            if query_words <= name_words:
                matches.append((code_point, char, original_name, None))
        else:
            msg = f"Unknown exact match mode: {exact_match_mode}"
            raise ValueError(msg)

    return matches


def _find_fuzzy_matches(
    norm_query: str,
    name_cache: dict[str, dict[str, str]],
    context: FuzzyMatchContext,
) -> list[tuple[int, str, str, float | None]]:
    """
    Internal helper to perform fuzzy matching.

    Args:
        norm_query: Normalized query.
        name_cache: Unicode name cache.
        context: FuzzyMatchContext instance.

    Returns:
        List of matches as (code, char, name, score).
    """
    matches: list[tuple[int, str, str, float | None]] = []

    if context.verbose:
        message = f"No exact match found for '{context.query}', "
        echo(message, style=lambda m: format_info(m, use_color=context.use_color))
        logger.info(message)
        message = f"Trying fuzzy matching (threshold={context.threshold})..."
        echo(message, style=lambda m: format_info(m, use_color=context.use_color))
        logger.info(message)

    for char, names in name_cache.items():
        score = compute_similarity(
            norm_query, names["normalized"], context.fuzzy_algo, context.match_mode
        )
        if score is None:
            if context.verbose:
                message = f"Skipped char '{char}' (no valid score computed)."
                echo(message, format_debug)
                logger.debug(message)
            continue
        if score >= context.threshold:
            matches.append((ord(char), char, names["original"], score))

    return matches
