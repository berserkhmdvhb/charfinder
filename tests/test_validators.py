"""Tests for validators.py – validation and resolution logic for config values."""

import pytest

from charfinder.config import constants as C
from charfinder import validators as V

# ---------------------------------------------------------------------
# Fuzzy Algorithm Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("algo", C.VALID_FUZZY_ALGO_NAMES)
def test_validate_fuzzy_algo_accepts_valid(algo: str) -> None:
    """Should return valid fuzzy algorithms unchanged."""
    assert V.validate_fuzzy_algo(algo) == algo


def test_validate_fuzzy_algo_rejects_invalid() -> None:
    """Should raise ValueError for unsupported algorithms."""
    with pytest.raises(ValueError, match="Unknown or unsupported fuzzy algorithm"):
        V.validate_fuzzy_algo("notarealalgo")


# ---------------------------------------------------------------------
# Match Mode Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("mode", C.VALID_FUZZY_MATCH_MODES)
def test_validate_fuzzy_match_mode_valid(mode: str) -> None:
    """Should accept valid fuzzy match modes."""
    assert V.validate_fuzzy_match_mode(mode) == mode


def test_validate_fuzzy_match_mode_invalid() -> None:
    """Should raise for invalid match mode."""
    with pytest.raises(ValueError, match="Invalid fuzzy match mode:"):
        V.validate_fuzzy_match_mode("invalid_mode")


@pytest.mark.parametrize("mode", C.VALID_EXACT_MATCH_MODES)
def test_validate_exact_match_mode_valid(mode: str) -> None:
    """Should accept valid exact match modes."""
    assert V.validate_exact_match_mode(mode) == mode


def test_validate_exact_match_mode_invalid() -> None:
    """Should raise for invalid exact match mode."""
    with pytest.raises(ValueError, match="Invalid exact match mode:"):
        V.validate_exact_match_mode("badmode")


# ---------------------------------------------------------------------
# Aggregation Function Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("agg", C.VALID_HYBRID_AGG_FUNCS)
def test_validate_hybrid_agg_fn_valid(agg: str) -> None:
    """Should accept all valid hybrid aggregation functions."""
    assert V.validate_hybrid_agg_fn(agg) == agg


def test_validate_hybrid_agg_fn_invalid() -> None:
    """Should raise for unknown hybrid aggregation functions."""
    with pytest.raises(ValueError, match="Got: funkyavg"):
        V.validate_hybrid_agg_fn("funkyavg")


# ---------------------------------------------------------------------
# Threshold Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("threshold", [0.0, 0.5, 1.0])
def test_validate_threshold_valid_values(threshold: float) -> None:
    """Should accept thresholds between 0.0 and 1.0 inclusive."""
    assert V.validate_threshold(threshold) == threshold


@pytest.mark.parametrize("threshold", [-0.1, 1.1, 99])
def test_validate_threshold_out_of_bounds(threshold: float) -> None:
    """Should raise ValueError for out-of-bound threshold values."""
    with pytest.raises(ValueError, match="Invalid threshold used"):
        V.validate_threshold(threshold)


def test_validate_threshold_type_error() -> None:
    """Should raise TypeError for non-numeric threshold values."""
    with pytest.raises(TypeError, match="Threshold must be a float"):
        V.validate_threshold("0.5")  # type: ignore


# ---------------------------------------------------------------------
# Color Mode Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("color", C.VALID_COLOR_MODES)
def test_validate_color_mode_valid(color: str) -> None:
    """Should accept all valid color modes."""
    assert V.validate_color_mode(color) == color


def test_validate_color_mode_invalid() -> None:
    """Should raise for unknown color mode."""
    with pytest.raises(ValueError, match="Invalid color mode:"):
        V.validate_color_mode("blackandwhite")


# ---------------------------------------------------------------------
# Output Format Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("fmt", C.VALID_OUTPUT_FORMATS)
def test_validate_output_format_valid(fmt: str) -> None:
    """Should accept all valid output formats."""
    assert V.validate_output_format(fmt) == fmt


def test_validate_output_format_invalid() -> None:
    """Should raise for unsupported output format."""
    with pytest.raises(ValueError, match="Invalid output format:"):
        V.validate_output_format("xml")


