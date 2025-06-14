"""Core logic for CharFinder.

Provides the public API surface for high-level character search,
delegating to internal finder implementations.

This module is intentionally kept free of any CLI-specific or I/O code
to maximize testability and reusability.

Now supports hybrid matching via `prefer_fuzzy=True`, allowing fuzzy
results to be included even if exact matches exist.

Functions:
    find_chars(): Search Unicode characters by exact or fuzzy name match (yields formatted lines).
    find_chars_raw(): Search Unicode characters and return raw results for JSON output.
"""


# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING, Literal

from charfinder.constants import (
    DEFAULT_EXACT_MATCH_MODE,
    DEFAULT_FUZZY_ALGO,
    DEFAULT_FUZZY_MATCH_MODE,
    DEFAULT_HYBRID_AGG_FUNC,
    DEFAULT_THRESHOLD,
    VALID_HYBRID_AGG_FUNCS,
    FuzzyAlgorithm,
    MatchMode,
)
from charfinder.core.finders import find_chars as _find_chars_impl
from charfinder.core.finders import find_chars_raw as _find_chars_raw_impl
from charfinder.core.finders import find_chars_with_info as _find_chars_info_impl
from charfinder.types import SearchConfig
from charfinder.utils.formatter import format_result_header, format_result_row

if TYPE_CHECKING:
    from charfinder.types import CharMatch

ExactMatchMode = Literal["substring", "word-subset"]

__all__ = ["find_chars", "find_chars_raw"]

# ---------------------------------------------------------------------
# Internal Helper
# ---------------------------------------------------------------------


def _build_config(
    *,
    fuzzy: bool,
    threshold: float,
    name_cache: dict[str, dict[str, str]] | None,
    verbose: bool,
    use_color: bool,
    fuzzy_algo: FuzzyAlgorithm,
    fuzzy_match_mode: MatchMode,
    exact_match_mode: ExactMatchMode,
    agg_fn: VALID_HYBRID_AGG_FUNCS,
    prefer_fuzzy: bool,
) -> SearchConfig:
    return SearchConfig(
        fuzzy=fuzzy,
        threshold=threshold,
        name_cache=name_cache,
        verbose=verbose,
        use_color=use_color,
        fuzzy_algo=fuzzy_algo,
        fuzzy_match_mode=fuzzy_match_mode,
        exact_match_mode=exact_match_mode,
        agg_fn=agg_fn,
        prefer_fuzzy=prefer_fuzzy,
    )


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def find_chars(
    query: str,
    *,
    fuzzy: bool = False,
    threshold: float = DEFAULT_THRESHOLD,
    name_cache: dict[str, dict[str, str]] | None = None,
    verbose: bool = True,
    use_color: bool = True,
    fuzzy_algo: FuzzyAlgorithm = DEFAULT_FUZZY_ALGO,
    fuzzy_match_mode: MatchMode = DEFAULT_FUZZY_MATCH_MODE,
    exact_match_mode: ExactMatchMode = DEFAULT_EXACT_MATCH_MODE,
    agg_fn: VALID_HYBRID_AGG_FUNCS = DEFAULT_HYBRID_AGG_FUNC,
    prefer_fuzzy: bool = False,
) -> Generator[str, None, None]:
    """
    Search for Unicode characters by name using exact or fuzzy matching.

    Delegates to `core.finders.find_chars`.

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
        agg_fn: Aggregation function for hybrid match mode.
        prefer_fuzzy: If True, include fuzzy matches even if exact matches are found (hybrid mode).

    Returns:
        Generator[str, None, None]: Yields each line of formatted CLI result output.
    """
    config = _build_config(
        fuzzy=fuzzy,
        threshold=threshold,
        name_cache=name_cache,
        verbose=verbose,
        use_color=use_color,
        fuzzy_algo=fuzzy_algo,
        fuzzy_match_mode=fuzzy_match_mode,
        exact_match_mode=exact_match_mode,
        agg_fn=agg_fn,
        prefer_fuzzy=prefer_fuzzy,
    )
    return _find_chars_impl(query, config)


