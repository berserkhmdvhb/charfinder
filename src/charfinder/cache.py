"""Caching utilities for Unicode normalization in Charfinder.

Provides an LRU cache for the `normalize()` function to avoid redundant
normalization computations and improve performance across repeated lookups.

Functions:
    cached_normalize(text): Return normalized version of text, with LRU caching.
    clear_all_caches(): Clear all internal function caches (useful for testing).
    print_cache_stats(): Print current LRU cache statistics to the log.

Constants:
    MAX_CACHE_SIZE: Maximum size of the LRU cache (default: 1024).
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from __future__ import annotations

from functools import lru_cache

from charfinder.utils.formatter import log_optionally_echo
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_info
from charfinder.utils.normalizer import normalize

__all__ = [
    "MAX_CACHE_SIZE",
    "cached_normalize",
    "clear_all_caches",
    "print_cache_stats",
]

MAX_CACHE_SIZE = 1024  # normalize() is used VERY often → large cache is safe
logger = get_logger()

# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


@lru_cache(maxsize=MAX_CACHE_SIZE)
def cached_normalize(text: str) -> str:
    """
    Cached wrapper for normalize() to speed up repeated normalization.

    Args:
        text: Input text.

    Returns:
        str: Normalized version of the text.
    """
    result = normalize(text)
    logger.debug("cached_normalize() hit for text: %r", text)
    return result


def clear_all_caches() -> None:
    """
    Clears all internal function caches. Useful for testing or debugging.
    """
    cached_normalize.cache_clear()
    log_optionally_echo("All caches cleared.", level="info", show=False, style=format_info)


def print_cache_stats() -> None:
    """
    Print the current cache statistics for all cached functions.
    Useful for debugging or performance monitoring.
    """
    log_optionally_echo(
        f"cached_normalize: {cached_normalize.cache_info()}",
        level="info",
        show=False,
        style=format_info,
    )
