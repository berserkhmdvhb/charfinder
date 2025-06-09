"""
Handlers for CLI output rendering and execution in CharFinder.

This module provides:

1. `should_use_color`: Determine whether color output should be used based on user settings.
2. `print_result_lines`: Print result lines to stdout, with consistent formatting.
3. `handle_find_chars`: Main CLI execution logic.
4. `get_version`: Retrieve installed package version.

This module delegates color formatting to `cli/formatter.py` and avoids using print().
"""

from __future__ import annotations

import json
import logging
import sys
from argparse import Namespace
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version

from charfinder.constants import (
    EXIT_CANCELLED,
    EXIT_INVALID_USAGE,
    EXIT_NO_RESULTS,
    EXIT_SUCCESS,
)
from charfinder.core.core_main import find_chars, find_chars_raw
from charfinder.utils.formatter import format_error, format_result_line, should_use_color

__all__ = [
    "get_version",
    "handle_find_chars",
    "print_result_lines",
    "should_use_color",
]

logger = logging.getLogger("charfinder")


@lru_cache(maxsize=1)
def get_version() -> str:
    """
    Retrieve the installed package version from importlib.metadata.

    Returns:
        str: The version string, or 'unknown' if not installed.
    """
    try:
        return version("charfinder")
    except PackageNotFoundError:
        return "unknown (not installed)"


def print_result_lines(lines: list[str], *, use_color: bool = False) -> None:
    """
    Print result lines to stdout, with consistent formatting.

    Args:
        lines (list[str]): The list of result lines to print.
        use_color (bool, optional): Whether to apply color formatting. Defaults to False.

    Returns:
        None
    """
    for line in lines:
        output = format_result_line(line, use_color=use_color)
        sys.stdout.write(output + "\n")


def handle_find_chars(args: Namespace) -> int:
    """
    Main CLI execution handler.

    Runs find_chars() or find_chars_raw() with the given args,
    prints results, and returns an appropriate exit code.

    Args:
        args (Namespace): Parsed CLI arguments.

    Returns:
        int: Exit code to be passed to sys.exit().
    """
    use_color = should_use_color(args.color)

    # Resolve query: prefer option_query over positional_query
    query_list = args.option_query if args.option_query else args.positional_query
    query_str = " ".join(query_list).strip()

    if not query_str:
        logger.error(format_error("Query must not be empty.", use_color=use_color))
        return EXIT_INVALID_USAGE

    try:
        if args.format == "json":
            # Structured output mode: use find_chars_raw()
            rows = find_chars_raw(
                query=query_str,
                fuzzy=args.fuzzy,
                threshold=args.threshold,
                verbose=args.verbose,
                fuzzy_algo=args.fuzzy_algo,
                fuzzy_match_mode=args.fuzzy_match_mode,
                exact_match_mode=args.exact_match_mode,
            )
            json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
            # In JSON mode, always return EXIT_SUCCESS (even if 0 results)
            return EXIT_SUCCESS

        # Text output mode → use find_chars() generator
        results = list(
            find_chars(
                query=query_str,
                fuzzy=args.fuzzy,
                threshold=args.threshold,
                verbose=args.verbose,
                use_color=use_color,
                fuzzy_algo=args.fuzzy_algo,
                fuzzy_match_mode=args.fuzzy_match_mode,
                exact_match_mode=args.exact_match_mode,
            )
        )

        if not results:
            return EXIT_NO_RESULTS

        print_result_lines(results, use_color=use_color)
        return EXIT_SUCCESS

    except KeyboardInterrupt:
        if args.verbose:
            logger.error(format_error("Search cancelled by user.", use_color=use_color))
        return EXIT_CANCELLED

    except Exception:
        message = "An unexpected error occurred during search."
        logger.error(format_error(message=message, use_color=use_color))
        logger.exception("Full exception details:")
        return EXIT_INVALID_USAGE
