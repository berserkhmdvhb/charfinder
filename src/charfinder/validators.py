"""
Validation utilities for CharFinder configuration and CLI input.

This module centralizes all validation logic for both core and CLI components,
ensuring consistent, safe interpretation of user inputs such as fuzzy algorithm names,
thresholds, color modes, and match modes. It also validates cache structures, file paths,
and Unicode data configurations.

Functions:
    is_supported_fuzzy_algo(): Check if a fuzzy algorithm name is supported.
    _normalize_and_validate_fuzzy_algo():
        Internal normalization and strict validation of fuzzy algorithm.
    validate_fuzzy_algo(): Public validator for fuzzy algorithm, with CLI/core context handling.
    apply_fuzzy_defaults(): Populate missing fuzzy settings in CLI args using fallback config.
    _validate_threshold_internal(): Internal float threshold range check.
    threshold_range(): Argparse-compatible converter for threshold values.
    validate_threshold(): Validate threshold, allowing CLI/default fallback logic.
    resolve_effective_threshold(): Resolve final threshold using CLI, env var, or default.
    cast_color_mode(): Cast a string to ColorMode type.
    validate_color_mode(): Validate and return effective color mode string.
    resolve_effective_color_mode(): Determine color mode from CLI or env.
    validate_fuzzy_match_mode(): Validate and normalize a fuzzy match mode string.
    validate_exact_match_mode(): Validate and normalize an exact match mode string.
    validate_dict_str_keys(): Ensure a nested string-keyed dictionary structure (e.g., name cache).
    validate_cache_rebuild_flag(): Validate that a rebuild flag is a proper boolean.
    validate_normalized_name(): Ensure a normalized name is a valid non-empty string.
    validate_unicode_data_url(): Validate that a Unicode data URL is well-formed.
    validate_cache_file_path(): Validate that a given or default cache file path exists.
    validate_unicode_data_file(): Confirm that a given file path points to an existing file.
    resolve_cli_settings(): Resolve CLI-derived color mode, use_color flag, and threshold.

Custom argparse:
    ValidateFuzzyAlgoAction: Argparse Action subclass for --fuzzy-algo validation.

Constants:
    ERROR_INVALID_THRESHOLD: Message used for invalid threshold input.
    ERROR_INVALID_NAME: Message used when a name is not a valid non-empty string.
    ERROR_INVALID_CACHE_PATH: Message used when the cache file path is not valid.
    ENV_MATCH_THRESHOLD: Env var key for threshold override.
    ENV_COLOR_MODE: Env var key for color mode override.

This module is shared across CLI and core layers to prevent duplicated validation logic
and ensure strict consistency for all user- or config-sourced inputs.
"""

import os
from argparse import Action, ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, cast
from urllib.parse import urlparse

from charfinder.config.constants import (
    DEFAULT_COLOR_MODE,
    DEFAULT_THRESHOLD,
    ENV_COLOR_MODE,
    ENV_MATCH_THRESHOLD,
    FUZZY_ALGO_ALIASES,
    VALID_COLOR_MODES,
    VALID_EXACT_MATCH_MODES,
    VALID_FUZZY_MATCH_MODES,
    VALID_HYBRID_AGG_FUNCS,
    VALID_OUTPUT_FORMATS,
    ColorMode,
    ExactMatchMode,
    FuzzyAlgorithm,
    FuzzyConfig,
    FuzzyMatchMode,
)
from charfinder.config.settings import get_cache_file
from charfinder.config.types import HybridAggFunc, NameCache
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
ERROR_MISSING_FUZZY_ALGO_VALUE = "Missing fuzzy algorithm value."
ERROR_EMPTY_FUZZY_ALGO_LIST = "Empty list of fuzzy algorithm values."
ERROR_INVALID_OUTPUT_FORMAT = (
    f"Invalid output format. Supported formats: {', '.join(sorted(VALID_OUTPUT_FORMATS))}."
)
ERROR_INVALID_AGG_FUNC = (
    "Invalid hybrid aggregation function. "
    "Expected one of: {', '.join(sorted(VALID_HYBRID_AGG_FUNCS))}."
)

ERROR_UNKNOWN_ALGO = "Unknown or unsupported fuzzy algorithm."
# ------------------------------------------------------------------------
# Fuzzy Algorithm Validators
# ------------------------------------------------------------------------


