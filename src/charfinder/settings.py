"""
Environment and configuration management for CharFinder.

- Loads `.env` file (optional) with override via DOTENV_PATH
- Provides access to environment variables
- Supports debug logging of dotenv resolution (via CHARFINDER_DEBUG_ENV_LOAD=1)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import cast

from dotenv import dotenv_values, load_dotenv

from charfinder.constants import ENV_ENVIRONMENT
from charfinder.utils.formatter import echo, format_settings

logger = logging.getLogger("charfinder")

# ---------------------------------------------------------------------
# Environment Accessors
# ---------------------------------------------------------------------


def get_environment() -> str:
    """
    Return MYPROJECT_ENV uppercased (default is DEV).

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


def _resolve_dotenv_path() -> Path | None:
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
            logger.warning(
                "[settings] DOTENV_PATH is set to %s but the file does not exist.",
                custom_path,
            )
        return custom_path

    default_env = root_dir / ".env"
    return default_env if default_env.exists() else None


# ---------------------------------------------------------------------
# Public Utilities
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
            logger.warning(
                "[settings] Invalid int for %r = %r; using default %d",
                env_var,
                val,
                default,
            )
    return default


# ---------------------------------------------------------------------
# .env loading
# ---------------------------------------------------------------------


def load_settings(*, verbose: bool = False) -> list[Path]:
    """
    Load environment variables from .env file if present.

    Args:
        verbose: Log loaded .env path if True or if CHARFINDER_DEBUG_ENV_LOAD=1.

    Returns:
        List of loaded .env file paths.
    """
    loaded: list[Path] = []
    dotenv_path = _resolve_dotenv_path()

    if dotenv_path and dotenv_path.is_file():
        load_dotenv(dotenv_path=dotenv_path)
        if verbose or os.getenv("CHARFINDER_DEBUG_ENV_LOAD") == "1":
            echo(f"Loaded environment variables from: {dotenv_path}", style=format_settings)
        loaded.append(dotenv_path)

    if not loaded and (verbose or os.getenv("CHARFINDER_DEBUG_ENV_LOAD") == "1"):
        echo("No .env file loaded — using system env or defaults.", style=format_settings)

    return loaded


# ---------------------------------------------------------------------
# Debug utilities
# ---------------------------------------------------------------------


def print_dotenv_debug() -> None:
    """
    Print details of the resolved .env file and its contents to stdout,
    and log them if appropriate.

    Intended for CLI `--debug` output.
    """
    dotenv_path = _resolve_dotenv_path()

    if not dotenv_path:
        echo("No .env file found or resolved.", style=format_settings)
        echo("Environment variables may only be coming from the OS.", style=format_settings)
        return

    echo(f"Selected .env file: {dotenv_path}", style=format_settings)

    try:
        values = dotenv_values(dotenv_path=dotenv_path)

        if not values:
            echo(
                ".env file exists but is empty or contains no key-value pairs.",
                style=format_settings,
            )
            return

        echo("Loaded key-value pairs:", style=format_settings)
        for key, value in values.items():
            echo(f"  {key}={value}", style=format_settings)

    except (OSError, UnicodeDecodeError) as exc:
        echo(f"Failed to read .env file: {exc}", style=format_settings)


# ---------------------------------------------------------------------
# CACHE File Retrieval
# ---------------------------------------------------------------------


def get_cache_file() -> str:
    return os.getenv("CHARFINDER_CACHE", "unicode_name_cache.json")
