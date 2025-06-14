"""
Routing logic for Unicode character matching in CharFinder.

This module defines the `find_chars_info_router()` function, which routes a
user query to either exact matching or fuzzy matching logic, depending on
the configured strategy and CLI arguments.

Responsibilities:
- Decide whether to attempt fuzzy match first, or fallback to fuzzy after exact match.
- Delegate to appropriate matching functions (`exact_match`, `fuzzy_match`).
- Return matched character info along with a flag indicating whether fuzzy was used.

Function:
    find_chars_info_router(): Perform routing between exact and fuzzy matching.
"""


# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Generator
from typing import NamedTuple

from charfinder.constants import VALID_FUZZY_MATCH_MODES
from charfinder.core.matching import find_exact_matches, find_fuzzy_matches
from charfinder.core.name_cache import build_name_cache
from charfinder.fuzzymatchlib import resolve_algorithm_name
from charfinder.types import CharMatch, FuzzyMatchContext, SearchConfig
from charfinder.utils.formatter import echo, format_result_header, format_result_row
from charfinder.utils.logger_styles import format_info
from charfinder.utils.normalizer import normalize

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


# ---------------------------------------------------------------------
# Internal Types
# ---------------------------------------------------------------------


class MatchTuple(NamedTuple):
    code: int
    char: str
    name: str
    score: float | None


# ---------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------


def _validate_query(query: str, config: SearchConfig) -> None:
    if not isinstance(query, str):
        raise TypeError(MSG_QUERY_TYPE_ERROR)

    if not query.strip():
        raise ValueError(MSG_QUERY_EMPTY_ERROR)

    if config.fuzzy_match_mode not in VALID_FUZZY_MATCH_MODES:
        raise ValueError(MSG_INVALID_MATCH_MODE.format(mode=config.fuzzy_match_mode))


def _resolve_matches(query: str, config: SearchConfig) -> tuple[list[MatchTuple], bool]:
    _validate_query(query, config)

    try:
        resolved_algo = resolve_algorithm_name(config.fuzzy_algo)
    except ValueError as exc:
        raise ValueError(MSG_INVALID_ALGO.format(error=str(exc))) from exc

    name_cache = config.name_cache or build_name_cache(
        show=config.verbose,
        use_color=config.use_color,
    )

    norm_query = normalize(query)
    exact_matches: list[MatchTuple] = [
        MatchTuple(*tpl)
        for tpl in find_exact_matches(norm_query, name_cache, config.exact_match_mode)
    ]

    fuzzy_matches: list[MatchTuple] = []
    fuzzy_executed = False

    # === Decides whether to run fuzzy matching
    run_fuzzy = config.fuzzy and (config.prefer_fuzzy or not exact_matches)

    if run_fuzzy:
        fuzzy_executed = True
        context = FuzzyMatchContext(
            threshold=config.threshold,
            fuzzy_algo=resolved_algo,
            match_mode=config.fuzzy_match_mode,
            agg_fn=config.agg_fn,
            verbose=config.verbose,
            use_color=config.use_color,
            query=query,
        )
        fuzzy_results = find_fuzzy_matches(norm_query, name_cache, context)
        fuzzy_matches.extend(MatchTuple(*tpl) for tpl in fuzzy_results)

    # === Logging (INFO messages)
    if config.verbose and exact_matches:
        if config.fuzzy and not config.prefer_fuzzy:
            echo(
                MSG_EXACT_SKIP_FUZZY,
                style=lambda m: format_info(m, use_color=config.use_color),
                show=True,
                log=True,
                log_method="info",
            )
        elif config.fuzzy and config.prefer_fuzzy:
            echo(
                MSG_EXACT_AND_FUZZY,
                style=lambda m: format_info(m, use_color=config.use_color),
                show=True,
                log=True,
                log_method="info",
            )

    # === Combine matches
    all_matches = exact_matches + fuzzy_matches

    message = (
        MSG_MATCH_FOUND.format(n=len(all_matches), query=query)
        if all_matches
        else MSG_MATCH_NOT_FOUND.format(query=query)
    )
    echo(
        message,
        style=lambda m: format_info(m, use_color=config.use_color),
        show=config.verbose,
        log=True,
        log_method="info",
    )

    return all_matches, fuzzy_executed


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def find_chars(query: str, config: SearchConfig) -> Generator[str, None, None]:
    """
    Search for Unicode characters by name using exact or fuzzy matching.

    Args:
        query (str): Input query string.
        config (SearchConfig): Configuration options for matching.

    Returns:
        Generator[str, None, None]: Formatted lines for CLI output.
    """
    matches, _ = _resolve_matches(query, config)
    if not matches:
        return

    yield from format_result_header(has_score=(matches[0].score is not None))
    for match in matches:
        yield format_result_row(match.code, match.char, match.name, match.score)


def find_chars_raw(query: str, config: SearchConfig) -> list[CharMatch]:
    """
    Search for Unicode characters and return raw results for JSON output.

    Args:
        query (str): Input query string.
        config (SearchConfig): Configuration options for matching.

    Returns:
        list[CharMatch]: List of Unicode character matches, formatted for JSON output.
    """
    matches, _ = _resolve_matches(query, config)

    results: list[CharMatch] = []
    for match in matches:
        item: CharMatch = {
            "code": f"U+{match.code:04X}",
            "char": match.char,
            "name": f"{match.name}  (\\u{match.code:04x})",
        }
        if match.score is not None:
            item["score"] = round(match.score, 3)
        results.append(item)

    return results


def find_chars_with_info(query: str, config: SearchConfig) -> tuple[list[CharMatch], bool]:
    """
    Search for Unicode characters and return raw results with fuzzy usage flag.

    Performs exact and optionally fuzzy matching depending on the config,
    returning JSON-serializable match records along with whether fuzzy
    matching was actually used.

    Args:
        query (str): Input query string.
        config (SearchConfig): Configuration options controlling matching behavior.

    Returns:
        tuple[list[CharMatch], bool]: A tuple containing:
            - List of match records (CharMatch) formatted for JSON output.
            - A boolean indicating whether fuzzy matching was used.
    """
    matches, used_fuzzy = _resolve_matches(query, config)

    results: list[CharMatch] = []
    for match in matches:
        item: CharMatch = {
            "code": f"U+{match.code:04X}",
            "char": match.char,
            "name": f"{match.name}  (\\u{match.code:04x})",
        }
        if match.score is not None:
            item["score"] = round(match.score, 3)
        results.append(item)

    return results, used_fuzzy
