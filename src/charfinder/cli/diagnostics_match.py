"""Fuzzy match diagnostics for CharFinder debug output.

Provides detailed debug information about match behavior based on CLI args and
matching configuration.

Functions:
    print_exact_match_diagnostics(): Explain the exact match strategy.
    print_fuzzy_match_diagnostics(): Explain the fuzzy match algorithm(s) used.
    print_match_diagnostics(): Dispatcher to print diagnostics for exact or fuzzy match.
"""

from __future__ import annotations

from argparse import Namespace
from typing import Any

from charfinder.constants import FUZZY_HYBRID_WEIGHTS
from charfinder.utils.formatter import echo
from charfinder.utils.logger_styles import format_debug

__all__ = [
    "print_exact_match_diagnostics",
    "print_fuzzy_match_diagnostics",
    "print_match_diagnostics",
]

# ---------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------

# Section headers
MSG_MATCH_HEADER = "=== MATCH STRATEGY ==="
MSG_MATCH_FOOTER = "=== END MATCH STRATEGY ==="

# Execution notices
MSG_EXACT_EXECUTED = "Exact match strategy executed."
MSG_FUZZY_EXECUTED = "Fuzzy match strategy executed."
MSG_FUZZY_NOT_REQUESTED = "Fuzzy matching was not requested."
MSG_FUZZY_SKIPPED = "Fuzzy matching was requested but skipped (exact match succeeded)."
MSG_FUZZY_SKIPPED_PREFERRED = (
    "Fuzzy matching was requested and preferred, but exact match was used."
)
MSG_FUZZY_USED = "Fuzzy matching was requested and used."

# Exact match config
MSG_EXACT_MODE = "Exact match mode: {!r}"

# Fuzzy match config
MSG_FUZZY_MODE = "Fuzzy match mode: {!r}"
MSG_FUZZY_ALGO = "Fuzzy algorithm: {!r}"

# Hybrid-specific config
MSG_HYBRID_AGG_FN = "Aggregation function: {!r}"
MSG_HYBRID_ALGOS_USED = "Fuzzy algorithms used:"
MSG_HYBRID_ALGO_WEIGHT = "  {0:<22} (weight={1})"
MSG_HYBRID_WEIGHTS = "Hybrid weights:"
MSG_HYBRID_WEIGHT_LINE = "  {:<20} = {:.2f}"


# ---------------------------------------------------------------------
# Diagnostics Dispatcher
# ---------------------------------------------------------------------


def print_match_diagnostics(
    args: Namespace,
    match_info: dict[str, Any] | None = None,
    *,
    use_color: bool = False,
    show: bool = True,
) -> None:
    """
    Dispatcher to print matching diagnostics based on actual matching behavior.

    Args:
        args (Namespace): Parsed CLI arguments.
        match_info (dict[str, Any] | None): Dictionary describing actual matching result and config.
        use_color (bool): Whether to colorize output.
        show (bool): Whether to show output to terminal.
    """
    if not match_info:
        return

    fuzzy_requested = match_info.get("fuzzy", False)
    fuzzy_used = match_info.get("fuzzy_was_used", False)

    if not fuzzy_requested:
        echo(
            MSG_FUZZY_NOT_REQUESTED,
            style=lambda m: format_debug(m, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )
        print_exact_match_diagnostics(args, use_color=use_color, show=show)
        return

    if fuzzy_used:
        print_fuzzy_match_diagnostics(match_info, use_color=use_color, show=show)
    else:
        if args.prefer_fuzzy:
            echo(
                MSG_FUZZY_SKIPPED_PREFERRED,
                style=lambda m: format_debug(m, use_color=use_color),
                show=show,
                log=True,
                log_method="debug",
            )
        else:
            echo(
                MSG_FUZZY_SKIPPED,
                style=lambda m: format_debug(m, use_color=use_color),
                show=show,
                log=True,
                log_method="debug",
            )
        print_exact_match_diagnostics(args, use_color=use_color, show=show)


# ---------------------------------------------------------------------
# Exact Match Diagnostics
# ---------------------------------------------------------------------


def print_exact_match_diagnostics(
    args: Namespace,
    *,
    use_color: bool = False,
    show: bool = True,
) -> None:
    """
    Print diagnostic details for exact match mode.

    Args:
        args (Namespace): Parsed CLI arguments.
        use_color (bool): Whether to colorize output.
        show (bool): Whether to show output to terminal.
    """
    echo(
        MSG_MATCH_HEADER,
        style=lambda m: format_debug(m, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )
    echo(
        MSG_EXACT_EXECUTED,
        style=lambda m: format_debug(m, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )
    echo(
        MSG_EXACT_MODE.format(args.exact_match_mode),
        style=lambda m: format_debug(m, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )
    echo(
        MSG_MATCH_FOOTER,
        style=lambda m: format_debug(m, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )


# ---------------------------------------------------------------------
# Fuzzy Match Diagnostics
# ---------------------------------------------------------------------


def print_fuzzy_match_diagnostics(
    match_info: dict[str, Any],
    *,
    use_color: bool = False,
    show: bool = True,
) -> None:
    """
    Print diagnostic details for fuzzy match configuration.

    Args:
        match_info (dict[str, Any]): Dictionary returned by the matching handler.
        use_color (bool): Whether to colorize output.
        show (bool): Whether to show output to terminal.
    """
    echo(
        MSG_MATCH_HEADER,
        style=lambda m: format_debug(m, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )
    echo(
        MSG_FUZZY_EXECUTED,
        style=lambda m: format_debug(m, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )

    mode = match_info.get("fuzzy_match_mode", "unknown")
    echo(
        MSG_FUZZY_MODE.format(mode),
        style=lambda m: format_debug(m, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )

    if mode == "hybrid":
        echo(
            MSG_HYBRID_AGG_FN.format(match_info.get("hybrid_agg_fn", "unknown")),
            style=lambda m: format_debug(m, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )

        echo(
            MSG_HYBRID_ALGOS_USED,
            style=lambda m: format_debug(m, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )

        for algo, weight in FUZZY_HYBRID_WEIGHTS.items():
            echo(
                MSG_HYBRID_ALGO_WEIGHT.format(algo, weight),
                style=lambda m: format_debug(m, use_color=use_color),
                show=show,
                log=True,
                log_method="debug",
            )

    echo(
        MSG_MATCH_FOOTER,
        style=lambda m: format_debug(m, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )
