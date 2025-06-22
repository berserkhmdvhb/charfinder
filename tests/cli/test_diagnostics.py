"""Tests for cli/diagnostics.py — user-facing debug and .env diagnostics."""

from argparse import Namespace
from pathlib import Path
from typing import Callable, List

import pytest
from _pytest.monkeypatch import MonkeyPatch
from dotenv import set_key

from charfinder.cli import diagnostics
from charfinder.config.types import MatchDiagnosticsInfo
from charfinder.config.messages import (
    MSG_DEBUG_DOTENV_EMPTY,
    MSG_DEBUG_DOTENV_END,
    MSG_DEBUG_DOTENV_READ_ERROR,
    MSG_DEBUG_NO_DOTENV_FOUND,
    MSG_DEBUG_DOTENV_SELECTED,
    MSG_DEBUG_DOTENV_ITEM,
    MSG_DEBUG_OS_ENV_ONLY,
    MSG_DEBUG_SECTION_START,
    MSG_DEBUG_PARSED_ARGS,
    MSG_DEBUG_ARG_ITEM,
    MSG_DEBUG_DOTENV_LOADED_FILES,
    MSG_DEBUG_EXACT_EXECUTED,
    MSG_DEBUG_DOTENV_START,
    MSG_DEBUG_SECTION_END,
    MSG_DEBUG_EXACT_MODE,
)

@pytest.fixture()
def mock_echo(monkeypatch: MonkeyPatch) -> List[str]:
    """Patch `echo()` to capture all diagnostic output."""
    output: List[str] = []

    def fake_echo(
        msg: str,
        *,
        style: Callable[[str], str] | None = None,
        show: bool = True,
        log: bool = True,
        log_method: str = "debug",
    ) -> None:
        output.append(str(msg))

    monkeypatch.setattr("charfinder.cli.diagnostics.echo", fake_echo)
    monkeypatch.setattr("charfinder.cli.diagnostics_match.echo", fake_echo)
    return output


# ---------------------------------------------------------------------
# print_debug_diagnostics
# ---------------------------------------------------------------------


def test_print_debug_diagnostics_outputs_expected(monkeypatch: MonkeyPatch, mock_echo: List[str]) -> None:
    """Should print args, env var, diagnostics, and dotenv info."""
    args = Namespace(verbose=True, debug=True, color="always", exact_match_mode="any")
    monkeypatch.setenv("CHARFINDER_DEBUG_ENV_LOAD", "1")

    diagnostics.print_debug_diagnostics(args, match_info=None, use_color=False, show=True)

    joined = "\n".join(mock_echo)
    assert MSG_DEBUG_SECTION_START in joined
    assert MSG_DEBUG_PARSED_ARGS in joined
    assert MSG_DEBUG_ARG_ITEM.format(key="CHARFINDER_DEBUG_ENV_LOAD", value="1") in joined
    assert MSG_DEBUG_DOTENV_LOADED_FILES in joined
    assert MSG_DEBUG_DOTENV_START in joined
    assert MSG_DEBUG_SECTION_END in joined


def test_print_debug_diagnostics_with_match_info(mock_echo: List[str]) -> None:
    """Should invoke match diagnostics and show exact mode."""
    args = Namespace(exact_match_mode="prefix")
    info = MatchDiagnosticsInfo(
        fuzzy=False,
        fuzzy_was_used=False,
        fuzzy_match_mode="single",
        fuzzy_algo="token_sort_ratio",
        hybrid_agg_fn=None,
        prefer_fuzzy=False,
        exact_match_mode="prefix",
        threshold=1.0,
    )
    diagnostics.print_debug_diagnostics(args, match_info=info, use_color=False, show=True)

    assert MSG_DEBUG_EXACT_EXECUTED in mock_echo
    assert MSG_DEBUG_EXACT_MODE.format(mode="prefix") in mock_echo


# ---------------------------------------------------------------------
# print_dotenv_debug
# ---------------------------------------------------------------------


def test_print_dotenv_debug_with_existing_file(tmp_path: Path, monkeypatch: MonkeyPatch, mock_echo: List[str]) -> None:
    """Should print values from .env file if exists."""
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("CHARFINDER_LOG_MAX_BYTES=123456\nCHARFINDER_ENV=UAT\n")

    monkeypatch.setenv("DOTENV_PATH", str(dotenv_path))
    diagnostics.print_dotenv_debug(use_color=False, show=True)
    print(f"[TEST:] {mock_echo}")
    assert MSG_DEBUG_DOTENV_SELECTED.format(path=dotenv_path) in mock_echo
    assert MSG_DEBUG_DOTENV_ITEM.format(key="CHARFINDER_LOG_MAX_BYTES", value="123456") in mock_echo
    assert MSG_DEBUG_DOTENV_ITEM.format(key="CHARFINDER_ENV", value="UAT") in mock_echo
    assert MSG_DEBUG_DOTENV_END in mock_echo



def test_print_dotenv_debug_with_empty_file(tmp_path: Path, monkeypatch: MonkeyPatch, mock_echo: List[str]) -> None:
    """Should handle empty .env file gracefully."""
    dotenv_path = tmp_path / ".env"
    dotenv_path.touch()

    monkeypatch.setenv("DOTENV_PATH", str(dotenv_path))
    diagnostics.print_dotenv_debug(use_color=False, show=True)

    assert MSG_DEBUG_DOTENV_EMPTY in "\n".join(mock_echo)


def test_print_dotenv_debug_file_missing(monkeypatch: MonkeyPatch, mock_echo: List[str]) -> None:
    """Should report that no .env file is found."""
    monkeypatch.delenv("DOTENV_PATH", raising=False)
    monkeypatch.setenv("CHARFINDER_ROOT_DIR_FOR_TESTS", "/nonexistent")

    diagnostics.print_dotenv_debug(use_color=False, show=True)

    joined = "\n".join(mock_echo)
    assert MSG_DEBUG_NO_DOTENV_FOUND in joined
    assert MSG_DEBUG_OS_ENV_ONLY in joined

def test_print_dotenv_debug_invalid_encoding(tmp_path: Path, monkeypatch: MonkeyPatch, mock_echo: List[str]) -> None:
    """Should catch UnicodeDecodeError gracefully."""
    path = tmp_path / ".env"
    path.write_bytes(b"\xff\xfe\xfd")  # invalid UTF-8

    monkeypatch.setenv("DOTENV_PATH", str(path))
    diagnostics.print_dotenv_debug(use_color=False, show=True)

    # Check that the error was reported
    assert any("Failed to read .env file:" in line for line in mock_echo)
    assert MSG_DEBUG_DOTENV_END in mock_echo
