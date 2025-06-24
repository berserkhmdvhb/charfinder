"""
Matching helpers for CharFinder.

Provides internal helpers for exact and fuzzy matching of
Unicode character names, including alternate Unicode aliases.

Functions:
    find_exact_matches(): Perform exact matching.
    find_fuzzy_matches(): Perform fuzzy matching with scoring.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from charfinder.config.messages import (
    MSG_EXACT_CHECKING,
    MSG_FUZZY_SETTINGS,
    MSG_FUZZY_START,
    MSG_NO_SCORE_COMPUTED,
    MSG_SUBSET_CHECKING,
)
from charfinder.config.types import FuzzyMatchContext, MatchTuple
from charfinder.fuzzymatchlib import compute_similarity
from charfinder.utils.formatter import echo, log_optionally_echo
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_debug, format_info
from charfinder.validators import (
    validate_exact_match_mode,
    validate_fuzzy_algo,
    validate_fuzzy_match_mode,
    validate_name_cache_structure,
    validate_threshold,
)

__all__ = ["find_exact_matches", "find_fuzzy_matches"]

logger = get_logger()


# ---------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------


def _max_score(*scores: float | None) -> float | None:
    """Return the max score ignoring None values."""
    return max(filter(None, scores), default=None)


# ---------------------------------------------------------------------
# Exact Matching
# ---------------------------------------------------------------------


def find_exact_matches(
    norm_query: str,
    name_cache: dict[str, dict[str, str]],
    exact_match_mode: str,
    *,
    verbose: bool = False,
    use_color: bool = False,
) -> list[MatchTuple]:
    """
    Perform exact matching based on the chosen exact match mode,
    using both official and alternate normalized names.

    Args:
        norm_query (str): The normalized query string.
        name_cache (dict): The name cache mapping characters to normalized names.
        exact_match_mode (str): The exact match strategy ("substring" or "word-subset").
        verbose (bool): If True, enables debug logging and echo.
        use_color (bool): Enables styled echo output if True.

    Returns:
        list[MatchTuple]: List of matched entries with score=None.
    """
    validate_exact_match_mode(exact_match_mode)
    validate_name_cache_structure(name_cache)

    matches: list[MatchTuple] = []

    for char, names in name_cache.items():
        code_point = ord(char)
        original_name = names["original"]
        norm_name = names["normalized"]
        alt_norm = names.get("alternate_normalized")

        if verbose:
            log_optionally_echo(
                msg=MSG_EXACT_CHECKING.format(code=code_point, name=norm_name, alt=alt_norm or ""),
                level="debug",
                show=True,
                style=lambda m: format_debug(message=m, use_color=use_color),
            )

        if exact_match_mode == "substring":
            if norm_query in norm_name or (alt_norm and norm_query in alt_norm):
                matches.append(MatchTuple(code_point, char, original_name, None))
        elif exact_match_mode == "word-subset":
            query_words = set(norm_query.split())
            name_words = set(norm_name.split())
            if alt_norm:
                name_words |= set(alt_norm.split())

            if verbose:
                log_optionally_echo(
                    msg=MSG_SUBSET_CHECKING.format(query=query_words, name=name_words),
                    level="debug",
                    show=True,
                    style=lambda m: format_debug(message=m, use_color=use_color),
                )

            if query_words <= name_words:
                matches.append(MatchTuple(code_point, char, original_name, None))

    return matches


# ---------------------------------------------------------------------
# Fuzzy Matching
# ---------------------------------------------------------------------


def find_fuzzy_matches(
    norm_query: str,
    name_cache: dict[str, dict[str, str]],
    context: FuzzyMatchContext,
) -> list[MatchTuple]:
    """
    Perform fuzzy matching using normalized and alternate normalized names.

    Scores are computed for:
        - norm_name (official name)
        - alt_norm (alternate name), if available

    The maximum score is retained. Matches that meet the threshold are returned.

    Args:
        norm_query (str): The normalized query string.
        name_cache (dict): The name cache with normalized and alternate names.
        context (FuzzyMatchContext): Context including threshold, algorithm, mode, etc.

    Returns:
        list[MatchTuple]: List of matches with computed scores.
    """
    validate_fuzzy_algo(context.fuzzy_algo)
    validate_fuzzy_match_mode(context.match_mode)
    validate_threshold(context.threshold)
    validate_name_cache_structure(name_cache)

    matches: list[MatchTuple] = []

    if context.verbose:
        echo(
            msg=MSG_FUZZY_START.format(query=context.query),
            style=lambda m: format_info(m, use_color=context.use_color),
            show=True,
            log=True,
            log_method="info",
        )
        echo(
            msg=MSG_FUZZY_SETTINGS.format(threshold=context.threshold, agg_fn=context.agg_fn),
            style=lambda m: format_info(m, use_color=context.use_color),
            show=True,
            log=True,
            log_method="info",
        )

    for char, names in name_cache.items():
        norm_name = names["normalized"]
        alt_norm = names.get("alternate_normalized")

        # Score against official name
        score1 = compute_similarity(
            norm_query,
            norm_name,
            context.fuzzy_algo,
            context.match_mode,
            agg_fn=context.agg_fn,
        )

        # Score against alternate name if present
        score2 = (
            compute_similarity(
                norm_query,
                alt_norm,
                context.fuzzy_algo,
                context.match_mode,
                agg_fn=context.agg_fn,
            )
            if alt_norm
            else None
        )

        score = _max_score(score1, score2)

        if score is None:
            if context.verbose and context.debug:
                echo(
                    msg=MSG_NO_SCORE_COMPUTED.format(char=char, code=ord(char)),
                    style=lambda m: format_debug(m, use_color=context.use_color),
                    show=True,
                    log=True,
                    log_method="debug",
                )
            continue

        if score >= context.threshold:
            matches.append(MatchTuple(ord(char), char, names["original"], score))

    return matches
