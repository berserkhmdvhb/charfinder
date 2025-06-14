"""Matching helpers for CharFinder.

Provides internal helpers for exact and fuzzy matching of
Unicode character names, including alternate Unicode aliases.

Functions:
    find_exact_matches(): Perform exact matching.
    find_fuzzy_matches(): Perform fuzzy matching with scoring.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from charfinder.fuzzymatchlib import compute_similarity
from charfinder.types import FuzzyMatchContext
from charfinder.utils.formatter import echo
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_debug, format_info

__all__ = [
    "find_exact_matches",
    "find_fuzzy_matches",
]

logger = get_logger()

# ---------------------------------------------------------------------
# Exact Matching
# ---------------------------------------------------------------------


def find_exact_matches(
    norm_query: str,
    name_cache: dict[str, dict[str, str]],
    exact_match_mode: str,
) -> list[tuple[int, str, str, float | None]]:
    """
    Perform exact matching based on the chosen exact match mode,
    using both official and alternate normalized names.

    Args:
        norm_query (str): Normalized query.
        name_cache (dict[str, dict[str, str]]): Unicode name cache.
        exact_match_mode (str): Exact match mode to use ('substring' or 'word-subset').

    Returns:
        list[tuple[int, str, str, float | None]]:
            List of matches as (code point, character, name, None).
    """

    matches: list[tuple[int, str, str, float | None]] = []
    # Matching Loop
    for char, names in name_cache.items():
        code_point = ord(char)
        original_name = names["original"]
        norm_name = names["normalized"]
        alt_norm = names.get("alternate_normalized")

        if exact_match_mode == "substring":
            if norm_query in norm_name or (alt_norm and norm_query in alt_norm):
                matches.append((code_point, char, original_name, None))
        elif exact_match_mode == "word-subset":
            query_words = set(norm_query.split())
            name_words = set(norm_name.split())
            if alt_norm:
                name_words |= set(alt_norm.split())
            if query_words <= name_words:
                matches.append((code_point, char, original_name, None))
        else:
            message = f"Unknown exact match mode: {exact_match_mode}"
            raise ValueError(message)

    return matches


# ---------------------------------------------------------------------
# Fuzzy Matching
# ---------------------------------------------------------------------


def find_fuzzy_matches(
    norm_query: str,
    name_cache: dict[str, dict[str, str]],
    context: FuzzyMatchContext,
) -> list[tuple[int, str, str, float | None]]:
    """
    Perform fuzzy matching using normalized and alternate normalized names.

    Args:
        norm_query: Normalized query.
        name_cache: Unicode name cache.
        context: FuzzyMatchContext instance.

    Returns:
        list[tuple[int, str, str, float]]: List of matches as (code point, character, name, score).
    """
    matches: list[tuple[int, str, str, float | None]] = []

    if context.verbose:
        message = f"No exact match found for '{context.query}', "
        echo(
            message,
            style=lambda m: format_info(m, use_color=context.use_color),
            show=True,
            log=True,
            log_method="info",
        )

        message = (
            f"Trying fuzzy matching (threshold={context.threshold}, agg_fn={context.agg_fn})..."
        )
        echo(
            message,
            style=lambda m: format_info(m, use_color=context.use_color),
            show=True,
            log=True,
            log_method="info",
        )

    for char, names in name_cache.items():
        norm_name = names["normalized"]
        alt_norm = names.get("alternate_normalized")

        score1 = compute_similarity(
            norm_query,
            norm_name,
            context.fuzzy_algo,
            context.match_mode,
            agg_fn=context.agg_fn,
        )
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
        score = max(filter(None, [score1, score2]), default=None)

        if score is None:
            if context.verbose:
                message = f"Skipped char '{char}' (no valid score computed)."
                echo(
                    message,
                    style=lambda m: format_debug(m, use_color=context.use_color),
                    show=True,
                    log=True,
                    log_method="debug",
                )
            continue

        if score >= context.threshold:
            matches.append((ord(char), char, names["original"], score))

    return matches
