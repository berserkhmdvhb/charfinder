from __future__ import annotations

import os
from pathlib import Path
from typing import cast

from dotenv import load_dotenv

from charfinder.constants import (
    DEFAULT_LOG_ROOT,
    ENV_ENVIRONMENT,
    ENV_LOG_BACKUP_COUNT,
    ENV_LOG_MAX_BYTES,
)
from charfinder.utils.formatter import echo
from charfinder.utils.logger_styles import format_error, format_settings, format_warning

# ---------------------------------------------------------------------
# Environment Accessors
# ---------------------------------------------------------------------


def get_environment() -> str:
    """
    Return CHARFINDER_ENV uppercased (default is DEV).

    Returns:
        One of DEV, UAT, PROD.
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

    Returns:
        Absolute path to the project's root directory.
    """
    return cast("Path", globals().get("ROOT_DIR", Path(__file__).resolve().parents[2]))


# ---------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------


def resolve_dotenv_path() -> Path | None:
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
            message = f"DOTENV_PATH is set to {custom_path} but the file does not exist."
            echo(msg=message, style=format_warning, show=True, log=False, log_method="warning")
        return custom_path

    default_env = root_dir / ".env"
    return default_env if default_env.exists() else None


def is_test_mode() -> bool:
    """Return True if running under pytest (PYTEST_CURRENT_TEST env var is set)."""
    return "PYTEST_CURRENT_TEST" in os.environ


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
            message = f"Invalid int for {env_var!r} = {val!r}; using default {default}"
            echo(msg=message, style=format_error, show=True, log=False, log_method="warning")
    return default


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
        load_dotenv(dotenv_path=dotenv_path)
        loaded.append(dotenv_path)

    if not loaded:
        message = "No .env file loaded — using system env or defaults."
        echo(
            msg=message, style=format_settings, show=debug or verbose, log=False, log_method="info"
        )
    return loaded


# ---------------------------------------------------------------------
# Cache Config
# ---------------------------------------------------------------------


def get_cache_file() -> str:
    """Return the cache file path."""
    return os.getenv("CHARFINDER_CACHE", "unicode_name_cache.json")


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
# Public API for CLI/debug
# ---------------------------------------------------------------------


def resolve_loaded_dotenv_paths() -> list[Path]:
    """Expose resolved .env paths for CLI debug introspection."""
    path = resolve_dotenv_path()
    return [path] if path else []
