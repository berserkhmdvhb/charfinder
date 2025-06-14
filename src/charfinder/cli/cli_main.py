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
    apply_fuzzy_defaults,
    resolve_effective_color_mode,
)
from charfinder.cli.parser import create_parser
from charfinder.cli.utils_runner import (
    auto_enable_debug,
    handle_cli_workflow,
    resolve_final_query,
    validate_and_resolve_fuzzy_algo,
)
from charfinder.constants import EXIT_SUCCESS
from charfinder.utils.formatter import should_use_color

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

    # Initial color mode before loading .env (used for early output)
    color_mode = resolve_effective_color_mode(args.color)
    use_color = should_use_color(color_mode)

    # Query handling
    query_str = resolve_final_query(args)
    if not query_str:
        parser.print_help()
        sys.exit(EXIT_SUCCESS)

    # Debug flag override via env
    auto_enable_debug(args)

    # Inject defaults for fuzzy behavior if --fuzzy is enabled
    apply_fuzzy_defaults(args)

    # Validate fuzzy algorithm (exit early if invalid)
    validate_and_resolve_fuzzy_algo(args=args, use_color=use_color)

    # Run the full CLI workflow
    exit_code = handle_cli_workflow(args=args, query_str=query_str, use_color=use_color)
    sys.exit(exit_code)
