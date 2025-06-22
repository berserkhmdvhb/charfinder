"""Unicode text normalization utility for CharFinder.

Provides a single function to normalize text using Unicode normalization,
whitespace cleanup, diacritic stripping, and uppercase conversion for consistent
character name matching.

Functions:
    normalize(): Normalize input text with configurable profile and Unicode normalization form.
"""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import unicodedata
from typing import Literal

from charfinder.config.constants import DEFAULT_NORMALIZATION_FORM, DEFAULT_NORMALIZATION_PROFILE
from charfinder.config.messages import MSG_ERROR_NORMALIZATION_FAILED
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
    *,
    profile: Literal["raw", "light", "medium", "aggressive"] = DEFAULT_NORMALIZATION_PROFILE,
    form: Literal["NFC", "NFD", "NFKC", "NFKD"] = DEFAULT_NORMALIZATION_FORM,
) -> str:
    """
    Normalize the input text using the selected normalization profile.

    Profiles:
        - raw: Return the input string unchanged.
        - light: Trim, collapse whitespace, and uppercase.
        - medium: light + Unicode normalization + uppercase.
        - aggressive: medium + remove diacritics + strip zero-width characters.

    Args:
        text: Input string.
        profile: Normalization profile to apply.
        form: Unicode normalization form (applied for medium/aggressive only).

    Returns:
        str: Normalized version of the input string.
    """
    try:
        if profile == "raw":
            return text

        # Step 1: Trim and collapse whitespace
        text = " ".join(text.strip().split())

        if profile in {"medium", "aggressive"}:
            # Step 2: Unicode normalization
            text = unicodedata.normalize(form, text)

        if profile == "aggressive":
            # Step 3: Remove zero-width characters
            text = "".join(c for c in text if c not in {"\u200b", "\u200c", "\u200d", "\ufeff"})

            # Step 4: Remove diacritics (force NFKD first)
            decomposed = unicodedata.normalize("NFKD", text)
            text = "".join(c for c in decomposed if not unicodedata.combining(c))

        # Step 5: Convert to uppercase
        return text.upper()

    except Exception as exc:
        echo(
            MSG_ERROR_NORMALIZATION_FAILED.format(error=exc),
            style=lambda m: format_error(m, use_color=True),
            show=True,
            log=False,
            log_method="error",
        )
        raise
