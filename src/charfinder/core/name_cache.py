"""Name cache builder for CharFinder.

Provides functionality to build and cache Unicode character names,
including alternate names from UnicodeData.txt.

This module is intentionally separated from CLI logic to support clean reuse
in both library and CLI contexts.

Functions:
    build_name_cache(): Build the Unicode name cache and optionally persist it.
"""

import json
import sys
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from charfinder.core.unicode_data_loader import load_alternate_names
from charfinder.settings import get_cache_file
from charfinder.utils.formatter import echo
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_error, format_info
from charfinder.utils.normalizer import normalize

__all__ = ["build_name_cache"]

logger = get_logger()


@dataclass
class CacheIOOptions:
    use_color: bool
    show: bool
    retry_attempts: int
    retry_delay: float


@dataclass
class BuildCacheOptions:
    force_rebuild: bool = False
    show: bool = True
    use_color: bool = True
    cache_file_path: Path | None = None
    retry_attempts: int = 3
    retry_delay: float = 2.0


def _load_existing_cache(path: Path, *, options: CacheIOOptions) -> dict[str, dict[str, str]]:
    """
    Attempt to load existing cache from disk.

    Args:
        path (Path): Path to the cache file.
        options (CacheIOOptions): Options controlling output and behavior.

    Returns:
        dict[str, dict[str, str]]: The loaded cache dictionary.

    Raises:
        ValueError: If the cache file is invalid or cannot be read.
    """
    try:
        with path.open(encoding="utf-8") as f:
            cache = cast("dict[str, dict[str, str]]", json.load(f))
    except (json.JSONDecodeError, OSError) as exc:
        error_msg = f"Failed to load cache from {path}: {exc}"
        raise ValueError(error_msg) from exc
    else:
        success_msg = f'Loaded Unicode name cache from: "{path}"'
        echo(
            success_msg,
            style=lambda m: format_info(m, use_color=options.use_color),
            stream=sys.stderr,
            show=options.show,
            log=True,
            log_method="info",
        )
        return cache


def _save_cache_with_retries(
    cache: dict[str, dict[str, str]],
    path: Path,
    *,
    options: CacheIOOptions,
) -> None:
    """
    Attempt to save the cache to disk with retries.

    Args:
        cache (dict[str, dict[str, str]]): Cache data to persist.
        path (Path): Target path for the cache file.
        options (CacheIOOptions): Retry settings and formatting options.

    Raises:
        OSError: If writing fails after all retry attempts.
    """
    for attempt in range(1, options.retry_attempts + 1):
        success = False
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False)
            success = True
        except OSError:
            if attempt < options.retry_attempts:
                retry_msg = (
                    f"Failed to write cache (attempt {attempt}/{options.retry_attempts}). "
                    f"Retrying in {options.retry_delay}s..."
                )
                echo(
                    retry_msg,
                    style=lambda m: format_error(m, use_color=options.use_color),
                    stream=sys.stderr,
                    show=True,
                    log=True,
                    log_method="warning",
                )
                time.sleep(options.retry_delay)
            else:
                fail_msg = "Failed to write cache after multiple attempts."
                echo(
                    fail_msg,
                    style=lambda m: format_error(m, use_color=options.use_color),
                    stream=sys.stderr,
                    show=True,
                    log=True,
                    log_method="error",
                )
                raise

        if success:
            success_msg = f'Cache written to: "{path}"'
            echo(
                success_msg,
                style=lambda m: format_info(m, use_color=options.use_color),
                stream=sys.stderr,
                show=options.show,
                log=True,
                log_method="info",
            )
            break


def build_name_cache(*, options: BuildCacheOptions | None = None) -> dict[str, dict[str, str]]:
    """
    Build and return a cache dictionary of characters to original and normalized names,
    including alternate names where available.

    This function will attempt to load an existing cache if present, or rebuild it if
    `force_rebuild=True`. The cache is written to a JSON file on disk for future reuse.

    Args:
        options (BuildCacheOptions): Configuration options.

    Returns:
        dict[str, dict[str, str]]: Mapping of characters to name metadata.

    Raises:
        OSError: If there is an error writing the cache file to disk.
        ValueError: If the cache file is malformed or cannot be read.
    """

    if options is None:
        options = BuildCacheOptions()

    if options.cache_file_path is not None and not isinstance(options.cache_file_path, Path):
        error_msg = "cache_file_path must be a valid Path object."
        raise ValueError(error_msg)

    if options.cache_file_path is None:
        options.cache_file_path = get_cache_file()

    path = Path(options.cache_file_path)

    io_options = CacheIOOptions(
        use_color=options.use_color,
        show=options.show,
        retry_attempts=options.retry_attempts,
        retry_delay=options.retry_delay,
    )

    if not options.force_rebuild and path.exists():
        return _load_existing_cache(path, options=io_options)

    rebuild_msg = "Rebuilding Unicode name cache. This may take a few seconds..."
    echo(
        rebuild_msg,
        style=lambda m: format_info(m, use_color=options.use_color),
        stream=sys.stderr,
        show=options.show,
        log=True,
        log_method="info",
    )

    alternate_names = load_alternate_names(show=options.show, use_color=options.use_color)
    cache: dict[str, dict[str, str]] = {}

    for code in range(sys.maxunicode + 1):
        char = chr(code)
        name = unicodedata.name(char, "")
        if not name:
            continue

        alt_name = alternate_names.get(char)
        entry = {
            "original": name,
            "normalized": normalize(name),
        }
        if alt_name:
            entry["alternate"] = alt_name
            entry["alternate_normalized"] = normalize(alt_name)

        cache[char] = entry

    _save_cache_with_retries(cache, path, options=io_options)
    return cache
