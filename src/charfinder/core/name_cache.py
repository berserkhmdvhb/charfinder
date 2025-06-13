"""Name cache builder for CharFinder.

Provides functionality to build and cache Unicode character names,
including alternate names from UnicodeData.txt.

This module is intentionally separated from CLI logic to support clean reuse
in both library and CLI contexts.

Functions:
    build_name_cache(): Build the Unicode name cache and optionally persist it.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import json
import sys
import unicodedata
from pathlib import Path
from typing import cast

from charfinder.core.unicode_data_loader import load_alternate_names
from charfinder.settings import get_cache_file
from charfinder.utils.formatter import echo
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_error, format_info
from charfinder.utils.normalizer import normalize

__all__ = [
    "build_name_cache",
]

logger = get_logger()

# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def build_name_cache(
    *,
    force_rebuild: bool = False,
    show: bool = True,
    use_color: bool = True,
    cache_file_path: Path | None = None,
) -> dict[str, dict[str, str]]:
    """
    Build and return a cache dictionary of characters to original and normalized names,
    including alternate names where available.

    Args:
        force_rebuild (bool): If True, force rebuild the cache even if a cached file exists.
        show (bool): Whether to display progress messages.
        use_color (bool): Whether to apply ANSI color formatting to messages.
        cache_file_path (Path | None):
            Optional path to use for cache file; defaults to standard cache path.

    Returns:
        dict[str, dict[str, str]]:
            Unicode name cache mapping each character to its names.
    """

    if cache_file_path is None:
        cache_file_path = get_cache_file()

    path = Path(cache_file_path)

    # Load from cache if available
    if not force_rebuild and path.exists():
        with path.open(encoding="utf-8") as f:
            cache = cast("dict[str, dict[str, str]]", json.load(f))
        message = f'Loaded Unicode name cache from: "{cache_file_path}"'
        echo(
            message,
            style=lambda m: format_info(m, use_color=use_color),
            stream=sys.stderr,
            show=show,
            log=True,
            log_method="info",
        )
        return cache

    # Rebuild the cache
    message = "Rebuilding Unicode name cache. This may take a few seconds..."
    echo(
        message,
        style=lambda m: format_info(m, use_color=use_color),
        stream=sys.stderr,
        show=show,
        log=True,
        log_method="info",
    )

    # Load alternate names once
    alternate_names = load_alternate_names(show=show)

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
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)
        message = f'Cache written to: "{cache_file_path}"'
        echo(
            message,
            style=lambda m: format_info(m, use_color=use_color),
            stream=sys.stderr,
            show=show,
            log=True,
            log_method="info",
        )
    except OSError:
        message = "Failed to write cache."
        echo(
            message,
            style=lambda m: format_error(m, use_color=use_color),
            stream=sys.stderr,
            show=True,
            log=True,
            log_method="error",
        )

    return cache
