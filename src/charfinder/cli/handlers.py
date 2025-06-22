"""Handlers for CLI output rendering and execution in CharFinder.

Delegates color formatting to `cli/formatter.py` and avoids using print().

Functions:
    get_version(): Retrieve installed package version.
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

from charfinder.config.constants import (
    EXIT_CANCELLED,
    EXIT_INVALID_USAGE,
    EXIT_NO_RESULTS,
    EXIT_SUCCESS,
)
from charfinder.config.messages import (
    MSG_ERROR_EMPTY_QUERY,
    MSG_ERROR_UNEXPECTED_EXCEPTION,
    MSG_ERROR_UNKNOWN_VERSION,
    MSG_INFO_SEARCH_CANCELLED,
)
from charfinder.config.types import MatchDiagnosticsInfo, MatchResult
from charfinder.core.core_main import find_chars_raw, find_chars_with_info
from charfinder.utils.formatter import (
    display_result_lines,
    echo,
    format_all_results,
    log_optionally_echo,
)
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_error, format_warning
from charfinder.validators import (
    resolve_cli_settings,
    validate_exact_match_mode,
    validate_fuzzy_match_mode,
    validate_output_format,
)

__all__ = [
    "get_version",
    "handle_find_chars",
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
    agg_fn: str | None
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
        return MSG_ERROR_UNKNOWN_VERSION


# ---------------------------------------------------------------------
# Main CLI Execution
# ---------------------------------------------------------------------


def handle_find_chars(args: Namespace, query_str: str) -> MatchResult:
    """
    Main CLI execution handler for CharFinder.

    This function validates and resolves the necessary parameters, including fuzzy and exact match
    modes, color settings, and threshold, then dispatches the query to the appropriate core search
    function based on the selected output format.

    Args:
        args (Namespace): Parsed CLI arguments from argparse.
        query_str (str): The normalized query string to search for.

    Returns:
        MatchResult: An object containing the CLI exit code and optional match diagnostics.
    """
    try:
        color_mode, use_color, threshold = resolve_cli_settings(args)

        # Validate match modes (explicitly CLI-sourced)
        fuzzy_mode = validate_fuzzy_match_mode(args.fuzzy_match_mode)
        exact_mode = validate_exact_match_mode(args.exact_match_mode)

        if not query_str:
            return handle_empty_query(use_color=use_color)

        params = SearchParams(
            query=query_str,
            fuzzy=args.fuzzy,
            fuzzy_algo=args.fuzzy_algo,
            fuzzy_match_mode=fuzzy_mode,
            exact_match_mode=exact_mode,
            agg_fn=args.hybrid_agg_fn,
            prefer_fuzzy=args.prefer_fuzzy,
            verbose=args.verbose,
            use_color=use_color,
            threshold=threshold,
        )

        return _run_query_and_return(params, output_format=args.format, args=args)

    except KeyboardInterrupt:
        return handle_keyboard_interrupt(verbose=args.verbose, use_color=use_color)

    except Exception as exc:
        if isinstance(exc, (SystemExit, KeyboardInterrupt, GeneratorExit)):
            raise
        log_optionally_echo(
            msg=MSG_ERROR_UNEXPECTED_EXCEPTION.format(error=exc),
            level="error",
            show=True,
            style=lambda m: format_error(
                message=m, use_color=args.use_color if hasattr(args, "use_color") else False
            ),
        )
        return MatchResult(exit_code=EXIT_INVALID_USAGE, match_info=None)


def _run_query_and_return(
    params: SearchParams,
    *,
    output_format: str,
    args: Namespace,
) -> MatchResult:
    """
    Run the character search query and dispatch the results using the appropriate output format.

    Args:
        params (SearchParams): Structured parameters for running the query.
        output_format (str): The desired output format ("json" or "text").
        args (Namespace): CLI arguments, used to construct diagnostic information.

    Returns:
        MatchResult: Structured CLI result with exit code and optional diagnostics.
    """

    validated_format = validate_output_format(output_format)

    if validated_format == "json":
        rows = find_chars_raw(**params.__dict__)
        sys.stdout.write(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
        sys.stdout.flush()
        return build_match_result(args, fuzzy_used=params.fuzzy, exit_code=EXIT_SUCCESS)

    matches, fuzzy_used = find_chars_with_info(**params.__dict__)
    if not matches:
        return MatchResult(exit_code=EXIT_NO_RESULTS, match_info=None)

    formatted_lines = format_all_results(
        matches,
        use_color=params.use_color,
        show_score=args.show_score,
    )
    display_result_lines(formatted_lines, use_color=params.use_color)
    return build_match_result(args, fuzzy_used=fuzzy_used, exit_code=EXIT_SUCCESS)


def handle_empty_query(*, use_color: bool) -> MatchResult:
    """
    Handle the case when the user provides an empty query.

    Args:
        use_color (bool): Whether to use colored formatting.

    Returns:
        MatchResult: Exit code and no diagnostic info.
    """
    echo(
        MSG_ERROR_EMPTY_QUERY,
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
        echo(
            MSG_INFO_SEARCH_CANCELLED,
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
