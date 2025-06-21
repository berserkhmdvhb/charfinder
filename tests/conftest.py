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

import errno
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

import pytest
from logging import StreamHandler

from charfinder.utils.logger_setup import get_logger, teardown_logger, setup_logging
from tests.helpers.conftest_helpers import invoke_cli

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch

__all__ = [
    "clean_charfinder_logger",
    "clear_charfinder_env",
    "load_fresh_settings",
    "setup_test_root",
    "use_isolated_test_root",
    "patch_env",
    "temp_log_dir",
    "log_stream",
    "debug_logger",
    "configured_logger",
    "patched_echo",
    "patched_stream_handler",
    "echo_output",
    "run_cli",
    "fail_unlink_for",
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
    """Clear all logging handlers for 'charfinder' before and after each test."""
    logger = get_logger()
    teardown_logger(logger)
    yield
    teardown_logger(logger)

# ---------------------------------------------------------------------
# Environment Cleanup
# ---------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_charfinder_env(monkeypatch: MonkeyPatch) -> None:
    """Clear all CHARFINDER-related env vars before each test for isolation."""
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
# Settings Reload and Test Root
# ---------------------------------------------------------------------

class LoadFreshSettings(Protocol):
    def __call__(self, dotenv_path: Path | None = ..., root_dir: Path | None = ...) -> ModuleType: ...

@pytest.fixture
def load_fresh_settings(monkeypatch: MonkeyPatch) -> LoadFreshSettings:
    """Reload `charfinder.config.settings` with optional DOTENV_PATH and ROOT override."""
    def _load(dotenv_path: Path | None = None, root_dir: Path | None = None) -> ModuleType:
        if dotenv_path:
            monkeypatch.setenv("DOTENV_PATH", str(dotenv_path.resolve()))
        else:
            monkeypatch.delenv("DOTENV_PATH", raising=False)

        if root_dir:
            monkeypatch.setenv("CHARFINDER_ROOT_DIR_FOR_TESTS", str(root_dir.resolve()))
        else:
            monkeypatch.delenv("CHARFINDER_ROOT_DIR_FOR_TESTS", raising=False)

        import charfinder.config.settings as sett
        importlib.reload(sett)
        sett.load_settings()
        return sett
    return _load

@pytest.fixture
def setup_test_root(monkeypatch: MonkeyPatch, tmp_path: Path) -> Callable[[], Path]:
    """Patch project root to tmp_path and reload settings."""
    def _setup() -> Path:
        monkeypatch.setenv("CHARFINDER_ROOT_DIR_FOR_TESTS", str(tmp_path.resolve()))
        import charfinder.config.settings as sett
        importlib.reload(sett)
        sett.load_settings()
        return tmp_path
    return _setup

# ---------------------------------------------------------------------
# Environment Mode Patcher
# ---------------------------------------------------------------------

@pytest.fixture
def patch_env(monkeypatch: MonkeyPatch) -> Callable[[str], None]:
    """Patch CHARFINDER_ENV dynamically (e.g., to 'UAT', 'PROD')."""
    def _patch(env_name: str) -> None:
        monkeypatch.setenv("CHARFINDER_ENV", env_name)
    return _patch

# ---------------------------------------------------------------------
# Logging Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def temp_log_dir(monkeypatch: MonkeyPatch) -> Generator[Path, None, None]:
    """Create temporary log directory and override get_log_dir()."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir).resolve()
        monkeypatch.setenv("CHARFINDER_ENV", "TEST")

        import charfinder.config.settings as sett
        importlib.reload(sett)
        monkeypatch.setattr("charfinder.config.settings.get_log_dir", lambda: tmp_path)

        yield tmp_path
        teardown_logger(logging.getLogger(LOGGER_NAME))

@pytest.fixture
def log_stream() -> StringIO:
    """Provide a reusable StringIO for log stream patching."""
    return StringIO()

@pytest.fixture
def debug_logger(log_stream: StringIO) -> logging.Logger:
    """Return DEBUG logger attached to log_stream."""
    teardown_logger()
    logger = get_logger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.addHandler(handler)
    return logger

@pytest.fixture
def patched_stream_handler(log_stream: StringIO) -> Callable[[list[logging.Handler]], None]:
    """Patch StreamHandler(s) to write to log_stream for test capture."""
    def _patch(handlers: list[logging.Handler]) -> None:
        for handler in handlers:
            if isinstance(handler, StreamHandler):
                handler.setStream(log_stream)
    return _patch

@pytest.fixture
def configured_logger(
    temp_log_dir: Path,
    log_stream: StringIO,
    patched_stream_handler: Callable[[list[logging.Handler]], None],
) -> logging.Logger:
    """Provides logger configured with log_stream-patched StreamHandler."""
    teardown_logger()
    handlers = setup_logging(
        log_dir=temp_log_dir,
        reset=True,
        return_handlers=True,
        suppress_echo=True,
    )
    if handlers:
        patched_stream_handler(handlers)
    return get_logger()

# ---------------------------------------------------------------------
# Echo and CLI Fixtures
# ---------------------------------------------------------------------
@pytest.fixture
def run_cli(tmp_path: Path) -> Callable[..., tuple[str, str, int]]:
    """Run CLI command in subprocess with tmp_path isolation."""
    def _run(*args: str, env: dict[str, str] | None = None) -> tuple[str, str, int]:
        return invoke_cli(args, tmp_path=tmp_path, env=env)
    return _run

# ---------------------------------------------------------------------
# Filesystem Failure Simulation
# ---------------------------------------------------------------------

@pytest.fixture
def fail_unlink_for() -> Callable[[Path], ContextManager[None]]:
    """Simulate failure of Path.unlink for a specific file."""
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
