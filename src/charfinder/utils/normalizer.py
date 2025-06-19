"""Unicode text normalization utility for CharFinder.

Provides a single function to normalize text using Unicode normalization,
whitespace cleanup, diacritic stripping, and uppercase conversion for consistent
character name matching.

Functions:
    normalize(): Normalize input text with configurable Unicode normalization form.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import unicodedata
from typing import Literal

from charfinder.config.constants import DEFAULT_NORMALIZATION_FORM
from charfinder.utils.formatter import echo
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_error

__all__ = ["normalize"]

logger = get_logger()

# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def normalize(
    text: str,
    form: Literal["NFC", "NFD", "NFKC", "NFKD"] = DEFAULT_NORMALIZATION_FORM,
) -> str:
    """
    Normalize the input text using Unicode normalization, strip diacritics,
    trim and collapse whitespace, remove zero-width characters, and convert to uppercase.

    Args:
        text: Input text.
        form:
            The normalization form ('NFC', 'NFD', 'NFKC', 'NFKD').
            Defaults to `DEFAULT_NORMALIZATION_FORM`.

    Returns:
        str: Fully normalized, cleaned, and uppercased text.
    """
    try:
        # Step 1: Trim leading/trailing whitespace and collapse internal whitespace
        text = " ".join(text.strip().split())

        # Step 2: Remove common zero-width characters
        text = "".join(c for c in text if c not in {"\u200b", "\u200c", "\u200d", "\ufeff"})

        # Step 3: Normalize using the specified Unicode form
        text = unicodedata.normalize(form, text)

        # Step 4: Remove diacritics (accents) by filtering combining characters
        text = "".join(c for c in text if not unicodedata.combining(c))

        # Step 5: Convert to uppercase
        return text.upper()

    except Exception as e:
        message = f"Error normalizing text: {e}"
        echo(
            message,
            style=lambda m: format_error(m, use_color=True),
            show=True,
            log=False,
            log_method="error",
        )
        raise
