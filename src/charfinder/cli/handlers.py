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
from dataclasses import dataclass
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version

from charfinder.constants import (
    EXIT_CANCELLED,
    EXIT_INVALID_USAGE,
    EXIT_NO_RESULTS,
    EXIT_SUCCESS,
)
from charfinder.core.core_main import find_chars_raw, find_chars_with_info
from charfinder.types import MatchDiagnosticsInfo, MatchResult
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
# Dataclasses
# ---------------------------------------------------------------------


@dataclass
class SearchParams:
    query: str
    fuzzy: bool
    fuzzy_algo: str
    fuzzy_match_mode: str
    exact_match_mode: str
    hybrid_agg_fn: str | None
    prefer_fuzzy: bool
    verbose: bool
    use_color: bool
    threshold: float


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


def handle_find_chars(args: Namespace, query_str: str) -> MatchResult:
    """
    Main CLI execution handler.

    Runs find_chars_with_info() or find_chars_raw() with the given args and query string,
    prints results, and returns an appropriate exit code and match diagnostics.

    Args:
        args (Namespace): Parsed CLI arguments.
        query_str (str): Query string to search for.

    Returns:
        MatchResult: Exit code and diagnostics for the CLI run.
    """
    try:
        color_mode, use_color, threshold = resolve_settings(args)

        args.fuzzy_algo = validate_fuzzy_algo(args.fuzzy_algo)
        args.fuzzy_match_mode = validate_fuzzy_match_mode(args.fuzzy_match_mode)
        args.exact_match_mode = validate_exact_match_mode(args.exact_match_mode)

        if not query_str:
            return handle_empty_query(use_color=use_color)

        params = SearchParams(
            query=query_str,
            fuzzy=args.fuzzy,
            fuzzy_algo=args.fuzzy_algo,
            fuzzy_match_mode=args.fuzzy_match_mode,
            exact_match_mode=args.exact_match_mode,
            hybrid_agg_fn=args.hybrid_agg_fn,
            prefer_fuzzy=args.prefer_fuzzy,
            verbose=args.verbose,
            use_color=use_color,
            threshold=threshold,
        )

        return _run_query_and_return(params, output_format=args.format, args=args)

    except KeyboardInterrupt:
        return handle_keyboard_interrupt(verbose=args.verbose, use_color=use_color)


def _run_query_and_return(
    params: SearchParams,
    *,
    output_format: str,
    args: Namespace,
) -> MatchResult:
    """
    Internal helper to run the appropriate query and return structured output.

    Args:
        params (SearchParams): All resolved parameters for search execution.
        output_format (str): Either "json" or "text".
        args (Namespace): CLI args for additional context (e.g., for diagnostics).

    Returns:
        MatchResult: Exit code and diagnostics info.
    """
    if output_format == "json":
        rows = find_chars_raw(**params.__dict__)
        sys.stdout.write(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
        sys.stdout.flush()
        return build_match_result(args, fuzzy_used=params.fuzzy, exit_code=EXIT_SUCCESS)

    results, fuzzy_used = find_chars_with_info(**params.__dict__)
    if not results:
        return MatchResult(exit_code=EXIT_NO_RESULTS, match_info=None)
    print_result_lines(results, use_color=params.use_color)
    return build_match_result(args, fuzzy_used=fuzzy_used, exit_code=EXIT_SUCCESS)


def resolve_settings(args: Namespace) -> tuple[str, bool, float]:
    """
    Resolve runtime settings such as color mode and match threshold.

    Args:
        args (Namespace): Parsed command-line arguments.

    Returns:
        tuple[str, bool, float]: Effective (color_mode, use_color, threshold)
    """
    color_mode = resolve_effective_color_mode(args.color)
    use_color = should_use_color(color_mode)
    threshold = resolve_effective_threshold(args.threshold, use_color=use_color)
    return color_mode, use_color, threshold


def handle_empty_query(*, use_color: bool) -> MatchResult:
    """
    Handle the case when the user provides an empty query.

    Args:
        use_color (bool): Whether to use colored formatting.

    Returns:
        MatchResult: Exit code and no diagnostic info.
    """
    message = "Query must not be empty."
    echo(
        message,
        style=lambda m: format_error(m, use_color=use_color),
        show=True,
        log=False,
        log_method="error",
    )
    return MatchResult(exit_code=EXIT_INVALID_USAGE, match_info=None)


def handle_keyboard_interrupt(*, verbose: bool, use_color: bool) -> MatchResult:
    """
    Handle a KeyboardInterrupt during CLI execution (e.g., Ctrl+C).

    Args:
        verbose (bool): Whether to show cancellation message.
        use_color (bool): Whether to apply colored formatting.

    Returns:
        MatchResult: Exit code indicating cancellation and no diagnostics.
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
    return MatchResult(exit_code=EXIT_CANCELLED, match_info=None)


def build_match_result(args: Namespace, *, fuzzy_used: bool, exit_code: int) -> MatchResult:
    """
    Build a MatchResult with structured diagnostics.

    Args:
        args (Namespace): CLI arguments with match settings.
        fuzzy_used (bool): Whether fuzzy matching was executed.
        exit_code (int): Exit code of the operation.

    Returns:
        MatchResult: Structured result including exit code and optional diagnostics.
    """
    match_info = MatchDiagnosticsInfo(
        fuzzy=args.fuzzy,
        fuzzy_was_used=fuzzy_used,
        fuzzy_algo=args.fuzzy_algo,
        fuzzy_match_mode=args.fuzzy_match_mode,
        hybrid_agg_fn=args.hybrid_agg_fn if args.fuzzy_match_mode == "hybrid" else None,
        prefer_fuzzy=args.prefer_fuzzy,
        exact_match_mode=args.exact_match_mode,
        threshold=args.threshold,
    )
    return MatchResult(exit_code=exit_code, match_info=match_info)
