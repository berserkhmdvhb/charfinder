"""
charfinder: Unicode character search with fuzzy and exact matching.

This module exposes the main library functions for searching Unicode characters.
"""

from .core import find_chars, find_chars_raw
from .core.name_cache import build_name_cache
from .utils.normalizer import normalize

__version__ = "1.0.9"

__all__ = [
    "build_name_cache",
    "find_chars",
    "find_chars_raw",
    "normalize",
]

