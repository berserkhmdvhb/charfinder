"""Unit tests for charfinder.config.constants.

Covers:
- Default thresholds and modes
- Alias mappings and valid sets
- Logging constants and field widths
- Environment variable names and exit codes
- Normalization profiles and Unicode field expectations
"""

from pathlib import Path
from types import SimpleNamespace
from typing import get_args

import charfinder.config.constants as C
from charfinder.config.aliases import (
    ColorMode,
    ExactMatchMode,
    FuzzyAlgorithm,
    FuzzyMatchMode,
    HybridAggFunc,
    NormalizationForm,
    NormalizationProfile,
    OutputFormat,
)


def test_default_config_constants() -> None:
    """Test default values and their types are valid."""
    assert isinstance(C.DEFAULT_THRESHOLD, float)
    assert 0.0 <= C.DEFAULT_THRESHOLD <= 1.0

    assert C.DEFAULT_FUZZY_ALGO in C.FUZZY_ALGO_ALIASES.values()
    assert C.DEFAULT_FUZZY_MATCH_MODE in get_args(FuzzyMatchMode)
    assert C.DEFAULT_EXACT_MATCH_MODE in get_args(ExactMatchMode)
    assert C.DEFAULT_HYBRID_AGG_FUNC in get_args(HybridAggFunc)
    assert C.DEFAULT_COLOR_MODE in get_args(ColorMode)
    assert C.DEFAULT_NORMALIZATION_FORM in get_args(NormalizationForm)
    assert C.DEFAULT_NORMALIZATION_PROFILE in get_args(NormalizationProfile)
    assert C.DEFAULT_OUTPUT_FORMAT in get_args(OutputFormat)
    assert isinstance(C.DEFAULT_SHOW_SCORE, bool)


def test_fuzzy_algo_aliases_are_valid() -> None:
    """Test that fuzzy aliases resolve to valid algorithm names."""
    assert isinstance(C.FUZZY_ALGO_ALIASES, dict)
    for alias, resolved in C.FUZZY_ALGO_ALIASES.items():
        assert isinstance(alias, str)
        assert resolved in get_args(FuzzyAlgorithm)


def test_valid_sets_are_correct() -> None:
    """Test valid sets of options."""
    assert "NFC" in C.VALID_NORMALIZATION_FORMS
    assert "text" in C.VALID_OUTPUT_FORMATS
    assert "mean" in C.VALID_HYBRID_AGG_FUNCS
    assert "debug" in C.VALID_LOG_METHODS
    assert "auto" in C.VALID_COLOR_MODES
    assert "1" in C.VALID_SHOW_SCORES_TRUE
    assert "false" in C.VALID_SHOW_SCORES_FALSE
    assert C.VALID_SHOW_SCORES == C.VALID_SHOW_SCORES_TRUE | C.VALID_SHOW_SCORES_FALSE


def test_logging_constants_and_methods() -> None:
    """Test logging-related constants and method namespace."""
    assert isinstance(C.LOG_FILE_NAME, str)
    assert C.LOG_FILE_NAME.endswith(".log")
    assert "%(asctime)s" in C.LOG_FORMAT
    assert "%(levelname)s" in C.LOG_FORMAT
    assert "%(env)s" in C.LOG_FORMAT
    assert isinstance(C.DEFAULT_LOG_ROOT, Path)

    assert isinstance(C.LOG_METHODS, SimpleNamespace)
    for method in ("DEBUG", "INFO", "WARNING", "ERROR", "EXCEPTION"):
        assert hasattr(C.LOG_METHODS, method)
        assert getattr(C.LOG_METHODS, method).lower() in C.VALID_LOG_METHODS


def test_field_widths_have_expected_keys() -> None:
    """Test that FIELD_WIDTHS dict has correct fields and values."""
    required_keys = {"code", "char", "name", "score"}
    assert set(C.FIELD_WIDTHS.keys()) == required_keys
    for key in required_keys:
        assert isinstance(C.FIELD_WIDTHS[key], int)
        assert C.FIELD_WIDTHS[key] > 0


def test_exit_codes_are_unique_and_int() -> None:
    """Ensure CLI exit codes are distinct and valid integers."""
    codes = {
        C.EXIT_SUCCESS,
        C.EXIT_INVALID_USAGE,
        C.EXIT_NO_RESULTS,
        C.EXIT_CANCELLED,
        C.EXIT_ERROR,
    }
    assert len(codes) == 5
    for code in codes:
        assert isinstance(code, int)


def test_env_var_names_are_valid_strings() -> None:
    """Check that environment variable names are properly formatted."""
    env_vars = [
        C.ENV_ENVIRONMENT,
        C.ENV_LOG_MAX_BYTES,
        C.ENV_LOG_BACKUP_COUNT,
        C.ENV_LOG_LEVEL,
        C.ENV_DEBUG_ENV_LOAD,
        C.ENV_MATCH_THRESHOLD,
        C.ENV_COLOR_MODE,
        C.ENV_NORMALIZATION_PROFILE,
        C.ENV_SHOW_SCORE,
    ]
    for var in env_vars:
        assert isinstance(var, str)
        assert var.startswith("CHARFINDER_")


def test_normalization_profiles_structure() -> None:
    """Test that normalization profiles are present and well-formed."""
    assert isinstance(C.NORMALIZATION_PROFILES, dict)
    for key, value in C.NORMALIZATION_PROFILES.items():
        assert key in get_args(NormalizationProfile)
        assert isinstance(value, dict)
        assert "form" in value
        assert value["form"] in C.VALID_NORMALIZATION_FORMS
        if "strip_accents" in value:
            assert isinstance(value["strip_accents"], bool)


def test_fuzzy_hybrid_weights_sum_to_one() -> None:
    """Ensure hybrid weights sum to 1.0 or very close."""
    total = sum(C.FUZZY_HYBRID_WEIGHTS.values())
    assert abs(total - 1.0) < 1e-6


def test_unicode_data_constants() -> None:
    """Validate UnicodeData.txt field expectations."""
    assert isinstance(C.ALT_NAME_INDEX, int)
    assert isinstance(C.EXPECTED_MIN_FIELDS, int)
    assert C.ALT_NAME_INDEX < C.EXPECTED_MIN_FIELDS
