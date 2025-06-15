"""
Type definitions and reusable dataclasses for CharFinder.

Defines:
- AlgorithmFn: Callable type alias for fuzzy algorithm functions.
- FuzzyMatchContext: Dataclass holding parameters for fuzzy matching.
- SearchConfig: Dataclass grouping parameters for Unicode search.
- CharMatch: TypedDict representing a single match result.
- FormatterFunc: Protocol for formatting functions with [PREFIX] and optional color.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from typing_extensions import NotRequired, TypedDict

if TYPE_CHECKING:
    from charfinder.constants import VALID_HYBRID_AGG_FUNCS, FuzzyAlgorithm, MatchMode

# ---------------------------------------------------------------------
# Callable type aliases
# ---------------------------------------------------------------------

AlgorithmFn = Callable[[str, str], float]

# ---------------------------------------------------------------------
# Dataclass-based type definitions
# ---------------------------------------------------------------------


@dataclass
class FuzzyMatchContext:
    threshold: float
    fuzzy_algo: FuzzyAlgorithm
    match_mode: MatchMode
    agg_fn: VALID_HYBRID_AGG_FUNCS
    verbose: bool
    use_color: bool
    query: str


@dataclass
class SearchConfig:
    fuzzy: bool
    threshold: float
    name_cache: dict[str, dict[str, str]] | None
    verbose: bool
    use_color: bool
    fuzzy_algo: FuzzyAlgorithm
    fuzzy_match_mode: MatchMode
    exact_match_mode: str
    agg_fn: VALID_HYBRID_AGG_FUNCS
    prefer_fuzzy: bool


# ---------------------------------------------------------------------
# TypedDict definitions
# ---------------------------------------------------------------------


class CharMatch(TypedDict):
    code: str
    char: str
    name: str
    score: NotRequired[float]


# ---------------------------------------------------------------------
# Protocols (for testable function types)
# ---------------------------------------------------------------------
class FormatterFunc(Protocol):
    """
    Protocol for formatter functions that apply a [PREFIX] and optional color.
    """

    def __call__(self, message: str, *, use_color: bool) -> str: ...


class EchoFunc(Protocol):
    """
    Protocol for echo-like functions that write styled messages to a stream.
    """

    def __call__(
        self,
        msg: str,
        style: Callable[[str], str],
        *,
        stream_: object,
        show: bool = True,
        log: bool = False,
        log_method: str | None = None,
    ) -> None: ...


class MatchFunc(Protocol):
    """
    Protocol for a fuzzy match function returning a similarity score.
    """

    def __call__(self, query: str, candidate: str) -> float: ...


class DiagnosticFormatter(Protocol):
    """
    Protocol for diagnostic formatting functions for match analysis.
    """

    def __call__(
        self,
        query: str,
        candidate: str,
        *,
        score: float,
        algorithm: str,
        mode: str,
        use_color: bool,
    ) -> str: ...


class UnicodeDataLoader(Protocol):
    """
    Protocol for functions that load Unicode data from disk or cache.
    """

    def __call__(self, file_path: Path) -> dict[str, dict[str, str]]: ...
