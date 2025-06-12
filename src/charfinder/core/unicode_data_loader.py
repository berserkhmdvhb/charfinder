"""
Load and parse the UnicodeData.txt file for alternate character names.

This module extracts official and alternate names for Unicode characters
from the Unicode Character Database (UCD), specifically UnicodeData.txt.

Exports:
    - load_alternate_names: Return a mapping of characters to their alternate names.
"""

import sys
from urllib.error import URLError
from urllib.request import urlopen

from charfinder.settings import get_unicode_data_file, get_unicode_data_url
from charfinder.utils.formatter import echo
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_info, format_warning

logger = get_logger()

__all__ = ["load_alternate_names"]

ALT_NAME_INDEX = 10
EXPECTED_MIN_FIELDS = 11


def load_alternate_names(
    *,
    show: bool = True,
    use_color: bool = True,
) -> dict[str, str]:
    """
    Load alternate names from UnicodeData.txt.

    Attempts to download the file if not found locally. Falls back to
    using the local version if available.

    Args:
        show: If True, show progress messages to stderr.
        use_color: If True, apply color to terminal output.

    Returns:
        Dictionary mapping characters to their alternate names.
    """
    text: str | None = None

    unicode_data_url = get_unicode_data_url()
    unicode_data_file = get_unicode_data_file()

    # Attempt to download if local file is missing
    if not unicode_data_file.is_file():
        try:
            with urlopen(unicode_data_url, timeout=5) as response:  # noqa: S310
                text = response.read().decode("utf-8")
            unicode_data_file.parent.mkdir(parents=True, exist_ok=True)
            unicode_data_file.write_text(text, encoding="utf-8")
            message = f'Downloaded and cached "UnicodeData.txt" from {unicode_data_url}'
            echo(
                message,
                style=lambda m: format_info(m, use_color=use_color),
                stream=sys.stderr,
                show=show,
                log=True,
                log_method="info",
            )
        except (URLError, TimeoutError, OSError):
            fallback_message = 'Could not download "UnicodeData.txt". No local fallback found.'
            echo(
                fallback_message,
                style=lambda m: format_warning(m, use_color=use_color),
                stream=sys.stderr,
                show=show,
                log=True,
                log_method="warning",
            )
            return {}
    else:
        text = unicode_data_file.read_text(encoding="utf-8")
        message = f'Loaded "UnicodeData.txt" from local file: {unicode_data_file}'
        echo(
            message,
            style=lambda m: format_info(m, use_color=use_color),
            stream=sys.stderr,
            show=show,
            log=True,
            log_method="info",
        )

    alt_names: dict[str, str] = {}
    for line in text.splitlines():
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#"):
            continue
        fields = stripped_line.split(";")
        if len(fields) < EXPECTED_MIN_FIELDS:
            continue
        code_hex = fields[0]
        alt_name = fields[ALT_NAME_INDEX].strip()
        if alt_name:
            try:
                char = chr(int(code_hex, 16))
                alt_names[char] = alt_name
            except ValueError:
                continue

    return alt_names
