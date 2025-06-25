"""Tests for charfinder.utils.normalizer module."""

# ---------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------

import pytest
from typing import cast, NoReturn

import charfinder.utils.normalizer as normalizer_module
from charfinder.config.constants import (
    VALID_NORMALIZATION_FORMS,
    VALID_NORMALIZATION_PROFILES,
)
from charfinder.config.aliases import NormalizationForm, NormalizationProfile


# ---------------------------------------------------------------------
# Matrix 1: Unicode Normalization Forms (NFC, NFD, NFKC, NFKD)
# ---------------------------------------------------------------------

@pytest.mark.parametrize(
    "input_text, expected_by_form",
    [
        ("é", {  # decomposed 'e' + acute
            "NFC": "É",
            "NFD": "É",  # Still decomposed
            "NFKC": "É",
            "NFKD": "É",
        }),
        ("ﬁ", {  # ligature 'fi'
            "NFC": "FI",
            "NFD": "FI",
            "NFKC": "FI",  # Compatibility decomposition
            "NFKD": "FI",
        }),
        ("⅓", {  # vulgar fraction 1/3
            "NFC": "⅓",
            "NFD": "⅓",
            "NFKC": "1⁄3",  # Expanded fraction
            "NFKD": "1⁄3",
        }),
        ("œ", {  # ligature 'oe'
            "NFC": "Œ",
            "NFD": "Œ",
            "NFKC": "Œ",  # Compatibility decomposition
            "NFKD": "Œ",
        }),
        ("æ", {  # ligature 'ae'
            "NFC": "Æ",
            "NFD": "Æ",
            "NFKC": "Æ",  # Compatibility decomposition
            "NFKD": "Æ",
        }),
        ("ñ", {  # 'n' + combining tilde
            "NFC": "Ñ",     # Precomposed
            "NFD": "Ñ",     # Decomposed (N + ◌̃)
            "NFKC": "Ñ",
            "NFKD": "Ñ",
        }),
    ],
)
@pytest.mark.parametrize("form", sorted(VALID_NORMALIZATION_FORMS))
def test_unicode_normalization_forms(
    input_text: str,
    expected_by_form: dict[NormalizationForm, str],
    form: NormalizationForm,
) -> None:
    """Test normalization behavior across all Unicode normalization forms."""
    result = normalizer_module.normalize(input_text, profile="medium", form=form)
    expected = expected_by_form[form].upper()

    # Debug output
    print("\n" + "-" * 40)
    print(f"Input text           : {repr(input_text)}")
    print(f"Normalization form   : {form}")
    print(f"Expected (normalized): {repr(expected)}")
    print(f"Actual result        : {repr(result)}")
    print("-" * 40)

    assert result == expected


@pytest.mark.parametrize(
    "input_text, expected",
    [
        ("café", "CAFE"),
        ("café", "CAFE"),                     # 'e' + U+0301
        ("CAFÉ", "CAFE"),
        ("CAFÉ", "CAFE"),                     # capital E + U+0301
        ("𝒸𝒶𝓇é", "CARE"),                      # italic math letters → ASCII equivalents
        ("ｃａｆｅ́", "CAFE"),                  # fullwidth + U+0301
    ],
)
def test_readme_examples_aggressive(input_text: str, expected: str) -> None:
    """Test normalization of README examples under aggressive profile."""
    result = normalizer_module.normalize(input_text, profile="aggressive")
    print("\n" + "-" * 40)
    print(f"Input text   : {repr(input_text)}")
    print(f"Codepoints   : {' '.join(f'U+{ord(c):04X}' for c in input_text)}")
    print(f"Normalized   : {repr(result)}")
    print(f"Expected     : {repr(expected)}")
    print("-" * 40)
    assert result == expected

# ---------------------------------------------------------------------
# Matrix 2: Normalization Profiles (raw, light, medium, aggressive)
# ---------------------------------------------------------------------

@pytest.mark.parametrize(
    "input_text, expected_by_profile",
    [
        ("  café  ", {
            "raw": "  café  ",
            "light": "CAFÉ",
            "medium": "CAFÉ",
            "aggressive": "CAFE",
        }),
        ("Z\u200bE\u200cR\u200dO", {
            "raw": "Z\u200bE\u200cR\u200dO",
            "light": "Z\u200bE\u200cR\u200dO".strip().upper(),
            "medium": "Z\u200bE\u200cR\u200dO".strip().upper(),
            "aggressive": "ZERO",
        }),
        ("fiançée", {
            "raw": "fiançée",
            "light": "FIANÇÉE",
            "medium": "FIANÇÉE",
            "aggressive": "FIANCEE",
        }),
        ("  élève  ", {
            "raw": "  élève  ",
            "light": "ÉLÈVE",
            "medium": "ÉLÈVE",
            "aggressive": "ELEVE",
        }),
    ],
)
@pytest.mark.parametrize("profile", sorted(VALID_NORMALIZATION_PROFILES))
def test_normalization_profiles(
    input_text: str,
    expected_by_profile: dict[NormalizationProfile, str],
    profile: NormalizationProfile,
) -> None:
    """Test normalization behavior across all defined profiles."""
    result = normalizer_module.normalize(input_text, profile=profile, form="NFC")
    # Debug output
    print("\n" + "-" * 40)
    print(f"Input text       : {repr(input_text)}")
    print(f"Profile          : {profile}")
    print(f"Expected result  : {repr(expected_by_profile[profile])}")
    print(f"Actual result    : {repr(result)}")
    print("-" * 40)

    assert result == expected_by_profile[profile]


# ---------------------------------------------------------------------
# Edge Case Tests
# ---------------------------------------------------------------------

def test_normalize_empty_string() -> None:
    """An empty string should return an empty string under any profile."""
    for profile in sorted(VALID_NORMALIZATION_PROFILES):
        assert normalizer_module.normalize("", profile=cast(NormalizationProfile, profile)) == ""


def test_normalize_already_normalized_text() -> None:
    """Already normalized input should remain unchanged when using 'raw'."""
    assert normalizer_module.normalize("HELLO WORLD", profile="raw") == "HELLO WORLD"


def test_normalize_whitespace_handling() -> None:
    """Whitespace should be trimmed and collapsed in 'light' and higher."""
    input_text = "  foo   bar\tbaz \n"
    expected = "FOO BAR BAZ"
    for profile in ("light", "medium", "aggressive"):
        assert normalizer_module.normalize(input_text, profile=profile) == expected


# ---------------------------------------------------------------------
# Error Handling
# ---------------------------------------------------------------------


def test_normalize_raises_and_logs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simulate internal normalization error in our function only."""
    monkeypatch.setattr(normalizer_module, "unicodedata", BrokenUnicodeData())

    with pytest.raises(RuntimeError, match="Normalization failed!"):
        normalizer_module.normalize("crash", profile="medium", form="NFC")


class BrokenUnicodeData:
    def normalize(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise RuntimeError("Normalization failed!")
# ---------------------------------------------------------------------
# Diacritic and Zero-width Tests (Aggressive)
# ---------------------------------------------------------------------

def test_diacritic_removal_aggressive() -> None:
    """Aggressive profile should strip all diacritics."""
    input_text = "voilà naïve fiancé"
    result = normalizer_module.normalize(input_text, profile="aggressive")
    assert result == "VOILA NAIVE FIANCE"


def test_zero_width_removal_aggressive() -> None:
    """Aggressive profile should remove all zero-width characters."""
    input_text = "Z\u200bE\u200cR\u200dO\ufeff"
    result = normalizer_module.normalize(input_text, profile="aggressive")
    assert result == "ZERO"
