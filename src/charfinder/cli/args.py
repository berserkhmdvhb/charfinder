"""Argument names for CharFinder CLI.

Defines:

- CLI argument names used across the CLI components (parser, handlers).
- Argument validation is handled in `validators.py`, ensuring input consistency.

Used by:
    cli_main.py, parser.py

Constants:
    ARG_QUERY, ARG_THRESHOLD, ARG_COLOR, ARG_EXACT_MATCH_MODE, ARG_FUZZY_MATCH_MODE,
    ARG_HYBRID_AGG_FN, ARG_VERBOSE, ARG_DEBUG, ARG_FORMAT, ARG_VERSION,
    ARG_NORMALIZATION_PROFILE
"""

__all__ = [
    "ARG_COLOR",
    "ARG_DEBUG",
    "ARG_EXACT_MATCH_MODE",
    "ARG_FORMAT",
    "ARG_FUZZY",
    "ARG_FUZZY_ALGO",
    "ARG_FUZZY_MATCH_MODE",
    "ARG_HYBRID_AGG_FN",
    "ARG_NORMALIZATION_PROFILE",
    "ARG_POSITIONAL_QUERY",
    "ARG_PREFER_FUZZY",
    "ARG_QUERY",
    "ARG_QUERY_LONG",
    "ARG_SHOW_SCORE",
    "ARG_THRESHOLD",
    "ARG_VERBOSE",
    "ARG_VERBOSE_LONG",
    "ARG_VERSION",
]

# ---------------------------------------------------------------------
# Argument Names
# ---------------------------------------------------------------------

# Positional Arguments
ARG_POSITIONAL_QUERY = "positional_query"  # for query input as positional

# Optional Arguments (with short and long versions)
ARG_QUERY = "-q"
ARG_QUERY_LONG = "--query"

ARG_VERBOSE = "-v"
ARG_VERBOSE_LONG = "--verbose"

ARG_DEBUG = "--debug"

# Core Options
ARG_FUZZY = "--fuzzy"
ARG_PREFER_FUZZY = "--prefer-fuzzy"
ARG_THRESHOLD = "--threshold"
ARG_COLOR = "--color"

# Matching Options
ARG_EXACT_MATCH_MODE = "exact_match-mode"
ARG_FUZZY_MATCH_MODE = "fuzzy-match-mode"
ARG_FUZZY_ALGO = "--fuzzy-algo"
ARG_HYBRID_AGG_FN = "--hybrid-agg-fn"

# Normalization
ARG_NORMALIZATION_PROFILE = "--normalization-profile"

# Output Options
ARG_FORMAT = "--format"
ARG_SHOW_SCORE = "--show-score"

# Miscellaneous
ARG_VERSION = "--version"
