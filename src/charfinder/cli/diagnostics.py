"""
Diagnostics utilities for user-facing CLI debug output.

Provides human-readable runtime diagnostics when the `--debug` flag is passed.

Behavior:
    - Output is printed directly to stdout (if show=True).
    - ANSI coloring is applied based on `--color` flag or terminal support.
    - Output includes CLI arguments, match diagnostics, and .env file(s).
    - Output is always logged (level DEBUG).
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import os
from argparse import Namespace

from dotenv import dotenv_values

from charfinder.cli.diagnostics_match import print_match_diagnostics
from charfinder.config.constants import ENV_DEBUG_ENV_LOAD
from charfinder.config.messages import (
    MSG_DEBUG_ARG_ITEM,
    MSG_DEBUG_DOTENV_EMPTY,
    MSG_DEBUG_DOTENV_END,
    MSG_DEBUG_DOTENV_LOADED_FILES,
    MSG_DEBUG_DOTENV_READ_ERROR,
    MSG_DEBUG_DOTENV_START,
    MSG_DEBUG_ENV_VAR,
    MSG_DEBUG_NO_DOTENV_FOUND,
    MSG_DEBUG_PARSED_ARGS,
    MSG_DEBUG_SECTION_END,
)
from charfinder.config.settings import resolve_dotenv_path
from charfinder.config.types import MatchDiagnosticsInfo
from charfinder.utils.formatter import echo
from charfinder.utils.logger_styles import format_debug

__all__ = [
    "print_debug_diagnostics",
    "print_dotenv_debug",
]

# ---------------------------------------------------------------------
# Internal Utility
# ---------------------------------------------------------------------


def _debug_echo(msg: str, *, use_color: bool, show: bool = True) -> None:
    """Wrapper around echo for debug diagnostics."""
    echo(
        msg,
        style=lambda m: format_debug(m, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )


# ---------------------------------------------------------------------
# Diagnostics Functions
# ---------------------------------------------------------------------


def print_debug_diagnostics(
    args: Namespace,
    *,
    match_info: MatchDiagnosticsInfo | None = None,
    use_color: bool = False,
    show: bool = True,
) -> None:
    """
    Print structured diagnostics when `--debug` is active.

    Includes:
    - CLI arguments as parsed
    - Fuzzy/exact match info if provided
    - Loaded .env file details

    Args:
        args: Parsed CLI arguments (argparse.Namespace)
        match_info: Match context returned by matcher, if available
        use_color: Whether to apply ANSI formatting
        show: If True, print to terminal; always logged.
    """
    _debug_echo(msg=MSG_DEBUG_DOTENV_START, use_color=use_color, show=show)

    _debug_echo(msg=MSG_DEBUG_PARSED_ARGS, use_color=use_color, show=show)
    for key, value in sorted(vars(args).items()):
        _debug_echo(
            msg=MSG_DEBUG_ARG_ITEM.format(key=key, value=value), use_color=use_color, show=show
        )

    _debug_echo(
        msg=MSG_DEBUG_ENV_VAR.format(
            env_var=ENV_DEBUG_ENV_LOAD, value=os.getenv(ENV_DEBUG_ENV_LOAD, "0")
        ),
        use_color=use_color,
        show=show,
    )

    if match_info:
        print_match_diagnostics(
            args=args,
            match_info=match_info,
            use_color=use_color,
            show=show,
        )

    _debug_echo(msg=MSG_DEBUG_DOTENV_LOADED_FILES, use_color=use_color, show=show)
    print_dotenv_debug(use_color=use_color, show=show)

    _debug_echo(msg=MSG_DEBUG_SECTION_END, use_color=use_color, show=show)


def print_dotenv_debug(*, use_color: bool = False, show: bool = True) -> None:
    """
    Print details of the resolved .env file and its contents.

    Intended for CLI `--debug` output (diagnostics only).

    Args:
        use_color (bool): Whether to apply ANSI formatting.
        show: If True, print to terminal; always logged.

    Raises:
        OSError: If reading the .env file fails due to IO issues.
        UnicodeDecodeError: If the file contains non-decodable bytes.
    """
    dotenv_path = resolve_dotenv_path()

    _debug_echo(msg=MSG_DEBUG_DOTENV_START, use_color=use_color, show=show)

    if not dotenv_path:
        _debug_echo(msg=MSG_DEBUG_NO_DOTENV_FOUND, use_color=use_color, show=show)
        _debug_echo(
            "Environment variables may only be coming from the OS.",
            use_color=use_color,
            show=show,
        )
        _debug_echo(msg=MSG_DEBUG_DOTENV_END, use_color=use_color, show=show)
        return

    _debug_echo(
        msg=MSG_DEBUG_NO_DOTENV_FOUND.format(path=dotenv_path), use_color=use_color, show=show
    )

    try:
        values = dotenv_values(dotenv_path=dotenv_path)

        if not values:
            _debug_echo(
                msg=MSG_DEBUG_DOTENV_EMPTY,
                use_color=use_color,
                show=show,
            )
        else:
            for key, value in values.items():
                _debug_echo(
                    msg=MSG_DEBUG_ARG_ITEM.format(key=key, value=value),
                    use_color=use_color,
                    show=show,
                )

    except (OSError, UnicodeDecodeError) as exc:
        _debug_echo(
            msg=MSG_DEBUG_DOTENV_READ_ERROR.format(error=exc), use_color=use_color, show=show
        )

    _debug_echo(msg=MSG_DEBUG_DOTENV_END, use_color=use_color, show=show)
