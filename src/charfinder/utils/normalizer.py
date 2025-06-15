"""Unicode text normalization utility for CharFinder.

Provides a single function to normalize text using Unicode normalization
and uppercase conversion, for consistent matching and comparison.

Functions:
    normalize(): Normalize input text with specified Unicode normalization form.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import unicodedata
from typing import Literal

from charfinder.constants import DEFAULT_NORMALIZATION_FORM
from charfinder.utils.formatter import echo
from charfinder.utils.logger_setup import get_logger
from charfinder.utils.logger_styles import format_error

__all__ = ["normalize"]

logger = get_logger()

# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def normalize(
    text: str, form: Literal["NFC", "NFD", "NFKC", "NFKD"] = DEFAULT_NORMALIZATION_FORM
) -> str:
    """
    Normalize the input text using a specified Unicode normalization form and convert to uppercase.

    Args:
        text: Input text.
        form:
            The normalization form (NFC, NFD, NFKC, NFKD).
            Defaults to the configured `DEFAULT_NORMALIZATION_FORM`.

    Returns:
        str: Normalized and uppercased text.
    """
    try:
        # Normalize the text based on the provided form
        normalized_text = unicodedata.normalize(form, text)
        # Convert the normalized text to uppercase
        return normalized_text.upper()
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
