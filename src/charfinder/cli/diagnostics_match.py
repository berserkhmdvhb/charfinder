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

from charfinder.config.constants import FUZZY_HYBRID_WEIGHTS
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
        _debug_echo("Fuzzy matching was not requested.", use_color=use_color, show=show)
        print_exact_match_diagnostics(args, use_color=use_color, show=show)
        return

    if match_info.fuzzy_was_used:
        print_fuzzy_match_diagnostics(match_info, use_color=use_color, show=show)
    else:
        if match_info.prefer_fuzzy:
            _debug_echo(
                "Fuzzy was preferred but exact match was used.",
                use_color=use_color,
                show=show,
            )
        else:
            _debug_echo(
                "Fuzzy requested but skipped due to exact match success.",
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
    _debug_echo("=== MATCH STRATEGY ===", use_color=use_color, show=show)
    _debug_echo("Exact match strategy executed.", use_color=use_color, show=show)
    _debug_echo(
        f"Exact match mode: {args.exact_match_mode!r}",
        use_color=use_color,
        show=show,
    )
    _debug_echo("=== END MATCH STRATEGY ===", use_color=use_color, show=show)


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
    _debug_echo("=== MATCH STRATEGY ===", use_color=use_color, show=show)
    _debug_echo("Fuzzy match strategy executed.", use_color=use_color, show=show)
    _debug_echo(
        f"Fuzzy match mode: {match_info.fuzzy_match_mode!r}",
        use_color=use_color,
        show=show,
    )

    if match_info.fuzzy_match_mode == "hybrid":
        _debug_echo(
            f"Aggregation function: {match_info.hybrid_agg_fn!r}",
            use_color=use_color,
            show=show,
        )
        _debug_echo("Fuzzy algorithms used:", use_color=use_color, show=show)
        for algo, weight in FUZZY_HYBRID_WEIGHTS.items():
            _debug_echo(
                f"  {algo:<22} (weight={weight})",
                use_color=use_color,
                show=show,
            )
    else:
        _debug_echo(
            f"Fuzzy algorithm: {match_info.fuzzy_algo!r}",
            use_color=use_color,
            show=show,
        )

    _debug_echo("=== END MATCH STRATEGY ===", use_color=use_color, show=show)
