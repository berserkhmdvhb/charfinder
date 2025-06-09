"""
charfinder: Unicode character search with fuzzy and exact matching.

This module exposes the main library functions for searching Unicode characters.
"""

from .core import find_chars, find_chars_raw
from .core.name_cache import build_name_cache
from .utils.normalizer import normalize

__all__ = [
    "build_name_cache",
    "find_chars",
    "find_chars_raw",
    "normalize",
]
