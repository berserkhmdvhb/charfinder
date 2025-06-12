"""
Type definitions and reusable dataclasses for CharFinder.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict

try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired

if TYPE_CHECKING:
    from charfinder.constants import VALID_HYBRID_AGG_FUNCS, FuzzyAlgorithm, MatchMode

AlgorithmFn = Callable[[str, str], float]


@dataclass
class FuzzyMatchContext:
    threshold: float
    fuzzy_algo: FuzzyAlgorithm  # Literal[...] type
    match_mode: MatchMode  # Literal[...] type
    agg_fn: VALID_HYBRID_AGG_FUNCS  # Aggregation function for hybrid mode
    verbose: bool
    use_color: bool
    query: str


class CharMatch(TypedDict):
    code: str
    char: str
    name: str
    score: NotRequired[float]
