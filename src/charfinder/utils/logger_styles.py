"""
Logging style formatters for terminal output (with optional color).

Provides colorized prefixes for common log message types:

- [DEBUG]
- [INFO]
- [WARNING]
- [ERROR]
- [SETTINGS]
- [OK] (success)

Used to format user-facing messages consistently in terminal.

Exports:
    format_debug
    format_info
    format_warning
    format_error
    format_settings
    format_success
"""

from typing import Final

from colorama import Fore, Style

__all__ = [
    "format_debug",
    "format_error",
    "format_info",
    "format_settings",
    "format_success",
    "format_warning",
]

# ----------------------------------------------------------------------
# Color constants (used for terminal output)
# ----------------------------------------------------------------------

COLOR_HEADER: Final = Fore.CYAN
COLOR_CODELINE: Final = Fore.YELLOW
COLOR_ERROR: Final = Fore.RED
COLOR_INFO: Final = Fore.BLUE
COLOR_SUCCESS: Final = Fore.GREEN
COLOR_WARNING: Final = Fore.YELLOW
COLOR_DEBUG: Final = Fore.LIGHTBLACK_EX
COLOR_SETTINGS: Final = Fore.LIGHTBLACK_EX
RESET: Final = Style.RESET_ALL

# ----------------------------------------------------------------------
# Formatting functions
# ----------------------------------------------------------------------


def format_debug(message: str, *, use_color: bool = True) -> str:
    """Format debug message with [DEBUG] prefix."""
    prefix = f"{COLOR_DEBUG}[DEBUG]{RESET}" if use_color else "[DEBUG]"
    return f"{prefix} {message}"


def format_info(message: str, *, use_color: bool = True) -> str:
    """Format info message with [INFO] prefix."""
    prefix = f"{COLOR_INFO}[INFO]{RESET}" if use_color else "[INFO]"
    return f"{prefix} {message}"


def format_warning(message: str, *, use_color: bool = True) -> str:
    """Format warning message with [WARNING] prefix."""
    prefix = f"{COLOR_WARNING}[WARNING]{RESET}" if use_color else "[WARNING]"
    return f"{prefix} {message}"


def format_error(message: str, *, use_color: bool = True) -> str:
    """Format error message with [ERROR] prefix."""
    prefix = f"{COLOR_ERROR}[ERROR]{RESET}" if use_color else "[ERROR]"
    return f"{prefix} {message}"


def format_settings(message: str, *, use_color: bool = True) -> str:
    """Format settings message with [SETTINGS] prefix."""
    prefix = f"{COLOR_SETTINGS}[SETTINGS]{RESET}" if use_color else "[SETTINGS]"
    return f"{prefix} {message}"


def format_success(message: str, *, use_color: bool = True) -> str:
    """Format success message with [OK] prefix."""
    prefix = f"{COLOR_SUCCESS}[OK]{RESET}" if use_color else "[OK]"
    return f"{prefix} {message}"