def is_supported_fuzzy_algo(value: str) -> bool:
    """
    Check if a fuzzy algorithm name is supported.

    Args:
        value (str): The fuzzy algorithm name to check.

    Returns:
        bool: True if the algorithm is supported (including aliases), False otherwise.
    """
    return value in FUZZY_ALGO_ALIASES


def _normalize_and_validate_fuzzy_algo(fuzzy_algo: str) -> FuzzyAlgorithm:
    """
    Normalize and validate the given fuzzy algorithm name.

    Converts dashes to underscores and lowercases the input.
    Resolves aliases defined in FUZZY_ALGO_ALIASES and ensures
    the final result is registered in FUZZY_ALGORITHM_REGISTRY.

    Args:
        fuzzy_algo (str): The fuzzy algorithm name (alias or canonical).

    Returns:
        FuzzyAlgorithm: Canonical name of the validated fuzzy algorithm.

    Raises:
        ValueError: If the algorithm is not supported.
    """
    # Lazy import
    from charfinder.fuzzymatchlib import FUZZY_ALGORITHM_REGISTRY  # noqa: PLC0415

    normalized = fuzzy_algo.strip().lower().replace("-", "_")
    resolved = FUZZY_ALGO_ALIASES.get(normalized, normalized)

    if resolved in FUZZY_ALGORITHM_REGISTRY:
        return resolved  # type: ignore[return-value]

    valid_inputs = sorted(set(FUZZY_ALGO_ALIASES) | set(FUZZY_ALGORITHM_REGISTRY))
    message = f"{ERROR_UNKNOWN_ALGO} Supported values: {', '.join(valid_inputs)}"
    raise ValueError(message)


def validate_fuzzy_algo(
    fuzzy_algo: str, *, source: Literal["cli", "core"] = "core"
) -> FuzzyAlgorithm:
    """
    Validate and normalize a fuzzy algorithm name.

    In CLI context, assumes the value has already been validated via argparse.
    In core context, performs normalization and full validation using known aliases.

    Args:
        fuzzy_algo (str): The fuzzy algorithm name to validate.
        source (Literal["cli", "core"], optional):
            The source of the invocation. If "cli", skips redundant validation.
            Defaults to "core".

    Returns:
        FuzzyAlgorithm: The normalized fuzzy algorithm name.

    Raises:
        ValueError: If the algorithm is invalid and source is "core".
    """
    if source == "cli":
        return cast("FuzzyAlgorithm", fuzzy_algo)
    return _normalize_and_validate_fuzzy_algo(fuzzy_algo)


class ValidateFuzzyAlgoAction(Action):
    """
    Argparse custom action to validate and normalize fuzzy algorithm names.

    This action is used in CLI argument parsing to ensure that the fuzzy algorithm
    specified by the user is valid and normalized at parse time.

    Example:
        parser.add_argument(
            "--fuzzy-algo",
            action=ValidateFuzzyAlgoAction,
            help="Specify the fuzzy matching algorithm to use.",
        )

    Methods:
        __call__: Invoked by argparse to process and validate the argument.
    """

    def __call__(
        self,
        _: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[str] | None,
        __: str | None = None,
    ) -> None:
        """
        Validate the fuzzy algorithm argument and set it in the namespace.

        Args:
            _ (ArgumentParser): The argument parser (unused).
            namespace (Namespace): The argparse namespace to update.
            values (str | Sequence[str] | None): The raw input value(s) for the argument.
            __ (str | None): The option string used (unused).

        Raises:
            ValueError: If the provided value is not a supported fuzzy algorithm.
        """
        if values is None:
            raise ValueError(ERROR_MISSING_FUZZY_ALGO_VALUE)

        if isinstance(values, Sequence) and not isinstance(values, str):
            if not values:
                raise ValueError(ERROR_EMPTY_FUZZY_ALGO_LIST)
            target = values[0]
        else:
            target = values

        validated_value = _normalize_and_validate_fuzzy_algo(target)
        setattr(namespace, self.dest, validated_value)


