"""Diagnostics utilities for user-facing CLI debug output.

Provides human-readable runtime diagnostics when the `--debug` flag is passed.

Behavior:
    - Output is printed directly to stdout (if show=True).
    - ANSI coloring is applied based on `--color` flag or terminal support.
    - Output includes CLI arguments, match diagnostics, and .env file(s).
    - Output is always logged (level DEBUG).

Functions:
    print_debug_diagnostics(): Print CLI args, match info, and .env context.
    print_dotenv_debug(): Print loaded .env file content (via settings).
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import os
from argparse import Namespace
from typing import Any

from dotenv import dotenv_values

from charfinder.cli.diagnostics_match import print_match_diagnostics
from charfinder.constants import ENV_DEBUG_ENV_LOAD
from charfinder.settings import resolve_dotenv_path
from charfinder.utils.formatter import echo
from charfinder.utils.logger_styles import format_debug

__all__ = [
    "print_debug_diagnostics",
    "print_dotenv_debug",
]

# ---------------------------------------------------------------------
# Diagnostics Functions
# ---------------------------------------------------------------------


def print_debug_diagnostics(
    args: Namespace,
    *,
    match_info: dict[str, Any] | None = None,
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
    message = "=== DEBUG DIAGNOSTICS ==="
    echo(
        message,
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )

    message = "Parsed args:"
    echo(
        message,
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )

    for key, value in sorted(vars(args).items()):
        message = f"  {key:<20} = {value}"
        echo(
            message,
            style=lambda msg: format_debug(msg, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )

    message = f"{ENV_DEBUG_ENV_LOAD} = {os.getenv(ENV_DEBUG_ENV_LOAD, '0')}"
    echo(
        message,
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )

    if match_info:
        args_for_debug = Namespace(**match_info)
        print_match_diagnostics(
            args_for_debug,
            match_info=match_info,
            use_color=use_color,
            show=show,
        )

    message = "Loaded .env file(s):"
    echo(
        message,
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )
    print_dotenv_debug(use_color=use_color, show=show)

    message = "=== END DEBUG DIAGNOSTICS ==="
    echo(
        message,
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )


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

    message = "=== DOTENV DEBUG ==="
    echo(
        message,
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=False,
        log_method="debug",
    )

    if not dotenv_path:
        message = "No .env file found or resolved."
        echo(
            message,
            style=lambda msg: format_debug(msg, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )
        message = "Environment variables may only be coming from the OS."
        echo(
            message,
            style=lambda msg: format_debug(msg, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )
        message = "=== END DOTENV DEBUG ==="
        echo(
            message,
            style=lambda msg: format_debug(msg, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )
        return

    message = f"Selected .env file: {dotenv_path}"
    echo(
        message,
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )

    try:
        values = dotenv_values(dotenv_path=dotenv_path)

        if not values:
            message = ".env file exists but is empty or contains no key-value pairs."
            echo(
                message,
                style=lambda msg: format_debug(msg, use_color=use_color),
                show=show,
                log=True,
                log_method="debug",
            )
            message = "=== END DOTENV DEBUG ==="
            echo(
                message,
                style=lambda msg: format_debug(msg, use_color=use_color),
                show=show,
                log=True,
                log_method="debug",
            )
            return

        pairs_str = ", ".join(f"{key}={value}" for key, value in values.items())
        message = f"Loaded key-value pairs: {pairs_str}"
        echo(
            message,
            style=lambda msg: format_debug(msg, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )

    except (OSError, UnicodeDecodeError) as exc:
        message = f"Failed to read .env file: {exc}"
        echo(
            message,
            style=lambda msg: format_debug(msg, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )

    message = "=== END DOTENV DEBUG ==="
    echo(
        message,
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )
