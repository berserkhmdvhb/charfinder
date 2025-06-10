import unicodedata

from charfinder.utils.logger import get_logger

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
    return unicodedata.normalize("NFKD", text).upper()
