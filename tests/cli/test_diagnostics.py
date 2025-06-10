"""Unit tests for charfinder.cli.diagnostics."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path
from typing import Callable

import pytest

from charfinder.cli.diagnostics import print_debug_diagnostics, print_dotenv_debug


# ---------------------------------------------------------------------
# print_dotenv_debug basic test
# ---------------------------------------------------------------------


def test_print_dotenv_debug_no_dotenv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    setup_test_root: Callable[[], Path],
    echo_output: Callable[[], str],
) -> None:
    """Test print_dotenv_debug() output when no .env is present."""
    _ = setup_test_root()

    # Force DOTENV_PATH to dummy empty file to isolate test
    dummy_env = tmp_path / ".env"
    dummy_env.write_text("")
    monkeypatch.setenv("DOTENV_PATH", str(dummy_env.resolve()))

    print_dotenv_debug()

    output = echo_output()

    # Match the exact printed line
    assert "=== DOTENV DEBUG ===" in output
    assert f"Selected .env file: {dummy_env}" in output


# ---------------------------------------------------------------------
# print_debug_diagnostics basic smoke test
# ---------------------------------------------------------------------


def test_print_debug_diagnostics_smoke(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    setup_test_root: Callable[[], Path],
    echo_output: Callable[[], str],
) -> None:
    """Basic smoke test for print_debug_diagnostics()."""
    _ = setup_test_root()

    dummy_env = tmp_path / ".env"
    dummy_env.write_text("")
    monkeypatch.setenv("DOTENV_PATH", str(dummy_env.resolve()))

    args = Namespace(
        query="test",
        color="auto",
        debug=True,
        verbose=True,
    )

    print_debug_diagnostics(args, use_color=False)

    output = echo_output()

    assert "DEBUG DIAGNOSTICS" in output
    assert "Parsed args:" in output
    assert "query" in output and "test" in output
    assert "DOTENV DEBUG" in output or "dotenv-debug" in output
    assert f"Selected .env file: {dummy_env}" in output
