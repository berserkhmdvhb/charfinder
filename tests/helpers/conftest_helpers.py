"""
Helper utilities for the charfinder test suite.

This module includes:
- `invoke_cli`: Executes CLI commands in subprocess for integration tests.
- `SafeDummyHandler`: A logging handler used in teardown/error tests.
- `ArgcompleteStub`: A stub module to simulate `argcomplete` failures.

These tools are useful across CLI tests, diagnostics, logging, and
environmental isolation.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType
from typing import IO, NoReturn

__all__ = [
    "ArgcompleteStub",
    "SafeDummyHandler",
    "invoke_cli",
]


def invoke_cli(
    args: Sequence[str],
    tmp_path: Path,
    env: dict[str, str] | None = None,
) -> tuple[str, str, int]:
    """
    Invoke the CLI tool in subprocess for integration testing.

    Args:
        args: Command-line arguments to pass (e.g. ["--query", "hello"])
        tmp_path: Temporary directory used for DOTENV_PATH and isolation
        env: Optional dictionary of environment variables to inject

    Returns:
        A tuple of (stdout, stderr, returncode)
    """
    cmd = [sys.executable, "-m", "charfinder", *args]

    # Force --color=never if not already specified to avoid ANSI noise
    if not any(a.startswith("--color") for a in args):
        cmd.append("--color=never")

    # Combine test environment with overrides
    full_env = {
        **os.environ,
        "CHARFINDER_LOG_MAX_BYTES": "10000",
        "CHARFINDER_LOG_BACKUP_COUNT": "2",
        "CHARFINDER_DEBUG_ENV_LOAD": "0",
        **(env or {}),
    }

    # Provide an empty .env file to force dotenv parsing behavior
    dummy_env = tmp_path / ".env"
    dummy_env.write_text("")
    full_env["DOTENV_PATH"] = str(dummy_env.resolve())

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=full_env,
        check=False,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


# ---------------------------------------------------------------------
# Safe dummy handler (for teardown tests)
# ---------------------------------------------------------------------


class SafeDummyHandler(logging.StreamHandler):  # type: ignore[type-arg]
    """
    A dummy stream handler used in logger teardown tests.

    Overrides flush/close to avoid unintended stderr writes or
    resource cleanup side effects in tests.
    """

    def __init__(self, stream: IO[str] | None = None) -> None:
        super().__init__(stream)

    def flush(self) -> None:
        # Suppress flushing behavior
        pass

    def close(self) -> None:
        # Suppress cleanup to avoid triggering errors
        pass


class ArgcompleteStub(ModuleType):
    """
    A stub module to simulate `argcomplete` in tests.

    Designed for patching `sys.modules["argcomplete"]` to test
    autocomplete error handling logic.
    """

    def __init__(self) -> None:
        super().__init__("argcomplete")
        self.autocomplete = self._autocomplete
        self.__spec__ = None  # Ensure importlib treats as fake module

    @staticmethod
    def _autocomplete(*_args: object, **_kwargs: object) -> NoReturn:
        msg = "Simulated autocomplete failure"
        raise RuntimeError(msg)
