"""
Unit tests for charfinder.config.aliases module.

Covers:
- Valid instantiation of all Literal-based type aliases
- Compatibility checks with expected string values
"""

from typing import get_args

from charfinder.config import aliases


def test_fuzzy_algorithm_literals() -> None:
    expected = {"levenshtein_ratio", "simple_ratio", "normalized_ratio", "token_sort_ratio", "hybrid_score"}
    assert set(get_args(aliases.FuzzyAlgorithm)) == expected


def test_exact_match_mode_literals() -> None:
    expected = {"substring", "word-subset"}
    assert set(get_args(aliases.ExactMatchMode)) == expected


def test_fuzzy_match_mode_literals() -> None:
    expected = {"single", "hybrid"}
    assert set(get_args(aliases.FuzzyMatchMode)) == expected


def test_color_mode_literals() -> None:
    expected = {"auto", "always", "never"}
    assert set(get_args(aliases.ColorMode)) == expected


def test_hybrid_agg_func_literals() -> None:
    expected = {"mean", "median", "max", "min"}
    assert set(get_args(aliases.HybridAggFunc)) == expected


def test_output_format_literals() -> None:
    expected = {"text", "json"}
    assert set(get_args(aliases.OutputFormat)) == expected


def test_normalization_form_literals() -> None:
    expected = {"NFC", "NFD", "NFKC", "NFKD"}
    assert set(get_args(aliases.NormalizationForm)) == expected


def test_normalization_profile_literals() -> None:
    expected = {"raw", "light", "medium", "aggressive"}
    assert set(get_args(aliases.NormalizationProfile)) == expected


def test_show_score_literals() -> None:
    expected = {"true", "1", "yes", "false", "0", "no"}
    assert set(get_args(aliases.ShowScore)) == expected
