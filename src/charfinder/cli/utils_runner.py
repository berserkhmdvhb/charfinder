"""Utilities for orchestrating the CharFinder CLI runner.

This module contains reusable utility functions used by the CLI main entry point
for tasks like resolving the final query string, managing environment flags,
and invoking the main search handler with diagnostics support.

Functions:
    resolve_final_query(): Determine the query string from CLI args.
    auto_enable_debug(): Enable debug if CHARFINDER_DEBUG_ENV_LOAD is set.
    handle_cli_workflow(): Execute main CLI logic and diagnostics.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import logging
import os
import sys
import traceback
from argparse import Namespace
from typing import TYPE_CHECKING

from charfinder.cli.diagnostics import print_debug_diagnostics
from charfinder.cli.handlers import (
    get_version,
    handle_find_chars,
)
from charfinder.config.constants import (
    EXIT_CANCELLED,
    EXIT_ERROR,
)
from charfinder.config.messages import (
    MSG_ERROR_EXCEPTION_DETAIL,
    MSG_ERROR_UNHANDLED_EXCEPTION,
    MSG_INFO_CLI_STARTED,
    MSG_INFO_ENVIRONMENT,
    MSG_INFO_QUERY_FINISHED,
    MSG_WARNING_INTERRUPTED,
    MSG_WARNING_PROD_ENV,
)
from charfinder.config.settings import (
    get_environment,
    get_fuzzy_hybrid_weights,
    is_prod,
    load_settings,
)
from charfinder.config.types import (
    FuzzyConfig,
    MatchResult,
)
from charfinder.utils.formatter import echo, should_use_color
from charfinder.utils.logger_setup import get_logger, setup_logging, teardown_logger
from charfinder.utils.logger_styles import (
    format_error,
    format_info,
    format_settings,
    format_success,
    format_warning,
)
from charfinder.validators import resolve_effective_color_mode, validate_fuzzy_hybrid_weights

if TYPE_CHECKING:
    from charfinder.config.types import MatchResult


__all__ = [
    "auto_enable_debug",
    "build_fuzzy_config_from_args",
    "handle_cli_workflow",
    "resolve_final_query",
]

# ---------------------------------------------------------------------
# Query Handling
# ---------------------------------------------------------------------


def resolve_final_query(args: Namespace) -> str:
    """
    Determine the final query string based on CLI arguments.

    Prefers --query/-q if provided; otherwise falls back to positional args.

    Args:
        args (Namespace): Parsed CLI arguments.

    Returns:
        str: The final joint query string to use.
    """
    query_list = args.option_query if args.option_query else args.positional_query
    return " ".join(query_list).strip()


# ---------------------------------------------------------------------
# Environment and Flags
# ---------------------------------------------------------------------


def auto_enable_debug(args: Namespace) -> None:
    """
    Enable debug mode if CHARFINDER_DEBUG_ENV_LOAD=1 is set in the environment.

    Modifies `args.debug` in-place if not already set.

    Args:
        args (Namespace): Parsed CLI arguments.
    """
    if os.getenv("CHARFINDER_DEBUG_ENV_LOAD") == "1" and not args.debug:
        args.debug = True


# ---------------------------------------------------------------------
# Main Execution Logic
# ---------------------------------------------------------------------


def build_fuzzy_config_from_args(args: Namespace) -> FuzzyConfig:
    weights = validate_fuzzy_hybrid_weights(get_fuzzy_hybrid_weights())
    return FuzzyConfig(
        fuzzy_algo=args.fuzzy_algo,
        fuzzy_match_mode=args.fuzzy_match_mode,
        hybrid_weights=weights,
    )


def handle_cli_workflow(args: Namespace, query_str: str, *, use_color: bool) -> int:
    """
    Perform the main CLI workflow, including logging setup, environment loading,
    diagnostics, and matching dispatch.

    Args:
        args (Namespace): Parsed CLI arguments.
        query_str (str): Final query string.
        use_color (bool): Whether color output should be used.

    Returns:
        int: Exit code (EXIT_SUCCESS, EXIT_CANCELLED, or EXIT_ERROR).
    """
    # Logging Setup
    setup_logging(reset=True, log_level=None, suppress_echo=True, use_color=use_color)

    # Load .env settings
    load_settings(verbose=args.verbose, debug=args.debug)

    # Resolve settings and color mode
    color_mode = resolve_effective_color_mode(args.color)
    use_color = should_use_color(color_mode)

    # Finalize logging
    log_level = logging.DEBUG if args.debug else None
    setup_logging(
        reset=True,
        log_level=log_level,
        suppress_echo=not (args.verbose or args.debug),
        use_color=use_color,
    )

    logger = get_logger()

    try:
        echo(
            msg=MSG_INFO_ENVIRONMENT.format(env=get_environment()),
            style=lambda m: format_settings(m, use_color=use_color),
            show=args.verbose,
            log=True,
            log_method="info",
        )

        if is_prod():
            echo(
                msg=MSG_WARNING_PROD_ENV,
                style=lambda m: format_warning(m, use_color=use_color),
                stream=sys.stderr,
                show=True,
                log=True,
                log_method="warning",
            )

        echo(
            msg=MSG_INFO_CLI_STARTED.format(version=get_version()),
            style=lambda m: format_info(m, use_color=use_color),
            show=args.verbose,
            log=True,
            log_method="info",
        )

        result: MatchResult = handle_find_chars(args, query_str)

        if args.debug:
            print_debug_diagnostics(
                args=args,
                match_info=result.match_info,
                use_color=use_color,
                show=True,
            )

        echo(
            msg=MSG_INFO_QUERY_FINISHED.format(query=query_str),
            style=lambda m: format_success(m, use_color=use_color),
            show=args.verbose,
            log=True,
            log_method="info",
        )

    except KeyboardInterrupt:
        echo(
            msg=MSG_WARNING_INTERRUPTED,
            style=lambda msg: format_warning(msg, use_color=use_color),
            stream=sys.stderr,
            show=True,
            log=True,
            log_method="warning",
        )
        return EXIT_CANCELLED

    except Exception as exc:  # noqa: BLE001
        echo(
            msg=MSG_ERROR_UNHANDLED_EXCEPTION,
            style=lambda msg: format_error(msg, use_color=use_color),
            stream=sys.stderr,
            show=True,
            log=True,
            log_method="exception",
        )
        echo(
            msg=MSG_ERROR_EXCEPTION_DETAIL.format(error=exc),
            style=lambda msg: format_error(msg, use_color=use_color),
            stream=sys.stderr,
            show=True,
            log=True,
            log_method="exception",
        )

        if args.debug:
            traceback.print_exc()

        return EXIT_ERROR

    else:
        return result.exit_code

    finally:
        teardown_logger(logger)