def apply_fuzzy_defaults(args: Namespace, config: FuzzyConfig) -> None:
    """
    Apply default fuzzy algorithm and match mode to CLI args if missing.

    This function checks if `--fuzzy` was enabled by the user. If so, and if
    no algorithm or match mode was explicitly set in the CLI args, it assigns
    the defaults from the provided `FuzzyConfig`.

    Args:
        args (Namespace): Parsed CLI arguments from argparse.
        config (FuzzyConfig): Default configuration containing algorithm and match mode.

    Returns:
        None
    """
    if args.fuzzy:
        if not getattr(args, "fuzzy_algo", None):
            args.fuzzy_algo = config.fuzzy_algo
        if not getattr(args, "fuzzy_match_mode", None):
            args.fuzzy_match_mode = config.fuzzy_match_mode


# ------------------------------------------------------------------------
# Threshold Validators
# ------------------------------------------------------------------------


def _validate_threshold_internal(threshold: float) -> float:
    """
    Validate that a threshold is within the accepted range [0.0, 1.0].

    Args:
        threshold (float): The threshold value to validate.

    Returns:
        float: The validated threshold.

    Raises:
        ValueError: If the threshold is outside the range [0.0, 1.0].
    """
    if threshold < 0.0 or threshold > 1.0:
        raise ValueError(ERROR_INVALID_THRESHOLD)
    return threshold


def threshold_range(value: str) -> float:
    """
    Convert a string to a float and validate it as a threshold value.

    Intended for use with argparse `type=...` to ensure the threshold is
    a float between 0.0 and 1.0 inclusive.

    Args:
        value (str): The string input from the command line.

    Returns:
        float: The validated float threshold value.

    Raises:
        ValueError: If the string cannot be converted to float or is out of bounds.
    """
    try:
        fvalue = float(value)
    except ValueError as exc:
        raise ValueError(ERROR_INVALID_THRESHOLD) from exc
    return _validate_threshold_internal(fvalue)


def validate_threshold(
    threshold: float | None, *, source: Literal["cli", "core"] = "core"
) -> float:
    """
    Validate and normalize a threshold value between 0.0 and 1.0.

    Args:
        threshold (float | None): The threshold value to validate.
        source (Literal["cli", "core"], optional):
            Indicates the calling context. If 'cli', assumes prior validation
            by argparse and returns as-is or default. Defaults to 'core'.

    Returns:
        float: A valid threshold value within [0.0, 1.0].

    Raises:
        ValueError: If the threshold is outside the valid range (core only).
    """
    if source == "cli":
        return threshold if threshold is not None else DEFAULT_THRESHOLD
    if threshold is None:
        return DEFAULT_THRESHOLD
    return _validate_threshold_internal(threshold)


def resolve_effective_threshold(cli_threshold: float | None, *, use_color: bool = True) -> float:
    """
    Resolve the effective threshold value from CLI, environment variable, or default.

    Priority:
        1. CLI-provided threshold (already validated).
        2. Environment variable `CHARFINDER_MATCH_THRESHOLD`.
        3. Default value.

    Args:
        cli_threshold (float | None): Threshold value from CLI input, if any.
        use_color (bool, optional): Whether to use color in warning messages. Defaults to True.

    Returns:
        float: A valid threshold value within the range [0.0, 1.0].

    Logs:
        A warning if the environment variable is present but invalid.

    Raises:
        ValueError: Only indirectly via `_validate_threshold_internal` if CLI value is invalid.
    """
    if cli_threshold is not None:
        return validate_threshold(cli_threshold, source="cli")

    env_value = os.getenv(ENV_MATCH_THRESHOLD)
    if env_value is not None:
        try:
            return _validate_threshold_internal(float(env_value))
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
    """
    Cast a string value to the ColorMode type.

    This function assumes the input value is already validated and belongs
    to the set of valid color modes.

    Args:
        value (str): The color mode string.

    Returns:
        ColorMode: The value cast to the ColorMode type.
    """
    return cast("ColorMode", value)


