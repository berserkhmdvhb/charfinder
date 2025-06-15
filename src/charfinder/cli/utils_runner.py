"""Utilities for orchestrating the CharFinder CLI runner.

This module contains reusable utility functions used by the CLI main entry point
to organize logic such as:

- Determining the final query string (from positional or optional args).
- Managing environment variables and debug mode.
- Validating and normalizing fuzzy algorithm input.
- Displaying diagnostic banners and settings-related info.
- Executing the main character matching handler.
- Handling CLI completion, success, and exception exits.

All functions are used by `cli_main.py` to modularize and streamline execution.

Functions:
    resolve_final_query(): Determine the query string from CLI args.
    auto_enable_debug(): Enable debug if CHARFINDER_DEBUG_ENV_LOAD is set.
    validate_and_resolve_fuzzy_algo(): Normalize and validate fuzzy algorithm.
    handle_cli_workflow(): Execute main CLI logic and handler.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import logging
import os
import sys
import traceback
from argparse import Namespace

from charfinder.cli.diagnostics import print_debug_diagnostics
from charfinder.cli.handlers import (
    get_version,
    handle_find_chars,
    resolve_effective_color_mode,
)
from charfinder.constants import (
    EXIT_CANCELLED,
    EXIT_ERROR,
)
from charfinder.settings import get_environment, is_prod, load_settings
from charfinder.utils.formatter import echo, should_use_color
from charfinder.utils.logger_setup import get_logger, setup_logging, teardown_logger
from charfinder.utils.logger_styles import (
    format_error,
    format_info,
    format_settings,
    format_warning,
)
from charfinder.fuzzymatchlib import resolve_algorithm_name
__all__ = [
    "auto_enable_debug",
    "handle_cli_workflow",
    "resolve_final_query",
    "validate_and_resolve_fuzzy_algo",
]

# ---------------------------------------------------------------------
# Query Handling
# ---------------------------------------------------------------------


def resolve_final_query(args: Namespace) -> str:
    """
    Determine the final query string based on CLI arguments.

    Prefers --query/-q if provided; otherwise falls back to positional args.

    Args:
        args (Namespace): Parsed CLI arguments.

    Returns:
        str: The final normalized query string to use.
    """
    query_list = args.option_query if args.option_query else args.positional_query
    return " ".join(query_list).strip()


# ---------------------------------------------------------------------
# Environment and Flags
# ---------------------------------------------------------------------


def auto_enable_debug(args: Namespace) -> None:
    """
    Enable debug mode if CHARFINDER_DEBUG_ENV_LOAD=1 is set in the environment.

    Modifies `args.debug` in-place if not already set.

    Args:
        args (Namespace): Parsed CLI arguments.
    """
    if os.getenv("CHARFINDER_DEBUG_ENV_LOAD") == "1" and not args.debug:
        args.debug = True

"""
Centralized Validators for CharFinder.

This module provides shared validation functions that are used by both
the core and CLI modules of CharFinder. The validators ensure that input
values such as fuzzy algorithms, thresholds, match modes, and color modes
are validated consistently across the project.

Key Features:
- Centralized validation for core configuration options used across the project.
- Validation for fuzzy algorithms, thresholds, color modes, and match modes.
- Type guards for better type safety.
- Use of a dataclass to organize fuzzy configuration settings.
- Custom argparse actions for CLI validation.

Functions:
- threshold_range(value: str): Validates and converts the threshold value.
- fuzzy_algo_validator(value: str): Validates and normalizes the fuzzy algorithm.
- validate_fuzzy_algo(fuzzy_algo: str): Ensures the fuzzy algorithm is valid.
- validate_threshold(threshold: float | None): Validates the threshold value.
- validate_color_mode(color_mode: str | None): Validates the color mode.
- validate_fuzzy_match_mode(fuzzy_match_mode: str): Validates the fuzzy match mode.
- validate_exact_match_mode(exact_match_mode: str): Validates the exact match mode.
- resolve_effective_threshold(cli_threshold: float | None, use_color: bool):
    Resolves the effective threshold from CLI, environment, or default.
