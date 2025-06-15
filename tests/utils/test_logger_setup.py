"""Tests for charfinder.utils.logger_setup module."""

from __future__ import annotations

import logging
from pathlib import Path
from io import StringIO
from logging import StreamHandler
from typing import Callable

import pytest

from charfinder.utils.logger_setup import (
    get_logger,
    setup_logging,
    teardown_logger,
    get_default_formatter,
)
from charfinder.utils.logger_helpers import (
    EnvironmentFilter,
    StreamFilter,
    CustomRotatingFileHandler,
)


def test_setup_logging_creates_expected_handlers(
    temp_log_dir: Path,
    log_stream: StringIO,
    patched_stream_handler: Callable[[list[logging.Handler]], None],
) -> None:
    """setup_logging should return StreamHandler and FileHandler, and emit logs."""
    handlers = setup_logging(
        log_dir=temp_log_dir,
        reset=True,
        return_handlers=True,
        suppress_echo=True,
    )
    assert handlers is not None

    patched_stream_handler(handlers)
    logger = get_logger()
    logger.info("Logging initialized. Log file: %s", temp_log_dir)

    output = log_stream.getvalue()
    assert any(isinstance(h, StreamHandler) for h in handlers)
    assert any(isinstance(h, CustomRotatingFileHandler) for h in handlers)
    assert "Logging initialized. Log file:" in output
    assert str(temp_log_dir) in output


def test_teardown_logger_removes_all_handlers() -> None:
    """teardown_logger should remove all handlers."""
    logger = get_logger()
    setup_logging(reset=True)
    assert logger.hasHandlers()
    teardown_logger()
    assert not logger.hasHandlers()


def test_setup_logging_is_idempotent(temp_log_dir: Path) -> None:
    """Repeated setup_logging with reset=False should not add duplicate handlers."""
    setup_logging(log_dir=temp_log_dir, reset=True)
    first = set(type(h) for h in get_logger().handlers)

    setup_logging(log_dir=temp_log_dir, reset=False)
    second = set(type(h) for h in get_logger().handlers)

    assert first == second
    assert len(get_logger().handlers) == 2


def test_reset_true_reconfigures_handlers(temp_log_dir: Path) -> None:
    """reset=True should replace old handlers."""
    logger = get_logger()
    setup_logging(log_dir=temp_log_dir, reset=True)
    first_ids = [id(h) for h in logger.handlers]

    setup_logging(log_dir=temp_log_dir, reset=True)
    second_ids = [id(h) for h in logger.handlers]

    assert first_ids != second_ids
    assert len(second_ids) == 2


def test_console_log_level_respects_debug_flag(
    temp_log_dir: Path,
    log_stream: StringIO,
    patched_stream_handler: Callable[[list[logging.Handler]], None],
) -> None:
    """StreamHandler should emit DEBUG when log_level=DEBUG is passed."""
    handlers = setup_logging(
        log_dir=temp_log_dir,
        log_level=logging.DEBUG,
        reset=True,
        return_handlers=True,
        suppress_echo=True,
    )
    assert handlers is not None
    patched_stream_handler(handlers)

    logger = get_logger()
    logger.debug("debug message")

    assert "debug message" in log_stream.getvalue()


def test_console_log_level_defaults_to_info(
    temp_log_dir: Path,
    log_stream: StringIO,
    patched_stream_handler: Callable[[list[logging.Handler]], None],
) -> None:
    """StreamHandler defaults to INFO level and should not emit DEBUG logs."""
    handlers = setup_logging(
        log_dir=temp_log_dir,
        reset=True,
        return_handlers=True,
        suppress_echo=True,
    )
    assert handlers is not None
    patched_stream_handler(handlers)

    # Set handler to INFO, logger to DEBUG
    for handler in handlers:
        if isinstance(handler, StreamHandler):
            handler.setLevel(logging.INFO)

    logger = get_logger()
    logger.setLevel(logging.DEBUG)

    logger.debug("should not appear")
    logger.info("should appear")

    output = log_stream.getvalue()
    assert "should not appear" not in output
    assert "should appear" in output

@pytest.mark.parametrize("suppress_echo", [True, False])
def test_handlers_always_include_filters(
    temp_log_dir: Path,
    suppress_echo: bool,
) -> None:
    """
    All handlers must include EnvironmentFilter.
    Only the standard StreamHandler must include StreamFilter,
    regardless of echo suppression.
    """
    handlers = setup_logging(
        log_dir=temp_log_dir,
        reset=True,
        return_handlers=True,
        suppress_echo=suppress_echo,
    )
    assert handlers is not None

    for handler in handlers:
        # Expect EnvironmentFilter on all handlers
        has_env_filter = any(isinstance(f, EnvironmentFilter) for f in handler.filters)
        assert has_env_filter, f"{type(handler)} missing EnvironmentFilter"

        # Only the standard StreamHandler must include StreamFilter
        if type(handler) is logging.StreamHandler:
            has_stream_filter = any(isinstance(f, StreamFilter) for f in handler.filters)
            assert has_stream_filter, f"{type(handler)} missing StreamFilter"
        else:
            has_stream_filter = any(isinstance(f, StreamFilter) for f in handler.filters)
            assert not has_stream_filter, f"{type(handler)} should not have StreamFilter"


def test_get_default_formatter_returns_safeformatter_instance() -> None:
    """get_default_formatter should return a logging.Formatter-compatible instance."""
    formatter = get_default_formatter()
    assert isinstance(formatter, logging.Formatter)
