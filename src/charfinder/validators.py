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
    validate_fuzzy_hybrid_weights(): Validates hybrid weights given for aggregation of fuzzy algos.
    validate_exact_match_mode(): Validate and normalize an exact match mode string.
    validate_dict_str_keys(): Ensure a nested string-keyed dictionary structure (e.g., name cache).
    validate_cache_rebuild_flag(): Validate that a rebuild flag is a proper boolean.
    validate_normalized_name(): Ensure a normalized name is a valid non-empty string.
    validate_unicode_data_url(): Validate that a Unicode data URL is well-formed.
    validate_files_and_url(): Validate both file and url
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
import sys
from argparse import Action, ArgumentParser, ArgumentTypeError, Namespace
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal, cast
from urllib.parse import urlparse

from charfinder.config.aliases import (
    ColorMode,
    ExactMatchMode,
    FuzzyAlgorithm,
    FuzzyMatchMode,
    HybridAggFunc,
    NormalizationProfile,
)
from charfinder.config.constants import (
    DEFAULT_COLOR_MODE,
    DEFAULT_NORMALIZATION_PROFILE,
    DEFAULT_SHOW_SCORE,
    DEFAULT_THRESHOLD,
    ENV_COLOR_MODE,
    ENV_MATCH_THRESHOLD,
    ENV_NORMALIZATION_PROFILE,
    ENV_SHOW_SCORE,
    FUZZY_ALGO_ALIASES,
    FUZZY_WEIGHT_MAX_TOTAL,
    FUZZY_WEIGHT_MIN_TOTAL,
    VALID_COLOR_MODES,
    VALID_EXACT_MATCH_MODES,
    VALID_FUZZY_MATCH_MODES,
    VALID_HYBRID_AGG_FUNCS,
    VALID_NORMALIZATION_PROFILES,
    VALID_OUTPUT_FORMATS,
    VALID_SHOW_SCORES,
    VALID_SHOW_SCORES_FALSE,
    VALID_SHOW_SCORES_TRUE,
)
from charfinder.config.messages import (
    MSG_ERROR_EMPTY_FUZZY_ALGO_LIST,
    MSG_ERROR_ENV_INVALID_THRESHOLD,
    MSG_ERROR_EXPECTED_BOOL,
    MSG_ERROR_EXPECTED_DICT,
    MSG_ERROR_EXPECTED_DICT_KEY,
    MSG_ERROR_EXPECTED_DICT_VAL,
    MSG_ERROR_FILE_NOT_FOUND,
    MSG_ERROR_INVALID_AGG_FUNC,
    MSG_ERROR_INVALID_COLOR_MODE_WITH_VALUE,
    MSG_ERROR_INVALID_EXACT_MATCH_MODE,
    MSG_ERROR_INVALID_FUZZY_MATCH_MODE,
    MSG_ERROR_INVALID_NAME,
    MSG_ERROR_INVALID_NORMALIZATION_PROFILE,
    MSG_ERROR_INVALID_OUTPUT_FORMAT,
    MSG_ERROR_INVALID_PATH_TYPE,
    MSG_ERROR_INVALID_SHOW_SCORE_VALUE,
    MSG_ERROR_INVALID_THRESHOLD,
    MSG_ERROR_INVALID_THRESHOLD_TYPE,
    MSG_ERROR_INVALID_URL,
    MSG_ERROR_INVALID_WEIGHT_TOTAL,
    MSG_ERROR_INVALID_WEIGHT_TYPE,
    MSG_ERROR_MISSING_FUZZY_ALGO_VALUE,
    MSG_ERROR_UNSUPPORTED_ALGO_INPUT,
    MSG_ERROR_UNSUPPORTED_URL_SCHEME,
    MSG_ERROR_VALIDATION_FAILED,
)
from charfinder.config.settings import (
    get_cache_file,
    get_fuzzy_hybrid_weights,
    parse_fuzzy_weight_string,
)
from charfinder.config.types import (
    FuzzyConfig,
    NameCache,
)
from charfinder.utils.formatter import echo, should_use_color
from charfinder.utils.logger_styles import format_warning

