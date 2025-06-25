"""Environment and application settings management for Charfinder.

Provides dynamic loading of environment variables from .env files and system
environment, with support for development, testing, and production modes.

Functions:
    get_root_dir(): Return the root directory of the project.
    load_settings(): Load application settings from environment and .env file.
    resolve_loaded_dotenv_paths(): Return resolved .env paths (for debug/CLI).
    get_log_dir(): Return log directory based on current environment.
    get_cache_file(): Return cache file path.
    get_unicode_data_file(): Return UnicodeData.txt file path.
    get_environment(): Return current environment (DEV/UAT/PROD/TEST).
    is_dev(), is_uat(), is_prod(), is_test_mode(), is_test(): Check current environment.
    get_log_max_bytes(): Return maximum log size.
    get_log_backup_count(): Return number of log backups.
"""


# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, TextIO

from dotenv import load_dotenv

from charfinder.config.constants import (
    DEFAULT_LOG_ROOT,
    ENV_ENVIRONMENT,
    ENV_FUZZY_WEIGHTS,
    ENV_LOG_BACKUP_COUNT,
    ENV_LOG_MAX_BYTES,
    FUZZY_HYBRID_WEIGHTS,
    FUZZY_WEIGHT_MAX_TOTAL,
    FUZZY_WEIGHT_MIN_TOTAL,
)
from charfinder.config.messages import (
    MSG_ERROR_INVALID_WEIGHT_FORMAT,
    MSG_ERROR_INVALID_WEIGHT_TOTAL,
    MSG_INFO_NO_DOTENV_LOADED,
    MSG_WARNING_DOTENV_PATH_MISSING,
    MSG_WARNING_INVALID_ENV_INT,
)
from charfinder.utils.formatter import echo
from charfinder.utils.logger_styles import format_error, format_settings, format_warning

if TYPE_CHECKING:
    from charfinder.config.types import HybridWeights

__all__ = [
    "get_cache_file",
    "get_environment",
    "get_fuzzy_hybrid_weights",
    "get_log_backup_count",
    "get_log_dir",
    "get_log_max_bytes",
    "get_root_dir",
    "get_unicode_data_file",
    "get_unicode_data_url",
    "is_dev",
    "is_prod",
    "is_test",
    "is_test_mode",
    "is_uat",
    "load_settings",
    "resolve_loaded_dotenv_paths",
]

# ---------------------------------------------------------------------
# Environment Accessors
# ---------------------------------------------------------------------


def get_environment() -> str:
    """
    Return CHARFINDER_ENV uppercased (default is DEV).

    Returns:
        One of DEV, UAT, PROD, TEST.
    """
    val: str | None = os.getenv(ENV_ENVIRONMENT)
    return val.strip().upper() if val else "DEV"


def is_dev() -> bool:
    """Check if environment is DEV."""
    return get_environment() == "DEV"


def is_uat() -> bool:
    """Check if environment is UAT."""
    return get_environment() == "UAT"


def is_prod() -> bool:
    """Check if environment is PROD."""
    return get_environment() == "PROD"


def is_test_mode() -> bool:
    """
    Check if CHARFINDER_ENV is explicitly set to TEST.

    Returns:
        True if test mode is explicitly enabled via environment variable.
    """
    return get_environment() == "TEST"


def is_test() -> bool:
    """
    Check if running in test context.

    Returns:
        True if CHARFINDER_ENV is TEST or Pytest is active (PYTEST_CURRENT_TEST set).
    """
    return is_test_mode() or "PYTEST_CURRENT_TEST" in os.environ


# ---------------------------------------------------------------------
# Environment variable safe access helpers
# ---------------------------------------------------------------------


def safe_int(env_var: str, default: int) -> int:
    """
    Safely retrieve an integer from an environment variable, falling back to a default.

    Args:
        env_var: Name of the environment variable.
        default: Default value to use if missing or invalid.

    Returns:
        Integer from the environment or default.
    """
    val: str | None = os.getenv(env_var)
    if val is not None:
        try:
            return int(val)
        except ValueError:
            echo(
                msg=MSG_WARNING_INVALID_ENV_INT.format(env_var=env_var, value=val, default=default),
                style=format_error,
                show=True,
                log=False,
                log_method="warning",
            )
    return default


def get_log_max_bytes() -> int:
    """Return maximum log file size in bytes."""
    return safe_int(ENV_LOG_MAX_BYTES, 1_000_000)


def get_log_backup_count() -> int:
    """Return number of log file backups to keep."""
    return safe_int(ENV_LOG_BACKUP_COUNT, 5)


# ---------------------------------------------------------------------
# Root dir handling (used for locating .env if needed)
# ---------------------------------------------------------------------


def get_root_dir() -> Path:
    """
    Dynamically return the project root directory.

    Honors CHARFINDER_ROOT_DIR_FOR_TESTS for patching in unit tests.

    Returns:
        Absolute path to the project's root directory.
    """
    if "CHARFINDER_ROOT_DIR_FOR_TESTS" in os.environ:
        return Path(os.environ["CHARFINDER_ROOT_DIR_FOR_TESTS"]).resolve()
    return Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------


