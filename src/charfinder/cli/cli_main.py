"""
Main CLI entry point for CharFinder.

This module coordinates the full CLI workflow:

- Builds the CLI argument parser.
- Parses command-line arguments.
- Dispatches to the main handler (handle_find_chars).
- Acts as the main entry point when invoked via:
    python -m charfinder
    charfinder [args]

This module exposes:
- main(): The main CLI entry function.
"""

import logging
import os
import sys
import traceback

from charfinder.cli.diagnostics import print_debug_diagnostics
from charfinder.cli.handlers import get_version, handle_find_chars
from charfinder.cli.parser import create_parser
from charfinder.constants import EXIT_CANCELLED, EXIT_ERROR, EXIT_SUCCESS
from charfinder.settings import get_environment, load_settings
from charfinder.utils.formatter import (
    echo,
    format_error,
    format_info,
    format_settings,
    format_warning,
)
from charfinder.utils.logger import setup_logging, teardown_logger

__all__ = ["main"]


def main() -> None:
    """
    Main CLI entry function.

    - Parses CLI arguments.
    - Calls handle_find_chars() with parsed args.
    - Handles graceful shutdown and error reporting.
    """
    parser = create_parser()
    args = parser.parse_args()

    # Support both positional and optional --query/-q args
    query_list = args.option_query if args.option_query else args.positional_query
    query_str = " ".join(query_list).strip()

    if not query_str:
        parser.error("Query must not be empty.")

    # Auto-enable --debug if CHARFINDER_DEBUG_ENV_LOAD=1
    if os.getenv("CHARFINDER_DEBUG_ENV_LOAD") == "1" and not args.debug:
        args.debug = True

    # Load .env settings
    load_settings(verbose=args.verbose, debug=args.debug)

    # Setup logging (after loading settings, before printing debug diagnostics)
    log_level = logging.DEBUG if args.debug else None
    setup_logging(log_level=log_level)
    logger = logging.getLogger("charfinder")
    use_color = args.color != "never"

    try:
        # Show banner and environment info
        message1 = f"Using environment: {get_environment()}"
        logger.info(message1)
        message2 = f"CharFinder {get_version()} CLI started"
        logger.info(message2)

        if args.verbose:
            echo(message1, style=lambda m: format_settings(m, use_color=use_color))
            echo(message2, style=lambda m: format_info(m, use_color=use_color))

        # Print debug diagnostics if --debug enabled or CHARFINDER_DEBUG_ENV_LOAD=1
        if args.debug:
            print_debug_diagnostics(args, use_color=use_color)

        # Main handler
        handle_find_chars(args)

        final_message = f"Processing finished. Query: '{query_str}'"
        logger.info(final_message)
        sys.exit(EXIT_SUCCESS)

    except KeyboardInterrupt:
        message = "Execution interrupted by user."
        echo(
            message,
            style=lambda msg: format_warning(msg, use_color=use_color),
            stream=sys.stderr,
        )
        logger.warning(message)
        sys.exit(EXIT_CANCELLED)

    except Exception as exc:
        logger.exception("Unhandled error during CLI execution")
        echo(
            f"Error: {exc}",
            style=lambda msg: format_error(msg, use_color=use_color),
            stream=sys.stderr,
        )
        if args.debug:
            traceback.print_exc()

        sys.exit(EXIT_ERROR)

    finally:
        teardown_logger(logger)
