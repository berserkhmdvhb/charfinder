"""
Diagnostics utilities for user-facing CLI debug output.

Provides human-readable runtime diagnostics when the `--debug` flag is passed.

Behavior:
- Output is printed directly to stdout (not logging)
- ANSI coloring is applied based on `--color` flag or terminal support
- Output includes CLI arguments and .env file(s) diagnostics

Functions:
    - print_debug_diagnostics: Print args and .env context
    - print_dotenv_debug: Print loaded .env file content (via settings)
"""

import os
from argparse import Namespace

from charfinder.constants import ENV_DEBUG_ENV_LOAD
from charfinder.settings import print_dotenv_debug as settings_dotenv_debug
from charfinder.utils.formatter import echo, format_debug

__all__ = [
    "print_debug_diagnostics",
    "print_dotenv_debug",
]


def print_debug_diagnostics(
    args: Namespace,
    *,
    use_color: bool,
) -> None:
    """
    Print structured diagnostics when `--debug` is active.

    Includes:
    - CLI arguments as parsed
    - Loaded .env file details

    Args:
        args: Parsed CLI arguments (argparse.Namespace)
        use_color: Whether to apply ANSI formatting
    """
    # Diagnostic header
    echo("=== DEBUG DIAGNOSTICS ===", style=lambda msg: format_debug(msg, use_color=use_color))

    # CLI arguments
    echo("Parsed args:", style=lambda msg: format_debug(msg, use_color=use_color))
    for key, value in vars(args).items():
        echo(f"  {key:<20} = {value}", style=lambda msg: format_debug(msg, use_color=use_color))

    # CHARFINDER_DEBUG_ENV_LOAD
    debug_env = os.getenv(ENV_DEBUG_ENV_LOAD, "0")
    echo(
        f"{ENV_DEBUG_ENV_LOAD} = {debug_env}",
        style=lambda msg: format_debug(msg, use_color=use_color),
    )

    # Loaded .env
    echo("Loaded .env file(s):", style=lambda msg: format_debug(msg, use_color=use_color))
    print_dotenv_debug()

    # End footer
    echo("=== END DEBUG DIAGNOSTICS ===", style=lambda msg: format_debug(msg, use_color=use_color))


def print_dotenv_debug() -> None:
    """
    Print details of the resolved .env file and its contents.

    Calls `settings.print_dotenv_debug()`, which handles formatting.
    """
    settings_dotenv_debug()
