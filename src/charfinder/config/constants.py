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

from pathlib import Path
from types import SimpleNamespace

from charfinder.config.aliases import (
    ColorMode,
    ExactMatchMode,
    FuzzyAlgorithm,
    FuzzyMatchMode,
    HybridAggFunc,
    NormalizationForm,
    NormalizationProfile,
    OutputFormat,
)
from charfinder.config.types import NormalizationProfileDict

__all__ = [
    "ALT_NAME_INDEX",
    "DEFAULT_COLOR_MODE",
    "DEFAULT_ENCODING",
    "DEFAULT_EXACT_MATCH_MODE",
    "DEFAULT_FUZZY_ALGO",
    "DEFAULT_FUZZY_MATCH_MODE",
    "DEFAULT_LOG_ROOT",
    "DEFAULT_NORMALIZATION_FORM",
    "DEFAULT_NORMALIZATION_PROFILE",
    "DEFAULT_OUTPUT_FORMAT",
    "DEFAULT_THRESHOLD",
    "ENV_COLOR_MODE",
    "ENV_DEBUG_ENV_LOAD",
    "ENV_ENVIRONMENT",
    "ENV_FUZZY_WEIGHT",
    "ENV_LOG_BACKUP_COUNT",
    "ENV_LOG_LEVEL",
    "ENV_LOG_MAX_BYTES",
    "ENV_MATCH_THRESHOLD",
    "EXIT_CANCELLED",
    "EXIT_ERROR",
    "EXIT_INVALID_USAGE",
    "EXIT_NO_RESULTS",
    "EXIT_SUCCESS",
    "EXPECTED_MIN_FIELDS",
    "FIELD_WIDTHS",
    "FUZZY_ALGO_ALIASES",
    "FUZZY_WEIGHT_MAX_TOTAL",
    "FUZZY_WEIGHT_MIN_TOTAL",
    "LOG_FILE_NAME",
    "LOG_FORMAT",
    "LOG_METHODS",
    "NORMALIZATION_PROFILES",
    "PACKAGE_NAME",
    "VALID_EXACT_MATCH_MODES",
    "VALID_FUZZY_MATCH_MODES",
    "VALID_HYBRID_AGG_FUNCS",
    "VALID_LOG_METHODS",
    "VALID_NORMALIZATION_PROFILES",
    "VALID_OUTPUT_FORMATS",
]

# ---------------------------------------------------------------------
# Package Info
# ---------------------------------------------------------------------

PACKAGE_NAME = "charfinder"
DEFAULT_ENCODING = "utf-8"


# ---------------------------------------------------------------------
# Typing Aliases
# ---------------------------------------------------------------------

FUZZY_ALGO_ALIASES: dict[str, FuzzyAlgorithm] = {
    "lev": "levenshtein_ratio",
    "levenshtein": "levenshtein_ratio",
    "simple": "simple_ratio",
    "normalized": "normalized_ratio",
    "tsr": "token_sort_ratio",
    "token_sort": "token_sort_ratio",
    "token_sort_ratio": "token_sort_ratio",
    "token_subset": "token_subset_ratio",
    "token_subset_ratio": "token_subset_ratio",
    "tsub": "token_subset_ratio",
    "hybrid": "hybrid_score",
}


# ---------------------------------------------------------------------
# Valid Inputs
# ---------------------------------------------------------------------

VALID_COLOR_MODES = ("auto", "never", "always")
VALID_FUZZY_ALGO_NAMES: set[str] = set(FUZZY_ALGO_ALIASES.values())
VALID_FUZZY_ALGO_ALIASES: set[str] = set(FUZZY_ALGO_ALIASES.keys())
VALID_FUZZY_MATCH_MODES = ("single", "hybrid")
VALID_EXACT_MATCH_MODES = ("substring", "word-subset")
VALID_LOG_METHODS = {"debug", "info", "warning", "error", "exception"}
VALID_HYBRID_AGG_FUNCS = {"mean", "median", "max", "min"}
VALID_NORMALIZATION_FORMS = {"NFC", "NFD", "NFKC", "NFKD"}
VALID_NORMALIZATION_PROFILES = {"raw", "light", "medium", "aggressive"}
VALID_OUTPUT_FORMATS = {"text", "json"}
VALID_SHOW_SCORES_TRUE = {"true", "1", "yes"}
VALID_SHOW_SCORES_FALSE = {"false", "0", "no"}
VALID_SHOW_SCORES = VALID_SHOW_SCORES_TRUE | VALID_SHOW_SCORES_FALSE


LOG_METHODS = SimpleNamespace(
    DEBUG="debug",
    INFO="info",
    WARNING="warning",
    ERROR="error",
    EXCEPTION="exception",
)

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
    "name": 50,
    "score": 6,
}

# ---------------------------------------------------------------------
# Default Thresholds and Modes (with correct types)
# ---------------------------------------------------------------------

DEFAULT_COLOR_MODE: ColorMode = "auto"
DEFAULT_EXACT_MATCH_MODE: ExactMatchMode = "word-subset"
DEFAULT_FUZZY_ALGO: FuzzyAlgorithm = "token_subset_ratio"
DEFAULT_FUZZY_MATCH_MODE: FuzzyMatchMode = "single"
DEFAULT_HYBRID_AGG_FUNC: HybridAggFunc = "mean"
DEFAULT_NORMALIZATION_FORM: NormalizationForm = "NFKD"
DEFAULT_NORMALIZATION_PROFILE: NormalizationProfile = "aggressive"
DEFAULT_OUTPUT_FORMAT: OutputFormat = "text"
DEFAULT_SHOW_SCORE = True
DEFAULT_THRESHOLD: float = 0.65

# ---------------------------------------------------------------------
# Hybrid scoring weights for fuzzy match components
# ---------------------------------------------------------------------

FUZZY_HYBRID_WEIGHTS: dict[str, float] = {
    "simple_ratio": 0.10,
    "normalized_ratio": 0.10,
    "levenshtein_ratio": 0.10,
    "token_sort_ratio": 0.50,
    "token_subset_ratio": 0.20,
}

# ---------------------------------------------------------------------
# Normalization Profiles
# ---------------------------------------------------------------------

NORMALIZATION_PROFILES: dict[NormalizationProfile, NormalizationProfileDict] = {
    "raw": {
        "form": "NFC",
        "strip_accents": False,
        "strip_whitespace": False,
    },
    "light": {
        "form": "NFC",
        "strip_accents": False,
    },
    "medium": {
        "form": "NFKD",
        "strip_accents": False,
    },
    "aggressive": {
        "form": "NFKD",
        "strip_accents": True,
    },
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
ENV_MATCH_THRESHOLD = "CHARFINDER_MATCH_THRESHOLD"
ENV_COLOR_MODE = "CHARFINDER_COLOR_MODE"
ENV_NORMALIZATION_PROFILE = "CHARFINDER_NORMALIZATION_PROFILE"
ENV_SHOW_SCORE = "CHARFINDER_SHOW_SCORE"
ENV_FUZZY_WEIGHT = "CHARFINDER_FUZZY_WEIGHTS"

FUZZY_WEIGHT_MIN_TOTAL = 0.98
FUZZY_WEIGHT_MAX_TOTAL = 1.02

# ------------------------------------------------------------------------
# UnicodeData
# ------------------------------------------------------------------------

ALT_NAME_INDEX = 10  # index of alternate name in UnicodeData.txt fields
EXPECTED_MIN_FIELDS = 11  # fields expected per line in UnicodeData.txt
