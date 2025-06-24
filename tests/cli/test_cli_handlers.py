"""Tests for cli/handlers.py."""

from __future__ import annotations

from argparse import Namespace
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Callable, Any
from io import StringIO
from unittest.mock import patch, MagicMock
import pytest

from charfinder.config.types import MatchDiagnosticsInfo, MatchResult
from charfinder.cli.handlers import (
    get_version,
    handle_empty_query,
    handle_keyboard_interrupt,
    build_match_result,
    _run_query_and_return,
    handle_find_chars,
    SearchParams,
)
from charfinder.config.constants import (
    EXIT_CANCELLED,
    EXIT_INVALID_USAGE,
    EXIT_NO_RESULTS,
    EXIT_SUCCESS,
)
from charfinder.config.messages import (
    MSG_ERROR_EMPTY_QUERY,
    MSG_INFO_SEARCH_CANCELLED,
    MSG_ERROR_UNEXPECTED_EXCEPTION
)

@pytest.fixture(autouse=True)
def _use_isolated_root(setup_test_root: Callable[[], Path]) -> None:
    """Ensure CHARFINDER_ROOT_DIR_FOR_TESTS is isolated for all tests."""
    setup_test_root()


# ---------------------------------------------------------------------
# get_version
# ---------------------------------------------------------------------

def test_get_version_returns_string() -> None:
    result = get_version()
    assert isinstance(result, str)
    assert result


@patch("charfinder.cli.handlers.version", side_effect=PackageNotFoundError)
def test_get_version_package_not_found(mock_version: MagicMock) -> None:
    from charfinder.cli.handlers import get_version

    get_version.cache_clear()  # <-- Clear cached result to allow mock to take effect
    result = get_version()
    assert result == "unknown (not installed)"


# ---------------------------------------------------------------------
# handle_empty_query
# ---------------------------------------------------------------------

def test_handle_empty_query_logs_error() -> None:
    with patch("charfinder.cli.handlers.echo") as mock_echo:
        result = handle_empty_query(use_color=False)
        assert result.exit_code == EXIT_INVALID_USAGE
        assert result.match_info is None

        mock_echo.assert_called_once()
        called_msg = mock_echo.call_args[0][0]
        assert MSG_ERROR_EMPTY_QUERY in called_msg

# ---------------------------------------------------------------------
# handle_keyboard_interrupt
# ---------------------------------------------------------------------

def test_handle_keyboard_interrupt_verbose() -> None:
    with patch("charfinder.cli.handlers.echo") as mock_echo:
        result = handle_keyboard_interrupt(verbose=True, use_color=False)
        assert result.exit_code == EXIT_CANCELLED
        mock_echo.assert_called_once()
        called_msg = mock_echo.call_args[0][0]
        assert MSG_INFO_SEARCH_CANCELLED in called_msg

def test_handle_keyboard_interrupt_silent(log_stream: StringIO) -> None:
    result = handle_keyboard_interrupt(verbose=False, use_color=False)
    assert result.exit_code == EXIT_CANCELLED
    assert log_stream.getvalue() == ""


# ---------------------------------------------------------------------
# build_match_result
# ---------------------------------------------------------------------

def test_build_match_result_returns_structured_info() -> None:
    args = Namespace(
        fuzzy=True,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="basic",
        hybrid_agg_fn=None,
        prefer_fuzzy=True,
        exact_match_mode="strict",
        threshold=0.75,
        normalization_profile="aggressive",
    )

    result = build_match_result(args, fuzzy_used=True, exit_code=EXIT_SUCCESS)
    assert result.exit_code == EXIT_SUCCESS
    assert isinstance(result.match_info, MatchDiagnosticsInfo)
    assert result.match_info is not None
    assert result.match_info.fuzzy_algo == "token_sort_ratio"


def test_build_match_result_hybrid_mode_uses_agg_fn() -> None:
    args = Namespace(
        fuzzy=True,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="hybrid",
        hybrid_agg_fn="mean",
        prefer_fuzzy=False,
        exact_match_mode="loose",
        threshold=0.5,
        normalization_profile="aggressive",
    )
    result = build_match_result(args, fuzzy_used=True, exit_code=EXIT_SUCCESS)
    match_info = result.match_info
    assert match_info is not None
    assert match_info.hybrid_agg_fn == "mean"


# ---------------------------------------------------------------------
# _run_query_and_return
# ---------------------------------------------------------------------