def resolve_dotenv_path(stream: TextIO = sys.stdout) -> Path | None:
    """
    Determine which .env file to load.

    Priority:
      1. DOTENV_PATH (explicit override)
      2. .env in project root
      3. None if not found
    """
    root_dir = get_root_dir()

    if custom := os.getenv("DOTENV_PATH"):
        custom_path = Path(custom)
        if not custom_path.exists() and os.getenv("CHARFINDER_DEBUG_ENV_LOAD") == "1":
            echo(
                msg=MSG_WARNING_DOTENV_PATH_MISSING.format(path=custom_path),
                style=format_warning,
                stream=stream,
                show=True,
                log=False,
                log_method="warning",
            )
        return custom_path

    default_env = root_dir / ".env"
    return default_env if default_env.exists() else None


# ---------------------------------------------------------------------
# .env loading
# ---------------------------------------------------------------------


def load_settings(
    *, do_load_dotenv: bool = True, debug: bool = False, verbose: bool = False
) -> list[Path]:
    """
    Load .env settings and optionally log the process.

    Args:
        do_load_dotenv: Whether to load the .env file.
        debug: Whether debug mode is enabled.
        verbose: Whether verbose output is enabled.

    Returns:
        List of loaded .env file paths.
    """
    loaded: list[Path] = []
    dotenv_path = resolve_dotenv_path()

    if do_load_dotenv and dotenv_path and dotenv_path.is_file():
        load_dotenv(dotenv_path=dotenv_path, override=is_test())
        loaded.append(dotenv_path)

    if not loaded:
        echo(
            msg=MSG_INFO_NO_DOTENV_LOADED,
            style=format_settings,
            show=debug or verbose,
            log=True,
            log_method="info",
        )
    return loaded


# ---------------------------------------------------------------------
# Files Path Retrieval
# ---------------------------------------------------------------------


def get_cache_file() -> Path:
    """Return the cache file path."""
    env_value = os.getenv("CHARFINDER_CACHE_FILE_PATH")
    if env_value:
        return get_root_dir() / env_value
    return get_root_dir() / "data" / "cache" / "unicode_name_cache.json"


def get_unicode_data_file() -> Path:
    """Return the UnicodeData.txt file path."""
    env_value = os.getenv("CHARFINDER_UNICODE_DATA_FILE_PATH")
    if env_value:
        return get_root_dir() / env_value
    return get_root_dir() / "data" / "UnicodeData.txt"


def get_unicode_data_url() -> str:
    return os.getenv(
        "UNICODE_DATA_URL",
        "https://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt",
    )


# ---------------------------------------------------------------------
# Logging Config
# ---------------------------------------------------------------------


def get_log_dir() -> Path:
    """
    Return per-environment log directory path.

    Example: logs/DEV/, logs/PROD/
    """
    return DEFAULT_LOG_ROOT / get_environment()


# ---------------------------------------------------------------------
# Fuzzy Matching Config (Internal use only)
# ---------------------------------------------------------------------
def parse_fuzzy_weight_string(raw: str) -> HybridWeights:
    """
    Parse and validate a fuzzy weight string like 'a:0.2,b:0.3'.

    Args:
        raw (str): Raw string of algorithm:weight pairs.

    Returns:
        HybridWeights: Parsed algorithm-weight map.

    Raises:
        ValueError: On bad format or invalid total.
    """
    try:
        parts = raw.split(",")
        weights = {}
        for part in parts:
            key, val = part.strip().split(":")
            weights[key.strip()] = float(val.strip())
    except (ValueError, TypeError) as err:
        raise ValueError(MSG_ERROR_INVALID_WEIGHT_FORMAT.format(raw=raw)) from err

    total = sum(weights.values())
    if not (FUZZY_WEIGHT_MIN_TOTAL <= total <= FUZZY_WEIGHT_MAX_TOTAL):
        raise ValueError(MSG_ERROR_INVALID_WEIGHT_TOTAL.format(total=total, weights=weights))

    return weights


def get_fuzzy_hybrid_weights(env_value: str | None = None) -> HybridWeights:
    """
    Return hybrid fuzzy weights parsed from environment variable or default.

    Args:
        env_value (str | None): Optional override for raw weights string.

    Returns:
        HybridWeights: Parsed and validated fuzzy weight dictionary.
    """
    raw_value = env_value if env_value is not None else os.getenv(ENV_FUZZY_WEIGHTS)
    if raw_value:
        return parse_fuzzy_weight_string(raw_value)
    return FUZZY_HYBRID_WEIGHTS


# ---------------------------------------------------------------------
# Public API for CLI/debug
# ---------------------------------------------------------------------


def resolve_loaded_dotenv_paths() -> list[Path]:
    """Expose resolved .env paths for CLI debug introspection."""
    path = resolve_dotenv_path()
    return [path] if path else []
