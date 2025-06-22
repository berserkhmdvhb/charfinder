"""
Unicode Data Loader for CharFinder.

This module handles the loading of alternate names from the UnicodeData.txt file. It attempts
to download the file from the internet if it is not available locally and falls back to the local
version if the download fails.

Key Features:
- Downloads UnicodeData.txt if not found locally.
- Reads the local file and parses the content.
- Returns a dictionary of characters and their alternate names.
- Handles error and exception handling for file operations and network issues.

Functions:
- load_alternate_names(show: bool = True, use_color: bool = False):
    Loads alternate names from the UnicodeData.txt file.
- download_and_cache_unicode_data
    (unicode_data_url: str, unicode_data_file: Path, show: bool = True, use_color: bool = False):
    Downloads and caches the UnicodeData.txt file if not found locally.
- load_unicode_data_from_file(unicode_data_file: Path, show: bool = True, use_color: bool = False):
    Reads Unicode data from a local file.
- parse_unicode_data(text: str, show: bool = True, use_color: bool = False):
    Parses the Unicode data into a dictionary of alternate names.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from charfinder.config.constants import ALT_NAME_INDEX, EXPECTED_MIN_FIELDS
from charfinder.config.messages import (
    MSG_INFO_DOWNLOAD_SUCCESS,
    MSG_INFO_LOAD_LOCAL_FILE,
    MSG_WARNING_DOWNLOAD_FAILED,
    MSG_WARNING_INVALID_CODE,
    MSG_WARNING_MALFORMED_LINE,
    MSG_WARNING_READ_FAILED,
)
from charfinder.config.settings import get_unicode_data_file, get_unicode_data_url
from charfinder.utils.formatter import echo
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_info, format_warning
from charfinder.validators import validate_unicode_data_url

logger = get_logger()

__all__ = ["load_alternate_names"]


def download_and_cache_unicode_data(
    unicode_data_url: str,
    unicode_data_file: Path,
    *,
    show: bool = True,
    use_color: bool = True,
) -> bool:
    """
    Attempt to download and cache the UnicodeData.txt file if not found locally.

    Args:
        unicode_data_url (str): The URL to download the file from.
        unicode_data_file (Path): The path where the file should be cached.
        show (bool): If True, show progress messages.
        use_color (bool): If True, show colorized log output.

    Returns:
        bool: True if successful, False otherwise.

    Raises:
        ValueError: If the URL scheme is not HTTP/HTTPS.
    """
    validate_unicode_data_url(unicode_data_url)

    try:
        response = urlopen(unicode_data_url, timeout=5)  # noqa: S310
        with response:
            text = response.read().decode("utf-8")
        unicode_data_file.parent.mkdir(parents=True, exist_ok=True)
        unicode_data_file.write_text(text, encoding="utf-8")
        echo(
            msg=MSG_INFO_DOWNLOAD_SUCCESS.format(url=unicode_data_url),
            style=lambda m: format_info(m, use_color=use_color),
            stream=sys.stderr,
            show=show,
            log=True,
            log_method="info",
        )
    except (URLError, TimeoutError, OSError) as exc:
        echo(
            msg=MSG_WARNING_DOWNLOAD_FAILED.format(error=exc),
            style=lambda m: format_warning(m),
            stream=sys.stderr,
            show=show,
            log=True,
            log_method="warning",
        )
        return False
    else:
        return True


def load_unicode_data_from_file(
    unicode_data_file: Path,
    *,
    show: bool = True,
) -> str | None:
    """
    Load the Unicode data from a local file.

    Args:
        unicode_data_file (Path): The file path to read from.
        show (bool): If True, display progress messages.

    Returns:
        str | None: The content of the file or None if reading failed.
    """
    try:
        text = unicode_data_file.read_text(encoding="utf-8")
        echo(
            msg=MSG_INFO_LOAD_LOCAL_FILE.format(path=unicode_data_file),
            style=lambda m: format_info(m),
            stream=sys.stderr,
            show=show,
            log=True,
            log_method="info",
        )
    except OSError as exc:
        echo(
            msg=MSG_WARNING_READ_FAILED.format(path=unicode_data_file, error=exc),
            style=lambda m: format_warning(m),
            stream=sys.stderr,
            show=show,
            log=True,
            log_method="warning",
        )
        return None
    else:
        return text


def parse_unicode_data(text: str, *, show: bool = True) -> dict[str, str]:
    """
    Parse the Unicode data text and return a dictionary of alternate names.

    Args:
        text (str): The raw text of the Unicode data.
        show (bool): If True, display progress messages.

    Returns:
        dict[str, str]: A dictionary mapping characters to their alternate names.
    """
    alt_names: dict[str, str] = {}
    for line in text.splitlines():
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#"):
            continue
        fields = stripped_line.split(";")
        if len(fields) < EXPECTED_MIN_FIELDS:
            echo(
                msg=MSG_WARNING_MALFORMED_LINE.format(line=stripped_line),
                style=lambda m: format_warning(m),
                stream=sys.stderr,
                show=show,
                log=True,
                log_method="warning",
            )
            continue
        code_hex = fields[0]
        alt_name = fields[ALT_NAME_INDEX].strip()
        if alt_name:
            try:
                char = chr(int(code_hex, 16))
                alt_names[char] = alt_name
            except ValueError as exc:
                echo(
                    msg=MSG_WARNING_INVALID_CODE.format(code_hex=code_hex, error=exc),
                    style=lambda m: format_warning(m),
                    stream=sys.stderr,
                    show=show,
                    log=True,
                    log_method="warning",
                )
    return alt_names


def load_alternate_names(*, show: bool = True, use_color: bool = True) -> dict[str, str]:
    """
    Load alternate names from UnicodeData.txt.

    Attempts to download the file if not found locally. Falls back to
    using the local version if available.

    Args:
        show (bool): If True, show progress messages to stderr.
        use_color (bool): If True, colorize output.

    Returns:
        dict[str, str]: Dictionary mapping characters to their alternate names.

    Raises:
        ValueError: If validation or download of data fails.
    """
    unicode_data_url = get_unicode_data_url()
    unicode_data_file = get_unicode_data_file()

    text = None
    if unicode_data_file.exists():
        text = load_unicode_data_from_file(unicode_data_file, show=show)

    if not text:
        success = download_and_cache_unicode_data(
            unicode_data_url,
            unicode_data_file,
            show=show,
            use_color=use_color,
        )
        if not success:
            return {}
        text = load_unicode_data_from_file(unicode_data_file, show=show)
        if not text:
            return {}

    return parse_unicode_data(text, show=show)
