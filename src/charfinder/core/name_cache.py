"""
Name cache builder for CharFinder.

This module provides functionality to build and cache Unicode character names,
including alternate names from UnicodeData.txt.

It is intentionally separated from CLI logic to support clean reuse in both
library and CLI contexts.

Exports:
    - build_name_cache: Build the Unicode name cache and optionally persist it.
"""

import json
import sys
import unicodedata
from pathlib import Path
from typing import cast

from charfinder.core.unicode_data_loader import load_alternate_names
from charfinder.utils.formatter import echo
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_error, format_info
from charfinder.utils.normalizer import normalize

__all__ = [
    "build_name_cache",
]

logger = get_logger()


def build_name_cache(
    *,
    force_rebuild: bool = False,
    verbose: bool = True,
    use_color: bool = True,
    cache_file: str | None = None,
) -> dict[str, dict[str, str]]:
    """
    Build and return a cache dictionary of characters to original and normalized names,
    including alternate names where available.

    Args:
        force_rebuild: Force rebuilding even if cache file exists.
        verbose: Show logging messages.
        use_color: Colorize log output.
        cache_file: Path to the cache file.

    Returns:
        Dictionary mapping each character to its name data:
        {
            "original": official Unicode name,
            "normalized": normalized official name,
            "alternate": alternate name (if any),
            "alternate_normalized": normalized alternate name (if any),
        }
    """
    if cache_file is None:
        from charfinder.settings import get_cache_file

        cache_file = get_cache_file()

    path = Path(cache_file)

    # Load from cache if available
    if not force_rebuild and path.exists():
        with path.open(encoding="utf-8") as f:
            cache = cast("dict[str, dict[str, str]]", json.load(f))
        message = f"Loaded Unicode name cache from: {cache_file}"
        echo(
            message,
            style=lambda m: format_info(m, use_color=use_color),
            show=verbose,
            log=True,
            log_method="info",
        )
        return cache

    # Rebuild the cache
    message = "Rebuilding Unicode name cache. This may take a few seconds..."
    logger.info(message)
    if verbose:
        echo(
            message,
            style=lambda m: format_info(m, use_color=use_color),
            show=True,
            log=True,
            log_method="info",
        )

    # Load alternate names once
    alternate_names = load_alternate_names()

    cache = {}
    for code in range(sys.maxunicode + 1):
        char = chr(code)
        name = unicodedata.name(char, "")
        if not name:
            continue

        alt_name = alternate_names.get(char)

        cache_entry = {
            "original": name,
            "normalized": normalize(name),
        }
        if alt_name:
            cache_entry["alternate"] = alt_name
            cache_entry["alternate_normalized"] = normalize(alt_name)

        cache[char] = cache_entry

    # Write cache to disk
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)
        message = f"Cache written to: {cache_file}"
        logger.info(message)
        if verbose:
            echo(
                message,
                style=lambda m: format_info(m, use_color=use_color),
                show=True,
                log=True,
                log_method="info",
            )
    except Exception:
        message = "Failed to write cache."
        echo(
            message,
            style=lambda m: format_error(m, use_color=use_color),
            show=True,
            log=True,
            log_method="error",
        )
        logger.exception(message)

    return cache
