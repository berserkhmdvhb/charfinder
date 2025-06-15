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

# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

import time  # Added for retry logic


def build_name_cache(
    *,
    force_rebuild: bool = False,
    show: bool = True,
    use_color: bool = True,
    cache_file_path: Path | None = None,
    retry_attempts: int = 3,  # Added retry attempts parameter
    retry_delay: float = 2.0,  # Delay between retries (in seconds)
) -> dict[str, dict[str, str]]:
    """
    Build and return a cache dictionary of characters to original and normalized names,
    including alternate names where available.

    This function will attempt to load an existing cache if present, or rebuild it if
    `force_rebuild=True`. The cache is written to a JSON file on disk for future reuse.

    Args:
        force_rebuild (bool): If True, force rebuild the cache even if a cached file exists.
        show (bool): Whether to display progress messages.
        use_color (bool): Whether to apply ANSI color formatting to messages.
        cache_file_path (Path | None): Optional path to use for cache file; defaults to standard cache path.
        retry_attempts (int): Number of retry attempts if writing cache fails.
        retry_delay (float): Delay (in seconds) between retry attempts.

    Returns:
        dict[str, dict[str, str]]: A dictionary mapping each character to its original and normalized names, and optionally alternate names.

    Raises:
        OSError: If there is an error writing the cache file to disk.
        ValueError: If the cache file is malformed or cannot be read.
    """
    # Validate the cache_file_path argument
    if cache_file_path is not None and not isinstance(cache_file_path, Path):
        message = "cache_file_path must be a valid Path object."
        raise ValueError(message)

    if cache_file_path is None:
        cache_file_path = get_cache_file()

    path = Path(cache_file_path)

    # Load from cache if available and not forced to rebuild
    if not force_rebuild and path.exists():
        try:
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
        except (json.JSONDecodeError, OSError) as exc:
            message = f"Failed to load cache from {cache_file_path}: {exc}"
            raise ValueError(message)

    # Rebuild the cache if needed
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
    alternate_names = load_alternate_names(show=show, use_color=use_color)

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

    # Retry logic for writing the cache file if the first attempt fails
    attempt = 0
    while attempt < retry_attempts:
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
            break  # Exit the loop if the cache is written successfully
        except OSError as exc:
            attempt += 1
            if attempt < retry_attempts:
                # If the retry limit hasn't been reached, log and retry after a delay
                message = (
                    f"Failed to write cache (attempt {attempt}/{retry_attempts}). "
                    f"Retrying in {retry_delay}s..."
                )
                echo(
                    message,
                    style=lambda m: format_error(m, use_color=use_color),
                    stream=sys.stderr,
                    show=True,
                    log=True,
                    log_method="warning",
                )
                time.sleep(retry_delay)
            else:
                message = "Failed to write cache after multiple attempts."
                echo(
                    message,
                    style=lambda m: format_error(m, use_color=use_color),
                    stream=sys.stderr,
                    show=True,
                    log=True,
                    log_method="error",
                )
                raise exc  # Raise the exception if retries are exhausted

    return cache
