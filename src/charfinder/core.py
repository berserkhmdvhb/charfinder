import unicodedata
import json
import os
import sys
import logging
from typing import Generator
from colorama import Fore, Style

from .fuzzymatchlib import compute_similarity

CACHE_FILE = os.getenv("CHARFINDER_CACHE", "unicode_name_cache.json")

VALID_ALGOS = {"sequencematcher", "rapidfuzz", "levenshtein"}
VALID_MODES = {"single", "hybrid"}

FIELD_WIDTHS = {
    "code": 10,
    "char": 3,
    "name": 45,
}

logger = logging.getLogger("charfinder")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(message)s')  # Remove redundant level name
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def normalize(text: str) -> str:
    """
    Normalize the input text using Unicode NFKD normalization and convert to uppercase.
    """
    return unicodedata.normalize('NFKD', text).upper()

def build_name_cache(
    force_rebuild: bool = False,
    verbose: bool = True,
    use_color: bool = True,
    cache_file: str = CACHE_FILE
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
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
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
        name = unicodedata.name(char, '')
        if name:
            cache[char] = {
                "original": name,
                "normalized": normalize(name)
            }

    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
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
    threshold: float = 0.7,
    name_cache: dict[str, dict[str, str]] | None = None,
    verbose: bool = True,
    use_color: bool = True,
    fuzzy_algo: str = "sequencematcher",
    match_mode: str = "single"
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
        fuzzy_algo (str): Algorithm to use for fuzzy scoring.
        match_mode (str): 'single' for one algorithm or 'hybrid' to average scores.
    
    Yields:
        str: Each line of the formatted result output (including header and matches).
    """
    if fuzzy_algo not in VALID_ALGOS:
        raise ValueError(f"Invalid fuzzy algorithm: '{fuzzy_algo}'. Must be one of: {', '.join(VALID_ALGOS)}")
    if match_mode not in VALID_MODES:
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
        if norm_query in names['normalized']:
            matches.append((ord(char), char, names['original'], None))

    if not matches and fuzzy:
        if verbose:
            logger.info(
                f"{Fore.CYAN if use_color else ''}No exact match found for '{query}', trying fuzzy matching (threshold={threshold})...{Style.RESET_ALL if use_color else ''}"
            )
        for char, names in name_cache.items():
            score = compute_similarity(norm_query, names['normalized'], fuzzy_algo, match_mode)
            if score >= threshold:
                matches.append((ord(char), char, names['original'], score))

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