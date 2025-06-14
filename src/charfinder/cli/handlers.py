"""Handlers for CLI output rendering and execution in CharFinder.

Delegates color formatting to `cli/formatter.py` and avoids using print().

Functions:
    resolve_effective_threshold(): Resolve threshold from CLI arg, env var, or default.
    resolve_effective_color_mode(): Resolve color mode from CLI arg, env var, or default.
    apply_fuzzy_defaults(): Apply default fuzzy match behavior if not explicitly set.
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
from typing import Any

from charfinder.cli.args import threshold_range
from charfinder.constants import (
    DEFAULT_COLOR_MODE,
    DEFAULT_THRESHOLD,
    EXIT_CANCELLED,
    EXIT_INVALID_USAGE,
    EXIT_NO_RESULTS,
    EXIT_SUCCESS,
)
from charfinder.core.core_main import find_chars_raw, find_chars_with_info
from charfinder.utils.formatter import echo, format_result_line, should_use_color
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_error, format_warning

__all__ = [
    "apply_fuzzy_defaults",
    "get_version",
    "handle_find_chars",
    "print_result_lines",
    "resolve_effective_color_mode",
    "resolve_effective_threshold",
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


def apply_fuzzy_defaults(args: Namespace) -> None:
    """Apply default fuzzy match algorithm and mode if --fuzzy is set.

    If the user enables --fuzzy but does not specify --fuzzy-algo or --fuzzy-match-mode,
    this function injects safe and useful defaults:
        fuzzy_algo: "token_sort_ratio"
        fuzzy_match_mode: "hybrid"

    Args:
        args (Namespace): Parsed CLI arguments.
    """
    if args.fuzzy:
        if not getattr(args, "fuzzy_algo", None):
            args.fuzzy_algo = "token_sort_ratio"
        if not getattr(args, "fuzzy_match_mode", None):
            args.fuzzy_match_mode = "hybrid"


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


def handle_find_chars(args: Namespace, query_str: str) -> tuple[int, dict[str, Any] | None]:
    """
    Main CLI execution handler.

    Runs find_chars_with_info() or find_chars_raw() with the given args and query string,
    prints results, and returns an appropriate exit code and match diagnostics.

    Args:
        args (Namespace): Parsed CLI arguments.
        query_str (str): Query string to search for.

    Returns:
        tuple[int, dict[str, Any] | None]: Exit code and match info for diagnostics.
    """
    color_mode = resolve_effective_color_mode(args.color)
    use_color = should_use_color(color_mode)
    threshold = resolve_effective_threshold(args.threshold, use_color=use_color)

    if not query_str:
        message = "Query must not be empty."
        echo(
            message,
            style=lambda m: format_error(m, use_color=use_color),
            show=True,
            log=False,
            log_method="error",
        )
        return EXIT_INVALID_USAGE, None

    try:
        match_info = {
            "fuzzy": args.fuzzy,
            "fuzzy_algo": args.fuzzy_algo,
            "fuzzy_match_mode": args.fuzzy_match_mode,
            "exact_match_mode": args.exact_match_mode,
            "hybrid_agg_fn": args.hybrid_agg_fn,
            "prefer_fuzzy": args.prefer_fuzzy,
        }

        if args.format == "json":
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
            return EXIT_SUCCESS, match_info

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

        match_info["fuzzy_was_used"] = fuzzy_used

        if not results:
            return EXIT_NO_RESULTS, match_info

        print_result_lines(results, use_color=use_color)
        return EXIT_SUCCESS, match_info

    except KeyboardInterrupt:
        if args.verbose:
            message = "Search cancelled by user."
            echo(
                message,
                style=lambda m: format_error(m, use_color=use_color),
                show=True,
                log=False,
                log_method="warning",
            )
        return EXIT_CANCELLED, None
