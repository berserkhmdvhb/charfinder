"""
CLI argument parser definition for CharFinder.

This module defines the main ArgumentParser used by the CLI.

Responsibilities:
- Define CLI arguments and options.
- Attach custom validators (e.g. threshold_range).
- Provide choices for color output.
- Provide output format, json or text.
- Attach --version.
- Enable argcomplete tab completion.

Used by:
- cli_main.py to parse CLI arguments.

This module exposes:
- create_parser(): Returns the configured ArgumentParser instance.
"""

__all__ = ["create_parser"]

import argparse

from charfinder.cli.args import (
    ARG_COLOR,
    ARG_EXACT_MATCH_MODE,
    ARG_FORMAT,
    ARG_FUZZY_MATCH_MODE,
    ARG_THRESHOLD,
    DEFAULT_EXACT_MATCH_MODE,
    DEFAULT_FUZZY_ALGO,
    DEFAULT_FUZZY_MATCH_MODE,
    VALID_EXACT_MATCH_MODES,
    VALID_FUZZY_ALGOS,
    VALID_FUZZY_MATCH_MODES,
    threshold_range,
)
from charfinder.cli.handlers import get_version


def create_parser() -> argparse.ArgumentParser:
    """
    Build and return the CLI ArgumentParser.

    Defines the following arguments:
    - query: The search query string (required positional).
    - --fuzzy: Enable fuzzy search if no exact matches.
    - --threshold: Fuzzy match threshold (float between 0.0 and 1.0).
    - --color: Color output mode ('auto', 'always', 'never').
    - --verbose: Enable console output.
    - --debug: Enable debug diagnostics output.
    - --fuzzy-algo: Fuzzy algorithm to use.
    - --fuzzy-match-mode: Fuzzy match mode.
    - --exact-match-mode: Exact match strategy (substring or word-subset).
    - --format: Output format (text or json).
    - --version: Show version and exit.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Find Unicode characters by name using substring or fuzzy search.",
        epilog="""Examples:
            charfinder heart
            charfinder heart --verbose
            charfinder heart --fuzzy --threshold 0.6
            charfinder heart --debug
            CHARFINDER_DEBUG_ENV_LOAD=1 charfinder heart
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # ---------------------------------------------------------------------
    # Positional Arguments
    # ---------------------------------------------------------------------

    parser.add_argument(
        "positional_query",
        nargs="*",
        help="Search query for Unicode characters (positional).",
    )

    # Optional query
    parser.add_argument(
        "-q",
        "--query",
        dest="option_query",
        nargs="+",
        help="Search query for Unicode characters (alternative to positional).",
    )

    # ---------------------------------------------------------------------
    # Core Options
    # ---------------------------------------------------------------------

    parser.add_argument(
        "--fuzzy",
        action="store_true",
        help="Enable fuzzy search if no exact matches.",
    )

    parser.add_argument(
        ARG_THRESHOLD,
        type=threshold_range,
        default=None,
        help="Fuzzy match threshold (0.0 to 1.0).",
    )

    parser.add_argument(
        ARG_COLOR,
        choices=["auto", "always", "never"],
        default=None,
        help="Control color output.",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        dest="verbose",
        action="store_true",
        default=False,
        help="Enable console output (stdout/stderr). Default is off.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug diagnostics output.",
    )

    # ---------------------------------------------------------------------
    # Matching Options
    # ---------------------------------------------------------------------

    parser.add_argument(
        f"--{ARG_EXACT_MATCH_MODE.replace('_', '-')}",
        choices=VALID_EXACT_MATCH_MODES,
        default=DEFAULT_EXACT_MATCH_MODE,
        help=(
            "How to perform exact matching when --fuzzy is not enabled. "
            "substring: Match query string as a substring of the character name. "
            "word-subset (default): Match if all words in the query appear "
            "in the character name order-independent."
        ),
    )

    parser.add_argument(
        "--fuzzy-algo",
        choices=VALID_FUZZY_ALGOS,
        default=DEFAULT_FUZZY_ALGO,
        help="Fuzzy matching algorithm to use.",
    )

    parser.add_argument(
        f"--{ARG_FUZZY_MATCH_MODE.replace('_', '-')}",
        choices=VALID_FUZZY_MATCH_MODES,
        default=DEFAULT_FUZZY_MATCH_MODE,
        help="Fuzzy match mode when --fuzzy is enabled.",
    )

    parser.add_argument(
        "--hybrid-agg-fn",
        choices=["mean", "median", "max", "min"],
        default="mean",
        help="Aggregation function for hybrid match mode (default: mean).",
    )
    # ---------------------------------------------------------------------
    # Output Options
    # ---------------------------------------------------------------------

    parser.add_argument(
        ARG_FORMAT,
        choices=["text", "json"],
        default="text",
        help=(
            "Output format: "
            "'text' for human-friendly table (default), 'json' for structured output."
        ),
    )

    # Enable argcomplete
    try:
        import argcomplete

        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    # ---------------------------------------------------------------------
    # Version Option
    # ---------------------------------------------------------------------

    parser.add_argument(
        "--version",
        action="version",
        version=get_version(),
    )

    return parser
