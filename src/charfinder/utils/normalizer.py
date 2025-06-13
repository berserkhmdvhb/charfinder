"""Unicode text normalization utility for CharFinder.

Provides a single function to normalize text using Unicode normalization
and uppercase conversion, for consistent matching and comparison.

Functions:
    normalize(): Normalize input text with configured Unicode normalization form.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import unicodedata

from charfinder.constants import DEFAULT_NORMALIZATION_FORM
from charfinder.utils.logger_setup import get_logger

__all__ = ["normalize"]

logger = get_logger()

# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------


def normalize(text: str) -> str:
    """
    Normalize the input text using Unicode NFKD normalization and convert to uppercase.

    Args:
        text: Input text.

    Returns:
        str: Normalized and uppercased text.
    """
    return unicodedata.normalize(DEFAULT_NORMALIZATION_FORM, text).upper()
