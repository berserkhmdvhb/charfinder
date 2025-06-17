"""
Validation utilities for CharFinder configuration and CLI input.

Provides centralized validation logic shared by both core and CLI modules. Ensures that
all user-provided inputs—such as fuzzy algorithm names, thresholds, color modes, and
match modes—are consistently interpreted, validated, and normalized across the project.

Functions:
    validate_fuzzy_algo(): Normalize and validate fuzzy algorithm names.
    validate_threshold(): Ensure numeric threshold is within accepted bounds.
    validate_color_mode(): Validate and cast color display mode.
    validate_fuzzy_match_mode(): Check validity of fuzzy match mode.
    validate_exact_match_mode(): Check validity of exact match mode.
    resolve_effective_threshold(): Resolve CLI, environment, or default threshold.
    resolve_effective_color_mode(): Resolve CLI, environment, or default color mode.
    apply_fuzzy_defaults(): Apply default fuzzy config when CLI args are partial.

Type guards:
    is_supported_fuzzy_algo(): Check whether an algorithm is supported.

Custom argparse:
    ValidateFuzzyAlgoAction: Argparse Action class to validate --fuzzy-algo input.

Cache and Unicode data validators:
    validate_dict_str_keys(): Ensure cache dictionary structure is valid.
    validate_cache_rebuild_flag(): Enforce boolean flag integrity.
    validate_normalized_name(): Ensure a normalized name is valid.
    validate_cache_file_path(): Validate existence of a cache file path.
    validate_unicode_data_url(): Ensure Unicode data source URL is well-formed.
    validate_unicode_data_file(): Check that a Unicode data file exists and is readable.

Constants:
    ERROR_INVALID_THRESHOLD, ERROR_INVALID_NAME, ERROR_INVALID_CACHE_PATH:
        Standardized error messages.
    ENV_MATCH_THRESHOLD, ENV_COLOR_MODE: Environment variable names for config overrides.
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
    ENV_COLOR_MODE,
    ENV_MATCH_THRESHOLD,
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
from charfinder.utils.formatter import echo, should_use_color
from charfinder.utils.logger_styles import format_warning

# ------------------------------------------------------------------------
# Error Messages
# ------------------------------------------------------------------------

ERROR_INVALID_THRESHOLD = "Invalid threshold used."
ERROR_INVALID_CACHE_PATH = "Cache file path does not exist"
ERROR_INVALID_NAME = "Normalized name must be a non-empty string"
ERROR_EXPECTED_BOOL = "Expected a boolean value"
ERROR_EXPECTED_DICT = "Expected 'name_cache' to be a dictionary."
ERROR_EXPECTED_DICT_KEY = "Dictionary key must be a string"
ERROR_EXPECTED_DICT_VAL = "Value must be a dictionary"
ERROR_EXPECTED_PATH = "Expected 'cache_file_path' to be a Path object"

# ------------------------------------------------------------------------
# Fuzzy Algorithm Validators
# ------------------------------------------------------------------------


def is_supported_fuzzy_algo(value: str) -> bool:
    """Check if a fuzzy algorithm name is supported."""
    return value in FUZZY_ALGO_ALIASES


def validate_fuzzy_algo(fuzzy_algo: str) -> FuzzyAlgorithm:
    """
    Validate and normalize a fuzzy algorithm name.

    Args:
        fuzzy_algo (str): The fuzzy algorithm name (e.g., 'levenshtein', 'simple').

    Returns:
        FuzzyAlgorithm: The validated and normalized fuzzy algorithm.
    """
    fuzzy_algo = fuzzy_algo.lower()
    if not is_supported_fuzzy_algo(fuzzy_algo):
        return DEFAULT_FUZZY_ALGO
    return cast("FuzzyAlgorithm", FUZZY_ALGO_ALIASES[fuzzy_algo])


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
# Threshold Validators
# ------------------------------------------------------------------------


def resolve_cli_settings(args: Namespace) -> tuple[str, bool, float]:
    """
    Resolve runtime settings such as color mode and match threshold.

    Args:
        args (Namespace): Parsed command-line arguments.

    Returns:
        tuple[str, bool, float]: Effective (color_mode, use_color, threshold)
    """
    color_mode = resolve_effective_color_mode(args.color)
    use_color = should_use_color(color_mode)
    threshold = resolve_effective_threshold(args.threshold, use_color=use_color)
    return color_mode, use_color, threshold


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


def validate_threshold(threshold: float | None) -> float:
    """
    Validates and returns the threshold value. Ensures it's within the valid range [0.0, 1.0].

    Args:
        threshold (float | None): The threshold value to validate.

    Returns:
        float: The validated threshold value.
    """
    if threshold is None:
        return DEFAULT_THRESHOLD

    if threshold < 0.0 or threshold > 1.0:
        raise ValueError(ERROR_INVALID_THRESHOLD)

    return threshold


def resolve_effective_threshold(cli_threshold: float | None, *, use_color: bool = True) -> float:
    """
    Resolve threshold from CLI arg, env var, or default.

    Args:
        cli_threshold (float | None): Threshold value from CLI argument, or None.
        use_color (bool): Whether to apply ANSI formatting when logging warnings.

    Returns:
        float: The resolved threshold value.
    """
    if cli_threshold is not None:
        return validate_threshold(cli_threshold)

    env_value = os.getenv(ENV_MATCH_THRESHOLD)
    if env_value is not None:
        try:
            return validate_threshold(float(env_value))
        except ValueError:
            message = f"Invalid {ENV_MATCH_THRESHOLD} env var: {env_value!r}. Using default."
            echo(
                message,
                style=lambda m: format_warning(m, use_color=use_color),
                show=True,
                log=True,
                log_method="warning",
            )
    return DEFAULT_THRESHOLD


# ------------------------------------------------------------------------
# Color Mode & Match Mode Validators
# ------------------------------------------------------------------------


def cast_color_mode(value: str) -> ColorMode:
    return cast("ColorMode", value)


def validate_color_mode(color_mode: str | None) -> ColorMode:
    """
    Validate the color mode string and cast to the correct ColorMode literal.

    Args:
        color_mode (str | None): The input color mode (e.g., 'auto', 'always', 'never').

    Returns:
        ColorMode: A valid color mode literal.
    """
    if color_mode in VALID_COLOR_MODES:
        return cast_color_mode(color_mode)
    return DEFAULT_COLOR_MODE


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

    env_value = os.getenv(ENV_COLOR_MODE)
    if env_value in VALID_COLOR_MODES:
        return cast_color_mode(env_value)

    return DEFAULT_COLOR_MODE


def validate_fuzzy_match_mode(mode: str) -> FuzzyMatchMode:
    """
    Validates the fuzzy match mode. It must be either "single" or "hybrid".

    Args:
        mode (str): The fuzzy match mode to validate.

    Returns:
        FuzzyMatchMode: A valid fuzzy match mode ("single" or "hybrid").
    """
    mode = mode.lower()
    if mode not in VALID_FUZZY_MATCH_MODES:
        message = f"Invalid fuzzy match mode: {mode}. alid options are: {VALID_FUZZY_MATCH_MODES}"
        raise ValueError(message)
    return cast("FuzzyMatchMode", mode)


def validate_exact_match_mode(exact_match_mode: str) -> ExactMatchMode:
    """
    Validates the exact match mode. It must be either "substring" or "word-subset".

    Args:
        exact_match_mode (str): The exact match mode to validate.

    Returns:
        ExactMatchMode: A valid exact match mode.
    """
    if exact_match_mode not in VALID_EXACT_MATCH_MODES:
        message = (
            f"Invalid exact match mode: {exact_match_mode}. "
            f"Valid options are: {VALID_EXACT_MATCH_MODES}"
        )
        raise ValueError(message)
    return cast("ExactMatchMode", exact_match_mode)


# ------------------------------------------------------------------------
# Cache Validators
# ------------------------------------------------------------------------


def validate_dict_str_keys(name_cache: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """
    Validates that a dictionary has string keys and the values are dictionaries.

    Args:
        name_cache (dict): The dictionary to validate.

    Returns:
        dict: The validated dictionary.
    """
    if not isinstance(name_cache, dict):
        raise TypeError(ERROR_EXPECTED_DICT)

    for key, value in name_cache.items():
        if not isinstance(key, str):
            message = f"{ERROR_EXPECTED_DICT_KEY}. Found key of type {type(key)}."
            raise TypeError(message)
        if not isinstance(value, dict):
            message = f"{ERROR_EXPECTED_DICT_VAL} for key '{key}'."
            raise TypeError(message)

    return name_cache


def validate_cache_rebuild_flag(*, force_rebuild: bool) -> bool:
    """
    Validates that the 'force_rebuild' flag is a boolean.

    Args:
        force_rebuild (bool): The flag to validate.

    Returns:
        bool: The validated flag value.
    """
    if not isinstance(force_rebuild, bool):
        message = f"{ERROR_EXPECTED_BOOL}, got {type(force_rebuild)}."
        raise TypeError(message)
    return force_rebuild


def validate_normalized_name(name: str) -> str:
    """
    Validates the normalized name for Unicode characters.

    Args:
        name (str): The normalized name to validate.

    Returns:
        str: The validated normalized name.
    """
    if not isinstance(name, str) or not name.strip():
        message = f"{ERROR_INVALID_NAME}, got {name!r}."
        raise ValueError(message)
    return name


# ------------------------------------------------------------------------
# Unicode Data Validators
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
    """
    if cache_file_path is None:
        cache_file_path = get_cache_file()

    if not isinstance(cache_file_path, Path):
        message = f"{ERROR_EXPECTED_PATH}, got {type(cache_file_path)}"
        raise TypeError(message)

    if not cache_file_path.exists():
        message = f"{ERROR_INVALID_CACHE_PATH}: {cache_file_path}"
        raise ValueError(message)

    return cache_file_path


def validate_unicode_data_file(file_path: Path) -> bool:
    """Validate if the Unicode data file exists and is readable."""
    if not file_path.is_file():
        message = f"The file {file_path} does not exist."
        raise FileNotFoundError(message)
    return True
