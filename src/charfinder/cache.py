"""
Shared caching utilities for CharFinder.

This module provides reusable caching mechanisms for:
- Normalization of Unicode strings (highly repetitive in fuzzy matching)
- Optionally other pure functions (e.g., similarity computation) in future

It also exposes:
- clear_all_caches(): clears all function caches
- print_cache_stats(): prints current cache usage

This pattern mirrors the `cache.py` module in the ppt project.
"""

from __future__ import annotations

from functools import lru_cache

from charfinder.utils.logger import get_logger
from charfinder.utils.normalizer import normalize

__all__ = [
    "MAX_CACHE_SIZE",
    "cached_normalize",
    "clear_all_caches",
    "print_cache_stats",
]

MAX_CACHE_SIZE = 1024  # normalize() is used VERY often → large cache is safe
logger = get_logger()


@lru_cache(maxsize=MAX_CACHE_SIZE)
def cached_normalize(text: str) -> str:
    """
    Cached wrapper for normalize() to speed up repeated normalization.

    Args:
        text: Input text.

    Returns:
        Normalized version of the text.
    """
    result = normalize(text)
    logger.debug("cached_normalize() hit for text: %r", text)
    return result


def clear_all_caches() -> None:
    """
    Clears all internal function caches. Useful for testing or debugging.
    """
    cached_normalize.cache_clear()
    logger.info("All caches cleared.")


def print_cache_stats() -> None:
    """
    Print the current cache statistics for all cached functions.
    Useful for debugging or performance monitoring.
    """
    logger.info("cached_normalize: %s", cached_normalize.cache_info())
