"""Integration tests for cli_main.py (main CLI entry point)."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest

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


def test_main_displays_help_when_no_args(
    run_cli: Callable[..., tuple[str, str, int]],
) -> None:
    """Calling charfinder with no arguments should display help and exit with code 0."""
    stdout, stderr, code = run_cli()
    assert code == 0
    assert "--query" in stdout
    assert "usage:" in stdout.lower()


def test_main_basic_query_works(
    run_cli: Callable[..., tuple[str, str, int]],
) -> None:
    """charfinder --query A should return results including 'LATIN CAPITAL LETTER A'."""
    stdout, stderr, code = run_cli("--query", "A")
    assert code == 0
    assert "LATIN CAPITAL LETTER A" in stdout
