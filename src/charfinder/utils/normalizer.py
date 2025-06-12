import unicodedata

from charfinder.constants import DEFAULT_NORMALIZATION_FORM
from charfinder.utils.logger_setup import get_logger

__all__ = ["normalize"]

logger = get_logger()


def normalize(text: str) -> str:
    """
    Normalize the input text using Unicode NFKD normalization and convert to uppercase.

    Args:
        text: Input text.

    Returns:
        Normalized and uppercased text.
    """
    return unicodedata.normalize(DEFAULT_NORMALIZATION_FORM, text).upper()