@patch("charfinder.cli.handlers.find_chars_raw")
def test_run_query_json_output(
    mock_find_chars_raw: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    mock_find_chars_raw.return_value = [{"char": "A", "name": "LATIN CAPITAL LETTER A"}]
    args = Namespace(
        format="json",
        fuzzy=True,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="basic",
        exact_match_mode="strict",
        hybrid_agg_fn=None,
        prefer_fuzzy=False,
        threshold=0.8,
        show_score=False,
        normalization_profile="aggressive",
    )
    params = SearchParams(
        query="A",
        fuzzy=True,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="basic",
        exact_match_mode="strict",
        agg_fn=None,
        prefer_fuzzy=False,
        verbose=False,
        debug=False,
        use_color=False,
        threshold=0.8,
        normalization_profile="aggressive",
    )

    result = _run_query_and_return(params, output_format="json", args=args)

    assert result.exit_code == EXIT_SUCCESS
    assert mock_find_chars_raw.called
    out = capsys.readouterr().out
    assert '"name": "LATIN CAPITAL LETTER A"' in out


@patch("charfinder.cli.handlers.find_chars_with_info")
def test_run_query_text_output_with_matches(
    mock_find_with_info: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    mock_find_with_info.return_value = (
        [("A", "LATIN CAPITAL LETTER A", 1.0)],
        True,
    )
    args = Namespace(
        format="text",
        fuzzy=True,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="basic",
        exact_match_mode="strict",
        hybrid_agg_fn=None,
        prefer_fuzzy=False,
        threshold=0.8,
        show_score=True,
        normalization_profile="aggressive",
    )
    params = SearchParams(
        query="A",
        fuzzy=True,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="basic",
        exact_match_mode="strict",
        agg_fn=None,
        prefer_fuzzy=False,
        verbose=False,
        debug=False,
        use_color=False,
        threshold=0.8,
        normalization_profile="aggressive",
    )

    result = _run_query_and_return(params, output_format="text", args=args)

    assert result.exit_code == EXIT_SUCCESS
    assert mock_find_with_info.called
    out = capsys.readouterr().out
    assert "LATIN CAPITAL LETTER A" in out


@patch("charfinder.cli.handlers.find_chars_with_info")
def test_run_query_text_output_no_matches(
    mock_find_with_info: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    mock_find_with_info.return_value = (
        [],
        False,
    )
    args = Namespace(
        format="text",
        fuzzy=True,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="basic",
        exact_match_mode="strict",
        hybrid_agg_fn=None,
        prefer_fuzzy=False,
        threshold=0.8,
        show_score=False,
        normalization_profile="aggressive",
    )
    params = SearchParams(
        query="unknown",
        fuzzy=True,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="basic",
        exact_match_mode="strict",
        agg_fn=None,
        prefer_fuzzy=False,
        verbose=False,
        debug=False,
        use_color=False,
        threshold=0.8,
        normalization_profile="aggressive",
    )

    result = _run_query_and_return(params, output_format="text", args=args)

    assert result.exit_code == EXIT_NO_RESULTS
    out = capsys.readouterr().out
    assert out == ""


# ---------------------------------------------------------------------
# handle_find_chars
# ---------------------------------------------------------------------

def test_handle_find_chars_empty_query() -> None:
    args = Namespace(
        fuzzy=False,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="single",
        exact_match_mode="word-subset",
        hybrid_agg_fn=None,
        prefer_fuzzy=False,
        verbose=False,
        debug=False,
        use_color=False,
        format="text",
        threshold=0.7,
        color="auto",
        normalization_profile="aggressive",
    )
    result = handle_find_chars(args, query_str="")
    assert result.exit_code == EXIT_INVALID_USAGE


@patch("charfinder.cli.handlers.resolve_cli_settings", return_value=("default", False, 0.7))
@patch("charfinder.cli.handlers.validate_fuzzy_match_mode", return_value="basic")
@patch("charfinder.cli.handlers.validate_exact_match_mode", return_value="strict")
@patch("charfinder.cli.handlers._run_query_and_return", side_effect=KeyboardInterrupt)
def test_handle_find_chars_keyboard_interrupt(
    mock_run: MagicMock,
    mock_exact: MagicMock,
    mock_fuzzy: MagicMock,
    mock_settings: MagicMock,
) -> None:
    args = Namespace(
        fuzzy=False,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="basic",
        exact_match_mode="strict",
        hybrid_agg_fn=None,
        prefer_fuzzy=False,
        verbose=False,
        debug=False,
        use_color=False,
        format="text",
        threshold=0.7,
        normalization_profile="aggressive"
    )
    result = handle_find_chars(args, query_str="a")
    assert result.exit_code == EXIT_CANCELLED



@patch("charfinder.cli.handlers.resolve_cli_settings", return_value=("default", False, 0.7))
@patch("charfinder.cli.handlers.validate_fuzzy_match_mode", return_value="basic")
@patch("charfinder.cli.handlers.validate_exact_match_mode", return_value="strict")
@patch("charfinder.cli.handlers._run_query_and_return")
def test_handle_find_chars_success(
    mock_run: MagicMock,
    mock_exact: MagicMock,
    mock_fuzzy: MagicMock,
    mock_settings: MagicMock,
) -> None:
    mock_run.return_value = MatchResult(EXIT_SUCCESS, None)
    args = Namespace(
        fuzzy=False,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="basic",
        exact_match_mode="strict",
        hybrid_agg_fn=None,
        prefer_fuzzy=False,
        verbose=False,
        debug=False,
        use_color=False,
        format="text",
        threshold=0.7,
        normalization_profile="aggressive",
    )
    result = handle_find_chars(args, query_str="hello")
    assert result.exit_code == EXIT_SUCCESS
    mock_run.assert_called_once()


@patch("charfinder.cli.handlers.resolve_cli_settings", return_value=("default", False, 0.7))
@patch("charfinder.cli.handlers.validate_fuzzy_match_mode", return_value="basic")
@patch("charfinder.cli.handlers.validate_exact_match_mode", return_value="strict")
@patch("charfinder.cli.handlers._run_query_and_return", side_effect=RuntimeError("boom"))
@patch("charfinder.cli.handlers.log_optionally_echo")
def test_handle_find_chars_generic_exception(
    mock_log_optionally_echo: MagicMock,
    mock_run: MagicMock,
    mock_exact: MagicMock,
    mock_fuzzy: MagicMock,
    mock_settings: MagicMock,
) -> None:
    args = Namespace(
        fuzzy=False,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="basic",
        exact_match_mode="strict",
        hybrid_agg_fn=None,
        prefer_fuzzy=False,
        verbose=True,
        debug=False,
        use_color=False,
        format="text",
        threshold=0.7,
        normalization_profile="aggressive",
    )
    result = handle_find_chars(args, query_str="fail")

    assert result.exit_code == EXIT_INVALID_USAGE
    mock_log_optionally_echo.assert_called_once()
    call_args = mock_log_optionally_echo.call_args[1]  # kwargs of the call
    msg = call_args.get("msg", "") or call_args.get("message", "")
    assert "unexpected error" in msg.lower()


@patch("charfinder.cli.handlers.resolve_cli_settings", return_value=("default", False, 0.7))
@patch("charfinder.cli.handlers.validate_fuzzy_match_mode", return_value="basic")
@patch("charfinder.cli.handlers.validate_exact_match_mode", return_value="strict")
@patch("charfinder.cli.handlers._run_query_and_return", side_effect=SystemExit(2))
def test_handle_find_chars_reraises_system_exit(
    mock_run: MagicMock,
    mock_exact: MagicMock,
    mock_fuzzy: MagicMock,
    mock_settings: MagicMock,
) -> None:
    """Ensure SystemExit is not swallowed and is re-raised."""
    args = Namespace(
        fuzzy=False,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="basic",
        exact_match_mode="strict",
        hybrid_agg_fn=None,
        prefer_fuzzy=False,
        verbose=True,
        debug=False,
        use_color=False,
        format="text",
        threshold=0.7,
        normalization_profile="aggressive",
    )
    with pytest.raises(SystemExit):
        handle_find_chars(args, query_str="force exit")


def test_handle_find_chars_empty_direct_trigger() -> None:
    args = Namespace(
        fuzzy=False,
        fuzzy_algo="simple_ratio",
        fuzzy_match_mode="basic",
        exact_match_mode="substring",
        hybrid_agg_fn=None,
        prefer_fuzzy=False,
        verbose=False,
        debug=False,
        use_color=True,
        threshold=0.75,
        normalization_profile="raw",
        format="text",
        show_score=None,
    )
    result = handle_find_chars(args, query_str="")
    assert result.exit_code == EXIT_INVALID_USAGE
    assert result.match_info is None


@patch("charfinder.cli.handlers.resolve_cli_settings", return_value=("default", False, 0.7))
@patch("charfinder.cli.handlers.validate_fuzzy_match_mode", return_value="basic")
@patch("charfinder.cli.handlers.validate_exact_match_mode", return_value="strict")
@patch("charfinder.cli.handlers._run_query_and_return")
def test_handle_find_chars_reraises_generator_exit(
    mock_run: MagicMock,
    mock_exact: MagicMock,
    mock_fuzzy: MagicMock,
    mock_settings: MagicMock,
) -> None:
    """Ensure GeneratorExit is re-raised inside the generic exception handler."""
    def raise_generator_exit(*args: Any, **kwargs: Any) -> None:
        raise GeneratorExit()

    mock_run.side_effect = raise_generator_exit

    args = Namespace(
        fuzzy=False,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="basic",
        exact_match_mode="strict",
        hybrid_agg_fn=None,
        prefer_fuzzy=False,
        verbose=True,
        debug=False,
        use_color=False,
        format="text",
        threshold=0.7,
        normalization_profile="aggressive",
    )

    with pytest.raises(GeneratorExit):
        handle_find_chars(args, query_str="trigger")
