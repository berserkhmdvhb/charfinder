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

from charfinder.config.settings import get_cache_file
from charfinder.config.types import NameCache
from charfinder.core.unicode_data_loader import load_alternate_names
from charfinder.utils.formatter import echo
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_error, format_info
from charfinder.utils.normalizer import normalize

__all__ = ["build_name_cache"]

logger = get_logger()

# ---------------------------------------------------------------------
# Message Constants
# ---------------------------------------------------------------------

MSG_LOAD_SUCCESS = 'Loaded Unicode name cache from: "{path}"'
MSG_WRITE_FAIL = "Failed to write cache after multiple attempts."
MSG_WRITE_RETRY = (
    "Failed to write cache (attempt {attempt}/{max_attempts}). Retrying in {delay}s..."
)
MSG_WRITE_SUCCESS = 'Cache written to: "{path}"'
MSG_REBUILD = "Rebuilding Unicode name cache. This may take a few seconds..."
MSG_INVALID_PATH_TYPE = "cache_file_path must be a valid Path object."


# ---------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------


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


# ---------------------------------------------------------------------
# Cache I/O Utilities
# ---------------------------------------------------------------------


def _load_existing_cache(path: Path, *, options: CacheIOOptions) -> NameCache:
    """
    Attempt to load existing cache from disk.

    Args:
        path (Path): Path to the cache file.
        options (CacheIOOptions): Options controlling output and behavior.

    Returns:
        NameCache: The loaded cache dictionary.

    Raises:
        ValueError: If the cache file is invalid or cannot be read.
    """
    try:
        with path.open(encoding="utf-8") as f:
            cache = cast("NameCache", json.load(f))
    except (json.JSONDecodeError, OSError) as exc:
        message = f"Failed to load cache from {path}: {exc}"
        raise ValueError(message) from exc
    else:
        echo(
            MSG_LOAD_SUCCESS.format(path=path),
            style=lambda m: format_info(m, use_color=options.use_color),
            stream=sys.stderr,
            show=options.show,
            log=True,
            log_method="info",
        )
        return cache


def _save_cache_with_retries(
    cache: NameCache,
    path: Path,
    *,
    options: CacheIOOptions,
) -> None:
    """
    Attempt to save the cache to disk with retries.

    Args:
        cache (NameCache): Cache data to persist.
        path (Path): Target path for the cache file.
        options (CacheIOOptions): Retry settings and formatting options.

    Raises:
        OSError: If writing fails after all retry attempts.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    def _attempt_write() -> bool:
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False)
        except OSError:
            return False
        else:
            return True

    for attempt in range(1, options.retry_attempts + 1):
        if _attempt_write():
            echo(
                MSG_WRITE_SUCCESS.format(path=path),
                style=lambda m: format_info(m, use_color=options.use_color),
                stream=sys.stderr,
                show=options.show,
                log=True,
                log_method="info",
            )
            break
        if attempt < options.retry_attempts:
            echo(
                MSG_WRITE_RETRY.format(
                    attempt=attempt,
                    max_attempts=options.retry_attempts,
                    delay=options.retry_delay,
                ),
                style=lambda m: format_error(m, use_color=options.use_color),
                stream=sys.stderr,
                show=True,
                log=True,
                log_method="warning",
            )
            time.sleep(options.retry_delay)
        else:
            echo(
                MSG_WRITE_FAIL,
                style=lambda m: format_error(m, use_color=options.use_color),
                stream=sys.stderr,
                show=True,
                log=True,
                log_method="error",
            )
            message = f"Failed to write cache to {path} after {options.retry_attempts} attempts."
            raise OSError(message)


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def build_name_cache(*, options: BuildCacheOptions | None = None) -> NameCache:
    """
    Build and return a cache dictionary of characters to original and normalized names,
    including alternate names where available.

    This function will attempt to load an existing cache if present, or rebuild it if
    `force_rebuild=True`. The cache is written to a JSON file on disk for future reuse.

    Args:
        options (BuildCacheOptions): Configuration options.

    Returns:
        NameCache: Mapping of characters to name metadata.

    Raises:
        OSError: If there is an error writing the cache file to disk.
        ValueError: If the cache file is malformed or cannot be read.
    """
    if options is None:
        options = BuildCacheOptions()

    if options.cache_file_path is not None and not isinstance(options.cache_file_path, Path):
        raise ValueError(MSG_INVALID_PATH_TYPE)

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

    echo(
        MSG_REBUILD,
        style=lambda m: format_info(m, use_color=options.use_color),
        stream=sys.stderr,
        show=options.show,
        log=True,
        log_method="info",
    )

    alternate_names: dict[str, str] = load_alternate_names(
        show=options.show,
        use_color=options.use_color,
    )

    cache: NameCache = {}

    for code in range(sys.maxunicode + 1):
        char = chr(code)
        try:
            name = unicodedata.name(char, "")
        except ValueError:
            continue
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
