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
from charfinder.settings import load_settings
from charfinder.utils.formatter import format_error, format_info, format_warning
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

    # Auto-enable --debug if CHARFINDER_DEBUG_ENV_LOAD=1
    if os.getenv("CHARFINDER_DEBUG_ENV_LOAD") == "1" and not args.debug:
        args.debug = True

    # Load .env settings
    load_settings(verbose=args.verbose)

    # Setup logging (after loading settings, before printing debug diagnostics)
    setup_logging()

    logger = logging.getLogger("charfinder")
    use_color = args.color != "never"

    try:
        # Show banner and environment info
        if args.verbose:
            message = f"CharFinder {get_version()} CLI started, "
            sys.stdout.write(format_info(message, use_color=use_color) + "\n")

        # Print debug diagnostics if --debug enabled or CHARFINDER_DEBUG_ENV_LOAD=1
        if args.debug:
            print_debug_diagnostics(args, use_color=use_color)

        # Main handler
        handle_find_chars(args)

        sys.exit(EXIT_SUCCESS)

    except KeyboardInterrupt:
        logger.warning(format_warning("Execution interrupted by user.", use_color=use_color))
        sys.exit(EXIT_CANCELLED)

    except Exception as exc:
        logger.exception("Unhandled error during CLI execution")
        sys.stderr.write(format_error(f"Error: {exc}", use_color=use_color) + "\n")

        if args.debug:
            traceback.print_exc()

        sys.exit(EXIT_ERROR)

    finally:
        teardown_logger(logger)
