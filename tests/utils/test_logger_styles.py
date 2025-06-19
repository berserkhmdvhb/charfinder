"""Tests for charfinder.utils.logger_styles module."""

from __future__ import annotations

import pytest

from charfinder.utils.logger_styles import (
    format_debug,
    format_error,
    format_info,
    format_settings,
    format_success,
    format_warning,
)
from collections.abc import Callable
from colorama import Style
from charfinder.config.types import FormatterFunc


@pytest.mark.parametrize(
    "func,text,expected_prefix_colored,expected_prefix_plain",
    [
        (format_debug, "debugging", "[DEBUG]", "[DEBUG]"),
        (format_info, "info msg", "[INFO]", "[INFO]"),
        (format_warning, "warn now", "[WARNING]", "[WARNING]"),
        (format_error, "fail", "[ERROR]", "[ERROR]"),
        (format_settings, "conf", "[SETTINGS]", "[SETTINGS]"),
        (format_success, "done", "[OK]", "[OK]"),
    ],
)
def test_format_functions_with_and_without_color(
    func: FormatterFunc,  # Updated to use FormatterFunc
    text: str,
    expected_prefix_colored: str,
    expected_prefix_plain: str,
) -> None:
    """Each formatter should produce correct output with and without color."""
    colored_output = func(text, use_color=True)
    plain_output = func(text, use_color=False)

    assert colored_output.endswith(text)
    assert plain_output == f"{expected_prefix_plain} {text}"
    assert expected_prefix_colored in colored_output
    assert "\033[" in colored_output  # ANSI color check


def test_color_constants_are_ansi_sequences() -> None:
    """Color constants should be valid ANSI escape sequences."""
    from charfinder.utils import logger_styles as ls

    # Check all color constants
    color_constants = [
        ls.COLOR_HEADER,
        ls.COLOR_CODELINE,
        ls.COLOR_ERROR,
        ls.COLOR_INFO,
        ls.COLOR_SUCCESS,
        ls.COLOR_WARNING,
        ls.COLOR_DEBUG,
        ls.COLOR_SETTINGS,
        ls.RESET,
    ]
    
    for color in color_constants:
        assert isinstance(color, str)
        assert color.startswith("\033[")  # Ensure it's an ANSI escape sequence
        assert color.endswith(Style.RESET_ALL) or color.endswith("m")  # Ensure it ends with a reset or valid ANSI m sequence
