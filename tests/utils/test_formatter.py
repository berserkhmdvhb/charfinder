"""
Unit tests for formatter.py in charfinder.utils.
Covers formatting functions, color wrapping, and header/row formatting.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import sys
from io import StringIO
from types import SimpleNamespace
from typing import Callable

import pytest
from colorama import Fore, Style

from charfinder.utils import formatter as F

# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture(autouse=True)
def init_colorama() -> None:
    """Ensure colorama is initialized cleanly before each test."""
    from colorama import init
    init(autoreset=True)


# ---------------------------------------------------------------------
# _color_wrap
# ---------------------------------------------------------------------

def test_color_wrap_with_color() -> None:
    """Test _color_wrap applies color when use_color=True."""
    result = F._color_wrap("test", Fore.RED, use_color=True)
    expected = f"{Fore.RED}test{Style.RESET_ALL}"
    assert result == expected


def test_color_wrap_without_color() -> None:
    """Test _color_wrap returns plain text when use_color=False."""
    result = F._color_wrap("test", Fore.RED, use_color=False)
    assert result == "test"


# ---------------------------------------------------------------------
# should_use_color
# ---------------------------------------------------------------------

def test_should_use_color_always() -> None:
    """Test 'always' mode forces color usage."""
    assert F.should_use_color("always") is True


def test_should_use_color_never() -> None:
    """Test 'never' mode disables color usage."""
    assert F.should_use_color("never") is False


def test_should_use_color_auto(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test 'auto' mode reflects sys.stdout.isatty()."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    assert F.should_use_color("auto") is True
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    assert F.should_use_color("auto") is False


# ---------------------------------------------------------------------
# format_result_line
# ---------------------------------------------------------------------

def test_format_result_line_colored() -> None:
    """Test format_result_line applies yellow color when enabled."""
    line = "result"
    formatted = F.format_result_line(line, use_color=True)
    expected = f"{Fore.YELLOW}result{Style.RESET_ALL}"
    assert formatted == expected


def test_format_result_line_plain() -> None:
    """Test format_result_line returns plain line when color disabled."""
    line = "result"
    formatted = F.format_result_line(line, use_color=False)
    assert formatted == "result"


# ---------------------------------------------------------------------
# format_result_header
# ---------------------------------------------------------------------

def test_format_result_header_with_score() -> None:
    """Test header and divider line when score column is shown."""
    header, divider = F.format_result_header(has_score=True)
    assert "CODE" in header and "SCORE" in header
    assert len(divider) == len(header)


def test_format_result_header_without_score() -> None:
    """Test header and divider when score column is hidden."""
    header, divider = F.format_result_header(has_score=False)
    assert "CODE" in header and "SCORE" not in header
    assert len(divider) == len(header)


# ---------------------------------------------------------------------
# format_result_row
# ---------------------------------------------------------------------

def test_format_result_row_with_score() -> None:
    """Test formatting of result row with a score."""
    row = F.format_result_row(0x1F600, "😀", "GRINNING FACE", 0.98765)
    assert "U+1F600" in row
    assert "😀" in row
    assert "GRINNING FACE" in row
    assert "0.988" in row  # Rounded


def test_format_result_row_without_score() -> None:
    """Test result row formatting when score is None."""
    row = F.format_result_row(0x1F600, "😀", "GRINNING FACE", None)
    assert "U+1F600" in row
    assert "0.988" not in row


# ---------------------------------------------------------------------
# echo and log_optionally_echo (mocked)
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


def test_echo_logs_and_prints(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test echo writes styled message and logs it."""
    logger = fake_logger()
    monkeypatch.setattr("charfinder.utils.logger_setup.get_logger", lambda: logger)
    stream = StringIO()

    F.echo("test message", str.upper, stream=stream, log=True, log_method="info")

    assert stream.getvalue().strip() == "TEST MESSAGE"
    assert "info" in logger._calls
    assert logger._calls["info"] == ["test message"]


def test_echo_invalid_log_method(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test echo raises ValueError for invalid log method."""
    logger = fake_logger()
    monkeypatch.setattr("charfinder.utils.logger_setup.get_logger", lambda: logger)
    with pytest.raises(ValueError, match="Invalid log_method: foobar"):
        F.echo("oops", str, log=True, log_method="foobar")


def test_echo_missing_log_method(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test echo raises ValueError if log_method is missing."""
    logger = fake_logger()
    monkeypatch.setattr("charfinder.utils.logger_setup.get_logger", lambda: logger)
    with pytest.raises(ValueError, match="log_method must be provided if log=True"):
        F.echo("oops", str, log=True, log_method=None)


def test_log_optionally_echo_logs_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test log_optionally_echo logs but does not print when show=False."""
    logger = fake_logger()
    monkeypatch.setattr("charfinder.utils.logger_setup.get_logger", lambda: logger)

    F.log_optionally_echo("log only", level="info", show=False)
    assert "info" in logger._calls
    assert logger._calls["info"] == ["log only"]


def test_log_optionally_echo_logs_and_prints(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test log_optionally_echo logs and prints styled message."""
    logger = fake_logger()
    monkeypatch.setattr("charfinder.utils.logger_setup.get_logger", lambda: logger)
    stream = StringIO()

    F.log_optionally_echo("hi", level="warning", show=True, stream=stream, style=str.lower)
    assert stream.getvalue().strip() == "hi"
    assert "warning" in logger._calls
