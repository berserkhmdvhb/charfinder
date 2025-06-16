"""
Handlers for CLI output rendering and execution in CharFinder.

Delegates color formatting to `cli/formatter.py` and avoids using print().

Functions:
    get_version(): Retrieve installed package version.
    print_result_lines(): Print result lines to stdout.
    handle_find_chars(): Main CLI execution logic.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import json
import sys
from argparse import Namespace
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from charfinder.constants import (
    EXIT_CANCELLED,
    EXIT_INVALID_USAGE,
    EXIT_NO_RESULTS,
    EXIT_SUCCESS,
)
from charfinder.core.core_main import find_chars_raw, find_chars_with_info
from charfinder.types import CLIResult
from charfinder.utils.formatter import echo, format_result_line, should_use_color
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_error, format_warning
from charfinder.validators import (
    resolve_effective_color_mode,
    resolve_effective_threshold,
    validate_exact_match_mode,
    validate_fuzzy_algo,
    validate_fuzzy_match_mode,
)

__all__ = [
    "get_version",
    "handle_find_chars",
    "print_result_lines",
]

logger = get_logger()

# ---------------------------------------------------------------------
# Metadata Helpers
# ---------------------------------------------------------------------


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


# ---------------------------------------------------------------------
# Output Helpers
# ---------------------------------------------------------------------


def print_result_lines(lines: list[str], *, use_color: bool = False) -> None:
    """
    Print result lines to stdout, with consistent formatting.

    Args:
        lines (list[str]): The list of result lines to print.
        use_color (bool, optional): Whether to apply color formatting. Defaults to False.
    """
    for line in lines:
        output = format_result_line(line, use_color=use_color)
        sys.stdout.write(output + "\n")


# ---------------------------------------------------------------------
# Main CLI Execution
# ---------------------------------------------------------------------


def handle_find_chars(args: Namespace, query_str: str) -> CLIResult:
    """
    Main CLI execution handler.

    Runs find_chars_with_info() or find_chars_raw() with the given args and query string,
    prints results, and returns an appropriate exit code and match diagnostics.

    Args:
        args (Namespace): Parsed CLI arguments.
        query_str (str): Query string to search for.

    Returns:
        CLIResult: Exit code and match info for diagnostics.
    """
    try:
        # Validate and resolve settings
        color_mode, use_color, threshold = resolve_settings(args)

        # Validate fuzzy algorithm and modes using validators
        args.fuzzy_algo = validate_fuzzy_algo(args.fuzzy_algo)
        args.fuzzy_match_mode = validate_fuzzy_match_mode(args.fuzzy_match_mode)
        args.exact_match_mode = validate_exact_match_mode(args.exact_match_mode)

        # Check for an empty query
        if not query_str:
            return handle_empty_query(use_color=use_color)

        # Handle the search logic based on output format
        if args.format == "json":
            return handle_output_json(query_str, args, use_color=use_color, threshold=threshold)

        # Handle the main fuzzy search and output
        return handle_output_text(query_str, args, use_color=use_color, threshold=threshold)

    except KeyboardInterrupt:
        return handle_keyboard_interrupt(verbose=args.verbose, use_color=use_color)


def resolve_settings(args: Namespace) -> tuple[str, bool, float]:
    """
    Resolve runtime settings such as color mode and match threshold.

    This function computes:
    - The effective color mode from CLI arguments and environment.
    - Whether to use colored output.
    - The threshold to use for fuzzy matching.

    Args:
        args (Namespace): Parsed command-line arguments.

    Returns:
        tuple[str, bool, float]: A tuple containing:
            - color_mode (str): Effective color mode.
            - use_color (bool): Whether to use colored output.
            - threshold (float): Effective fuzzy match threshold.
    """
    color_mode = resolve_effective_color_mode(args.color)
    use_color = should_use_color(color_mode)
    threshold = resolve_effective_threshold(args.threshold, use_color=use_color)
    return color_mode, use_color, threshold


def handle_empty_query(*, use_color: bool) -> tuple[int, None]:
    """
    Handle the case when the user provides an empty query.

    Args:
        use_color (bool): Whether to use colored formatting.

    Returns:
        tuple[int, None]: An exit code indicating invalid usage, and no diagnostic info.
    """
    message = "Query must not be empty."
    echo(
        message,
        style=lambda m: format_error(m, use_color=use_color),
        show=True,
        log=False,
        log_method="error",
    )
    return EXIT_INVALID_USAGE, None


def handle_output_json(
    query_str: str,
    args: Namespace,
    *,
    use_color: bool,
    threshold: float,
) -> tuple[int, dict[str, Any]]:
    """
    Handle the JSON output mode by invoking the raw search function and printing as JSON.

    Args:
        query_str (str): The search query string.
        args (Namespace): Parsed CLI arguments.
        use_color (bool): Whether to apply colored formatting (has no effect on JSON).
        threshold (float): Fuzzy matching threshold.

    Returns:
        tuple[int, dict[str, Any]]: Exit code and match diagnostics dictionary.
    """
    rows = find_chars_raw(
        query=query_str,
        fuzzy=args.fuzzy,
        threshold=threshold,
        verbose=args.verbose,
        use_color=use_color,
        fuzzy_algo=args.fuzzy_algo,
        fuzzy_match_mode=args.fuzzy_match_mode,
        exact_match_mode=args.exact_match_mode,
        agg_fn=args.hybrid_agg_fn,
        prefer_fuzzy=args.prefer_fuzzy,
    )

    message = json.dumps(rows, ensure_ascii=False, indent=2)
    sys.stdout.write(message + "\n")
    sys.stdout.flush()
    return EXIT_SUCCESS, {"fuzzy": args.fuzzy, "fuzzy_algo": args.fuzzy_algo}


def handle_output_text(
    query_str: str,
    args: Namespace,
    *,
    use_color: bool,
    threshold: float,
) -> CLIResult:
    """
    Handle the text output mode: run search, format, and print to console.

    Args:
        query_str (str): The search query string.
        args (Namespace): Parsed CLI arguments.
        use_color (bool): Whether to use colored output.
        threshold (float): Fuzzy matching threshold.

    Returns:
        tuple[int, dict[str, Any]]: Exit code and match diagnostics dictionary.
    """
    results, fuzzy_used = find_chars_with_info(
        query=query_str,
        fuzzy=args.fuzzy,
        threshold=threshold,
        verbose=args.verbose,
        use_color=use_color,
        fuzzy_algo=args.fuzzy_algo,
        fuzzy_match_mode=args.fuzzy_match_mode,
        exact_match_mode=args.exact_match_mode,
        agg_fn=args.hybrid_agg_fn,
        prefer_fuzzy=args.prefer_fuzzy,
    )

    if not results:
        return EXIT_NO_RESULTS, None

    print_result_lines(results, use_color=use_color)
    return EXIT_SUCCESS, {"fuzzy_was_used": fuzzy_used}


def handle_keyboard_interrupt(*, verbose: bool, use_color: bool) -> tuple[int, None]:
    """
    Handle a KeyboardInterrupt during CLI execution (e.g., Ctrl+C).

    Args:
        verbose (bool): Whether to show cancellation message.
        use_color (bool): Whether to apply colored formatting.

    Returns:
        tuple[int, None]: Exit code indicating user cancelled, and no diagnostics.
    """
    if verbose:
        message = "Search cancelled by user."
        echo(
            message,
            style=lambda m: format_warning(m, use_color=use_color),
            show=True,
            log=False,
            log_method="warning",
        )
    return EXIT_CANCELLED, None
