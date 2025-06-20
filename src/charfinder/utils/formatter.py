"""Shared formatting utilities for CharFinder.

Provides reusable formatting functions for:

- Writing informational, warning, error, debug, success, and settings messages
  to both terminal and logger (via `echo()` and `log_optionally_echo()`).
- Formatting result lines for Unicode character search results.
- Determining whether color output should be used.

All functions are pure formatters: they return formatted strings and do not print
(unless echoing is explicitly requested).

Color handling is provided via `colorama`.

Functions:
    echo(): Write a formatted message to terminal and logger.
    log_optionally_echo(): Log a message and optionally echo to terminal.
    should_use_color(): Determine whether color output should be used.
    format_result_line(): Format a result line for CLI display.
    format_result_header(): Format the result table header and divider.
    format_result_row(): Format a single result row.
    matchtuple_to_charmatch(): Converts a MatchTuple to a CharMatch dictionary.
    format_all_results(): Formats all result rows with headers and color support.

Note:
    Color constants should be factored out to `logger_styles.py` in the future
    to avoid duplication.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from __future__ import annotations

import sys
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, TextIO

from colorama import Fore, Style, init

if TYPE_CHECKING:
    from charfinder.config.types import CharMatch, MatchTuple

from charfinder.config.constants import DEFAULT_COLOR_MODE, FIELD_WIDTHS, VALID_LOG_METHODS
from charfinder.utils.logger_helpers import strip_color_codes, suppress_console_logging
from charfinder.utils.logger_styles import format_debug

__all__ = [
    "display_result_lines",
    "echo",
    "format_all_results",
    "format_result_header",
    "format_result_line",
    "format_result_row",
    "log_optionally_echo",
    "matchtuple_to_charmatch",
    "should_use_color",
]

# ---------------------------------------------------------------------
# Init & Setup
# ---------------------------------------------------------------------

init(autoreset=True)

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Template for result table header with dynamic field widths
HEADER_FMT = (
    f"{{:<{FIELD_WIDTHS['code']}}} "
    f"{{:<{FIELD_WIDTHS['char']}}} "
    f"{{:<{FIELD_WIDTHS['name']}}} "
    f"{{:>{FIELD_WIDTHS['score']}}}"
)
# ---------------------------------------------------------------------
# Color Utilities
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
    return f"{color}{msg}{Style.RESET_ALL}" if use_color else msg


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
    return sys.stdout.isatty()


# ---------------------------------------------------------------------
# Echo & Log Helpers
# ---------------------------------------------------------------------


def echo(
    msg: str,
    style: Callable[[str], str],
    *,
    stream: TextIO = sys.stdout,
    show: bool = True,
    log: bool = False,
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

    Raises:
        ValueError: If log=True but log_method is not provided, or if log_method is invalid.
    """
    from charfinder.utils.logger_setup import get_logger  # noqa: PLC0415

    logger = get_logger()
    styled = style(msg)

    if log and not log_method:
        message = "log_method must be provided if log=True"
        raise ValueError(message)

    if log_method and log_method not in VALID_LOG_METHODS:
        message = f"Invalid log_method: {log_method}"
        raise ValueError(message)

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
    from charfinder.utils.logger_setup import get_logger  # noqa: PLC0415

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
# Result Formatters
# ---------------------------------------------------------------------


def format_result_line(line: str, *, use_color: bool = False) -> str:
    """
    Format a result line for display in the CLI.

    Args:
        line (str): The line to format.
        use_color (bool): Whether to apply color formatting.

    Returns:
        str: The formatted result line.
    """
    return _color_wrap(line, Fore.YELLOW, use_color=use_color)


def format_result_header(*, show_score: bool = True) -> list[str]:
    """
    Format the result table header and divider.

    Args:
        show_score (bool): Whether to include the SCORE column.

    Returns:
        list[str]: A list of two strings: header line and divider line.
    """
    if show_score:
        header = (
            f"{'CODE':<{FIELD_WIDTHS['code']}} "
            f"{'CHAR':<{FIELD_WIDTHS['char']}} "
            f"{'NAME':<{FIELD_WIDTHS['name']}} "
            f"{'SCORE':>{FIELD_WIDTHS['score']}}"
        )
    else:
        header = (
            f"{'CODE':<{FIELD_WIDTHS['code']}} "
            f"{'CHAR':<{FIELD_WIDTHS['char']}} "
            f"{'NAME':<{FIELD_WIDTHS['name']}}"
        )

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
    score_str = f"{score:>6.3f}" if score is not None else " " * FIELD_WIDTHS["score"]

    return (
        f"{code_str:<{FIELD_WIDTHS['code']}} "
        f"{char:<{FIELD_WIDTHS['char']}} "
        f"{name_str:<{FIELD_WIDTHS['name']}} "
        f"{score_str:<{FIELD_WIDTHS['score']}}"
    )


def format_all_results(
    matches: list[CharMatch],
    *,
    use_color: bool = False,
    show_score: bool = True,
) -> list[str]:
    """
    Format a list of CharMatch dictionaries into styled output lines.

    This builds the result header followed by formatted rows for each result,
    applying color styling if requested.

    Args:
        matches (list[CharMatch]): List of character match dictionaries.
        use_color (bool): Whether to apply color styling to the output lines.
        show_score (bool): Whether to display the score column.

    Returns:
        list[str]: List of formatted lines ready for display or logging.
    """
    lines = format_result_header(show_score=show_score)

    for match in matches:
        lines.append(_safe_format_match(match, use_color=use_color, show_score=show_score))

    return lines


def _safe_format_match(match: CharMatch, *, use_color: bool, show_score: bool) -> str:
    """
    Format a CharMatch safely, returning a colorized or plain line.

    Args:
        match (CharMatch): A single match result.
        use_color (bool): Whether to colorize output.
        show_score (bool): Whether to include the score column.

    Returns:
        str: Formatted line (with or without color).
    """
    try:
        code = match["code_int"]
        char = match["char"]
        name = match["name"]
        score = match.get("score") if show_score else None
        row = format_result_row(code, char, name, score)
        return format_result_line(row, use_color=use_color)
    except (KeyError, ValueError, TypeError) as exc:
        error_msg = f"[Error formatting match: {exc!r}] → {match!r}"
        log_optionally_echo(
            error_msg,
            level="debug",
            show=False,
            style=lambda m: format_debug(m, use_color=use_color),
        )
        return format_result_line(error_msg, use_color=use_color)


def matchtuple_to_charmatch(mt: MatchTuple) -> CharMatch:
    """
    Convert a MatchTuple to a display-friendly CharMatch dictionary.

    Args:
        mt (MatchTuple): Match tuple containing match metadata.

    Returns:
        CharMatch: Dictionary with stringified display fields and raw score.
    """
    code_str = f"U+{mt.code:04X}"
    return {
        "code": code_str,
        "code_int": mt.code,
        "char": mt.char,
        "name": mt.name,
        "score": mt.score,
    }


def display_result_lines(
    lines: Iterable[str], *, use_color: bool | str = DEFAULT_COLOR_MODE
) -> None:
    """
    Display a list of result lines to the terminal without log-style prefixes.

    Args:
        lines (list[str]): The formatted output lines to print.
        use_color (bool): Whether to allow ANSI color codes.
    """
    for line in lines:
        # Already formatted (e.g., with color if needed), so direct print
        sys.stdout.write((line if use_color else strip_color_codes(line)) + "\n")
        sys.stdout.flush()
