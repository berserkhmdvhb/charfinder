"""
Matching coordinator and config builder for CharFinder.

Centralizes internal logic for validating user input,
resolving matches using exact/fuzzy modes, and logging summary messages.

Responsibilities:
    - Validate queries and fuzzy mode.
    - Construct SearchConfig from keyword arguments.
    - Route to exact and/or fuzzy match functions.
    - Report number of matches found.

Used by:
    - finders.py to resolve queries and build configs.
    - core_main.py for CLI and programmatic APIs.

Functions:
    - _validate_query(): Checks query type and content.
    - _resolve_matches(): Runs exact/fuzzy logic and returns results.
    - _log_match_message(): Echoes summary to user and log.
    - build_search_config(): Creates validated SearchConfig.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from charfinder.core.matching import find_exact_matches, find_fuzzy_matches
from charfinder.core.name_cache import BuildCacheOptions, build_name_cache
from charfinder.fuzzymatchlib import resolve_algorithm_name
from charfinder.types import FuzzyMatchContext, MatchTuple, SearchConfig
from charfinder.utils.formatter import echo
from charfinder.utils.logger_styles import format_info
from charfinder.utils.normalizer import normalize
from charfinder.validators import (
    validate_exact_match_mode,
    validate_fuzzy_algo,
    validate_fuzzy_match_mode,
    validate_threshold,
)

if TYPE_CHECKING:
    from charfinder.constants import FuzzyAlgorithm, FuzzyMatchMode, HybridAggFunc


# ---------------------------------------------------------------------
# Message Constants
# ---------------------------------------------------------------------

MSG_QUERY_TYPE_ERROR = "Query must be a string."
MSG_QUERY_EMPTY_ERROR = "Query string must not be empty."
MSG_INVALID_ALGO = "Invalid fuzzy algorithm: {error}"
MSG_MATCH_FOUND = "Found {n} match(es) for query: '{query}'"
MSG_MATCH_NOT_FOUND = "No matches found for query: '{query}'"


def _log_match_message(
    matches: list[MatchTuple],
    query: str,
    *,
    use_color: bool,
    verbose: bool,
) -> None:
    """
    Log a message indicating how many matches were found.

    Args:
        matches (list[MatchTuple]): List of matches found.
        query (str): Original query string.
        use_color (bool): Whether to use color formatting.
        verbose (bool): Whether to print to console.
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
    Validate the user query and fuzzy match mode.

    Args:
        query (str): Query string to validate.
        config (SearchConfig): Config object containing match mode.

    Raises:
        TypeError: If query is not a string.
        ValueError: If query is empty or match mode is invalid.
    """
    if not isinstance(query, str):
        raise TypeError(MSG_QUERY_TYPE_ERROR)
    if not query.strip():
        raise ValueError(MSG_QUERY_EMPTY_ERROR)
    validate_fuzzy_match_mode(config.fuzzy_match_mode)


def _resolve_matches(
    query: str,
    config: SearchConfig,
) -> tuple[list[MatchTuple], Literal[True, False]]:
    """
    Perform matching logic: exact match, then optional fuzzy fallback.

    Args:
        query (str): Search string provided by user.
        config (SearchConfig): Configuration for matching.

    Returns:
        tuple[list[MatchTuple], bool]: List of matches and a flag
        indicating whether fuzzy matching was used.
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

    should_fuzzy = config.fuzzy and (config.prefer_fuzzy or not exact_matches)
    if should_fuzzy:
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


def build_search_config(
    *,
    fuzzy: bool,
    threshold: float,
    name_cache: dict[str, dict[str, str]] | None,
    verbose: bool,
    use_color: bool,
    fuzzy_algo: FuzzyAlgorithm,
    fuzzy_match_mode: FuzzyMatchMode,
    exact_match_mode: str,
    agg_fn: HybridAggFunc,
    prefer_fuzzy: bool,
) -> SearchConfig:
    """
    Validate inputs and return a full SearchConfig object.

    Args:
        fuzzy (bool): Enable fuzzy matching.
        threshold (float): Similarity threshold for fuzzy scoring.
        name_cache (dict | None): Cached Unicode name data.
        verbose (bool): Whether to print logs.
        use_color (bool): Whether to use ANSI color output.
        fuzzy_algo (FuzzyAlgorithm): Selected fuzzy algorithm.
        fuzzy_match_mode (FuzzyMatchMode): 'single' or 'hybrid'.
        exact_match_mode (str): 'substring' or 'word-subset'.
        agg_fn (HybridAggFunc): Aggregation method for hybrid mode.
        prefer_fuzzy (bool): Whether to include fuzzy even with exact match.

    Returns:
        SearchConfig: Fully validated search configuration object.
    """
    return SearchConfig(
        fuzzy=fuzzy,
        threshold=validate_threshold(threshold),
        name_cache=name_cache,
        verbose=verbose,
        use_color=use_color,
        fuzzy_algo=validate_fuzzy_algo(fuzzy_algo),
        fuzzy_match_mode=validate_fuzzy_match_mode(fuzzy_match_mode),
        exact_match_mode=validate_exact_match_mode(exact_match_mode),
        agg_fn=agg_fn,
        prefer_fuzzy=bool(prefer_fuzzy),
    )
