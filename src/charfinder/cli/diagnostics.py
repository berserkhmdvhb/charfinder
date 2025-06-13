"""Diagnostics utilities for user-facing CLI debug output.

Provides human-readable runtime diagnostics when the `--debug` flag is passed.

Behavior:
    - Output is printed directly to stdout (if show=True).
    - ANSI coloring is applied based on `--color` flag or terminal support.
    - Output includes CLI arguments and .env file(s) diagnostics.
    - Output is always logged (level DEBUG).

Functions:
    print_debug_diagnostics(): Print CLI args and .env context.
    print_dotenv_debug(): Print loaded .env file content (via settings).
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import os
from argparse import Namespace

from dotenv import dotenv_values

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
    use_color: bool = False,
    show: bool = True,
) -> None:
    """
    Print structured diagnostics when `--debug` is active.

    Includes:
    - CLI arguments as parsed
    - Loaded .env file details

    Args:
        args: Parsed CLI arguments (argparse.Namespace)
        use_color: Whether to apply ANSI formatting
        show: If True, print to terminal; always logged.
    """
    # Diagnostic header
    echo(
        "=== DEBUG DIAGNOSTICS ===",
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )

    # CLI arguments
    echo(
        "Parsed args:",
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )
    for key, value in vars(args).items():
        echo(
            f"  {key:<20} = {value}",
            style=lambda msg: format_debug(msg, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )

    # CHARFINDER_DEBUG_ENV_LOAD
    debug_env = os.getenv(ENV_DEBUG_ENV_LOAD, "0")
    echo(
        f"{ENV_DEBUG_ENV_LOAD} = {debug_env}",
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )

    # Loaded .env
    echo(
        "Loaded .env file(s):",
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )
    print_dotenv_debug(use_color=use_color, show=show)

    # End footer
    echo(
        "=== END DEBUG DIAGNOSTICS ===",
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
    """
    dotenv_path = resolve_dotenv_path()

    echo(
        "=== DOTENV DEBUG ===",
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=False,
        log_method="debug",
    )

    if not dotenv_path:
        echo(
            "No .env file found or resolved.",
            style=lambda msg: format_debug(msg, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )
        echo(
            "Environment variables may only be coming from the OS.",
            style=lambda msg: format_debug(msg, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )
        echo(
            "=== END DOTENV DEBUG ===",
            style=lambda msg: format_debug(msg, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )
        return

    echo(
        f"Selected .env file: {dotenv_path}",
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )

    try:
        values = dotenv_values(dotenv_path=dotenv_path)

        if not values:
            echo(
                ".env file exists but is empty or contains no key-value pairs.",
                style=lambda msg: format_debug(msg, use_color=use_color),
                show=show,
                log=True,
                log_method="debug",
            )
            echo(
                "=== END DOTENV DEBUG ===",
                style=lambda msg: format_debug(msg, use_color=use_color),
                show=show,
                log=True,
                log_method="debug",
            )
            return

        pairs_str = ", ".join(f"{key}={value}" for key, value in values.items())
        echo(
            f"Loaded key-value pairs: {pairs_str}",
            style=lambda msg: format_debug(msg, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )

    except (OSError, UnicodeDecodeError) as exc:
        echo(
            f"Failed to read .env file: {exc}",
            style=lambda msg: format_debug(msg, use_color=use_color),
            show=show,
            log=True,
            log_method="debug",
        )

    echo(
        "=== END DOTENV DEBUG ===",
        style=lambda msg: format_debug(msg, use_color=use_color),
        show=show,
        log=True,
        log_method="debug",
    )
