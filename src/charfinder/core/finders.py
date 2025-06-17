"""Routing logic for Unicode character matching in CharFinder.

This module defines the public API for searching Unicode characters
by name using exact or fuzzy matching strategies.

Responsibilities:
- Validate the query and match configuration.
- Decide whether to use fuzzy matching first or fallback to it.
- Route to exact or fuzzy match logic via core.matching.
- Build results for CLI or JSON output.
- Return results and fuzzy-used flag when required.

Functions:
    - find_chars(): Perform character search and format output for CLI.
    - find_chars_raw(): Perform character search and return raw structured data.
    - find_chars_with_info(): Perform search and return data + fuzzy-used flag.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Literal

from charfinder.core.matching import find_exact_matches, find_fuzzy_matches
from charfinder.core.name_cache import BuildCacheOptions, build_name_cache
from charfinder.fuzzymatchlib import resolve_algorithm_name
from charfinder.types import CharMatch, FuzzyMatchContext, MatchTuple, SearchConfig
from charfinder.utils.formatter import (
    echo,
    format_result_header,
    format_result_row,
    matchtuple_to_charmatch,
)
from charfinder.utils.logger_styles import format_info
from charfinder.utils.normalizer import normalize
from charfinder.validators import validate_fuzzy_match_mode

__all__ = ["find_chars", "find_chars_raw", "find_chars_with_info"]

# ---------------------------------------------------------------------
# Message Constants
# ---------------------------------------------------------------------

MSG_QUERY_TYPE_ERROR = "Query must be a string."
MSG_QUERY_EMPTY_ERROR = "Query string must not be empty."
MSG_INVALID_MATCH_MODE = "Invalid fuzzy match mode: '{mode}'. Must be 'single' or 'hybrid'."
MSG_INVALID_ALGO = "Invalid fuzzy algorithm: {error}"
MSG_MATCH_FOUND = "Found {n} match(es) for query: '{query}'"
MSG_MATCH_NOT_FOUND = "No matches found for query: '{query}'"
MSG_EXACT_SKIP_FUZZY = "Exact match found — skipping fuzzy match."
MSG_EXACT_AND_FUZZY = "Exact match found — also running fuzzy match (prefer-fuzzy mode)."


def _log_match_message(
    matches: list[MatchTuple],
    query: str,
    *,
    use_color: bool,
    verbose: bool,
) -> None:
    """
    Logs the result summary for a given query.

    Args:
        matches (list[MatchTuple]): Match results.
        query (str): User's search string.
        use_color (bool): Whether to use color formatting.
        verbose (bool): Whether to show output in verbose mode.
    """
    message = (
        MSG_MATCH_FOUND.format(n=len(matches), query=query)
        if matches
        else MSG_MATCH_NOT_FOUND.format(query=query)
    )
    echo(
        message,
        style=lambda m: format_info(m, use_color=use_color),
        show=verbose,
        log=True,
        log_method="info",
    )


def _validate_query(query: str, config: SearchConfig) -> None:
    """
    Validates the input query and fuzzy mode.

    Args:
        query (str): Input search query.
        config (SearchConfig): Search configuration.

    Raises:
        TypeError: If query is not a string.
        ValueError: If query is empty or mode is invalid.
    """
    if not isinstance(query, str):
        raise TypeError(MSG_QUERY_TYPE_ERROR)

    if not query.strip():
        raise ValueError(MSG_QUERY_EMPTY_ERROR)

    validate_fuzzy_match_mode(config.fuzzy_match_mode)


def _should_use_fuzzy(config: SearchConfig, exact_matches: list[MatchTuple]) -> bool:
    """
    Determines whether fuzzy matching should be used.

    Args:
        config (SearchConfig): Matching configuration.
        exact_matches (list[MatchTuple]): Results from exact match.

    Returns:
        bool: Whether fuzzy matching should be performed.
    """
    return config.fuzzy and (config.prefer_fuzzy or not exact_matches)


def _resolve_matches(
    query: str, config: SearchConfig
) -> tuple[list[MatchTuple], Literal[True, False]]:
    """
    Resolve the query using exact and/or fuzzy matching.

    Args:
        query (str): User search input.
        config (SearchConfig): Matching configuration.

    Returns:
        tuple[list[MatchTuple], bool]: Match list and fuzzy-used flag.

    Raises:
        ValueError: If algorithm is invalid.
    """
    _validate_query(query, config)

    try:
        resolved_algo = resolve_algorithm_name(config.fuzzy_algo)
    except ValueError as exc:
        raise ValueError(MSG_INVALID_ALGO.format(error=str(exc))) from exc

    name_cache = config.name_cache or build_name_cache(
        options=BuildCacheOptions(
            force_rebuild=False,
            show=config.verbose,
            use_color=config.use_color,
            cache_file_path=None,
            retry_attempts=3,
            retry_delay=2.0,
        )
    )

    norm_query = normalize(query)
    exact_matches = [
        MatchTuple(code=tpl[0], char=tpl[1], name=tpl[2], score=tpl[3])
        for tpl in find_exact_matches(norm_query, name_cache, config.exact_match_mode)
    ]

    fuzzy_matches: list[MatchTuple] = []
    used_fuzzy = False

    if _should_use_fuzzy(config, exact_matches):
        used_fuzzy = True
        context = FuzzyMatchContext(
            threshold=config.threshold,
            fuzzy_algo=resolved_algo,
            match_mode=config.fuzzy_match_mode,
            agg_fn=config.agg_fn,
            verbose=config.verbose,
            use_color=config.use_color,
            query=query,
        )
        fuzzy_matches = [
            MatchTuple(code=tpl[0], char=tpl[1], name=tpl[2], score=tpl[3])
            for tpl in find_fuzzy_matches(norm_query, name_cache, context)
        ]

    all_matches = exact_matches + fuzzy_matches
    _log_match_message(all_matches, query, use_color=config.use_color, verbose=config.verbose)
    return all_matches, used_fuzzy


def find_chars(query: str, config: SearchConfig) -> Generator[str, None, None]:
    """
    Perform character search and yield formatted output lines.

    Args:
        query (str): Input query string.
        config (SearchConfig): Search behavior.

    Yields:
        str: CLI output lines with formatted results.
    """
    matches, _ = _resolve_matches(query, config)
    if not matches:
        return

    yield from format_result_header(has_score=(matches[0].score is not None))
    for match in matches:
        yield format_result_row(match.code, match.char, match.name, match.score)


def find_chars_raw(query: str, config: SearchConfig) -> list[CharMatch]:
    """
    Perform character search and return raw results for JSON output.

    Args:
        query (str): Input query string.
        config (SearchConfig): Search behavior.

    Returns:
        list[CharMatch]: List of matches with metadata.
    """
    matches, _ = _resolve_matches(query, config)
    return [matchtuple_to_charmatch(m) for m in matches]


def find_chars_with_info(query: str, config: SearchConfig) -> tuple[list[CharMatch], bool]:
    """
    Perform character search and return results with fuzzy usage flag.

    Args:
        query (str): Input query string.
        config (SearchConfig): Search behavior.

    Returns:
        tuple[list[CharMatch], bool]: Matches and whether fuzzy was used.
    """
    matches, used_fuzzy = _resolve_matches(query, config)
    return [matchtuple_to_charmatch(m) for m in matches], used_fuzzy
