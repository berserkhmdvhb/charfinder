"""
Fuzzy match diagnostics for CharFinder debug output.

Provides detailed debug information about the matching strategy used,
based on CLI arguments and matching results.

Functions:
    print_exact_match_diagnostics(): Explain the exact match strategy.
    print_fuzzy_match_diagnostics(): Explain the fuzzy match algorithm(s) used.
    print_match_diagnostics(): Dispatcher for diagnostics based on actual result.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from __future__ import annotations

from argparse import Namespace
from typing import TYPE_CHECKING

from charfinder.config.messages import (
    MSG_DEBUG_EXACT_EXECUTED,
    MSG_DEBUG_EXACT_MODE,
    MSG_DEBUG_FUZZY_ALGO,
    MSG_DEBUG_FUZZY_EXECUTED,
    MSG_DEBUG_FUZZY_MODE,
    MSG_DEBUG_FUZZY_NOT_REQUESTED,
    MSG_DEBUG_FUZZY_SKIPPED_DUE_TO_EXACT,
    MSG_DEBUG_HYBRID_AGG_FN,
    MSG_DEBUG_HYBRID_ALGO_WEIGHT,
    MSG_DEBUG_HYBRID_ALGOS_HEADER,
    MSG_DEBUG_MATCH_SECTION_END,
    MSG_DEBUG_MATCH_SECTION_START,
    MSG_DEBUG_PREFER_FUZZY_USED_EXACT,
)
from charfinder.utils.formatter import echo
from charfinder.utils.logger_styles import format_debug

if TYPE_CHECKING:
    from charfinder.config.types import MatchDiagnosticsInfo

__all__ = [
    "print_exact_match_diagnostics",
    "print_fuzzy_match_diagnostics",
    "print_match_diagnostics",
]

# ---------------------------------------------------------------------
# Internal Utility
# ---------------------------------------------------------------------


def _debug_echo(msg: str, *, use_color: bool, show: bool = True) -> None:
    echo(
        msg,
        style=lambda m: format_debug(m, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )


# ---------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------


def print_match_diagnostics(
    args: Namespace,
    match_info: MatchDiagnosticsInfo | None,
    *,
    use_color: bool = False,
    show: bool = True,
) -> None:
    """
    Print diagnostics based on whether fuzzy or exact match was used.

    Args:
        args: Parsed CLI arguments
        match_info: Result diagnostics returned by the matcher
        use_color: Whether to apply ANSI formatting
        show: If True, print to terminal
    """
    if not match_info:
        return

    if not match_info.fuzzy:
        _debug_echo(msg=MSG_DEBUG_FUZZY_NOT_REQUESTED, use_color=use_color, show=show)
        print_exact_match_diagnostics(args, use_color=use_color, show=show)
        return

    if match_info.fuzzy_was_used:
        print_fuzzy_match_diagnostics(match_info, use_color=use_color, show=show)
    else:
        if match_info.prefer_fuzzy:
            _debug_echo(
                msg=MSG_DEBUG_PREFER_FUZZY_USED_EXACT,
                use_color=use_color,
                show=show,
            )
        else:
            _debug_echo(
                msg=MSG_DEBUG_FUZZY_SKIPPED_DUE_TO_EXACT,
                use_color=use_color,
                show=show,
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
    Print diagnostic info about exact match mode.

    Args:
        args: Parsed CLI arguments
        use_color: ANSI formatting toggle
        show: Terminal output toggle
    """
    _debug_echo(msg=MSG_DEBUG_MATCH_SECTION_START, use_color=use_color, show=show)
    _debug_echo(msg=MSG_DEBUG_EXACT_EXECUTED, use_color=use_color, show=show)
    _debug_echo(
        msg=MSG_DEBUG_EXACT_MODE.format(mode=args.exact_match_mode),
        use_color=use_color,
        show=show,
    )
    _debug_echo(msg=MSG_DEBUG_MATCH_SECTION_END, use_color=use_color, show=show)


# ---------------------------------------------------------------------
# Fuzzy Match Diagnostics
# ---------------------------------------------------------------------


def print_fuzzy_match_diagnostics(
    match_info: MatchDiagnosticsInfo,
    *,
    use_color: bool = False,
    show: bool = True,
) -> None:
    """
    Print diagnostic info about fuzzy match configuration.

    Args:
        match_info: Result diagnostics returned by the matcher
        use_color: ANSI formatting toggle
        show: Terminal output toggle
    """
    _debug_echo(msg=MSG_DEBUG_MATCH_SECTION_START, use_color=use_color, show=show)
    _debug_echo(msg=MSG_DEBUG_FUZZY_EXECUTED, use_color=use_color, show=show)
    _debug_echo(
        msg=MSG_DEBUG_FUZZY_MODE.format(mode=match_info.fuzzy_match_mode),
        use_color=use_color,
        show=show,
    )

    if match_info.fuzzy_match_mode == "hybrid":
        _debug_echo(
            msg=MSG_DEBUG_HYBRID_AGG_FN.format(agg_fn=match_info.hybrid_agg_fn),
            use_color=use_color,
            show=show,
        )
        _debug_echo(msg=MSG_DEBUG_HYBRID_ALGOS_HEADER, use_color=use_color, show=show)
        for algo, weight in (match_info.hybrid_weights or {}).items():
            _debug_echo(
                msg=MSG_DEBUG_HYBRID_ALGO_WEIGHT.format(algo=algo, weight=weight),
                use_color=use_color,
                show=show,
            )
    else:
        _debug_echo(
            msg=MSG_DEBUG_FUZZY_ALGO.format(algo=match_info.fuzzy_algo),
            use_color=use_color,
            show=show,
        )

    _debug_echo(msg=MSG_DEBUG_MATCH_SECTION_END, use_color=use_color, show=show)
