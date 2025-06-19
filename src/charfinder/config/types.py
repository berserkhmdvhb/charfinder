"""
Type definitions and reusable dataclasses for CharFinder.

Defines:
- SearchConfig: Dataclass grouping parameters for Unicode search.
- AlgorithmFn: Callable type alias for fuzzy algorithm functions.

"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple, Protocol

from typing_extensions import NotRequired, TypedDict

from charfinder.config.aliases import (
    FuzzyAlgorithm,
    FuzzyMatchMode,
    HybridAggFunc,
    NormalizationForm,
)

__all__ = [
    "AlgorithmFn",
    "CLIResult",
    "CharMatch",
    "DiagnosticFormatter",
    "EchoFunc",
    "FormatterFunc",
    "FuzzyMatchContext",
    "HybridAggFunc",
    "MatchDiagnosticsInfo",
    "MatchFunc",
    "MatchResult",
    "MatchTuple",
    "NameCache",
    "NormalizationProfileDict",
    "SearchConfig",
    "UnicodeDataLoader",
]
# ---------------------------------------------------------------------
# Callable type aliases
# ---------------------------------------------------------------------

AlgorithmFn = Callable[[str, str], float]
NameCache = dict[str, dict[str, str]]

# ---------------------------------------------------------------------
# Dataclass-based type definitions
# ---------------------------------------------------------------------


@dataclass
class FuzzyMatchContext:
    threshold: float
    fuzzy_algo: FuzzyAlgorithm
    match_mode: FuzzyMatchMode
    agg_fn: HybridAggFunc
    verbose: bool
    use_color: bool
    query: str


@dataclass
class SearchConfig:
    fuzzy: bool
    threshold: float
    name_cache: NameCache | None
    verbose: bool
    use_color: bool
    fuzzy_algo: FuzzyAlgorithm
    fuzzy_match_mode: FuzzyMatchMode
    exact_match_mode: str
    agg_fn: HybridAggFunc
    prefer_fuzzy: bool


# ---------------------------------------------------------------------
# TypedDict definitions
# ---------------------------------------------------------------------


class CharMatch(TypedDict):
    code: str
    char: str
    name: str
    score: NotRequired[float]
    is_fuzzy: NotRequired[bool]



@dataclass
@dataclass
class MatchDiagnosticsInfo:
    """
    Dataclass for structured match diagnostics used in --debug CLI output.
    """

    fuzzy: bool
    fuzzy_was_used: bool
    fuzzy_algo: str
    fuzzy_match_mode: str
    prefer_fuzzy: bool
    exact_match_mode: str
    threshold: float
    hybrid_agg_fn: str | None = None


CLIResult = tuple[int, dict[str, Any] | MatchDiagnosticsInfo | None]


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

    def __call__(self, file_path: Path) -> NameCache: ...


@dataclass
class MatchResult:
    """
    Represents the outcome of a character search, including the exit code and optional diagnostics.
    """

    exit_code: int
    match_info: MatchDiagnosticsInfo | None = None


@dataclass
class MatchTuple:
    code: int
    char: str
    name: str
    score: float | None = None
    is_fuzzy: bool = False

class NormalizationProfileDict(TypedDict, total=False):
    form: NormalizationForm
    strip_accents: bool
    strip_whitespace: bool


# ------------------------------------------------------------------------
# Dataclasses for Fuzzy Configuration
# ------------------------------------------------------------------------


@dataclass
class FuzzyConfig:
    fuzzy_algo: FuzzyAlgorithm
    fuzzy_match_mode: FuzzyMatchMode
