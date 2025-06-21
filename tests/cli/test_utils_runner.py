"""Tests for cli.utils_runner.py."""

from __future__ import annotations

from argparse import Namespace
from io import StringIO
import logging
from pathlib import Path
from typing import Callable
from unittest.mock import patch, MagicMock

import pytest

from charfinder.cli import utils_runner
from charfinder.cli.handlers import get_version
from charfinder.config.constants import EXIT_CANCELLED, EXIT_ERROR, EXIT_SUCCESS
from charfinder.config.types import FuzzyConfig, MatchResult


@pytest.fixture(autouse=True)
def _use_isolated_root(setup_test_root: Callable[[], Path]) -> None:
    """Ensure CHARFINDER_ROOT_DIR_FOR_TESTS is isolated for all tests."""
    setup_test_root()

# ---------------------------------------------------------------------
# resolve_final_query
# ---------------------------------------------------------------------

def test_resolve_final_query_option_query_takes_precedence() -> None:
    """Uses --query over positional arguments if both are present."""
    args = Namespace(option_query=["A"], positional_query=["B"])
    result = utils_runner.resolve_final_query(args)
    assert result == "A"

def test_resolve_final_query_falls_back_to_positional() -> None:
    """Falls back to positional arguments when --query is empty."""
    args = Namespace(option_query=[], positional_query=["C", "D"])
    result = utils_runner.resolve_final_query(args)
    assert result == "C D"

def test_resolve_final_query_strips_whitespace() -> None:
    """Strips whitespace from the final query."""
    args = Namespace(option_query=["   X  "], positional_query=[])
    result = utils_runner.resolve_final_query(args)
    assert result == "X"

# ---------------------------------------------------------------------
# auto_enable_debug
# ---------------------------------------------------------------------

def test_auto_enable_debug_enables_if_env_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """Enables args.debug if CHARFINDER_DEBUG_ENV_LOAD=1 and debug is False."""
    monkeypatch.setenv("CHARFINDER_DEBUG_ENV_LOAD", "1")
    args = Namespace(debug=False)
    utils_runner.auto_enable_debug(args)
    assert args.debug is True

def test_auto_enable_debug_respects_existing_flag() -> None:
    """Does not override debug if already set to True."""
    args = Namespace(debug=True)
    utils_runner.auto_enable_debug(args)
    assert args.debug is True

def test_auto_enable_debug_does_nothing_if_env_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    """Leaves debug as False when CHARFINDER_DEBUG_ENV_LOAD is not set."""
    monkeypatch.delenv("CHARFINDER_DEBUG_ENV_LOAD", raising=False)
    args = Namespace(debug=False)
    utils_runner.auto_enable_debug(args)
    assert args.debug is False

# ---------------------------------------------------------------------
# build_fuzzy_config_from_args
# ---------------------------------------------------------------------

def test_build_fuzzy_config_from_args() -> None:
    """Correctly builds FuzzyConfig from argparse args."""
    args = Namespace(fuzzy_algo="token_sort_ratio", fuzzy_match_mode="hybrid")
    result = utils_runner.build_fuzzy_config_from_args(args)
    assert isinstance(result, FuzzyConfig)
    assert result.fuzzy_algo == "token_sort_ratio"
    assert result.fuzzy_match_mode == "hybrid"

# ---------------------------------------------------------------------
# handle_cli_workflow
# ---------------------------------------------------------------------

@patch("charfinder.cli.utils_runner.echo")
@patch("charfinder.cli.utils_runner.get_version", return_value="TEST_VERSION")
@patch("charfinder.cli.utils_runner.teardown_logger")
@patch("charfinder.cli.utils_runner.handle_find_chars")
@patch("charfinder.cli.utils_runner.get_environment", return_value="DEV")
def test_handle_cli_workflow_success(
    mock_get_environment: MagicMock,
    mock_handle_find_chars: MagicMock,
    mock_teardown_logger: MagicMock,
    mock_get_version: MagicMock,
    mock_echo: MagicMock,
) -> None:
    """Runs CLI workflow successfully and emits correct echo message."""
    args = Namespace(verbose=True, debug=False, color="auto", threshold=0.75)
    mock_handle_find_chars.return_value = MatchResult(exit_code=EXIT_SUCCESS, match_info=None)

    exit_code = utils_runner.handle_cli_workflow(args, query_str="✓", use_color=True)

    assert exit_code == EXIT_SUCCESS

    # Find the echo call that contains the version log
    called_msgs = [call.args[0] for call in mock_echo.call_args_list]
    debug_print = "\n".join(called_msgs)
    print("---- Echo Messages ----")
    print(debug_print)
    print("------------------------")

    assert any("CharFinder TEST_VERSION CLI started" in msg for msg in called_msgs)

@patch("charfinder.cli.utils_runner.echo")
@patch("charfinder.cli.utils_runner.get_logger")
@patch("charfinder.cli.utils_runner.teardown_logger")
@patch("charfinder.cli.utils_runner.handle_find_chars", side_effect=KeyboardInterrupt)
@patch("charfinder.cli.utils_runner.get_environment", return_value="DEV")
def test_handle_cli_workflow_keyboard_interrupt(
    mock_env: MagicMock,
    mock_handler: MagicMock,
    mock_teardown: MagicMock,
    mock_logger: MagicMock,
    mock_echo: MagicMock,
) -> None:
    """Gracefully handles Ctrl+C and returns EXIT_CANCELLED."""
    args = Namespace(verbose=True, debug=False, color="auto", threshold=0.75)

    exit_code = utils_runner.handle_cli_workflow(args, query_str="abc", use_color=True)

    assert exit_code == EXIT_CANCELLED

    # Validate echo was called with the right message
    called_msgs = [call.args[0].lower() for call in mock_echo.call_args_list]
    print("---- Echo Output ----")
    print("\n".join(called_msgs))
    print("----------------------")
    assert any("interrupted by user" in msg for msg in called_msgs)


@patch("charfinder.cli.utils_runner.get_logger")
@patch("charfinder.cli.utils_runner.teardown_logger")
@patch("charfinder.cli.utils_runner.handle_find_chars", side_effect=RuntimeError("BOOM"))
@patch("charfinder.cli.utils_runner.get_environment", return_value="UAT")
def test_handle_cli_workflow_unhandled_exception_debug_on(
    mock_env: MagicMock,
    mock_handler: MagicMock,
    mock_teardown: MagicMock,
    mock_logger: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Handles unexpected errors and prints full traceback when debug=True."""
    args = Namespace(verbose=True, debug=True, color="auto", threshold=0.75)

    exit_code = utils_runner.handle_cli_workflow(args, query_str="fail", use_color=True)
    captured = capsys.readouterr()

    print("---- STDERR ----")
    print(captured.err)
    print("---- END STDERR ----")

    assert exit_code == EXIT_ERROR
    assert "Unhandled error during CLI execution" in captured.err
    assert "RuntimeError: BOOM" in captured.err
