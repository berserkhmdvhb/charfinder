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
    - _normalize_and_build_config():
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from charfinder.config.messages import (
    MSG_DEBUG_REMOVED_DUPLICATE_FUZZY,
    MSG_ERROR_INVALID_ALGORITHM,
    MSG_ERROR_QUERY_EMPTY,
    MSG_ERROR_QUERY_TYPE,
    MSG_INFO_MATCH_FOUND,
    MSG_INFO_MATCH_NOT_FOUND,
)
from charfinder.config.types import FuzzyMatchContext, MatchTuple, SearchConfig
from charfinder.core.matching import find_exact_matches, find_fuzzy_matches
from charfinder.core.name_cache import BuildCacheOptions, build_name_cache
from charfinder.fuzzymatchlib import resolve_algorithm_name
from charfinder.utils.formatter import echo
from charfinder.utils.logger_styles import format_debug, format_info
from charfinder.utils.normalizer import normalize
from charfinder.validators import (
    validate_exact_match_mode,
    validate_fuzzy_algo,
    validate_fuzzy_match_mode,
    validate_normalization_profile,
    validate_threshold,
)

if TYPE_CHECKING:
    from charfinder.config.aliases import (
        FuzzyAlgorithm,
        FuzzyMatchMode,
        HybridAggFunc,
        NormalizationProfile,
    )


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
        MSG_INFO_MATCH_FOUND.format(n=len(matches), query=query)
        if matches
        else MSG_INFO_MATCH_NOT_FOUND.format(query=query)
    )
    echo(
        msg=message,
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
        raise TypeError(MSG_ERROR_QUERY_TYPE)
    if not query.strip():
        raise ValueError(MSG_ERROR_QUERY_EMPTY)
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
    q = query
    _validate_query(query, config)

    try:
        resolved_algo = resolve_algorithm_name(config.fuzzy_algo)
    except ValueError as exc:
        raise ValueError(MSG_ERROR_INVALID_ALGORITHM.format(error=str(exc))) from exc

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

    norm_query = normalize(query, profile=config.normalization_profile)
    exact_matches = [
        MatchTuple(
            code=tpl.code,
            char=tpl.char,
            name=tpl.name,
            score=1.0,
            is_fuzzy=False,
        )
        for tpl in find_exact_matches(norm_query, name_cache, config.exact_match_mode)
    ]
    exact_codes = {m.code for m in exact_matches}

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
            debug=config.debug,
            use_color=config.use_color,
            query=norm_query,
        )

        raw_fuzzy_results = find_fuzzy_matches(norm_query, name_cache, context)
        fuzzy_matches = [
            MatchTuple(
                code=tpl.code,
                char=tpl.char,
                name=tpl.name,
                score=tpl.score,
                is_fuzzy=True,
            )
            for tpl in raw_fuzzy_results
            # Remove fuzzy results already returned by exact match
            if tpl.code not in exact_codes
        ]
        removed_count = len(raw_fuzzy_results) - len(fuzzy_matches)
        if removed_count > 0 and config.verbose:
            echo(
                msg=MSG_DEBUG_REMOVED_DUPLICATE_FUZZY.format(removed_count=removed_count),
                style=lambda m: format_debug(m, use_color=config.use_color),
                show=config.verbose,
                log=True,
                log_method="debug",
            )
    all_matches = sorted(
        exact_matches + fuzzy_matches, key=lambda m: (m.is_fuzzy, -(m.score or 0.0))
    )
    _log_match_message(all_matches, query=q, use_color=config.use_color, verbose=config.verbose)
    return all_matches, used_fuzzy


