"""
Unit tests for charfinder.constants.

Covers:
- Default thresholds and modes
- Valid algorithm aliases
- Logging constants and field widths
- Environment variable names and exit codes
"""

from pathlib import Path
from typing import get_args


import charfinder.constants as C



def test_default_constants() -> None:
    assert isinstance(C.DEFAULT_THRESHOLD, float)
    assert 0.0 <= C.DEFAULT_THRESHOLD <= 1.0

    assert isinstance(C.DEFAULT_FUZZY_ALGO, str)
    assert C.DEFAULT_FUZZY_ALGO in C.FUZZY_ALGO_ALIASES.values()

    assert isinstance(C.DEFAULT_FUZZY_MATCH_MODE, str)
    assert C.DEFAULT_FUZZY_MATCH_MODE in C.VALID_FUZZY_MATCH_MODES

    assert isinstance(C.DEFAULT_EXACT_MATCH_MODE, str)
    assert C.DEFAULT_EXACT_MATCH_MODE in C.VALID_EXACT_MATCH_MODES

    assert isinstance(C.DEFAULT_HYBRID_AGG_FUNC, str)
    assert C.DEFAULT_HYBRID_AGG_FUNC in get_args(C.VALID_HYBRID_AGG_FUNCS)

    assert isinstance(C.DEFAULT_COLOR_MODE, str)
    assert C.DEFAULT_COLOR_MODE in get_args(C.ColorMode)


def test_logging_constants() -> None:
    assert isinstance(C.LOG_FILE_NAME, str)
    assert C.LOG_FILE_NAME.endswith(".log")

    assert isinstance(C.LOG_FORMAT, str)
    assert "%(asctime)s" in C.LOG_FORMAT
    assert "%(levelname)s" in C.LOG_FORMAT
    assert "%(env)s" in C.LOG_FORMAT

    assert isinstance(C.DEFAULT_LOG_ROOT, Path)


def test_field_widths() -> None:
    assert isinstance(C.FIELD_WIDTHS, dict)
    for field in ("code", "char", "name"):
        assert field in C.FIELD_WIDTHS
        assert isinstance(C.FIELD_WIDTHS[field], int)


def test_exit_codes_are_unique() -> None:
    codes = {
        C.EXIT_SUCCESS,
        C.EXIT_INVALID_USAGE,
        C.EXIT_NO_RESULTS,
        C.EXIT_CANCELLED,
        C.EXIT_ERROR,
    }
    assert len(codes) == 5  # no duplicates


def test_env_var_names_are_strings() -> None:
    for var in (
        C.ENV_ENVIRONMENT,
        C.ENV_LOG_MAX_BYTES,
        C.ENV_LOG_BACKUP_COUNT,
        C.ENV_LOG_LEVEL,
        C.ENV_DEBUG_ENV_LOAD,
    ):
        assert isinstance(var, str)
        assert var.startswith("CHARFINDER_")