- resolve_effective_color_mode(cli_color_mode: str | None):
    Resolves the effective color mode from CLI, environment, or default.
- apply_fuzzy_defaults(args: Namespace, config: FuzzyConfig):
    Applies default fuzzy settings if necessary.
- ValidateFuzzyAlgoAction: Custom argparse action for validating fuzzy algorithm.

This module centralizes the validation logic for CharFinder, ensuring that all
configuration values are validated in a consistent and maintainable way across
both the core logic and CLI components of the project.
"""

import os
from argparse import Action, Namespace
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from charfinder.constants import (
    DEFAULT_COLOR_MODE,
    DEFAULT_FUZZY_ALGO,
    DEFAULT_THRESHOLD,
    FUZZY_ALGO_ALIASES,
    VALID_EXACT_MATCH_MODES,
    VALID_FUZZY_MATCH_MODES,
    ColorMode,
    ExactMatchMode,
    FuzzyAlgorithm,
)
from charfinder.settings import get_cache_file
from charfinder.utils.formatter import echo
from charfinder.utils.logger_styles import format_warning

ERROR_INVALID_THRESHOLD = "Invalied Threshold Used."
# ------------------------------------------------------------------------
# Type Guard for Fuzzy Algorithm Validation
# ------------------------------------------------------------------------


def is_valid_fuzzy_algo(value: str) -> bool:
    """Type guard to check if the algorithm is valid."""
    return value in FUZZY_ALGO_ALIASES


# ------------------------------------------------------------------------
# Dataclasses for Fuzzy Configuration
# ------------------------------------------------------------------------


@dataclass
class FuzzyConfig:
    fuzzy_algo: FuzzyAlgorithm
    fuzzy_match_mode: ExactMatchMode


# ------------------------------------------------------------------------
# Validators
# ------------------------------------------------------------------------


def threshold_range(value: str) -> float:
    """
    Validate that the threshold is a float between 0.0 and 1.0.

    Args:
        value (str): The input string from the command-line argument.

    Returns:
        float: The validated threshold as a float.

    Raises:
        ValueError: If the value is not a float, or not in the [0.0, 1.0] range.
    """
    try:
        fvalue = float(value)
    except ValueError as exc:
        raise ValueError(ERROR_INVALID_THRESHOLD) from exc

    if not 0.0 <= fvalue <= 1.0:
        raise ValueError(ERROR_INVALID_THRESHOLD)

    return fvalue


def fuzzy_algo_validator(value: str) -> FuzzyAlgorithm:
    """
    Validate and normalize the fuzzy algorithm name (case-insensitive).

    Args:
        value (str): Input from CLI (e.g., 'Levenshtein').

    Returns:
        FuzzyAlgorithm: Valid internal algorithm name string.

    Raises:
        ValueError: If the name is invalid.
    """
    return validate_fuzzy_algo(value)


def validate_fuzzy_algo(fuzzy_algo: str) -> FuzzyAlgorithm:
    """
    Validates the fuzzy algorithm name. If the provided algorithm name is invalid,
    it returns the default fuzzy algorithm.

    Args:
        fuzzy_algo (str): The fuzzy algorithm to validate.

    Returns:
        FuzzyAlgorithm: A valid fuzzy algorithm name.
    """
    if not fuzzy_algo.strip():
        message = "Fuzzy algorithm cannot be empty."
        raise ValueError(message)

    fuzzy_algo = fuzzy_algo.lower()
    if not is_valid_fuzzy_algo(fuzzy_algo):
        return DEFAULT_FUZZY_ALGO  # Use the default algorithm from constants.py
    return fuzzy_algo


def validate_threshold(threshold: float | None) -> float:
    """
    Validates and returns the threshold value. Ensures it's within the valid range [0.0, 1.0].

    Args:
        threshold (float | None): The threshold value to validate.

    Returns:
        float: The validated threshold value.
    """
    if threshold is None:
        return DEFAULT_THRESHOLD  # Use the default threshold from constants.py

    if threshold < 0.0 or threshold > 1.0:
        raise ValueError(ERROR_INVALID_THRESHOLD)

    return threshold


def validate_color_mode(color_mode: str | None) -> ColorMode:
    """
    Validates and returns the color mode. Ensures it's one of 'auto', 'always', or 'never'.

    Args:
        color_mode (str | None): The color mode value to validate.

    Returns:
        str: The validated color mode.
    """
    if color_mode in {"auto", "always", "never"}:
        return color_mode

    return DEFAULT_COLOR_MODE  # Use the default color mode from constants.py


def validate_fuzzy_match_mode(fuzzy_match_mode: str) -> str:
    """
    Validates the fuzzy match mode. It must be either "single" or "hybrid".

    Args:
        fuzzy_match_mode (str): The fuzzy match mode to validate.

    Returns:
        str: A valid fuzzy match mode ("single" or "hybrid").
    """
    if fuzzy_match_mode not in VALID_FUZZY_MATCH_MODES:
        message = (
            f"Invalid fuzzy match mode: {fuzzy_match_mode}. "
            f"Valid options are: {VALID_FUZZY_MATCH_MODES}"
        )
        raise ValueError(message)
    return fuzzy_match_mode


def validate_exact_match_mode(exact_match_mode: str) -> ExactMatchMode:
    """
    Validates the exact match mode. It must be either "substring" or "word-subset".

    Args:
        exact_match_mode (str): The exact match mode to validate.

    Returns:
        ExactMatchMode: A valid exact match mode ("substring" or "word-subset").
    """
    if exact_match_mode not in VALID_EXACT_MATCH_MODES:
        message = (
            f"Invalid exact match mode: {exact_match_mode}. "
            f"Valid options are: {VALID_EXACT_MATCH_MODES}"
        )
        raise ValueError(message)
    return exact_match_mode


def resolve_effective_threshold(cli_threshold: float | None, *, use_color: bool = True) -> float:
    """Resolve threshold from CLI arg, env var, or default.

    Args:
        cli_threshold (float | None): Threshold value from CLI argument, or None.
        use_color (bool): Whether to apply ANSI formatting when logging warnings.

    Returns:
        float: The resolved threshold value.
    """
    if cli_threshold is not None:
        return validate_threshold(cli_threshold)

    env_value = os.getenv("CHARFINDER_MATCH_THRESHOLD")
    if env_value is not None:
        try:
            return validate_threshold(float(env_value))
        except ValueError:
            message = f"Invalid CHARFINDER_MATCH_THRESHOLD env var: {env_value!r}. Using default."
            echo(
                message,
                style=lambda m: format_warning(m, use_color=use_color),
                show=True,
                log=True,
                log_method="warning",
            )
    return DEFAULT_THRESHOLD  # Use the default threshold from constants.py


def resolve_effective_color_mode(cli_color_mode: str | None) -> ColorMode:
    """Resolve color mode from CLI arg, env var, or default.

    Args:
        cli_color_mode (str | None): Color mode from CLI argument, or None.

    Returns:
        ColorMode: The resolved color mode.
    """
    if cli_color_mode is not None:
        return validate_color_mode(cli_color_mode)

    env_value = os.getenv("CHARFINDER_COLOR_MODE")
    if env_value in {"auto", "always", "never"}:
        return env_value

    return DEFAULT_COLOR_MODE  # Use the default color mode from constants.py


def apply_fuzzy_defaults(args: Namespace, config: FuzzyConfig) -> None:
    """Apply default fuzzy match algorithm and mode if --fuzzy is set.

    Args:
        args (Namespace): Parsed CLI arguments.
        config (FuzzyConfig): Configuration object for fuzzy settings.
    """
    if args.fuzzy:
        if not getattr(args, "fuzzy_algo", None):
            args.fuzzy_algo = config.fuzzy_algo
        if not getattr(args, "fuzzy_match_mode", None):
            args.fuzzy_match_mode = config.fuzzy_match_mode


# ------------------------------------------------------------------------
# Custom argparse Action for Fuzzy Algorithm Validation
# ------------------------------------------------------------------------


class ValidateFuzzyAlgoAction(Action):
    def __call__(self, namespace: Namespace, values: str, __: str | None = None) -> None:
        validated_value = validate_fuzzy_algo(values)
        setattr(namespace, self.dest, validated_value)


# ------------------------------------------------------------------------
# Caching Validators
# ------------------------------------------------------------------------


def validate_dict_str_keys(name_cache: dict) -> dict:
    """
    Validates that a dictionary has string keys and the values are dictionaries.

    Args:
        name_cache (dict): The dictionary to validate.

    Returns:
        dict: The validated dictionary.

    Raises:
        ValueError: If the dictionary contains invalid keys or values.
    """
    if not isinstance(name_cache, dict):
        message = "Expected 'name_cache' to be a dictionary."
        raise TypeError(message)

    for key, value in name_cache.items():
        if not isinstance(key, str):
            message = f"Dictionary key must be a string. Found key of type {type(key)}."
            raise TypeError(message)
        if not isinstance(value, dict):
            message = f"Value for key '{key}' must be a dictionary."
            raise TypeError(message)

    return name_cache


def validate_cache_rebuild_flag(*, force_rebuild: bool) -> bool:
    """
    Validates that the 'force_rebuild' flag is a boolean.

    Args:
        force_rebuild (bool): The flag to validate.

    Returns:
        bool: The validated flag value.

    Raises:
        ValueError: If the value is not a boolean.
    """
    if not isinstance(force_rebuild, bool):
        message = f"Expected 'force_rebuild' to be a boolean, but got {type(force_rebuild)}."
        raise TypeError(message)
    return force_rebuild


def validate_normalized_name(name: str) -> str:
    """
    Validates the normalized name for Unicode characters.

    Args:
        name (str): The normalized name to validate.

    Returns:
        str: The validated normalized name.

    Raises:
        ValueError: If the name is empty or improperly normalized.
    """
    if not isinstance(name, str) or not name.strip():
        message = f"Normalized name must be a non-empty string, but got '{name}'."
        raise ValueError(message)
    return name


# ------------------------------------------------------------------------
# Unicode Data Retrieval Validators
# ------------------------------------------------------------------------


def validate_unicode_data_url(url: str) -> bool:
    """Validate the Unicode data URL."""
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        message = f"Invalid URL: {url}"
        raise ValueError(message)
    return True


def validate_cache_file_path(cache_file_path: Path | None) -> Path:
    """
    Validates the provided cache file path.

    Args:
        cache_file_path (Path | None): The cache file path to validate.

    Returns:
        Path: The validated file path.

    Raises:
        ValueError: If the path is not a valid `Path` or does not exist.
    """
    if cache_file_path is None:
        cache_file_path = get_cache_file()  # Default to standard cache file if None

    if not isinstance(cache_file_path, Path):
        message = (
            f"Expected 'cache_file_path' to be a Path object, but got {type(cache_file_path)}."
        )
        raise TypeError(message)

    if not cache_file_path.exists():
        message = f"Cache file path does not exist: {cache_file_path}"
        raise ValueError(message)

    return cache_file_path


def validate_unicode_data_file(file_path: Path) -> bool:
    """Validate if the Unicode data file exists and is readable."""
    if not file_path.is_file():
        message = f"The file {file_path} does not exist."
        raise FileNotFoundError(message)
    return True



def validate_and_resolve_fuzzy_algo(args: Namespace, *, use_color: bool) -> None:
    """
    Normalize and validate the fuzzy algorithm argument if provided.

    Args:
        args (Namespace): Parsed CLI arguments.
        use_color (bool): Whether to use color in error messages.

    Raises:
        SystemExit: If the algorithm is invalid, with appropriate error message.
    """
    if args.fuzzy_algo:
        try:
            args.fuzzy_algo = resolve_algorithm_name(args.fuzzy_algo)
        except ValueError as exc:
            echo(
                f"Invalid --fuzzy-algo: {exc}",
                style=lambda msg: format_error(msg, use_color=use_color),
                stream=sys.stderr,
                show=True,
                log=True,
                log_method="error",
            )
            sys.exit(EXIT_ERROR)


# ---------------------------------------------------------------------
# Main Execution Logic
# ---------------------------------------------------------------------


def handle_cli_workflow(args: Namespace, query_str: str, *, use_color: bool) -> int:
    """
    Perform the main CLI workflow, including logging setup, environment loading,
    diagnostics, and matching dispatch.

    Args:
        args (Namespace): Parsed CLI arguments.
        query_str (str): Final query string.
        use_color (bool): Whether color output should be used.

    Returns:
        int: Exit code (EXIT_SUCCESS, EXIT_CANCELLED, or EXIT_ERROR).
    """
    # Logging Setup
    setup_logging(reset=True, log_level=None, suppress_echo=True, use_color=use_color)

    # Load .env settings
    load_settings(verbose=args.verbose, debug=args.debug)

    # Resolve settings and color mode (new)
    color_mode = resolve_effective_color_mode(args.color)
    use_color = should_use_color(color_mode)

    # Finalize logging
    log_level = logging.DEBUG if args.debug else None
    setup_logging(
        reset=True,
        log_level=log_level,
        suppress_echo=not (args.verbose or args.debug),
        use_color=use_color,
    )

    logger = get_logger()

    try:
        # Echo environment info
        echo(
            f"Using environment: {get_environment()}",
            style=lambda m: format_settings(m, use_color=use_color),
            show=args.verbose,
            log=True,
            log_method="info",
        )

        # Prod warning
        if is_prod():
            echo(
                "You are running in PROD environment!",
                style=lambda m: format_warning(m, use_color=use_color),
                stream=sys.stderr,
                show=True,
                log=True,
                log_method="warning",
            )

        # CharFinder CLI start
        echo(
            f"CharFinder {get_version()} CLI started",
            style=lambda m: format_info(m, use_color=use_color),
            show=args.verbose,
            log=True,
            log_method="info",
        )

        # Execute the main search handler
        exit_code, match_info = handle_find_chars(args, query_str)

        # Print diagnostics if debug is enabled
        if args.debug:
            print_debug_diagnostics(
                args=args,
                match_info=match_info,
                use_color=use_color,
                show=True,
            )

        echo(
            f"Processing finished. Query: '{query_str}'",
            style=lambda m: format_info(m, use_color=use_color),
            show=args.verbose,
            log=True,
            log_method="info",
        )

    except KeyboardInterrupt:
        echo(
            "Execution interrupted by user.",
            style=lambda msg: format_warning(msg, use_color=use_color),
            stream=sys.stderr,
            show=True,
            log=True,
            log_method="warning",
        )
        return EXIT_CANCELLED

    except Exception as exc:  # noqa: BLE001
        echo(
            "Unhandled error during CLI execution",
            style=lambda msg: format_error(msg, use_color=use_color),
            stream=sys.stderr,
            show=True,
            log=True,
            log_method="exception",
        )
        echo(
            f"Error: {exc}",
            style=lambda msg: format_error(msg, use_color=use_color),
            stream=sys.stderr,
            show=True,
            log=True,
            log_method="exception",
        )

        if args.debug:
            traceback.print_exc()

        return EXIT_ERROR

    else:
        return exit_code

    finally:
        teardown_logger(logger)
