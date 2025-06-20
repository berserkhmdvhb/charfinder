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

from charfinder.cli.parser import create_parser
from charfinder.cli.utils_runner import (
    auto_enable_debug,
    build_fuzzy_config_from_args,
    handle_cli_workflow,
    resolve_final_query,
)
from charfinder.config.constants import EXIT_SUCCESS
from charfinder.utils.normalizer import normalize
from charfinder.validators import (
    apply_fuzzy_defaults,
    resolve_cli_settings,
    resolve_effective_show_score,
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

    # Resolve settings: color mode, use_color flag, and threshold (validated inside)
    args.color, use_color, args.threshold = resolve_cli_settings(args)

    # Resolve show_score (CLI > env > default)
    args.show_score = resolve_effective_show_score(cli_value=args.show_score)

    # Query handling: resolve final query string
    raw_query = resolve_final_query(args)
    if not raw_query:
        parser.print_help()
        sys.exit(EXIT_SUCCESS)

    # Normalize query for consistent matching
    norm_query = normalize(raw_query, profile=args.normalization_profile)

    # Enable debug mode if required by CHARFINDER_DEBUG_ENV_LOAD
    auto_enable_debug(args)

    # Apply fuzzy algorithm/mode defaults (if --fuzzy was enabled)
    config = build_fuzzy_config_from_args(args)
    apply_fuzzy_defaults(args, config)

    # Execute full CLI pipeline
    exit_code = handle_cli_workflow(
        args=args,
        query_str=norm_query,
        use_color=use_color,
    )
    sys.exit(exit_code)
