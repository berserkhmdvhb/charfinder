import pytest
from charfinder.utils.normalizer import normalize
from charfinder.constants import DEFAULT_NORMALIZATION_FORM

# Define the normalization forms matrix with multiple characters
test_characters = {
    'é': {'NFC': 'É', 'NFD': 'É', 'NFKC': 'É', 'NFKD': 'É'},
    'è': {'NFC': 'È', 'NFD': 'È', 'NFKC': 'È', 'NFKD': 'È'},
    'ü': {'NFC': 'Ü', 'NFD': 'Ü', 'NFKC': 'Ü', 'NFKD': 'Ü'},
    'ç': {'NFC': 'Ç', 'NFD': 'Ç', 'NFKC': 'Ç', 'NFKD': 'Ç'},
    'ö': {'NFC': 'Ö', 'NFD': 'Ö', 'NFKC': 'Ö', 'NFKD': 'Ö'},
    'œ': {'NFC': 'Œ', 'NFD': 'Œ', 'NFKC': 'Œ', 'NFKD': 'Œ'},
    'æ': {'NFC': 'Æ', 'NFD': 'Æ', 'NFKC': 'Æ', 'NFKD': 'Æ'},
    'é': {'NFC': 'É', 'NFD': 'É', 'NFKC': 'É', 'NFKD': 'É'},
    'á': {'NFC': 'Á', 'NFD': 'Á', 'NFKC': 'Á', 'NFKD': 'Á'},
    'à': {'NFC': 'À', 'NFD': 'À', 'NFKC': 'À', 'NFKD': 'À'},
    'ñ': {'NFC': 'Ñ', 'NFD': 'Ñ', 'NFKC': 'Ñ', 'NFKD': 'Ñ'},
    'ø': {'NFC': 'Ø', 'NFD': 'Ø', 'NFKC': 'Ø', 'NFKD': 'Ø'}
}

@pytest.mark.parametrize(
    "input_text, expected_normalized_text",
    [
        # Test all characters with their expected normalized values
        (char, expected) for char, expected in test_characters.items()
    ]
)
def test_normalization_matrix(input_text: str, expected_normalized_text: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Test normalization for all Unicode normalization methods."""
    
    # Loop through all normalization forms and assert the correct normalization
    for norm_form, expected in expected_normalized_text.items():
        # Temporarily mock the normalization form for this test case
        monkeypatch.setattr("charfinder.constants.DEFAULT_NORMALIZATION_FORM", norm_form)
        
        normalized_text = normalize(input_text)

        # Debug output
        print(f"Input: {input_text}, Norm Method: {norm_form}, Expected: {expected}, Normalized: {normalized_text}")

        assert normalized_text == expected


# ---------------------------------------------------------------------
# Basic normalization tests
# ---------------------------------------------------------------------

def test_normalize_basic() -> None:
    """Test that text is normalized and converted to uppercase."""
    input_text = "café"
    expected = "CAFÉ"
    normalized_text = normalize(input_text)
    assert normalized_text == expected


def test_normalize_empty_string() -> None:
    """Test that an empty string returns an empty string."""
    input_text = ""
    expected = ""
    normalized_text = normalize(input_text)
    assert normalized_text == expected


def test_normalize_already_normalized() -> None:
    """Test that already normalized text is not modified."""
    input_text = "HELLO"
    expected = "HELLO"
    normalized_text = normalize(input_text)
    assert normalized_text == expected


def test_normalize_mixed_case() -> None:
    """Test that text is converted to uppercase during normalization."""
    input_text = "Hello World"
    expected = "HELLO WORLD"
    normalized_text = normalize(input_text)
    assert normalized_text == expected


# ---------------------------------------------------------------------
# Unicode normalization tests
# ---------------------------------------------------------------------

def test_normalize_unicode_composition() -> None:
    """Test that composed Unicode characters are normalized to NFC."""
    input_text = "é"  # Composed 'e' with acute accent
    expected = "É"  # Composed 'E' with acute accent (uppercased)
    normalized_text = normalize(input_text)
    # Ensure that normalization uses NFC and then uppercases
    assert normalized_text == expected


def test_normalize_unicode_decomposition() -> None:
    """Test that decomposed Unicode characters are normalized to NFKD."""
    input_text = "é"  # Decomposed 'e' + acute accent
    expected = "É"  # Uppercased
    normalized_text = normalize(input_text)
    assert normalized_text == expected


# ---------------------------------------------------------------------
# Test with special characters
# ---------------------------------------------------------------------

def test_normalize_special_characters() -> None:
    """Test that special characters are normalized correctly."""
    input_text = "noël"
    expected = "NOËL"
    normalized_text = normalize(input_text)
    assert normalized_text == expected


@pytest.mark.parametrize("input_text, expected", [
    ("à", "À"),
    ("ö", "Ö"),
    ("ü", "Ü"),
    ("ç", "Ç"),
    ("ñ", "Ñ"),
])
def test_normalize_various_unicode(input_text: str, expected: str) -> None:
    """Test normalization of various Unicode characters."""
    normalized_text = normalize(input_text)
    assert normalized_text == expected
