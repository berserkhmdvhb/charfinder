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
from argparse import Action, ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

from charfinder.constants import (
    DEFAULT_COLOR_MODE,
    DEFAULT_FUZZY_ALGO,
    DEFAULT_THRESHOLD,
    FUZZY_ALGO_ALIASES,
    VALID_COLOR_MODES,
    VALID_EXACT_MATCH_MODES,
    VALID_FUZZY_MATCH_MODES,
    ColorMode,
    ExactMatchMode,
    FuzzyAlgorithm,
    FuzzyConfig,
    FuzzyMatchMode,
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
    Validate and normalize a fuzzy algorithm name.

    Args:
        fuzzy_algo (str): The fuzzy algorithm name (e.g., 'levenshtein', 'simple').

    Returns:
        FuzzyAlgorithm: The validated and normalized fuzzy algorithm.
    """
    fuzzy_algo = fuzzy_algo.lower()
    if not is_valid_fuzzy_algo(fuzzy_algo):
        return DEFAULT_FUZZY_ALGO
    return cast("FuzzyAlgorithm", FUZZY_ALGO_ALIASES[fuzzy_algo])


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
    Validate the color mode string and cast to the correct ColorMode literal.

    Args:
        color_mode (str | None): The input color mode (e.g., 'auto', 'always', 'never').

    Returns:
        ColorMode: A valid color mode literal.
    """
    from typing import cast

    if color_mode in VALID_COLOR_MODES:
        return cast("ColorMode", color_mode)
    return DEFAULT_COLOR_MODE


def validate_fuzzy_match_mode(mode: str) -> FuzzyMatchMode:
    """
    Validates the fuzzy match mode. It must be either "single" or "hybrid".

    Args:
        mode (str): The fuzzy match mode to validate.

    Returns:
        str: A valid fuzzy match mode ("single" or "hybrid").
    """
    mode = mode.lower()
    if mode not in VALID_FUZZY_MATCH_MODES:
        message = f"Invalid fuzzy match mode: {mode}. Valid options are: {VALID_FUZZY_MATCH_MODES}"
        raise ValueError(message)
    return cast("FuzzyMatchMode", mode)


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
    return cast("ExactMatchMode", exact_match_mode)


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
    """
    Determine the effective color mode based on CLI input or environment variables.

    Args:
        cli_color_mode (str | None): CLI-specified color mode.

    Returns:
        ColorMode: The resolved color mode.
    """
    if cli_color_mode is not None:
        return validate_color_mode(cli_color_mode)

    env_value = os.getenv("CHARFINDER_COLOR_MODE")
    if env_value in VALID_COLOR_MODES:
        from typing import cast

        return cast("ColorMode", env_value)

    return DEFAULT_COLOR_MODE


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
    def __call__(
        self,
        _: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[str] | None,
        __: str | None = None,
    ) -> None:
        target = (
            values[0] if isinstance(values, Sequence) and not isinstance(values, str) else values
        )
        validated_value = validate_fuzzy_algo(cast("str", target))
        setattr(namespace, self.dest, validated_value)


# ------------------------------------------------------------------------
# Caching Validators
# ------------------------------------------------------------------------


def validate_dict_str_keys(name_cache: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
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