# ---------------------------------------------------------------------
# Show Score Validation
# ---------------------------------------------------------------------

@pytest.mark.parametrize("val", ["true", "1", "yes"])
def test_validate_show_score_truthy(val: str) -> None:
    """Should resolve truthy values to True."""
    assert V.validate_show_score(val) is True


@pytest.mark.parametrize("val", ["false", "0", "no"])
def test_validate_show_score_falsy(val: str) -> None:
    """Should resolve falsy values to False."""
    assert V.validate_show_score(val) is False


def test_validate_show_score_invalid() -> None:
    """Should raise for unknown show score values."""
    with pytest.raises(ValueError, match="Invalid value for show_score:"):
        V.validate_show_score("maybe")


# ---------------------------------------------------------------------
# Effective Resolver Logic
# ---------------------------------------------------------------------

# Threshold Validators

def test_resolve_effective_threshold_invalid_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Invalid env var should trigger fallback to default."""
    monkeypatch.setenv("CHARFINDER_MATCH_THRESHOLD", "not-a-float")
    assert V.resolve_effective_threshold(None) == C.DEFAULT_THRESHOLD


def test_resolve_effective_threshold_cli_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI value should override environment variable."""
    monkeypatch.setenv("CHARFINDER_MATCH_THRESHOLD", "0.1")
    assert V.resolve_effective_threshold(0.9) == 0.9


def test_resolve_effective_threshold_env_used(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment value should be used if CLI is None."""
    monkeypatch.setenv("CHARFINDER_MATCH_THRESHOLD", "0.75")
    assert V.resolve_effective_threshold(None) == 0.75


def test_resolve_effective_threshold_out_of_range(monkeypatch: pytest.MonkeyPatch) -> None:
    """Out-of-range env var should fallback to default with warning."""
    monkeypatch.setenv("CHARFINDER_MATCH_THRESHOLD", "2.0")
    assert V.resolve_effective_threshold(None) == C.DEFAULT_THRESHOLD


def test_resolve_effective_threshold_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default should be used if CLI and ENV are missing."""
    monkeypatch.delenv("CHARFINDER_MATCH_THRESHOLD", raising=False)
    assert V.resolve_effective_threshold(None) == C.DEFAULT_THRESHOLD


# Color Mode Validators

def test_resolve_effective_color_mode_cli_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI value should override environment variable."""
    monkeypatch.setenv("CHARFINDER_COLOR_MODE", "always")
    assert V.resolve_effective_color_mode("never") == "never"


def test_resolve_effective_color_mode_env_used(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment value should be used if CLI is None."""
    monkeypatch.setenv("CHARFINDER_COLOR_MODE", "auto")
    assert V.resolve_effective_color_mode(None) == "auto"


def test_resolve_effective_color_mode_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default should be used if CLI and ENV are missing."""
    monkeypatch.delenv("CHARFINDER_COLOR_MODE", raising=False)
    assert V.resolve_effective_color_mode(None) == C.DEFAULT_COLOR_MODE


def test_resolve_effective_color_mode_env_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Should fall back to default if ENV value is invalid."""
    monkeypatch.setenv("CHARFINDER_COLOR_MODE", "invalid_mode")
    assert V.resolve_effective_color_mode(None) == C.DEFAULT_COLOR_MODE


def test_resolve_effective_color_mode_cli_invalid_raises() -> None:
    """Passing an invalid CLI value should raise ValueError."""
    with pytest.raises(ValueError):
        V.resolve_effective_color_mode("invalid_cli_mode")


# Show Score Validators

def test_resolve_effective_show_score_cli_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI value should override environment variable."""
    monkeypatch.setenv("CHARFINDER_SHOW_SCORE", "no")
    assert V.resolve_effective_show_score(cli_value=True) is True


def test_resolve_effective_show_score_env_used(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment value should be used if CLI is None."""
    monkeypatch.setenv("CHARFINDER_SHOW_SCORE", "yes")
    assert V.resolve_effective_show_score(cli_value=None) is True


def test_resolve_effective_show_score_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default should be used if CLI and ENV are missing."""
    monkeypatch.delenv("CHARFINDER_SHOW_SCORE", raising=False)
    assert V.resolve_effective_show_score(cli_value=None) == C.DEFAULT_SHOW_SCORE