def validate_color_mode(
    color_mode: str | None, *, source: Literal["cli", "core"] = "core"
) -> ColorMode:
    """
    Validate and normalize a color mode string.

    If the color mode is valid, it is cast to the appropriate ColorMode type.
    If not provided or invalid, the default color mode is returned.

    Args:
        color_mode (str | None): The color mode string to validate.
        source (Literal["cli", "core"]): The context of invocation.
            "cli" assumes argparse has already validated the value.

    Returns:
        ColorMode: The validated and normalized color mode.
    """
    if source == "cli" and color_mode in VALID_COLOR_MODES:
        return cast_color_mode(color_mode)
    if color_mode in VALID_COLOR_MODES:
        return cast_color_mode(color_mode)
    return DEFAULT_COLOR_MODE


def resolve_effective_color_mode(cli_color_mode: str | None) -> ColorMode:
    """
    Determine the effective color mode by prioritizing CLI, then environment variable, then default.

    This function checks:
    1. CLI-supplied value (assumed validated by argparse).
    2. Environment variable `CHARFINDER_COLOR_MODE`.
    3. Fallback to the default color mode.

    Args:
        cli_color_mode (str | None): The color mode string from CLI arguments.

    Returns:
        ColorMode: The resolved color mode.
    """
    if cli_color_mode is not None:
        return validate_color_mode(cli_color_mode, source="cli")

    env_value = os.getenv(ENV_COLOR_MODE)
    if env_value in VALID_COLOR_MODES:
        return cast_color_mode(env_value)

    return DEFAULT_COLOR_MODE


def validate_fuzzy_match_mode(mode: str) -> FuzzyMatchMode:
    """
    Validate and normalize the fuzzy match mode.

    Converts the mode to lowercase and ensures it is one of the supported fuzzy match modes.
    Raises a ValueError if the input is not a valid mode.

    Args:
        mode (str): The fuzzy match mode to validate.

    Returns:
        FuzzyMatchMode: The validated and normalized fuzzy match mode.

    Raises:
        ValueError: If the mode is not in the list of VALID_FUZZY_MATCH_MODES.
    """
    mode = mode.lower()
    if mode not in VALID_FUZZY_MATCH_MODES:
        message = f"Invalid fuzzy match mode: {mode}. Valid options: {VALID_FUZZY_MATCH_MODES}"
        raise ValueError(message)
    return cast("FuzzyMatchMode", mode)


def validate_exact_match_mode(exact_match_mode: str) -> ExactMatchMode:
    """
    Validate the exact match mode string.

    Ensures the given string is one of the valid exact match modes and casts it to ExactMatchMode.
    Raises a ValueError if the input is invalid.

    Args:
        exact_match_mode (str): The exact match mode to validate.

    Returns:
        ExactMatchMode: The validated and cast exact match mode.

    Raises:
        ValueError: If the exact match mode is not one of VALID_EXACT_MATCH_MODES.
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


def validate_dict_str_keys(name_cache: NameCache) -> NameCache:
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
    Validate that the `force_rebuild` flag is a boolean.

    Args:
        force_rebuild (bool): A flag indicating whether to force rebuild the cache.

    Raises:
        TypeError: If `force_rebuild` is not a boolean.

    Returns:
        bool: The validated `force_rebuild` flag.
    """
    if not isinstance(force_rebuild, bool):
        message = f"{ERROR_EXPECTED_BOOL}, got {type(force_rebuild)}."
        raise TypeError(message)
    return force_rebuild


def validate_normalized_name(name: str) -> str:
    """
    Validate that a name is a non-empty, non-whitespace string.

    This function is typically used to ensure that normalized character names
    are valid before being used in lookups or comparisons.

    Args:
        name (str): The name string to validate.

    Raises:
        ValueError: If the name is not a string or is empty/whitespace only.

    Returns:
        str: The validated name string.
    """
    if name is None or not isinstance(name, str) or not name.strip():
        message = f"{ERROR_INVALID_NAME},got {{name!r}}."
        raise ValueError(message)
    return name


# ------------------------------------------------------------------------
# Unicode Data Validators
# ------------------------------------------------------------------------


def validate_unicode_data_url(url: str) -> bool:
    """
    Validate that a given string is a well-formed URL.

    This function checks whether the provided string has both a scheme and a netloc,
    ensuring it represents a valid URL for accessing remote Unicode data.

    Args:
        url (str): The URL string to validate.

    Raises:
        ValueError: If the string is not a valid URL.

    Returns:
        bool: True if the URL is valid.
    """
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        message = f"Invalid URL: {url}"
        raise ValueError(message)
    return True


