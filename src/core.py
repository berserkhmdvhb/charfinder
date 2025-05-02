...
import unicodedata
import difflib
import json
import os
import sys
import logging
from typing import Generator, Dict, Optional

logger = logging.getLogger("cf_lib")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

CACHE_FILE = "unicode_name_cache.json"

def normalize(text: str) -> str:
    """
    Normalize the input text using Unicode NFKD normalization and convert to uppercase.
    """
    return unicodedata.normalize('NFKD', text).upper()

def build_name_cache(force_rebuild: bool = False, verbose: bool = True) -> Dict[str, Dict[str, str]]:
    """
    Build and return a cache dictionary of characters to original and normalized names.
    Optionally force cache regeneration even if the file exists.

    Args:
        force_rebuild (bool): Force rebuilding the cache even if file exists.
        verbose (bool): If True, show info messages.

    Returns:
        dict: Mapping of characters to original and normalized names.
    """
    if not force_rebuild and os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        if verbose:
            logger.info(f"Loaded Unicode name cache from: {CACHE_FILE}")
        return cache

    if verbose:
        logger.info("Rebuilding Unicode name cache. This may take a few seconds...")

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
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False)
        if verbose:
            logger.info(f"Cache written to: {CACHE_FILE}")
    except Exception as e:
        logger.error(f"Failed to write cache: {e}")

    return cache

def find_chars(query: str, fuzzy: bool = False, threshold: float = 0.7,
               name_cache: Optional[Dict[str, Dict[str, str]]] = None,
               verbose: bool = True) -> Generator[str, None, None]:
    """
    Generate a list of Unicode characters matching a query.

    Args:
        query (str): Search term.
        fuzzy (bool): Enable fuzzy matching if no strict matches.
        threshold (float): Similarity threshold for fuzzy match.
        name_cache (dict): Optional preloaded cache.
        verbose (bool): Show info messages.

    Yields:
        str: Formatted string with Unicode info.
    """
    if not isinstance(query, str):
        raise TypeError("Query must be a string.")
    if not query.strip():
        return

    if name_cache is None:
        name_cache = build_name_cache(verbose=verbose)

    norm_query = normalize(query)
    matches = []

    for char, names in name_cache.items():
        if norm_query in names['normalized']:
            matches.append((ord(char), char, names['original']))

    if not matches and fuzzy:
        if verbose:
            logger.info(f"No exact match found for '{query}', trying fuzzy matching (threshold={threshold})...")
        norm_names = {char: data['normalized'] for char, data in name_cache.items()}
        close = difflib.get_close_matches(norm_query, norm_names.values(), n=20, cutoff=threshold)
        for char, data in name_cache.items():
            if data['normalized'] in close:
                matches.append((ord(char), char, data['original']))

    if verbose:
        if matches:
            logger.info(f"Found {len(matches)} match(es) for query: '{query}'")
        else:
            logger.info(f"No matches found for query: '{query}'")

    for code, char, name in matches:
        code_str = f"U+{code:04X}"
        char_str = char
        name_str = f"{name}  (\\u{code:04x})"
        yield f"{code_str}\t{char_str}\t{name_str}"