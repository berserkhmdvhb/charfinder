"""Handlers for CLI output rendering and execution in CharFinder.

Delegates color formatting to `cli/formatter.py` and avoids using print().

Functions:
    resolve_effective_threshold(): Resolve threshold from CLI arg, env var, or default.
    resolve_effective_color_mode(): Resolve color mode from CLI arg, env var, or default.
    get_version(): Retrieve installed package version.
    print_result_lines(): Print result lines to stdout.
    handle_find_chars(): Main CLI execution logic.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from __future__ import annotations

import json
import os
import sys
from argparse import ArgumentTypeError, Namespace
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version

from charfinder.cli.args import threshold_range
from charfinder.constants import (
    DEFAULT_COLOR_MODE,
    DEFAULT_THRESHOLD,
    EXIT_CANCELLED,
    EXIT_INVALID_USAGE,
    EXIT_NO_RESULTS,
    EXIT_SUCCESS,
)
from charfinder.core.core_main import find_chars, find_chars_raw
from charfinder.utils.formatter import echo, format_result_line, should_use_color
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_error, format_warning

__all__ = [
    "get_version",
    "handle_find_chars",
    "print_result_lines",
    "resolve_effective_color_mode",
    "resolve_effective_threshold",
    "should_use_color",
]

logger = get_logger()

# ---------------------------------------------------------------------
# Argument Resolution Helpers
# ---------------------------------------------------------------------


def resolve_effective_threshold(cli_threshold: float | None, *, use_color: bool = True) -> float:
    """Resolve threshold from CLI arg, env var, or default.

    Priority:
        1. CLI argument (--threshold)
        2. Environment variable CHARFINDER_MATCH_THRESHOLD
        3. DEFAULT_THRESHOLD

    Args:
        cli_threshold (float | None): Threshold value from CLI argument, or None.
        use_color (bool): Whether to apply ANSI formatting when logging warnings.

    Returns:
        float: The resolved threshold value.
    """

    if cli_threshold is not None:
        return cli_threshold

    env_value = os.getenv("CHARFINDER_MATCH_THRESHOLD")
    if env_value is not None:
        try:
            # Reuse your existing CLI validator for consistency
            return threshold_range(env_value)
        except ArgumentTypeError:
            message = (
                f"Invalid CHARFINDER_MATCH_THRESHOLD env var: {env_value!r} — "
                f"using default {DEFAULT_THRESHOLD}"
            )
            echo(
                message,
                style=lambda m: format_warning(m, use_color=use_color),
                show=True,
                log=True,
                log_method="warning",
                stream=sys.stderr,
            )
    return DEFAULT_THRESHOLD


def resolve_effective_color_mode(cli_color_mode: str | None) -> str:
    """Resolve color mode from CLI arg, env var, or default.

    Priority:
        1. CLI argument (--color)
        2. Environment variable CHARFINDER_COLOR_MODE
        3. DEFAULT_COLOR_MODE

    Args:
        cli_color_mode (str | None): Color mode from CLI argument, or None.

    Returns:
        str: The resolved color mode ("auto", "always", or "never").
    """

    if cli_color_mode is not None:
        return cli_color_mode

    env_value = os.getenv("CHARFINDER_COLOR_MODE")
    if env_value in {"auto", "always", "never"}:
        return env_value

    return DEFAULT_COLOR_MODE


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

    Returns:
        None
    """
    for line in lines:
        output = format_result_line(line, use_color=use_color)
        sys.stdout.write(output + "\n")


# ---------------------------------------------------------------------
# Main CLI Execution
# ---------------------------------------------------------------------


def handle_find_chars(args: Namespace) -> int:
    """
    Main CLI execution handler.

    Runs find_chars() or find_chars_raw() with the given args,
    prints results, and returns an appropriate exit code.

    Args:
        args (Namespace): Parsed CLI arguments.

    Returns:
        int: Exit code to be passed to sys.exit().

    Raises:
        KeyboardInterrupt: If the user interrupts execution.
        Exception: For unexpected errors (logged and handled internally).
    """
    color_mode = resolve_effective_color_mode(args.color)
    use_color = should_use_color(color_mode)
    threshold = resolve_effective_threshold(args.threshold, use_color=use_color)

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
                threshold=threshold,
                verbose=args.verbose,
                use_color=use_color,
                fuzzy_algo=args.fuzzy_algo,
                fuzzy_match_mode=args.fuzzy_match_mode,
                exact_match_mode=args.exact_match_mode,
                agg_fn=args.hybrid_agg_fn,
            )
            json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
            sys.stdout.flush()
            # In JSON mode, always return EXIT_SUCCESS (even if 0 results)
            return EXIT_SUCCESS

        # Text output mode => use find_chars() generator
        results = list(
            find_chars(
                query=query_str,
                fuzzy=args.fuzzy,
                threshold=threshold,
                verbose=args.verbose,
                use_color=use_color,
                fuzzy_algo=args.fuzzy_algo,
                fuzzy_match_mode=args.fuzzy_match_mode,
                exact_match_mode=args.exact_match_mode,
                agg_fn=args.hybrid_agg_fn,
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
