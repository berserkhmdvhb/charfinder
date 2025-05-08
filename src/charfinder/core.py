import json
import logging
import os
import sys
import unicodedata
from collections.abc import Generator
from typing import cast

from colorama import Fore, Style

# constants and aliases
from .constants import (
    CACHE_FILE,
    DEFAULT_THRESHOLD,
    FIELD_WIDTHS,
    VALID_FUZZY_ALGOS,
    VALID_MATCH_MODES,
    FuzzyAlgorithm,
    MatchMode,
)
from .fuzzymatchlib import compute_similarity

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(message)s")  # Remove redundant level name
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def normalize(text: str) -> str:
    """
    Normalize the input text using Unicode NFKD normalization and convert to uppercase.
    """
    return unicodedata.normalize("NFKD", text).upper()


def build_name_cache(
    force_rebuild: bool = False,
    verbose: bool = True,
    use_color: bool = True,
    cache_file: str = CACHE_FILE,
) -> dict[str, dict[str, str]]:
    """
    Build and return a cache dictionary of characters to original and normalized names.

    Args:
        force_rebuild (bool): Force rebuilding even if cache file exists.
        verbose (bool): Show logging messages.
        use_color (bool): Colorize log output.
        cache_file (str): Path to the cache file. Defaults to CACHE_FILE/global default.

    Returns:
        dict[str, dict[str, str]]: Character to name mapping.
    """
    if not force_rebuild and os.path.exists(cache_file):
        with open(cache_file, encoding="utf-8") as f:
            cache = cast(dict[str, dict[str, str]], json.load(f))
        if verbose:
            logger.info(
                f"{Fore.CYAN if use_color else ''}Loaded Unicode name cache from: {cache_file}{Style.RESET_ALL if use_color else ''}"
            )
        return cache

    if verbose:
        logger.info(
            f"{Fore.CYAN if use_color else ''}Rebuilding Unicode name cache. This may take a few seconds...{Style.RESET_ALL if use_color else ''}"
        )

    cache = {}
    for code in range(sys.maxunicode + 1):
        char = chr(code)
        name = unicodedata.name(char, "")
        if name:
            cache[char] = {"original": name, "normalized": normalize(name)}

    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)
        if verbose:
            logger.info(
                f"{Fore.CYAN if use_color else ''}Cache written to: {cache_file}{Style.RESET_ALL if use_color else ''}"
            )
    except Exception as e:
        logger.error(
            f"{Fore.RED if use_color else ''}Failed to write cache: {e}{Style.RESET_ALL if use_color else ''}"
        )

    return cache


def find_chars(
    query: str,
    fuzzy: bool = False,
    threshold: float = DEFAULT_THRESHOLD,
    name_cache: dict[str, dict[str, str]] | None = None,
    verbose: bool = True,
    use_color: bool = True,
    fuzzy_algo: FuzzyAlgorithm = "sequencematcher",
    match_mode: MatchMode = "single",
) -> Generator[str, None, None]:
    """
    Search for Unicode characters by name using exact or fuzzy matching.

    Args:
        query (str): Input query string.
        fuzzy (bool): Whether to enable fuzzy matching.
        threshold (float): Fuzzy match threshold between 0.0 and 1.0.
        name_cache (dict | None): Optional prebuilt Unicode name cache.
        verbose (bool): Whether to log progress.
        use_color (bool): Whether to colorize log output.
        fuzzy_algo (str): Algorithm to use for fuzzy scoring. Accepted values are 'sequencematcher', 'rapidfuzz', or 'levenshtein'.
        match_mode (str): 'single' for one algorithm or 'hybrid' to average scores. Accepted values are 'single' or 'hybrid'.

    Yields:
        str: Each line of the formatted result output (including header and matches).
    """
    if fuzzy_algo not in VALID_FUZZY_ALGOS:
        raise ValueError(
            f"Invalid fuzzy algorithm: '{fuzzy_algo}'. Must be one of: {', '.join(VALID_FUZZY_ALGOS)}"
        )
    if match_mode not in VALID_MATCH_MODES:
        raise ValueError(f"Invalid match mode: '{match_mode}'. Must be 'single' or 'hybrid'.")

    if not isinstance(query, str):
        raise TypeError("Query must be a string.")
    if not query.strip():
        return

    if name_cache is None:
        name_cache = build_name_cache(verbose=verbose, use_color=use_color)

    norm_query = normalize(query)
    matches: list[tuple[int, str, str, float | None]] = []

    for char, names in name_cache.items():
        if norm_query in names["normalized"]:
            matches.append((ord(char), char, names["original"], None))

    if not matches and fuzzy:
        if verbose:
            logger.info(
                f"{Fore.CYAN if use_color else ''}No exact match found for '{query}', trying fuzzy matching (threshold={threshold})...{Style.RESET_ALL if use_color else ''}"
            )
        for char, names in name_cache.items():
            score: float | None = compute_similarity(
                norm_query, names["normalized"], fuzzy_algo, match_mode
            )
            if score is None:
                if verbose:
                    logger.debug(
                        f"{Fore.MAGENTA if use_color else ''}Skipped char '{char}' (no valid score computed).{Style.RESET_ALL if use_color else ''}"
                    )
                continue
            if score >= threshold:
                matches.append((ord(char), char, names["original"], score))

    if verbose:
        logger.info(
            f"{Fore.CYAN if use_color else ''}{'Found ' + str(len(matches)) + ' match(es)' if matches else 'No matches found'} for query: '{query}'{Style.RESET_ALL if use_color else ''}"
        )

    if not matches:
        return  # Avoid yielding headers when no match is found

    if matches[0][3] is not None:
        header = f"{'CODE':<{FIELD_WIDTHS['code']}} {'CHAR':<{FIELD_WIDTHS['char']}} {'NAME':<{FIELD_WIDTHS['name']}} SCORE"
        divider = "-" * len(header)
    else:
        header = f"{'CODE':<{FIELD_WIDTHS['code']}} {'CHAR':<{FIELD_WIDTHS['char']}} {'NAME'}"
        divider = "-" * 50

    yield header
    yield divider

    for code, char, name, score in matches:
        code_str = f"U+{code:04X}"
        name_str = f"{name}  (\\u{code:04x})"
        score_str = f"{score:>6.3f}" if score is not None else ""
        yield f"{code_str:<{FIELD_WIDTHS['code']}} {char:<{FIELD_WIDTHS['char']}} {name_str:<{FIELD_WIDTHS['name']}} {score_str}".rstrip()
