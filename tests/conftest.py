"""
Global pytest fixtures for charfinder test suite.

This file provides reusable fixtures to:
- Clean up logger state
- Isolate environment variables and .env usage
- Simulate test/non-test execution behavior
- Capture CLI, logging, and echo output
- Reload settings with optional DOTENV_PATH
"""

from __future__ import annotations

import importlib
import logging
import tempfile
from collections.abc import Callable, Generator
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Final, Protocol, ContextManager
from unittest.mock import patch
import errno

import pytest

from charfinder.utils.logger_setup import get_logger, teardown_logger
from tests.helpers.conftest_helpers import invoke_cli

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch

# ---------------------------------------------------------------------
# __all__ export (for clarity and control)
# ---------------------------------------------------------------------

__all__ = [
    "clean_charfinder_logger",
    "clear_charfinder_env",
    "load_fresh_settings",
    "setup_test_root",
    "patch_env",
    "temp_log_dir",
    "log_stream",
    "debug_logger",
    "echo_output",
    "run_cli",
]

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

LOGGER_NAME: Final = "charfinder"

# ---------------------------------------------------------------------
# Logger Isolation
# ---------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clean_charfinder_logger() -> Generator[None, None, None]:
    """
    Clears all logging handlers for 'charfinder' before and after each test
    to avoid log pollution and duplicate handlers.
    """
    logger = get_logger()
    teardown_logger(logger)
    yield
    teardown_logger(logger)


# ---------------------------------------------------------------------
# Environment Cleanup
# ---------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_charfinder_env(monkeypatch: MonkeyPatch) -> None:
    """
    Clears all CHARFINDER-related env vars before each test to ensure test isolation.
    """
    for var in [
        "CHARFINDER_ENV",
        "CHARFINDER_LOG_MAX_BYTES",
        "CHARFINDER_LOG_BACKUP_COUNT",
        "CHARFINDER_DEBUG_ENV_LOAD",
        "DOTENV_PATH",
        "CHARFINDER_ROOT_DIR_FOR_TESTS",
    ]:
        monkeypatch.delenv(var, raising=False)

    monkeypatch.setenv("CHARFINDER_DEBUG_ENV_LOAD", "0")


# ---------------------------------------------------------------------
# Settings Reload (with optional .env and root)
# ---------------------------------------------------------------------


class LoadFreshSettings(Protocol):
    def __call__(self, dotenv_path: Path | None = ..., root_dir: Path | None = ...) -> ModuleType:
        ...


@pytest.fixture
def load_fresh_settings(monkeypatch: MonkeyPatch) -> LoadFreshSettings:
    """
    Reload `charfinder.settings` with optional DOTENV_PATH and CHARFINDER_ROOT_DIR_FOR_TESTS overrides.

    Returns:
        Callable that accepts optional dotenv_path and root_dir, reloads settings, and returns the module.
    """

    def _load(dotenv_path: Path | None = None, root_dir: Path | None = None) -> ModuleType:
        if dotenv_path:
            monkeypatch.setenv("DOTENV_PATH", str(dotenv_path.resolve()))
        else:
            monkeypatch.delenv("DOTENV_PATH", raising=False)

        if root_dir:
            monkeypatch.setenv("CHARFINDER_ROOT_DIR_FOR_TESTS", str(root_dir.resolve()))
        else:
            monkeypatch.delenv("CHARFINDER_ROOT_DIR_FOR_TESTS", raising=False)

        import charfinder.settings as sett
        importlib.reload(sett)
        sett.load_settings()
        return sett

    return _load


# ---------------------------------------------------------------------
# Setup test root and patch ROOT_DIR global
# ---------------------------------------------------------------------


@pytest.fixture
def setup_test_root(monkeypatch: MonkeyPatch, tmp_path: Path) -> Callable[[], Path]:
    """
    Patch project root to tmp_path and reload settings.
    Used to isolate test-specific file systems and config roots.
    """

    def _setup() -> Path:
        monkeypatch.setenv("CHARFINDER_ROOT_DIR_FOR_TESTS", str(tmp_path.resolve()))

        import charfinder.settings as sett
        importlib.reload(sett)
        sett.load_settings()

        return tmp_path

    return _setup


# ---------------------------------------------------------------------
# Patch environment name
# ---------------------------------------------------------------------


@pytest.fixture
def patch_env(monkeypatch: MonkeyPatch) -> Callable[[str], None]:
    """
    Fixture that returns a function to patch CHARFINDER_ENV dynamically.

    Usage:
        patch_env("UAT")
    """

    def _patch(env_name: str) -> None:
        monkeypatch.setenv("CHARFINDER_ENV", env_name)

    return _patch


# ---------------------------------------------------------------------
# Temporary log directory override
# ---------------------------------------------------------------------


@pytest.fixture
def temp_log_dir(monkeypatch: MonkeyPatch) -> Generator[Path, None, None]:
    """
    Provide a temporary directory for logs, overriding get_log_dir() to isolate log output.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir).resolve()
        monkeypatch.setenv("CHARFINDER_ENV", "TEST")

        import charfinder.settings as sett
        importlib.reload(sett)

        monkeypatch.setattr("charfinder.settings.get_log_dir", lambda: tmp_path)
        yield tmp_path

        teardown_logger(logging.getLogger(LOGGER_NAME))


# ---------------------------------------------------------------------
# Logging capture
# ---------------------------------------------------------------------


@pytest.fixture
def log_stream() -> Generator[StringIO, None, None]:
    """
    Capture log output to a StringIO stream.
    """
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    logger = get_logger()
    logger.addHandler(handler)

    yield stream

    logger.removeHandler(handler)
    handler.close()


@pytest.fixture
def debug_logger(log_stream: StringIO) -> logging.Logger:
    """
    Configure DEBUG logger attached to log_stream.
    """
    teardown_logger()
    logger = get_logger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.addHandler(handler)
    return logger


# ---------------------------------------------------------------------
# Echo output capture
# ---------------------------------------------------------------------


@pytest.fixture
def echo_output(capsys: pytest.CaptureFixture[str]) -> Callable[[], str]:
    """
    Capture and return combined echo (stdout + stderr) output.

    Usage:
        echo_output() -> returns captured output since last call.
    """

    def _get_output() -> str:
        captured = capsys.readouterr()
        return captured.out + captured.err

    return _get_output


# ---------------------------------------------------------------------
# CLI subprocess runner
# ---------------------------------------------------------------------


@pytest.fixture
def run_cli(tmp_path: Path) -> Callable[..., tuple[str, str, int]]:
    """
    Run CLI in subprocess with tmp_path isolation.
    """

    def _run(*args: str, env: dict[str, str] | None = None) -> tuple[str, str, int]:
        return invoke_cli(args, tmp_path=tmp_path, env=env)

    return _run

# ---------------------------------------------------------------------
# Log Path Unlink
# ---------------------------------------------------------------------
@pytest.fixture
def fail_unlink_for() -> Callable[[Path], ContextManager[None]]:
    """Returns a context manager that patches Path.unlink to raise PermissionError for the given path."""

    def _mock(file_to_fail: Path) -> ContextManager[None]:
        @contextmanager
        def _context() -> Generator[None, None, None]:
            original_unlink = Path.unlink

            def side_effect(self: Path, *args: Any, **kwargs: Any) -> None:
                if self == file_to_fail:
                    raise PermissionError(errno.EACCES, "Permission denied", str(self))
                return original_unlink(self, *args, **kwargs)

            with patch.object(Path, "unlink", side_effect):
                yield

        return _context()

    return _mock