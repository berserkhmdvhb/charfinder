"""Tests for cli.utils_runner.py.

This file validates the CLI entrypoint behavior in utils_runner,
including workflow execution and logging configuration.
"""

from __future__ import annotations

# ---------------------------------------------------------------------
# Imports 
# ---------------------------------------------------------------------

from pathlib import Path
from unittest.mock import patch, MagicMock
from argparse import Namespace
from typing import Callable
import pytest

from charfinder.cli import utils_runner
from charfinder.cli.handlers import get_version
from charfinder.config.types import (
    FuzzyConfig,
    MatchResult,
    MatchDiagnosticsInfo
)    
from charfinder.config.constants import (
    EXIT_SUCCESS,
    EXIT_CANCELLED,
    EXIT_ERROR,
)    
from charfinder.config.messages import (
    MSG_ERROR_UNHANDLED_EXCEPTION,
    MSG_WARNING_PROD_ENV,
    MSG_WARNING_INTERRUPTED

)


# ---------------------------------------------------------------------
# Autouse Fixture: Isolate CHARFINDER_ROOT_DIR_FOR_TESTS for this module
# ---------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _use_isolated_root(setup_test_root: Callable[[], Path]) -> None:
    """Ensure CHARFINDER_ROOT_DIR_FOR_TESTS is isolated for all tests."""
    setup_test_root()


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------

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
    called_msgs = [call.kwargs.get("msg") for call in mock_echo.call_args_list]
    assert any(isinstance(msg, str) and "CharFinder TEST_VERSION CLI started" in msg for msg in called_msgs)


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

    # Validate echo was called with a message mentioning interruption
    called_msgs = [call.kwargs.get("msg") for call in mock_echo.call_args_list]
    assert any(isinstance(msg, str) and MSG_WARNING_INTERRUPTED in msg for msg in called_msgs)


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

    assert exit_code == EXIT_ERROR
    assert MSG_ERROR_UNHANDLED_EXCEPTION in captured.err
    assert "RuntimeError: BOOM" in captured.err

# ---------------------------------------------------------------------
# handle_cli_workflow – PROD environment warning
# ---------------------------------------------------------------------

@patch("charfinder.cli.utils_runner.echo")
@patch("charfinder.cli.utils_runner.get_logger")
@patch("charfinder.cli.utils_runner.teardown_logger")
@patch("charfinder.cli.utils_runner.handle_find_chars")
@patch("charfinder.cli.utils_runner.is_prod", return_value=True)
def test_handle_cli_workflow_warns_in_prod(
    mock_is_prod: MagicMock,
    mock_handler: MagicMock,
    mock_teardown: MagicMock,
    mock_logger: MagicMock,
    mock_echo: MagicMock,
) -> None:
    """Covers warning when CHARFINDER_ENV is PROD."""
    from charfinder.config.messages import MSG_WARNING_PROD_ENV

    args = Namespace(verbose=True, debug=False, color="auto", threshold=0.75)
    mock_handler.return_value = MatchResult(exit_code=EXIT_SUCCESS, match_info=None)

    exit_code = utils_runner.handle_cli_workflow(args, query_str="prod", use_color=True)
    assert exit_code == EXIT_SUCCESS

    called_msgs = [call.kwargs.get("msg") for call in mock_echo.call_args_list]
    assert any(MSG_WARNING_PROD_ENV in msg for msg in called_msgs if isinstance(msg, str))
    
# ---------------------------------------------------------------------
# handle_cli_workflow – debug diagnostics print when args.debug = True
# ---------------------------------------------------------------------

@patch("charfinder.cli.utils_runner.print_debug_diagnostics")
@patch("charfinder.cli.utils_runner.get_logger")
@patch("charfinder.cli.utils_runner.teardown_logger")
@patch("charfinder.cli.utils_runner.handle_find_chars")
@patch("charfinder.cli.utils_runner.get_environment", return_value="DEV")
def test_handle_cli_workflow_prints_debug_diagnostics(
    mock_env: MagicMock,
    mock_handler: MagicMock,
    mock_teardown: MagicMock,
    mock_logger: MagicMock,
    mock_print_debug: MagicMock,
) -> None:
    """Covers print_debug_diagnostics when debug=True and successful run."""
    args = Namespace(verbose=False, debug=True, color="auto", threshold=0.75)
    mock_handler.return_value = MatchResult(
        exit_code=EXIT_SUCCESS,
        match_info=MatchDiagnosticsInfo(
            fuzzy=True,
            fuzzy_was_used=True,
            fuzzy_algo="token_sort_ratio",
            fuzzy_match_mode="basic",
            prefer_fuzzy=True,
            exact_match_mode="strict",
            threshold=0.75,
            hybrid_agg_fn=None,
        ),
    )
    exit_code = utils_runner.handle_cli_workflow(args, query_str="debug", use_color=True)
    assert exit_code == EXIT_SUCCESS
    mock_print_debug.assert_called_once()
