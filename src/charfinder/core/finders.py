"""
Match output formatter and public routing logic for CharFinder.

This module formats and routes the output of Unicode name searches
based on a validated SearchConfig object.

Responsibilities:
    - Route queries to the internal _resolve_matches().
    - Format match results for CLI (text) or JSON output.
    - Convert internal match tuples to CharMatch dictionaries.

Used by:
    - core_main.py to expose search APIs.
    - CLI and tests for rendering or exporting results.

Functions:
    - find_chars(): Yields formatted result rows for CLI.
    - find_chars_raw(): Returns raw result objects.
    - find_chars_with_info(): Returns raw results and fuzzy-used flag.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

from charfinder.core.handlers import _resolve_matches
from charfinder.utils.formatter import (
    format_result_header,
    format_result_row,
    matchtuple_to_charmatch,
)

if TYPE_CHECKING:
    from charfinder.config.types import CharMatch, SearchConfig

__all__ = [
    "find_chars",
    "find_chars_raw",
    "find_chars_with_info",
]


def find_chars(query: str, config: SearchConfig) -> Generator[str, None, None]:
    """
    Perform character search and yield formatted output lines.

    Args:
        query (str): Input query string.
        config (SearchConfig): Validated search behavior.

    Yields:
        str: CLI-formatted output lines with matched characters.
    """
    matches, _ = _resolve_matches(query, config)
    has_score = bool(matches) and matches[0].score is not None

    yield from format_result_header(has_score=has_score)
    for match in matches:
        yield format_result_row(
            match.code,
            match.char,
            match.name,
            match.score,
        )


def find_chars_raw(query: str, config: SearchConfig) -> list[CharMatch]:
    """
    Perform character search and return raw results for JSON output.

    Args:
        query (str): Input query string.
        config (SearchConfig): Validated search behavior.

    Returns:
        list[CharMatch]: List of match records with metadata.
    """
    matches, _ = _resolve_matches(query, config)
    return [matchtuple_to_charmatch(m) for m in matches]


def find_chars_with_info(query: str, config: SearchConfig) -> tuple[list[CharMatch], bool]:
    """
    Perform character search and return results with fuzzy usage flag.

    Args:
        query (str): Input query string.
        config (SearchConfig): Validated search behavior.

    Returns:
        tuple[list[CharMatch], bool]: Matches and whether fuzzy matching was used.
    """
    matches, fuzzy_used = _resolve_matches(query, config)
    return [matchtuple_to_charmatch(m) for m in matches], fuzzy_used
