"""Main CLI entry point for CharFinder.

Coordinates the full CLI workflow:

- Builds the CLI argument parser.
- Parses command-line arguments.
- Resolves query and fuzzy algorithm.
- Executes the full CLI lifecycle via handle_cli_workflow().
- Acts as the main entry point when invoked via:
    python -m charfinder
    charfinder [args]

Functions:
    main(): The main CLI entry function.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import sys

from charfinder.cli.handlers import (
    resolve_settings,
)
from charfinder.cli.parser import create_parser
from charfinder.cli.utils_runner import (
    auto_enable_debug,
    handle_cli_workflow,
    resolve_final_query,
)
from charfinder.constants import EXIT_SUCCESS
from charfinder.validators import (
    validate_color_mode,
    validate_fuzzy_algo,
    validate_threshold,
    apply_fuzzy_defaults
)

__all__ = ["main"]

# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def main() -> None:
    """
    Main CLI entry function.

    - Parses CLI arguments.
    - Resolves query and fuzzy algorithm.
    - Executes CLI workflow and handles final exit.
    """
    parser = create_parser()
    args = parser.parse_args()

    # Resolve settings, including color mode, threshold, and debug flags
    color_mode, use_color, threshold = resolve_settings(args)

    # Query handling: Resolve final query string
    query_str = resolve_final_query(args)
    if not query_str:
        parser.print_help()
        sys.exit(EXIT_SUCCESS)

    # Enable debug mode if required by environment variable (CHARFINDER_DEBUG_ENV_LOAD)
    auto_enable_debug(args)

    # Validate fuzzy algorithm **before** applying defaults
    args.fuzzy_algo = validate_fuzzy_algo(args.fuzzy_algo)

    # Validate threshold to ensure it aligns with the .env or CLI
    args.threshold = validate_threshold(args.threshold)

    # Validate color mode (if set)
    args.color = validate_color_mode(args.color)

    # Apply defaults for fuzzy behavior if --fuzzy is enabled (after validation)
    apply_fuzzy_defaults(args)

    # Run the full CLI workflow
    exit_code = handle_cli_workflow(args=args, query_str=query_str, use_color=use_color)

    # Exit with the determined exit code
    sys.exit(exit_code)