def find_chars_raw(
    query: str,
    *,
    fuzzy: bool = False,
    threshold: float = DEFAULT_THRESHOLD,
    name_cache: dict[str, dict[str, str]] | None = None,
    verbose: bool = True,
    use_color: bool = True,
    fuzzy_algo: FuzzyAlgorithm = DEFAULT_FUZZY_ALGO,
    fuzzy_match_mode: MatchMode = DEFAULT_FUZZY_MATCH_MODE,
    exact_match_mode: ExactMatchMode = DEFAULT_EXACT_MATCH_MODE,
    agg_fn: VALID_HYBRID_AGG_FUNCS = DEFAULT_HYBRID_AGG_FUNC,
    prefer_fuzzy: bool = False,
) -> list[CharMatch]:
    """
    Search for Unicode characters and return raw results for JSON output.

    Delegates to `core.finders.find_chars_raw`.

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
        agg_fn: Aggregation function for hybrid match mode.
        prefer_fuzzy: If True, include fuzzy matches even if exact matches are found (hybrid mode).

    Returns:
        list[CharMatch]: List of Unicode character matches, formatted for JSON output.
    """
    config = _build_config(
        fuzzy=fuzzy,
        threshold=threshold,
        name_cache=name_cache,
        verbose=verbose,
        use_color=use_color,
        fuzzy_algo=fuzzy_algo,
        fuzzy_match_mode=fuzzy_match_mode,
        exact_match_mode=exact_match_mode,
        agg_fn=agg_fn,
        prefer_fuzzy=prefer_fuzzy,
    )
    return _find_chars_raw_impl(query, config)


def find_chars_with_info(
    query: str,
    *,
    fuzzy: bool = False,
    threshold: float = DEFAULT_THRESHOLD,
    name_cache: dict[str, dict[str, str]] | None = None,
    verbose: bool = True,
    use_color: bool = True,
    fuzzy_algo: FuzzyAlgorithm = DEFAULT_FUZZY_ALGO,
    fuzzy_match_mode: MatchMode = DEFAULT_FUZZY_MATCH_MODE,
    exact_match_mode: ExactMatchMode = DEFAULT_EXACT_MATCH_MODE,
    agg_fn: VALID_HYBRID_AGG_FUNCS = DEFAULT_HYBRID_AGG_FUNC,
    prefer_fuzzy: bool = False,
) -> tuple[list[str], bool]:
    """
    Search for Unicode characters and return both output lines and fuzzy usage flag.

    This wraps `core.finders.find_chars_with_info()` and returns:
      - The formatted output lines.
      - A boolean indicating whether fuzzy matching was actually used.

    Args:
        query (str): Input query string.
        fuzzy (bool): Whether to enable fuzzy matching.
        threshold (float): Fuzzy match threshold.
        name_cache (dict[str, dict[str, str]] | None): Optional prebuilt name cache.
        verbose (bool): Whether to show progress messages.
        use_color (bool): Whether to enable ANSI color formatting.
        fuzzy_algo (FuzzyAlgorithm): Algorithm used for fuzzy scoring.
        fuzzy_match_mode (MatchMode): 'single' or 'hybrid' match scoring mode.
        exact_match_mode (Literal): 'substring' or 'word-subset' for exact match logic.
        agg_fn (str): Aggregation function to use for hybrid fuzzy matching.
        prefer_fuzzy (bool): If True, include fuzzy matches even if exact matches are found.

    Returns:
        tuple[list[str], bool]: A tuple containing:
            - A list of formatted CLI output lines.
            - A boolean indicating whether fuzzy matching was used.
    """
    config = _build_config(
        fuzzy=fuzzy,
        threshold=threshold,
        name_cache=name_cache,
        verbose=verbose,
        use_color=use_color,
        fuzzy_algo=fuzzy_algo,
        fuzzy_match_mode=fuzzy_match_mode,
        exact_match_mode=exact_match_mode,
        agg_fn=agg_fn,
        prefer_fuzzy=prefer_fuzzy,
    )

    raw_matches, fuzzy_used = _find_chars_info_impl(query, config)

    lines: list[str] = []
    if raw_matches:
        has_score = raw_matches and "score" in raw_matches[0]
        has_score = bool(raw_matches) and "score" in raw_matches[0]
        lines.extend(format_result_header(has_score=has_score))
        lines.extend(
            format_result_row(
                code := int(match["code"][2:], 16),
                match["char"],
                match["name"].removesuffix(f"  (\\u{code:04x})"),
                match.get("score"),
            )
            for match in raw_matches
        )
    return lines, fuzzy_used
