"""
CharFinder package initializer.

Defines the public library API:

- build_name_cache
- find_chars
- normalize

Also defines __version__.
"""

from .core.core_main import build_name_cache, find_chars, normalize

__all__ = ["build_name_cache", "find_chars", "normalize"]
__version__ = "1.0.8"