# ------------------------------------------------------------------------
# Fuzzy Algorithm Validators
# ------------------------------------------------------------------------


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

    valid_options = sorted(set(FUZZY_ALGO_ALIASES) | set(FUZZY_ALGORITHM_REGISTRY))
    raise ValueError(
        MSG_ERROR_UNSUPPORTED_ALGO_INPUT.format(
            valid_options=", ".join(valid_options), name=fuzzy_algo
        )
    )


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

    This action ensures the fuzzy algorithm specified by the user is valid and
    normalized at parse time.

    Example:
        parser.add_argument(
            "--fuzzy-algo",
            action=ValidateFuzzyAlgoAction,
            help="Specify the fuzzy matching algorithm to use.",
        )

    Methods:
        __call__: Invoked by argparse to process and validate the argument.
    """

    def __init__(
        self,
        option_strings: Sequence[str],
        dest: str,
        **kwargs: Mapping[str, Any],
    ) -> None:
        super().__init__(option_strings, dest, **kwargs)  # type: ignore[arg-type]

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
            raise ValueError(MSG_ERROR_MISSING_FUZZY_ALGO_VALUE)

        if isinstance(values, Sequence) and not isinstance(values, str):
            if not values:
                raise ValueError(MSG_ERROR_EMPTY_FUZZY_ALGO_LIST)
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
        TypeError: If the input is not a float or int.
        ValueError: If the threshold is outside the range [0.0, 1.0].
    """
    if not isinstance(threshold, (float, int)):
        raise TypeError(MSG_ERROR_INVALID_THRESHOLD_TYPE)
    if threshold < 0.0 or threshold > 1.0:
        raise ValueError(MSG_ERROR_INVALID_THRESHOLD)
    return float(threshold)


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
        raise ValueError(MSG_ERROR_INVALID_THRESHOLD) from exc
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
            echo(
                msg=MSG_ERROR_ENV_INVALID_THRESHOLD.format(
                    env_var=ENV_MATCH_THRESHOLD, value=env_value
                ),
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

    Args:
        color_mode (str | None): The color mode string to validate.
        source (Literal["cli", "core"]): Context of invocation.

    Returns:
        ColorMode: The validated and normalized color mode.

    Raises:
        ValueError: If color_mode is invalid and source is "core".
    """
    if source == "cli" and color_mode in VALID_COLOR_MODES:
        return cast_color_mode(color_mode)
    if color_mode in VALID_COLOR_MODES:
        return cast_color_mode(color_mode)

    if source == "core":
        raise ValueError(
            MSG_ERROR_INVALID_COLOR_MODE_WITH_VALUE.format(
                value=color_mode, valid_options=", ".join(sorted(VALID_COLOR_MODES))
            )
        )
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
        raise ValueError(
            MSG_ERROR_INVALID_FUZZY_MATCH_MODE.format(
                value=mode, valid_options=", ".join(sorted(VALID_FUZZY_MATCH_MODES))
            )
        )
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
        raise ValueError(
            MSG_ERROR_INVALID_EXACT_MATCH_MODE.format(
                value=exact_match_mode, valid_options=", ".join(sorted(VALID_EXACT_MATCH_MODES))
            )
        )
    return cast("ExactMatchMode", exact_match_mode)


def validate_fuzzy_hybrid_weights(weights: str | dict[str, float] | None) -> dict[str, float]:
    """
    Validate and normalize the fuzzy hybrid weights input.

    Accepts None (defaults to settings), raw string (parses it), or dict (validates sum).

    Args:
        weights (str | dict | None): User-provided weights.

    Returns:
        dict[str, float]: Validated weight dictionary.

    Raises:
        ValueError: If format is invalid or weights do not sum to ~1.0.
    """
    if weights is None:
        return get_fuzzy_hybrid_weights()

    if isinstance(weights, dict):
        total = sum(weights.values())
        if not (FUZZY_WEIGHT_MIN_TOTAL <= total <= FUZZY_WEIGHT_MAX_TOTAL):
            raise ValueError(MSG_ERROR_INVALID_WEIGHT_TOTAL.format(total=total, weights=weights))
        return weights

    if isinstance(weights, str):
        return parse_fuzzy_weight_string(weights)

    raise TypeError(MSG_ERROR_INVALID_WEIGHT_TYPE.format(type=type(weights)))


# ------------------------------------------------------------------------
# Cache Validators
# ------------------------------------------------------------------------


def validate_dict_str_keys(name_cache: NameCache) -> NameCache:
    if not isinstance(name_cache, dict):
        raise TypeError(MSG_ERROR_EXPECTED_DICT)

    for key, value in name_cache.items():
        if not isinstance(key, str):
            raise TypeError(MSG_ERROR_EXPECTED_DICT_KEY.format(type=type(key), key=key))
        if not isinstance(value, dict):
            raise TypeError(MSG_ERROR_EXPECTED_DICT_VAL.format(type=type(value), key=key))

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
        raise TypeError(MSG_ERROR_EXPECTED_BOOL.format(type=type(force_rebuild)))
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
        raise ValueError(MSG_ERROR_INVALID_NAME.format(value=name))
    return name


# ------------------------------------------------------------------------
# Unicode Data Validators
# ------------------------------------------------------------------------


def validate_unicode_data_url(url: str) -> bool:
    """
    Validate that a given string is a well-formed URL with HTTP or HTTPS scheme.

    This function checks whether the provided string has both a scheme and a netloc,
    and ensures it uses either the HTTP or HTTPS scheme, suitable for remote Unicode data access.

    Args:
        url (str): The URL string to validate.

    Raises:
        ValueError: If the string is not a valid HTTP/HTTPS URL.

    Returns:
        bool: True if the URL is valid and uses an accepted scheme.
    """
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError(MSG_ERROR_INVALID_URL.format(url=url))
    if parsed_url.scheme.lower() not in {"http", "https"}:
        raise ValueError(MSG_ERROR_UNSUPPORTED_URL_SCHEME.format(scheme=parsed_url.scheme, url=url))
    return True


def validate_cache_file_path(cache_file_path: Path | str | None) -> Path:
    """
    Validate and normalize the provided cache file path.

    Ensures the input is a valid `Path` object. This function does not require
    the file to exist, making it suitable for cache creation.

    Args:
        cache_file_path (Path | None): The cache file path to validate.

    Raises:
        TypeError: If the input is not a Path instance or a string.

    Returns:
        Path: A valid Path object to the cache file.
    """
    if cache_file_path is None:
        return get_cache_file()

    if isinstance(cache_file_path, str):
        return Path(cache_file_path)

    if not isinstance(cache_file_path, Path):
        raise TypeError(MSG_ERROR_INVALID_PATH_TYPE.format(type=type(cache_file_path)))

    return cache_file_path


def validate_files_and_url(
    unicode_data_url: str,
    unicode_data_file: Path,
    *,
    show: bool = True,
) -> str | None:
    """
    Validate the Unicode data URL and the local file path.

    Args:
        unicode_data_url (str): The URL for the Unicode data file.
        unicode_data_file (Path): The local path to the Unicode data file.
        show (bool): If True, display progress messages.

    Returns:
        str | None: A message if validation fails, or None if validation is successful.
    """
    try:
        validate_unicode_data_url(unicode_data_url)
        validate_cache_file_path(unicode_data_file)
    except ValueError as exc:
        message = MSG_ERROR_VALIDATION_FAILED.format(error=exc)
        echo(msg=message, style=format_warning, stream=sys.stderr, show=show)
        return message
    return None


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
        raise FileNotFoundError(MSG_ERROR_FILE_NOT_FOUND.format(path=file_path))
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
    if fmt not in VALID_OUTPUT_FORMATS:
        raise ValueError(
            MSG_ERROR_INVALID_OUTPUT_FORMAT.format(
                format=fmt, valid_options=", ".join(sorted(VALID_OUTPUT_FORMATS))
            )
        )
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
        raise ValueError(
            MSG_ERROR_INVALID_AGG_FUNC.format(
                func=fn, valid_options=", ".join(sorted(VALID_HYBRID_AGG_FUNCS))
            )
        )
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


def validate_normalization_profile(
    value: str | None, *, source: Literal["cli", "env"] = "cli"
) -> NormalizationProfile:
    """
    Validate and normalize a normalization profile string input.

    Args:
        value: Input string from CLI or environment.
        source: Indicates input origin ("cli" or "env").

    Returns:
        A valid NormalizationProfile literal.

    Raises:
        ValueError: If the profile name is not recognized.
    """

    if value is None:
        return DEFAULT_NORMALIZATION_PROFILE

    lowered = value.lower()
    if lowered in VALID_NORMALIZATION_PROFILES:
        return cast("NormalizationProfile", lowered)
    raise ValueError(
        MSG_ERROR_INVALID_NORMALIZATION_PROFILE.format(
            value=value, source=source, valid_options=", ".join(VALID_NORMALIZATION_PROFILES)
        )
    )


def resolve_effective_normalization_profile(
    cli_value: str | None,
) -> NormalizationProfile:
    """
    Determine the effective normalization profile based on CLI, env, or default.

    Args:
        cli_value: Value from CLI or None.

    Returns:
        A valid NormalizationProfile.
    """
    if cli_value is not None:
        return validate_normalization_profile(cli_value, source="cli")

    env_value = os.getenv(ENV_NORMALIZATION_PROFILE)
    if env_value is not None:
        try:
            return validate_normalization_profile(env_value, source="env")
        except ValueError:
            pass

    return DEFAULT_NORMALIZATION_PROFILE


def validate_show_score(value: str) -> bool:
    """
    Normalize and convert a show_score value to a boolean.

    Args:
        value (str): A string representation of a boolean.

    Returns:
        bool: True if value is in VALID_SHOW_SCORES_TRUE, False if in VALID_SHOW_SCORES_FALSE.

    Raises:
        ArgumentTypeError: If the value is not recognized.
    """
    lowered = value.strip().lower()
    if lowered in VALID_SHOW_SCORES_TRUE:
        return True
    if lowered in VALID_SHOW_SCORES_FALSE:
        return False
    raise ArgumentTypeError(
        MSG_ERROR_INVALID_SHOW_SCORE_VALUE.format(
            value=value, valid_options=", ".join(sorted(VALID_SHOW_SCORES))
        )
    )


def resolve_effective_show_score(*, cli_value: bool | None) -> bool:
    """
    Determine whether to show scores based on CLI, environment variable, or default.

    This function checks:
    1. CLI-supplied value (True/False).
    2. Environment variable `CHARFINDER_SHOW_SCORE`.
    3. Fallback to DEFAULT_SHOW_SCORE.

    Args:
        cli_value (bool | None): The value from the CLI (already a boolean if set).

    Returns:
        bool: Final resolved value indicating whether to show scores.
    """
    if cli_value is not None:
        return cli_value

    env_value = os.getenv(ENV_SHOW_SCORE)
    if env_value is not None:
        try:
            return validate_show_score(env_value)
        except (ValueError, ArgumentTypeError):
            pass  # Fall back to default if env var is invalid

    return DEFAULT_SHOW_SCORE
