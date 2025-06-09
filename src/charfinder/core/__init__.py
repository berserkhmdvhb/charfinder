"""
Core API for CharFinder.

Exports:
    - build_name_cache: Build the Unicode name cache.
    - find_chars: Search Unicode characters.
    - find_chars_raw: Return raw Unicode character matches.
    - load_alternate_names: Load alternate names from UnicodeData.txt.
"""

from .core_main import find_chars, find_chars_raw
from .name_cache import build_name_cache
from .unicode_data_loader import load_alternate_names

__all__ = [
    "build_name_cache",
    "find_chars",
    "find_chars_raw",
    "load_alternate_names",
]
