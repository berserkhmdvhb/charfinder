"""
Constants for CharFinder.

Defines:
- Package metadata
- Valid fuzzy algorithms and match modes
- Typing aliases
- Exact match modes
- Exit codes used by CLI
- Output field widths
- Default thresholds and modes
- Logging configuration
- Environment variable names
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Literal

# ---------------------------------------------------------------------
# Typing Aliases
# ---------------------------------------------------------------------

FuzzyAlgorithm = Literal[
    "sequencematcher",
    "rapidfuzz",
    "levenshtein",
    "simple_ratio",
    "normalized_ratio",
    "levenshtein_ratio",
    "token_sort_ratio",
    "hybrid_score",
]

ExactMatchMode = Literal["substring", "word-subset"]
FuzzyMatchMode = Literal["single", "hybrid"]
ColorMode = Literal["auto", "always", "never"]
HybridAggFunc = Literal["mean", "median", "max", "min"]
OutputFormat = Literal["text", "json"]
NormalizationForm = Literal["NFC", "NFD", "NFKC", "NFKD"]

# ---------------------------------------------------------------------
# Package Info
# ---------------------------------------------------------------------

PACKAGE_NAME = "charfinder"
DEFAULT_ENCODING = "utf-8"

# ---------------------------------------------------------------------
# Valid Inputs
# ---------------------------------------------------------------------

VALID_COLOR_MODES = ("auto", "never", "always")
VALID_FUZZY_MATCH_MODES = ("single", "hybrid")
VALID_EXACT_MATCH_MODES = ("substring", "word-subset")
VALID_LOG_METHODS = {"debug", "info", "warning", "error", "exception"}
VALID_HYBRID_AGG_FUNCS = {"mean", "median", "max", "min"}
VALID_OUTPUT_FORMATS = {"text", "json"}
VALID_NORMALIZATION_FORMS = {"NFC", "NFD", "NFKC", "NFKD"}

LOG_METHODS = SimpleNamespace(
    DEBUG="debug",
    INFO="info",
    WARNING="warning",
    ERROR="error",
    EXCEPTION="exception",
)

FUZZY_ALGO_ALIASES: dict[str, str] = {
    "levenshtein": "levenshtein_ratio",
    "simple": "simple_ratio",
    "normalized": "normalized_ratio",
    "token_sort": "token_sort_ratio",
    "hybrid": "hybrid_score",
    "sequencematcher": "sequencematcher",
    "rapidfuzz": "rapidfuzz",
}

# ---------------------------------------------------------------------
# Exit Codes
# ---------------------------------------------------------------------

EXIT_SUCCESS = 0
EXIT_INVALID_USAGE = 1
EXIT_NO_RESULTS = 2
EXIT_CANCELLED = 130
EXIT_ERROR = 3

# ---------------------------------------------------------------------
# Output Constants
# ---------------------------------------------------------------------

FIELD_WIDTHS = {
    "code": 10,
    "char": 3,
    "name": 45,
}

# ---------------------------------------------------------------------
# Default Thresholds and Modes (with correct types)
# ---------------------------------------------------------------------

DEFAULT_THRESHOLD: float = 0.7
DEFAULT_FUZZY_ALGO: FuzzyAlgorithm = "token_sort_ratio"
DEFAULT_FUZZY_MATCH_MODE: FuzzyMatchMode = "single"
DEFAULT_EXACT_MATCH_MODE: ExactMatchMode = "word-subset"
DEFAULT_HYBRID_AGG_FUNC: HybridAggFunc = "mean"
DEFAULT_COLOR_MODE: ColorMode = "auto"
DEFAULT_OUTPUT_FORMAT: OutputFormat = "text"
DEFAULT_NORMALIZATION_FORM: NormalizationForm = "NFC"
# ---------------------------------------------------------------------
# Hybrid scoring weights for fuzzy match components
# ---------------------------------------------------------------------

FUZZY_HYBRID_WEIGHTS: dict[str, float] = {
    "simple_ratio": 0.15,
    "normalized_ratio": 0.15,
    "levenshtein_ratio": 0.15,
    "token_sort_ratio": 0.55,
}

# ---------------------------------------------------------------------
# Logging (static pieces)
# ---------------------------------------------------------------------

LOG_FILE_NAME = "charfinder.log"
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(env)s] %(message)s"
DEFAULT_LOG_ROOT = Path("logs")

# ---------------------------------------------------------------------
# Environment Variable Names
# ---------------------------------------------------------------------

ENV_ENVIRONMENT = "CHARFINDER_ENV"
ENV_LOG_MAX_BYTES = "CHARFINDER_LOG_MAX_BYTES"
ENV_LOG_BACKUP_COUNT = "CHARFINDER_LOG_BACKUP_COUNT"
ENV_LOG_LEVEL = "CHARFINDER_LOG_LEVEL"
ENV_DEBUG_ENV_LOAD = "CHARFINDER_DEBUG_ENV_LOAD"


# ---------------------------------------------------------------------
# Supported Fuzzy Algorithms
# ---------------------------------------------------------------------

SUPPORTED_ALGORITHMS: dict[str, FuzzyAlgorithm] = {
    "sequencematcher": "sequencematcher",
    "rapidfuzz": "rapidfuzz",
    "levenshtein": "levenshtein",
    "simple_ratio": "simple_ratio",
    "normalized_ratio": "normalized_ratio",
    "token_sort_ratio": "token_sort_ratio",
    "hybrid_score": "hybrid_score",
}

# ------------------------------------------------------------------------
# Dataclasses for Fuzzy Configuration
# ------------------------------------------------------------------------


@dataclass
class FuzzyConfig:
    fuzzy_algo: FuzzyAlgorithm
    fuzzy_match_mode: FuzzyMatchMode


# ---------------------------------------------------------------------
# __all__
# ---------------------------------------------------------------------

__all__ = [
    "DEFAULT_COLOR_MODE",
    "DEFAULT_ENCODING",
    "DEFAULT_EXACT_MATCH_MODE",
    "DEFAULT_FUZZY_ALGO",
    "DEFAULT_FUZZY_MATCH_MODE",
    "DEFAULT_LOG_ROOT",
    "DEFAULT_NORMALIZATION_FORM",
    "DEFAULT_OUTPUT_FORMAT",
    "DEFAULT_THRESHOLD",
    "ENV_DEBUG_ENV_LOAD",
    "ENV_ENVIRONMENT",
    "ENV_LOG_BACKUP_COUNT",
    "ENV_LOG_LEVEL",
    "ENV_LOG_MAX_BYTES",
    "EXIT_CANCELLED",
    "EXIT_ERROR",
    "EXIT_INVALID_USAGE",
    "EXIT_NO_RESULTS",
    "EXIT_SUCCESS",
    "FIELD_WIDTHS",
    "LOG_FILE_NAME",
    "LOG_FORMAT",
    "LOG_METHODS",
    "PACKAGE_NAME",
    "VALID_EXACT_MATCH_MODES",
    "VALID_FUZZY_MATCH_MODES",
    "VALID_HYBRID_AGG_FUNCS",
    "VALID_LOG_METHODS",
    "VALID_OUTPUT_FORMATS",
    "ColorMode",
    "ExactMatchMode",
    "FuzzyAlgorithm",
    "FuzzyMatchMode",
    "HybridAggFunc",
    "NormalizationForm",
    "OutputFormat",
]
