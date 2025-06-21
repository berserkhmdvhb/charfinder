"""Tests for cli/diagnostics_match.py – fuzzy/exact diagnostics output logic."""

from argparse import Namespace
from typing import Callable, List

import pytest

from charfinder.cli import diagnostics_match
from charfinder.config.types import MatchDiagnosticsInfo


# ---------------------------------------------------------------------
# Fixtures and Helpers
# ---------------------------------------------------------------------


@pytest.fixture()
def mock_echo(monkeypatch: pytest.MonkeyPatch) -> List[str]:
    """Patch `echo()` to record debug output for assertions."""
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

    monkeypatch.setattr("charfinder.cli.diagnostics_match.echo", fake_echo)
    return output


# ---------------------------------------------------------------------
# print_exact_match_diagnostics
# ---------------------------------------------------------------------


def test_print_exact_match_diagnostics_outputs_expected_lines(mock_echo: List[str]) -> None:
    """Ensure exact match diagnostics prints correct lines."""
    args = Namespace(exact_match_mode="prefix")
    diagnostics_match.print_exact_match_diagnostics(args, use_color=True, show=True)

    expected_lines = [
        "=== MATCH STRATEGY ===",
        "Exact match strategy executed.",
        "Exact match mode: 'prefix'",
        "=== END MATCH STRATEGY ===",
    ]
    assert mock_echo == expected_lines


# ---------------------------------------------------------------------
# print_fuzzy_match_diagnostics
# ---------------------------------------------------------------------


def test_print_fuzzy_match_diagnostics_non_hybrid(mock_echo: List[str]) -> None:
    """Ensure non-hybrid fuzzy diagnostics prints correct values."""
    info = MatchDiagnosticsInfo(
        fuzzy=True,
        fuzzy_was_used=True,
        fuzzy_match_mode="single",
        fuzzy_algo="token_sort_ratio",
        hybrid_agg_fn=None,
        prefer_fuzzy=True,
        exact_match_mode="any",
        threshold=0.75,
    )
    diagnostics_match.print_fuzzy_match_diagnostics(info, use_color=True, show=True)

    assert "Fuzzy algorithm: 'token_sort_ratio'" in mock_echo


def test_print_fuzzy_match_diagnostics_hybrid(mock_echo: List[str]) -> None:
    """Ensure hybrid fuzzy diagnostics prints all weights and settings."""
    info = MatchDiagnosticsInfo(
        fuzzy=True,
        fuzzy_was_used=True,
        fuzzy_match_mode="hybrid",
        fuzzy_algo="hybrid",
        hybrid_agg_fn="weighted_avg",
        prefer_fuzzy=True,
        exact_match_mode="any",
        threshold=0.75,
    )
    diagnostics_match.print_fuzzy_match_diagnostics(info, use_color=False, show=True)

    assert "Fuzzy match strategy executed." in mock_echo
    assert "Fuzzy algorithms used:" in mock_echo
    assert "Aggregation function: 'weighted_avg'" in mock_echo
    assert "=== END MATCH STRATEGY ===" in mock_echo


# ---------------------------------------------------------------------
# print_match_diagnostics dispatcher
# ---------------------------------------------------------------------


def test_print_match_diagnostics_none(mock_echo: List[str]) -> None:
    """Should return early and output nothing if match_info is None."""
    args = Namespace(exact_match_mode="any")
    diagnostics_match.print_match_diagnostics(args, None, use_color=True, show=True)
    assert mock_echo == []


def test_print_match_diagnostics_exact_used(mock_echo: List[str]) -> None:
    """Should output exact match info if fuzzy=False."""
    info = MatchDiagnosticsInfo(
        fuzzy=False,
        fuzzy_was_used=False,
        fuzzy_match_mode="single",
        fuzzy_algo="token_sort_ratio",
        hybrid_agg_fn=None,
        prefer_fuzzy=False,
        exact_match_mode="strict",
        threshold=1.0,
    )
    args = Namespace(exact_match_mode="strict")
    diagnostics_match.print_match_diagnostics(args, info, use_color=True, show=True)

    assert "Exact match strategy executed." in mock_echo


def test_print_match_diagnostics_fuzzy_used(mock_echo: List[str]) -> None:
    """Should dispatch to fuzzy if fuzzy_was_used=True."""
    info = MatchDiagnosticsInfo(
        fuzzy=True,
        fuzzy_was_used=True,
        fuzzy_match_mode="single",
        fuzzy_algo="token_sort_ratio",
        hybrid_agg_fn=None,
        prefer_fuzzy=True,
        exact_match_mode="any",
        threshold=0.75,
    )
    args = Namespace(exact_match_mode="any")
    diagnostics_match.print_match_diagnostics(args, info, use_color=True, show=True)

    assert "Fuzzy match strategy executed." in mock_echo


def test_print_match_diagnostics_fuzzy_skipped_but_preferred(mock_echo: List[str]) -> None:
    """Should explain that fuzzy was preferred but exact used."""
    info = MatchDiagnosticsInfo(
        fuzzy=True,
        fuzzy_was_used=False,
        fuzzy_match_mode="single",
        fuzzy_algo="token_sort_ratio",
        hybrid_agg_fn=None,
        prefer_fuzzy=True,
        exact_match_mode="any",
        threshold=0.8,
    )
    args = Namespace(exact_match_mode="any")
    diagnostics_match.print_match_diagnostics(args, info, use_color=False, show=True)

    assert "Fuzzy was preferred but exact match was used." in mock_echo


def test_print_match_diagnostics_fuzzy_skipped_not_preferred(mock_echo: List[str]) -> None:
    """Should explain fuzzy was requested but skipped due to exact match."""
    info = MatchDiagnosticsInfo(
        fuzzy=True,
        fuzzy_was_used=False,
        fuzzy_match_mode="single",
        fuzzy_algo="token_sort_ratio",
        hybrid_agg_fn=None,
        prefer_fuzzy=False,
        exact_match_mode="any",
        threshold=0.85,
    )
    args = Namespace(exact_match_mode="any")
    diagnostics_match.print_match_diagnostics(args, info, use_color=False, show=True)

    assert "Fuzzy requested but skipped due to exact match success." in mock_echo
