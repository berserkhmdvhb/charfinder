"""Main CLI entry point for CharFinder.

Coordinates the full CLI lifecycle when run as `charfinder` or `python -m charfinder`.

Responsibilities:
    - Parse CLI arguments.
    - Validate and normalize input values.
    - Resolve final search query.
    - Build fuzzy configuration.
    - Execute the search and output routines.

Used by:
    - CLI startup via `__main__.py` or console script entry point.

Functions:
    main(): Primary CLI entry function.
"""


# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import sys

from charfinder.cli.handlers import resolve_settings
from charfinder.cli.parser import create_parser
from charfinder.cli.utils_runner import (
    auto_enable_debug,
    build_fuzzy_config_from_args,
    handle_cli_workflow,
    resolve_final_query,
)
from charfinder.constants import (
    EXIT_SUCCESS,
)
from charfinder.validators import (
    apply_fuzzy_defaults,
    validate_color_mode,
    validate_threshold,
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

    # Threshold and color mode validation
    args.threshold = validate_threshold(args.threshold)
    args.color = validate_color_mode(args.color)

    # Build fuzzy configuration
    config = build_fuzzy_config_from_args(args)

    # Resolve settings, including color mode, threshold, and debug flags
    _, use_color, _ = resolve_settings(args)

    # Query handling: Resolve final query string
    query_str = resolve_final_query(args)
    if not query_str:
        parser.print_help()
        sys.exit(EXIT_SUCCESS)

    # Enable debug mode if required by CHARFINDER_DEBUG_ENV_LOAD
    auto_enable_debug(args)

    # Apply default fuzzy match settings (if --fuzzy is enabled)
    apply_fuzzy_defaults(args, config)

    # Execute the full search and output pipeline
    exit_code = handle_cli_workflow(
        args=args,
        query_str=query_str,
        use_color=use_color,
    )

    sys.exit(exit_code)
