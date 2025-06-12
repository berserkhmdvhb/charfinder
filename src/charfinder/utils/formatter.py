"""
Shared formatting utilities for CharFinder.

This module provides reusable formatting functions for:

1. Writing informational, warning, error, debug, success, and settings messages
   to both terminal and logger (via `echo()` and `log_optionally_echo()`).
2. Formatting result lines for Unicode character search results.
3. Determining whether color output should be used.

All functions are pure formatters: they return formatted strings and do not print
(unless echoing is explicitly requested).

Color handling is provided via `colorama`.

The helper `_color_wrap` centralizes color wrapping logic.

NOTE: Color constants should be factored out to `logger_styles.py` in the future
to avoid duplication.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import TextIO

from colorama import Fore, Style, init

from charfinder.constants import FIELD_WIDTHS, VALID_LOG_METHODS
from charfinder.utils.logger_helpers import suppress_console_logging

__all__ = [
    "echo",
    "format_result_header",
    "format_result_line",
    "format_result_row",
    "log_optionally_echo",
    "should_use_color",
]


# Initialize colorama once
init(autoreset=True)

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
# Standard message formatters
# ---------------------------------------------------------------------


def echo(
    msg: str,
    style: Callable[[str], str],
    *,
    stream: TextIO = sys.stdout,
    show: bool = True,
    log: bool = True,
    log_method: str | None = None,
) -> None:
    """
    Write a formatted message to stdout and optionally to logger.

    Args:
        msg: The message text.
        style: The formatting function to apply.
        stream: Output stream (default sys.stdout).
        show: If True, print to terminal; if False, suppress terminal output.
        log: If True, log the message (requires log_method).
        log_method: If provided, log using the corresponding logger method.
    """
    from charfinder.utils.logger_setup import get_logger

    logger = get_logger()
    styled = style(msg)

    if log and not log_method:
        msg_error = "log_method must be provided if log=True"
        raise ValueError(msg_error)

    if log_method and log_method not in VALID_LOG_METHODS:
        msg_error = f"Invalid log_method: {log_method}"
        raise ValueError(msg_error)

    log_func = getattr(logger, log_method, None) if log_method else None
    if log and callable(log_func):
        with suppress_console_logging():
            log_func(msg)

    if show:
        with suppress_console_logging():
            stream.write(styled + "\n")
            stream.flush()


def log_optionally_echo(
    msg: str,
    level: str = "info",
    *,
    show: bool = False,
    style: Callable[[str], str] | None = None,
    stream: TextIO = sys.stdout,
) -> None:
    """
    Log the message and optionally echo it to terminal.

    Args:
        msg: The message text.
        level: 'info', 'warning', 'error', 'debug', 'exception'.
        show: If True, print to terminal.
        style: Optional style function for terminal output.
        stream: Output stream for terminal (default sys.stdout).
    """
    from charfinder.utils.logger_setup import get_logger

    logger = get_logger()
    log_func = getattr(logger, level, None)
    if callable(log_func):
        with suppress_console_logging():
            log_func(msg)

    if show:
        styled = style(msg) if style else msg
        with suppress_console_logging():
            stream.write(styled + "\n")
            stream.flush()


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
