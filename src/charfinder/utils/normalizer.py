import logging
import unicodedata

__all__ = ["normalize"]

logger = logging.getLogger(__name__)


def normalize(text: str) -> str:
    """
    Normalize the input text using Unicode NFKD normalization and convert to uppercase.

    Args:
        text: Input text.

    Returns:
        Normalized and uppercased text.
    """
    return unicodedata.normalize("NFKD", text).upper()