def build_search_config(
    *,
    fuzzy: bool,
    threshold: float,
    name_cache: dict[str, dict[str, str]] | None,
    verbose: bool,
    debug: bool,
    use_color: bool,
    fuzzy_algo: FuzzyAlgorithm,
    fuzzy_match_mode: FuzzyMatchMode,
    exact_match_mode: str,
    agg_fn: HybridAggFunc,
    prefer_fuzzy: bool,
    normalization_profile: NormalizationProfile,
) -> SearchConfig:
    """
    Validate inputs and return a full SearchConfig object.

    Args:
        fuzzy (bool): Enable fuzzy matching.
        threshold (float): Similarity threshold for fuzzy scoring.
        name_cache (dict | None): Cached Unicode name data.
        verbose (bool): Whether to print logs.
        debug (bool): Wether to print diagnostics.
        use_color (bool): Whether to use ANSI color output.
        fuzzy_algo (FuzzyAlgorithm): Selected fuzzy algorithm.
        fuzzy_match_mode (FuzzyMatchMode): 'single' or 'hybrid'.
        exact_match_mode (str): 'substring' or 'word-subset'.
        agg_fn (HybridAggFunc): Aggregation method for hybrid mode.
        prefer_fuzzy (bool): Whether to include fuzzy even with exact match.
        normalization_profile (Literal): Profile for Unicode normalization.

    Returns:
        SearchConfig: Fully validated search configuration object.
    """
    return SearchConfig(
        fuzzy=fuzzy,
        threshold=validate_threshold(threshold),
        name_cache=name_cache,
        verbose=verbose,
        debug=debug,
        use_color=use_color,
        fuzzy_algo=validate_fuzzy_algo(fuzzy_algo),
        fuzzy_match_mode=validate_fuzzy_match_mode(fuzzy_match_mode),
        exact_match_mode=validate_exact_match_mode(exact_match_mode),
        agg_fn=agg_fn,
        prefer_fuzzy=bool(prefer_fuzzy),
        normalization_profile=validate_normalization_profile(normalization_profile),
    )


def _normalize_and_build_config(
    query: str,
    *,
    fuzzy: bool,
    threshold: float,
    name_cache: dict[str, dict[str, str]] | None,
    verbose: bool,
    debug: bool,
    use_color: bool,
    fuzzy_algo: FuzzyAlgorithm,
    fuzzy_match_mode: FuzzyMatchMode,
    exact_match_mode: str,
    agg_fn: HybridAggFunc,
    prefer_fuzzy: bool,
    normalization_profile: NormalizationProfile,
) -> tuple[str, SearchConfig]:
    """
    Normalize the query and return it alongside a validated SearchConfig.

    Args:
        query (str): Raw search string.
        fuzzy (bool): Enable fuzzy matching.
        threshold (float): Similarity threshold for fuzzy scoring.
        name_cache (dict | None): Cached Unicode name data.
        verbose (bool): Whether to print logs.
        debug (bool): Whether to print diagnostics.
        use_color (bool): Whether to use ANSI color output.
        fuzzy_algo (FuzzyAlgorithm): Selected fuzzy algorithm.
        fuzzy_match_mode (FuzzyMatchMode): 'single' or 'hybrid'.
        exact_match_mode (str): 'substring' or 'word-subset'.
        agg_fn (HybridAggFunc): Aggregation method for hybrid mode.
        prefer_fuzzy (bool): Whether to include fuzzy even with exact match.
        normalization_profile (Literal): Profile for Unicode normalization.

    Returns:
        tuple[str, SearchConfig]: Normalized query, and validated config.
    """
    norm_query = normalize(query, profile=normalization_profile)
    config = build_search_config(
        fuzzy=fuzzy,
        threshold=threshold,
        name_cache=name_cache,
        verbose=verbose,
        debug=debug,
        use_color=use_color,
        fuzzy_algo=fuzzy_algo,
        fuzzy_match_mode=fuzzy_match_mode,
        exact_match_mode=exact_match_mode,
        agg_fn=agg_fn,
        prefer_fuzzy=prefer_fuzzy,
        normalization_profile=normalization_profile,
    )
    return norm_query, config