def validate_cache_file_path(cache_file_path: Path | None) -> Path:
    """
    Validate the provided cache file path or resolve the default one.

    Ensures that the input is a valid `Path` object and that the file exists.
    If `None` is passed, the function will use the default cache file path
    as defined by `get_cache_file()`.

    Args:
        cache_file_path (Path | None): The cache file path to validate or None to use default.

    Raises:
        TypeError: If the resolved value is not a Path instance.
        ValueError: If the file does not exist.

    Returns:
        Path: A valid, existing Path object to the cache file.
    """
    if cache_file_path is None:
        cache_file_path = get_cache_file()

    if not isinstance(cache_file_path, Path):
        message = f"{ERROR_EXPECTED_PATH}, got {type(cache_file_path)}"
        raise TypeError(message)

    if not cache_file_path.is_file():
        message = f"{ERROR_INVALID_CACHE_PATH}: {cache_file_path}"
        raise ValueError(message)

    return cache_file_path


def validate_unicode_data_file(file_path: Path) -> bool:
    """
    Validate that the given file path points to an existing file.

    Args:
        file_path (Path): The path to the Unicode data file.

    Raises:
        FileNotFoundError: If the file does not exist or is not a file.

    Returns:
        bool: True if the file exists and is valid.
    """
    if not file_path.is_file():
        message = f"The file {file_path} does not exist."
        raise FileNotFoundError(message)
    return True


def resolve_cli_settings(args: Namespace) -> tuple[str, bool, float]:
    """
    Resolve CLI-derived settings for color mode, terminal color usage, and threshold.

    This function determines the effective color mode, whether terminal output should use color,
    and the fuzzy match threshold by considering CLI arguments and environment variables.

    Args:
        args (Namespace): The parsed CLI arguments namespace.

    Returns:
        tuple[str, bool, float]: A tuple containing:
            - color_mode (str): The effective color mode.
            - use_color (bool): Whether color output should be used.
            - threshold (float): The effective match threshold.
    """
    color_mode = resolve_effective_color_mode(args.color)
    use_color = should_use_color(color_mode)
    threshold = resolve_effective_threshold(args.threshold, use_color=use_color)
    return color_mode, use_color, threshold


# ------------------------------------------------------------------------
# Output Format Validator
# ------------------------------------------------------------------------


def validate_output_format(fmt: str) -> str:
    """
    Validate the output format string used by the CLI.

    Ensures the specified output format is one of the supported options ("json" or "text").

    Args:
        fmt (str): The output format string to validate.

    Raises:
        ValueError: If the format is not one of the supported values.

    Returns:
        str: The validated output format.
    """
    if fmt not in ("json", "text"):
        message = f"{ERROR_INVALID_OUTPUT_FORMAT} Got: {fmt}"
        raise ValueError(message)
    return fmt


def validate_hybrid_agg_fn(fn: str) -> HybridAggFunc:
    """
    Validate and normalize the hybrid aggregation function.

    Args:
        fn: Aggregation function name.

    Returns:
        HybridAggFunc: Validated aggregation function.

    Raises:
        ValueError: If function is invalid.
    """
    if fn not in VALID_HYBRID_AGG_FUNCS:
        message = f"{ERROR_INVALID_AGG_FUNC} Got: {fn}"
        raise ValueError(message)
    return cast("HybridAggFunc", fn)


def validate_name_cache_structure(name_cache: object) -> None:
    """
    Validate that the name_cache is a dictionary mapping characters to name info.

    Each entry must map a character to a dict with at least 'original' and 'normalized' keys.

    Args:
        name_cache (object): The name cache object to validate.

    Raises:
        TypeError: If name_cache is not a dict.
        ValueError: If an entry is not a dict or lacks required keys.
    """
    if not isinstance(name_cache, dict):
        message = "Expected name_cache to be a dict."
        raise TypeError(message)

    for key, value in name_cache.items():
        if not isinstance(value, dict):
            message = f"Invalid entry for {key!r}: expected a dict."
            raise TypeError(message)
        if "original" not in value or "normalized" not in value:
            message = (
                f"Missing required keys in name_cache entry for {key!r}. "
                "Expected keys: 'original', 'normalized'."
            )
            raise ValueError(message)
