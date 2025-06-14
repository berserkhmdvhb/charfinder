"""
Type definitions and reusable dataclasses for CharFinder.

Defines:
- AlgorithmFn: Callable type alias for fuzzy algorithm functions.
- FuzzyMatchContext: Dataclass holding parameters for fuzzy matching.
- SearchConfig: Dataclass grouping parameters for Unicode search.
- CharMatch: TypedDict representing a single match result.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict

try:
    from typing import NotRequired, TypedDict
except ImportError:
    from typing_extensions import NotRequired, TypedDict 


if TYPE_CHECKING:
    from charfinder.constants import VALID_HYBRID_AGG_FUNCS, FuzzyAlgorithm, MatchMode


# ---------------------------------------------------------------------
# Type definitions
# ---------------------------------------------------------------------

AlgorithmFn = Callable[[str, str], float]


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


class CharMatch(TypedDict):
    code: str
    char: str
    name: str
    score: NotRequired[float]
