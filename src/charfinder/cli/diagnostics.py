"""
Diagnostics utilities for user-facing CLI debug output.

Provides human-readable runtime diagnostics when the `--debug` flag is passed.

Behavior:
- Output is printed directly to stdout (not logging)
- ANSI coloring is applied based on `--color` flag or terminal support
- Output includes CLI arguments, loaded .env file(s)

Functions:
    - print_debug_diagnostics: Print args and .env context
    - print_dotenv_debug: Print loaded .env file content (via settings)
"""

import os
import sys
from argparse import Namespace

from charfinder.constants import ENV_DEBUG_ENV_LOAD
from charfinder.settings import print_dotenv_debug as settings_dotenv_debug
from charfinder.utils.formatter import format_debug

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
    sys.stdout.write(format_debug(message="=== DEBUG DIAGNOSTICS ===", use_color=use_color) + "\n")
    sys.stdout.write(
        format_debug(message=f"Parsed args     : {vars(args)}", use_color=use_color) + "\n"
    )
    sys.stdout.write(
        format_debug(
            message=f"{ENV_DEBUG_ENV_LOAD} = {os.getenv(ENV_DEBUG_ENV_LOAD, '0')}",
            use_color=use_color,
        )
        + "\n"
    )
    sys.stdout.write(format_debug(message="Loaded .env file(s):", use_color=use_color) + "\n")

    # Call settings' print_dotenv_debug() via wrapper
    print_dotenv_debug()

    sys.stdout.write(
        format_debug(message="=== END DEBUG DIAGNOSTICS ===", use_color=use_color) + "\n"
    )


def print_dotenv_debug() -> None:
    """
    Print details of the resolved .env file and its contents.

    Calls `settings.print_dotenv_debug()`, which logs the info.
    """
    settings_dotenv_debug()
