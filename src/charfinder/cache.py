"""Persistent cache for Unicode character names and normalized names.

Stores cached data in a JSON file inside the user's cache directory.
Supports lazy loading and saving to disk.

Attributes:
    cache_file: Path to the cache file.
    _cache: In-memory dictionary of cached data.

Methods:
    get(key): Return cached value if exists.
    set(key, value): Store a value in the cache.
    clear(): Clear the cache in memory and on disk.
"""


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
