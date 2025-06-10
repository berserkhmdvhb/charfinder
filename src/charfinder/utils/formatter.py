"""
Shared formatting utilities for CharFinder.

This module provides reusable formatting functions for:

1. Formatting informational, warning, error, debug, success, and settings messages
   with optional color.
2. Formatting result lines for Unicode character search results.
3. Determining whether color output should be used.

This module is used by CLI components, settings, core modules, and tests.

All functions are pure formatters: they return formatted strings and do not print.

Color handling is provided via `colorama`.

The helper `_color_wrap` centralizes color wrapping logic.
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Final, TextIO

from colorama import Fore, Style, init

from charfinder.constants import FIELD_WIDTHS, VALID_LOG_METHODS

__all__ = [
    "echo",
    "format_debug",
    "format_error",
    "format_info",
    "format_result_header",
    "format_result_line",
    "format_result_row",
    "format_settings",
    "format_success",
    "format_warning",
    "should_use_color",
]

# Initialize colorama once
init(autoreset=True)

logger = logging.getLogger("charfinder")

# Color constants
COLOR_HEADER: Final = Fore.CYAN
COLOR_CODELINE: Final = Fore.YELLOW
COLOR_ERROR: Final = Fore.RED
COLOR_INFO: Final = Fore.BLUE
COLOR_SUCCESS: Final = Fore.GREEN
COLOR_WARNING: Final = Fore.YELLOW
COLOR_DEBUG: Final = Fore.LIGHTBLACK_EX
COLOR_SETTINGS: Final = Fore.LIGHTBLACK_EX
RESET: Final = Style.RESET_ALL

# Windows: Ensure terminal handles UTF-8 output
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------
# Color support utilities
# ---------------------------------------------------------------------


def _color_wrap(msg: str, color: str, *, use_color: bool) -> str:
    """
    Apply color formatting to a message if requested.

    Args:
        msg: The message text.
        color: The Fore color to apply.
        use_color: Whether to apply color formatting.

    Returns:
        The formatted message.
    """
    if use_color:
        return f"{color}{msg}{Style.RESET_ALL}"
    return msg


def should_use_color(mode: str) -> bool:
    """
    Determine whether color output should be used.

    Args:
        mode (str): One of 'always', 'never', or 'auto'.

    Returns:
        bool: True if color output should be used, False otherwise.
    """
    if mode == "always":
        return True
    if mode == "never":
        return False
    # auto mode — use color if stdout is a tty
    return sys.stdout.isatty()


# ---------------------------------------------------------------------
# Log Message Management
# ---------------------------------------------------------------------


@contextmanager
def suppress_console_logging() -> Iterator[None]:
    # Find StreamHandler
    stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
    # Disable them
    for h in stream_handlers:
        h.setLevel(logging.CRITICAL + 1)  # Effectively disables normal log levels

    try:
        yield
    finally:
        # Restore normal levels
        for h in stream_handlers:
            h.setLevel(logging.NOTSET)


# ---------------------------------------------------------------------
# Standard message formatters
# ---------------------------------------------------------------------


def echo(
    msg: str,
    style: Callable[[str], str],
    *,
    stream: TextIO = sys.stdout,
    show: bool = True,
    log: bool = True,
    log_method: str | None = None,  # 'debug', 'info', 'warning', 'error', 'exception'
) -> None:
    """
    Write a formatted message to stdout and optionally to logger.

    Args:
        msg: The message text.
        style: The formatting function to apply.
        stream: Output stream (default sys.stdout).
        show: If True, print to terminal; if False, suppress terminal output.
        log: If False, do not log at all.
        log_method: If provided, log using the corresponding logger method
                    ('debug', 'info', 'warning', 'error', 'exception').
    """
    styled = style(msg)
    if log_method not in VALID_LOG_METHODS:
        message = f"Invalid log_method: {log_method}"
        raise ValueError(message)

    if log and log_method:
        log_func = getattr(logger, log_method, None)
        if callable(log_func):
            log_func(msg)

    if show:
        # with suppress_console_logging():
        stream.write(styled + "\n")
        stream.flush()


def format_debug(message: str, *, use_color: bool = True) -> str:
    """Format debug message with [DEBUG] prefix."""
    prefix = f"{COLOR_DEBUG}[DEBUG]{RESET}" if use_color else "[DEBUG]"
    return f"{prefix} {message}"


def format_error(message: str, *, use_color: bool = True) -> str:
    """Format error message with [ERROR] prefix."""
    prefix = f"{COLOR_ERROR}[ERROR]{RESET}" if use_color else "[ERROR]"
    return f"{prefix} {message}"


def format_info(message: str, *, use_color: bool = True) -> str:
    """Format info message with [INFO] prefix."""
    prefix = f"{COLOR_INFO}[INFO]{RESET}" if use_color else "[INFO]"
    return f"{prefix} {message}"


def format_warning(message: str, *, use_color: bool = True) -> str:
    """Format warning message with [WARNING] prefix."""
    prefix = f"{COLOR_WARNING}[WARNING]{RESET}" if use_color else "[WARNING]"
    return f"{prefix} {message}"


def format_settings(message: str, *, use_color: bool = True) -> str:
    """Format settings message with [SETTINGS] prefix."""
    prefix = f"{COLOR_SETTINGS}[SETTINGS]{RESET}" if use_color else "[SETTINGS]"
    return f"{prefix} {message}"


def format_success(message: str, *, use_color: bool = True) -> str:
    """Format success message with [OK] prefix."""
    prefix = f"{COLOR_SUCCESS}[OK]{RESET}" if use_color else "[OK]"
    return f"{prefix} {message}"


# ---------------------------------------------------------------------
# Result table formatters
# ---------------------------------------------------------------------


def format_result_line(line: str, *, use_color: bool = False) -> str:
    """
    Format a result line for display in the CLI.
    """
    return _color_wrap(line, Fore.YELLOW, use_color=use_color)


def format_result_header(*, has_score: bool) -> list[str]:
    """
    Format the result table header and divider.

    Args:
        has_score: Whether the results include a score column.

    Returns:
        A list of two strings: header line and divider line.
    """
    if has_score:
        header = (
            f"{'CODE':<{FIELD_WIDTHS['code']}} "
            f"{'CHAR':<{FIELD_WIDTHS['char']}} "
            f"{'NAME':<{FIELD_WIDTHS['name']}} "
            "SCORE"
        )
    else:
        header = f"{'CODE':<{FIELD_WIDTHS['code']}} {'CHAR':<{FIELD_WIDTHS['char']}} NAME"

    divider = "-" * len(header)

    return [header, divider]


def format_result_row(code: int, char: str, name: str, score: float | None) -> str:
    """
    Format a single result row.

    Args:
        code: Unicode code point.
        char: Unicode character.
        name: Unicode character name.
        score: Optional fuzzy match score, or None for exact match.

    Returns:
        A formatted string representing the result row.
    """
    code_str = f"U+{code:04X}"
    name_str = f"{name}  (\\u{code:04x})"
    score_str = f"{score:>6.3f}" if score is not None else ""

    return (
        f"{code_str:<{FIELD_WIDTHS['code']}} "
        f"{char:<{FIELD_WIDTHS['char']}} "
        f"{name_str:<{FIELD_WIDTHS['name']}} "
        f"{score_str}".rstrip()
    )
