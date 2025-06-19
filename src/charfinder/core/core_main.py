"""
Public API for high-level character search in CharFinder.

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
    DEFAULT_THRESHOLD,
    FuzzyAlgorithm,
    FuzzyMatchMode,
    HybridAggFunc,
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
from charfinder.core.handlers import build_search_config
from charfinder.utils.formatter import format_result_header, format_result_row
from charfinder.utils.normalizer import normalize

if TYPE_CHECKING:
    from charfinder.config.types import CharMatch, SearchConfig

ExactMatchMode = Literal["substring", "word-subset"]

__all__ = ["find_chars", "find_chars_raw", "find_chars_with_info"]


def find_chars(
    query: str,
    *,
    fuzzy: bool = False,
    threshold: float = DEFAULT_THRESHOLD,
    name_cache: dict[str, dict[str, str]] | None = None,
    verbose: bool = True,
    use_color: bool = True,
    fuzzy_algo: FuzzyAlgorithm = DEFAULT_FUZZY_ALGO,
    fuzzy_match_mode: FuzzyMatchMode = DEFAULT_FUZZY_MATCH_MODE,
    exact_match_mode: ExactMatchMode = DEFAULT_EXACT_MATCH_MODE,
    agg_fn: HybridAggFunc = DEFAULT_HYBRID_AGG_FUNC,
    prefer_fuzzy: bool = False,
) -> Generator[str, None, None]:
    norm_query = normalize(query)

    config: SearchConfig = build_search_config(
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
    return _find_chars_impl(norm_query, config)


def find_chars_raw(
    query: str,
    *,
    fuzzy: bool = False,
    threshold: float = DEFAULT_THRESHOLD,
    name_cache: dict[str, dict[str, str]] | None = None,
    verbose: bool = True,
    use_color: bool = True,
    fuzzy_algo: FuzzyAlgorithm = DEFAULT_FUZZY_ALGO,
    fuzzy_match_mode: FuzzyMatchMode = DEFAULT_FUZZY_MATCH_MODE,
    exact_match_mode: ExactMatchMode = DEFAULT_EXACT_MATCH_MODE,
    agg_fn: HybridAggFunc = DEFAULT_HYBRID_AGG_FUNC,
    prefer_fuzzy: bool = False,
) -> list[CharMatch]:
    norm_query = normalize(query)

    config: SearchConfig = build_search_config(
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
    return _find_chars_raw_impl(norm_query, config)


def find_chars_with_info(
    query: str,
    *,
    fuzzy: bool = False,
    threshold: float = DEFAULT_THRESHOLD,
    name_cache: dict[str, dict[str, str]] | None = None,
    verbose: bool = True,
    use_color: bool = True,
    fuzzy_algo: FuzzyAlgorithm = DEFAULT_FUZZY_ALGO,
    fuzzy_match_mode: FuzzyMatchMode = DEFAULT_FUZZY_MATCH_MODE,
    exact_match_mode: ExactMatchMode = DEFAULT_EXACT_MATCH_MODE,
    agg_fn: HybridAggFunc = DEFAULT_HYBRID_AGG_FUNC,
    prefer_fuzzy: bool = False,
) -> tuple[list[str], bool]:
    norm_query = normalize(query)

    config: SearchConfig = build_search_config(
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

    raw_matches, fuzzy_used = _find_chars_info_impl(norm_query, config)

    lines: list[str] = []
    if raw_matches:
        has_score = bool(raw_matches) and "score" in raw_matches[0]
        lines.extend(format_result_header(has_score=has_score))
        lines.extend(
            format_result_row(
                code := int(match["code"].removeprefix("U+"), 16),
                match["char"],
                match["name"].removesuffix(f"  (\\u{code:04x})"),
                match.get("score"),
            )
            for match in raw_matches
        )
    return lines, fuzzy_used
