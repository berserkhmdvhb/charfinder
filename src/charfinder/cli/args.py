"""
Argument names and argument validators for CharFinder CLI.

This module defines:

1. CLI argument names used across the CLI components (parser, handlers).
2. Custom argument validators (such as `threshold_range` for --threshold).

This module is used by `cli_main.py` and `parser.py` during CLI argument parsing.
"""

from __future__ import annotations

import argparse

from charfinder.constants import (
    DEFAULT_COLOR_MODE,
    DEFAULT_EXACT_MATCH_MODE,
    DEFAULT_FUZZY_ALGO,
    DEFAULT_FUZZY_MATCH_MODE,
    DEFAULT_THRESHOLD,
    VALID_EXACT_MATCH_MODES,
    VALID_FUZZY_ALGOS,
    VALID_FUZZY_MATCH_MODES,
)

__all__ = [
    "ARG_COLOR",
    "ARG_EXACT_MATCH_MODE",
    "ARG_FUZZY_MATCH_MODE",
    "ARG_HYBRID_AGG_FN",
    "ARG_QUERY",
    "ARG_THRESHOLD",
    "DEFAULT_COLOR_MODE",
    "DEFAULT_EXACT_MATCH_MODE",
    "DEFAULT_FUZZY_ALGO",
    "DEFAULT_FUZZY_MATCH_MODE",
    "DEFAULT_THRESHOLD",
    "VALID_EXACT_MATCH_MODES",
    "VALID_FUZZY_ALGOS",
    "VALID_FUZZY_MATCH_MODES",
    "threshold_range",
]

# Argument names (used in parser.py and handlers.py)
ARG_QUERY = "query"
ARG_THRESHOLD = "--threshold"
ARG_COLOR = "--color"
ARG_FORMAT = "--format"

ARG_EXACT_MATCH_MODE = "exact_match_mode"
ARG_FUZZY_MATCH_MODE = "fuzzy_match_mode"
ARG_HYBRID_AGG_FN = "hybrid_agg_fn"


def threshold_range(value: str) -> float:
    """
    Validate that the threshold is a float between 0.0 and 1.0.

    Args:
        value (str): The input string from the command-line argument.

    Returns:
        float: The validated threshold as a float.

    Raises:
        argparse.ArgumentTypeError: If the value is not a float, or not in the [0.0, 1.0] range.
    """
    try:
        fvalue = float(value)
    except ValueError as exc:
        message = f"Invalid threshold value: {value}"
        raise argparse.ArgumentTypeError(message) from exc

    if not 0.0 <= fvalue <= 1.0:
        message = "Threshold must be between 0.0 and 1.0"
        raise argparse.ArgumentTypeError(message)

    return fvalue
