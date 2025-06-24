"""Public API for high-level character search in CharFinder.

Provides a user-facing wrapper for executing Unicode character searches
with validated configuration and optional CLI-style parameters.

Responsibilities:
    - Accept search parameters as keyword arguments.
    - Validate and normalize inputs using build_search_config().
    - Delegate actual matching to core.finders.
    - Return output in text or JSON-ready formats.

Used by:
    - CLI interface to run text or JSON output.
    - External integrations or scripts needing CharFinder results.

Functions:
    - find_chars(): Yields formatted lines for terminal output.
    - find_chars_raw(): Returns raw list of match objects.
    - find_chars_with_info(): Returns formatted lines and fuzzy flag.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING, Literal

from charfinder.config.constants import (
    DEFAULT_EXACT_MATCH_MODE,
    DEFAULT_FUZZY_ALGO,
    DEFAULT_FUZZY_MATCH_MODE,
    DEFAULT_HYBRID_AGG_FUNC,
    DEFAULT_NORMALIZATION_PROFILE,
    DEFAULT_THRESHOLD,
)
from charfinder.core.finders import (
    find_chars as _find_chars_impl,
)
from charfinder.core.finders import (
    find_chars_raw as _find_chars_raw_impl,
)
from charfinder.core.finders import (
    find_chars_with_info as _find_chars_info_impl,
)
from charfinder.core.handlers import _normalize_and_build_config

if TYPE_CHECKING:
    from charfinder.config.aliases import FuzzyAlgorithm, FuzzyMatchMode, HybridAggFunc
    from charfinder.config.types import CharMatch

ExactMatchMode = Literal["substring", "word-subset"]
NormalizationProfile = Literal["raw", "light", "medium", "aggressive"]

__all__ = ["find_chars", "find_chars_raw", "find_chars_with_info"]


def find_chars(
    query: str,
    *,
    fuzzy: bool = False,
    threshold: float = DEFAULT_THRESHOLD,
    name_cache: dict[str, dict[str, str]] | None = None,
    verbose: bool = True,
    debug: bool = False,
    use_color: bool = True,
    fuzzy_algo: FuzzyAlgorithm = DEFAULT_FUZZY_ALGO,
    fuzzy_match_mode: FuzzyMatchMode = DEFAULT_FUZZY_MATCH_MODE,
    exact_match_mode: ExactMatchMode = DEFAULT_EXACT_MATCH_MODE,
    agg_fn: HybridAggFunc = DEFAULT_HYBRID_AGG_FUNC,
    prefer_fuzzy: bool = False,
    normalization_profile: NormalizationProfile = DEFAULT_NORMALIZATION_PROFILE,
) -> Generator[str, None, None]:
    """
    Perform character search and yield CLI-formatted output lines.

    Args:
        query (str): Input query string.
        ... (same for all kwargs)

    Returns:
        Generator[str]: Formatted result rows for terminal display.
    """
    norm_query, config = _normalize_and_build_config(
        query,
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
    return _find_chars_impl(query=norm_query, config=config)


def find_chars_raw(
    query: str,
    *,
    fuzzy: bool = False,
    threshold: float = DEFAULT_THRESHOLD,
    name_cache: dict[str, dict[str, str]] | None = None,
    verbose: bool = True,
    debug: bool = True,
    use_color: bool = True,
    fuzzy_algo: FuzzyAlgorithm = DEFAULT_FUZZY_ALGO,
    fuzzy_match_mode: FuzzyMatchMode = DEFAULT_FUZZY_MATCH_MODE,
    exact_match_mode: ExactMatchMode = DEFAULT_EXACT_MATCH_MODE,
    agg_fn: HybridAggFunc = DEFAULT_HYBRID_AGG_FUNC,
    prefer_fuzzy: bool = False,
    normalization_profile: NormalizationProfile = DEFAULT_NORMALIZATION_PROFILE,
) -> list[CharMatch]:
    """
    Perform character search and return raw match result objects.

    Returns:
        list[CharMatch]:
            Structured result rows with metadata, suitable for JSON or programmatic use.
    """
    norm_query, config = _normalize_and_build_config(
        query,
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
    return _find_chars_raw_impl(query=norm_query, config=config)


def find_chars_with_info(
    query: str,
    *,
    fuzzy: bool = False,
    threshold: float = DEFAULT_THRESHOLD,
    name_cache: dict[str, dict[str, str]] | None = None,
    verbose: bool = True,
    debug: bool = False,
    use_color: bool = True,
    fuzzy_algo: FuzzyAlgorithm = DEFAULT_FUZZY_ALGO,
    fuzzy_match_mode: FuzzyMatchMode = DEFAULT_FUZZY_MATCH_MODE,
    exact_match_mode: ExactMatchMode = DEFAULT_EXACT_MATCH_MODE,
    agg_fn: HybridAggFunc = DEFAULT_HYBRID_AGG_FUNC,
    prefer_fuzzy: bool = False,
    normalization_profile: NormalizationProfile = DEFAULT_NORMALIZATION_PROFILE,
) -> tuple[list[CharMatch], bool]:
    """
    Perform character search and return raw match results and fuzzy-used flag.

    Returns:
        tuple[list[CharMatch], bool]: Matches and whether fuzzy matching was used.
    """
    norm_query, config = _normalize_and_build_config(
        query,
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
    return _find_chars_info_impl(query=norm_query, config=config)
