"""Utilities for orchestrating the CharFinder CLI runner.

This module contains reusable utility functions used by the CLI main entry point
to organize logic such as:

- Determining the final query string (from positional or optional args).
- Managing environment variables and debug mode.
- Validating and normalizing fuzzy algorithm input.
- Displaying diagnostic banners and settings-related info.
- Executing the main character matching handler.
- Handling CLI completion, success, and exception exits.

All functions are used by `cli_main.py` to modularize and streamline execution.

Functions:
    resolve_final_query(): Determine the query string from CLI args.
    auto_enable_debug(): Enable debug if CHARFINDER_DEBUG_ENV_LOAD is set.
    validate_and_resolve_fuzzy_algo(): Normalize and validate fuzzy algorithm.
    handle_cli_workflow(): Execute main CLI logic and handler.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import logging
import os
import sys
import traceback
from argparse import Namespace

from charfinder.cli.diagnostics import print_debug_diagnostics
from charfinder.cli.handlers import (
    get_version,
    handle_find_chars,
    resolve_effective_color_mode,
)
from charfinder.constants import EXIT_CANCELLED, EXIT_ERROR
from charfinder.fuzzymatchlib import resolve_algorithm_name
from charfinder.settings import get_environment, is_prod, load_settings
from charfinder.utils.formatter import echo, should_use_color
from charfinder.utils.logger_setup import get_logger, setup_logging, teardown_logger
from charfinder.utils.logger_styles import (
    format_error,
    format_info,
    format_settings,
    format_warning,
)

__all__ = [
    "auto_enable_debug",
    "handle_cli_workflow",
    "resolve_final_query",
    "validate_and_resolve_fuzzy_algo",
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
        str: The final normalized query string to use.
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


def validate_and_resolve_fuzzy_algo(args: Namespace, *, use_color: bool) -> None:
    """
    Normalize and validate the fuzzy algorithm argument if provided.

    Args:
        args (Namespace): Parsed CLI arguments.
        use_color (bool): Whether to use color in error messages.

    Raises:
        SystemExit: If the algorithm is invalid, with appropriate error message.
    """
    if args.fuzzy_algo:
        try:
            args.fuzzy_algo = resolve_algorithm_name(args.fuzzy_algo)
        except ValueError as exc:
            echo(
                f"Invalid --fuzzy-algo: {exc}",
                style=lambda msg: format_error(msg, use_color=use_color),
                stream=sys.stderr,
                show=True,
                log=True,
                log_method="error",
            )
            sys.exit(EXIT_ERROR)


# ---------------------------------------------------------------------
# Main Execution Logic
# ---------------------------------------------------------------------


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

    # Recompute color mode (after .env)
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
            f"Using environment: {get_environment()}",
            style=lambda m: format_settings(m, use_color=use_color),
            show=args.verbose,
            log=True,
            log_method="info",
        )

        if is_prod():
            echo(
                "You are running in PROD environment!",
                style=lambda m: format_warning(m, use_color=use_color),
                stream=sys.stderr,
                show=True,
                log=True,
                log_method="warning",
            )

        echo(
            f"CharFinder {get_version()} CLI started",
            style=lambda m: format_info(m, use_color=use_color),
            show=args.verbose,
            log=True,
            log_method="info",
        )

        # === STEP 4: Dispatch to character search
        exit_code, match_info = handle_find_chars(args, query_str)

        # === STEP 5: Print diagnostics if --debug is enabled
        if args.debug:
            print_debug_diagnostics(
                args=args,
                match_info=match_info,
                use_color=use_color,
                show=True,
            )

        echo(
            f"Processing finished. Query: '{query_str}'",
            style=lambda m: format_info(m, use_color=use_color),
            show=args.verbose,
            log=True,
            log_method="info",
        )

    except KeyboardInterrupt:
        echo(
            "Execution interrupted by user.",
            style=lambda msg: format_warning(msg, use_color=use_color),
            stream=sys.stderr,
            show=True,
            log=True,
            log_method="warning",
        )
        return EXIT_CANCELLED

    except Exception as exc:  # noqa: BLE001
        echo(
            "Unhandled error during CLI execution",
            style=lambda msg: format_error(msg, use_color=use_color),
            stream=sys.stderr,
            show=True,
            log=True,
            log_method="exception",
        )
        echo(
            f"Error: {exc}",
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
        return exit_code

    finally:
        teardown_logger(logger)
