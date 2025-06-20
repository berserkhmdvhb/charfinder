"""
Unit tests for formatter.py in charfinder.utils.
Covers formatting functions, color wrapping, and header/row formatting.
"""

from __future__ import annotations

import sys
from io import StringIO
from types import SimpleNamespace
from typing import Callable

import pytest
from colorama import Fore, Style

from charfinder.utils import formatter as F
from charfinder.config.constants import VALID_COLOR_MODES

# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture(autouse=True)
def init_colorama() -> None:
    """Ensure colorama is initialized cleanly before each test (resets ANSI)."""
    from colorama import init
    init(autoreset=True)



# ---------------------------------------------------------------------
# _color_wrap
# ---------------------------------------------------------------------

def test_color_wrap_with_color() -> None:
    """_color_wrap applies color when use_color=True."""
    result = F._color_wrap("test", Fore.RED, use_color=True)
    expected = f"{Fore.RED}test{Style.RESET_ALL}"
    assert result == expected


def test_color_wrap_without_color() -> None:
    """_color_wrap returns plain text when use_color=False."""
    result = F._color_wrap("test", Fore.RED, use_color=False)
    assert result == "test"


# ---------------------------------------------------------------------
# should_use_color
# ---------------------------------------------------------------------




@pytest.mark.parametrize("color_mode", VALID_COLOR_MODES)
def test_should_use_color_behavior(monkeypatch: pytest.MonkeyPatch, color_mode: str) -> None:
    """Test should_use_color behavior for each color mode."""
    if color_mode == "auto":
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
        assert F.should_use_color("auto") is True
        monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
        assert F.should_use_color("auto") is False
    elif color_mode == "always":
        assert F.should_use_color(color_mode) is True
    elif color_mode == "never":
        assert F.should_use_color(color_mode) is False


# ---------------------------------------------------------------------
# format_result_line
# ---------------------------------------------------------------------

def test_format_result_line_colored() -> None:
    """format_result_line applies yellow color when enabled."""
    line = "result"
    formatted = F.format_result_line(line, use_color=True)
    expected = f"{Fore.YELLOW}result{Style.RESET_ALL}"
    assert formatted == expected


def test_format_result_line_plain() -> None:
    """format_result_line returns plain line when color disabled."""
    line = "result"
    formatted = F.format_result_line(line, use_color=False)
    assert formatted == "result"


# ---------------------------------------------------------------------
# format_result_header
# ---------------------------------------------------------------------

def test_format_result_header_with_score() -> None:
    """Header and divider line when score column is shown."""
    header, divider = F.format_result_header(show_score=True)
    assert "CODE" in header and "SCORE" in header
    assert len(divider) == len(header)


def test_format_result_header_without_score() -> None:
    """Header and divider when score column is hidden."""
    header, divider = F.format_result_header(show_score=False)
    assert "CODE" in header and "SCORE" not in header
    assert len(divider) == len(header)


# ---------------------------------------------------------------------
# format_result_row
# ---------------------------------------------------------------------

def test_format_result_row_with_score() -> None:
    """Formatting of result row with a score."""
    row = F.format_result_row(0x1F600, "😀", "GRINNING FACE", 0.98765)
    assert "U+1F600" in row
    assert "😀" in row
    assert "GRINNING FACE" in row
    assert "0.988" in row  # Rounded


def test_format_result_row_without_score() -> None:
    """Result row formatting when score is None."""
    row = F.format_result_row(0x1F600, "😀", "GRINNING FACE", None)
    assert "U+1F600" in row
    assert "0.988" not in row


# ---------------------------------------------------------------------
# echo and log_optionally_echo (mocked logger, real stream)
# ---------------------------------------------------------------------

def fake_logger() -> SimpleNamespace:
    """Create a fake logger with counters for method calls."""
    calls: dict[str, list[str]] = {}

    def make_mock_method(name: str) -> Callable[[str], None]:
        def mock(msg: str) -> None:
            calls.setdefault(name, []).append(msg)
        return mock

    return SimpleNamespace(
        debug=make_mock_method("debug"),
        info=make_mock_method("info"),
        warning=make_mock_method("warning"),
        error=make_mock_method("error"),
        exception=make_mock_method("exception"),
        _calls=calls,
    )


def test_echo_logs_and_prints(monkeypatch: pytest.MonkeyPatch, log_stream: StringIO) -> None:
    """echo writes styled message and logs it."""
    logger = fake_logger()
    monkeypatch.setattr("charfinder.utils.logger_setup.get_logger", lambda: logger)

    F.echo("test message", str.upper, stream=log_stream, log=True, log_method="info")

    assert log_stream.getvalue().strip() == "TEST MESSAGE"
    assert "info" in logger._calls
    assert logger._calls["info"] == ["test message"]


def test_echo_applies_style(monkeypatch: pytest.MonkeyPatch, log_stream: StringIO) -> None:
    """echo should apply custom style function to output stream."""
    logger = fake_logger()
    monkeypatch.setattr("charfinder.utils.logger_setup.get_logger", lambda: logger)

    def star_wrap(msg: str) -> str:
        return f"***{msg}***"

    F.echo("styled", star_wrap, stream=log_stream, show=True, log=False)
    assert log_stream.getvalue().strip() == "***styled***"


def test_echo_invalid_log_method(monkeypatch: pytest.MonkeyPatch) -> None:
    """echo raises ValueError for invalid log method."""
    logger = fake_logger()
    monkeypatch.setattr("charfinder.utils.logger_setup.get_logger", lambda: logger)

    with pytest.raises(ValueError, match="Invalid log_method: foobar"):
        F.echo("oops", str, log=True, log_method="foobar")


def test_echo_missing_log_method(monkeypatch: pytest.MonkeyPatch) -> None:
    """echo raises ValueError if log_method is missing when log=True."""
    logger = fake_logger()
    monkeypatch.setattr("charfinder.utils.logger_setup.get_logger", lambda: logger)

    with pytest.raises(ValueError, match="log_method must be provided if log=True"):
        F.echo("oops", str, log=True, log_method=None)


def test_log_optionally_echo_logs_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """log_optionally_echo logs but does not print when show=False."""
    logger = fake_logger()
    monkeypatch.setattr("charfinder.utils.logger_setup.get_logger", lambda: logger)

    F.log_optionally_echo("log only", level="info", show=False)
    assert "info" in logger._calls
    assert logger._calls["info"] == ["log only"]


def test_log_optionally_echo_logs_and_prints(monkeypatch: pytest.MonkeyPatch, log_stream: StringIO) -> None:
    """log_optionally_echo logs and prints styled message."""
    logger = fake_logger()
    monkeypatch.setattr("charfinder.utils.logger_setup.get_logger", lambda: logger)

    F.log_optionally_echo("hi", level="warning", show=True, stream=log_stream, style=str.lower)
    assert log_stream.getvalue().strip() == "hi"
    assert "warning" in logger._calls
