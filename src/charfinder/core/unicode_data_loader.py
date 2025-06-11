"""
Load and parse the UnicodeData.txt file for alternate character names.

This module extracts official and alternate names for Unicode characters
from the Unicode Character Database (UCD), specifically UnicodeData.txt.

Exports:
    - load_alternate_names: Return a mapping of characters to their alternate names.
"""

from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from charfinder.utils.logger_setup import get_logger

logger = get_logger()

UNICODE_DATA_URL = "https://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt"
UNICODE_DATA_FILE = Path(__file__).parent.parent.parent / "data" / "UnicodeData.txt"

__all__ = ["load_alternate_names"]

ALT_NAME_INDEX = 10
EXPECTED_MIN_FIELDS = 11


def load_alternate_names() -> dict[str, str]:
    """
    Load alternate names from UnicodeData.txt.

    Attempts to download the file if not found locally. Falls back to
    using the local version if available.

    Returns:
        Dictionary mapping characters to their alternate names.
    """
    text: str | None = None

    # Attempt to download if local file is missing
    if not UNICODE_DATA_FILE.is_file():
        try:
            with urlopen(UNICODE_DATA_URL, timeout=5) as response:  # noqa: S310
                text = response.read().decode("utf-8")
            UNICODE_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            UNICODE_DATA_FILE.write_text(text, encoding="utf-8")
            logger.info("Downloaded and cached UnicodeData.txt from unicode.org")
        except (URLError, TimeoutError, OSError) as err:
            fallback_msg = "Could not download UnicodeData.txt. No local fallback found."
            logger.warning("%s Error: %s", fallback_msg, err)
            return {}
    else:
        text = UNICODE_DATA_FILE.read_text(encoding="utf-8")
        logger.info("Loaded UnicodeData.txt from local file: %s", UNICODE_DATA_FILE)

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
                continue  # skip malformed code point

    return alt_names
