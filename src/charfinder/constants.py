"""
Constants for CharFinder.

Defines:
- Package metadata
- Valid fuzzy algorithms and match modes
- Typing aliases
- Exact match modes
- Exit codes used by CLI
- Output field widths
- Cache file path
- Default thresholds and modes
- Logging configuration
- Environment variable names
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

from pathlib import Path
from typing import Literal

# ---------------------------------------------------------------------
# Package Info
# ---------------------------------------------------------------------

PACKAGE_NAME = "charfinder"
DEFAULT_ENCODING = "utf-8"

# ---------------------------------------------------------------------
# Valid Inputs
# ---------------------------------------------------------------------

VALID_FUZZY_ALGOS = ("sequencematcher", "rapidfuzz", "levenshtein")
VALID_FUZZY_MATCH_MODES = ("single", "hybrid")
VALID_EXACT_MATCH_MODES = ("substring", "word-subset")
VALID_LOG_METHODS = {"debug", "info", "warning", "error", "exception"}

# ---------------------------------------------------------------------
# Typing Aliases
# ---------------------------------------------------------------------

FuzzyAlgorithm = Literal["sequencematcher", "rapidfuzz", "levenshtein"]
MatchMode = Literal["single", "hybrid"]
ExactMatchMode = Literal["substring", "word-subset"]
ColorMode = Literal["auto", "always", "never"]

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
# Default Thresholds and Modes
# ---------------------------------------------------------------------

DEFAULT_THRESHOLD: float = 0.7
DEFAULT_FUZZY_ALGO = "sequencematcher"
DEFAULT_FUZZY_MATCH_MODE = "single"
DEFAULT_EXACT_MATCH_MODE = "word-subset"
DEFAULT_COLOR_MODE = "auto"

# ---------------------------------------------------------------------
# Logging (static pieces)
# ---------------------------------------------------------------------

LOG_FILE_NAME = "charfinder.log"

# Log format string (simple — no env filter yet)
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(env)s] %(message)s"

# Default root directory for log files
DEFAULT_LOG_ROOT = Path("logs")

# ---------------------------------------------------------------------
# Environment Variable Names
# ---------------------------------------------------------------------

ENV_ENVIRONMENT = "CHARFINDER_ENV"
ENV_LOG_MAX_BYTES = "CHARFINDER_LOG_MAX_BYTES"
ENV_LOG_BACKUP_COUNT = "CHARFINDER_LOG_BACKUP_COUNT"
ENV_LOG_LEVEL = "CHARFINDER_LOG_LEVEL"
ENV_DEBUG_ENV_LOAD = "CHARFINDER_DEBUG_ENV_LOAD"
