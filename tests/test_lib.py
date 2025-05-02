import pytest
import unicodedata
import os
import json
import re
from cf_lib import find_chars, normalize, build_name_cache, CACHE_FILE

def test_strict_match():
    results = list(find_chars("snowman", verbose=False))
    assert any("SNOWMAN" in line for line in results)
    assert any("U+2603" in line and "☃" in line for line in results)

def test_strict_match_case_insensitive():
    results_lower = list(find_chars("snowman", verbose=False))
    results_upper = list(find_chars("SNOWMAN", verbose=False))
    assert results_lower == results_upper

def test_strict_match_accented():
    results = list(find_chars("acute", verbose=False))
    assert any("LATIN SMALL LETTER E WITH ACUTE" in line for line in results)

def test_no_match_without_fuzzy():
    results = list(find_chars("smilng", verbose=False))
    assert results == []

def test_fuzzy_match():
    results = list(find_chars("grnning", fuzzy=True, verbose=False))
    assert any("GRINNING" in line for line in results)

def test_fuzzy_does_not_override_strict():
    strict = list(find_chars("heart", verbose=False))
    fuzzy = list(find_chars("heart", fuzzy=True, verbose=False))
    assert strict == fuzzy

def test_output_format_fields():
    results = list(find_chars("heart", verbose=False))
    pattern = re.compile(r"^U\+[0-9A-F]{4,6}\t.{1,4}\t.+\(\\u[0-9a-f]{4,6}\)$")

    for line in results:
        assert line.startswith("U+")
        assert pattern.match(line), f"Line does not match expected format: {line}"

def test_unicode_escape_format():
    results = list(find_chars("heart", verbose=False))
    for line in results:
        assert "\\u" in line
        assert line.startswith("U+")

def test_normalization_function():
    assert normalize("\u00e9") == "E\u0301"
    assert normalize("caf\u00e9") == "CAFE\u0301"

def test_name_cache_exists():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    assert not os.path.exists(CACHE_FILE)
    cache = build_name_cache(verbose=False)
    assert os.path.exists(CACHE_FILE)
    assert isinstance(cache, dict)
    assert all(isinstance(k, str) and isinstance(v, dict) for k, v in cache.items())

def test_multiple_matches():
    results = list(find_chars("arrow", verbose=False))
    assert len(results) > 10
    assert all("ARROW" in line for line in results)

def test_nfkd_decomposition_behavior():
    decomposed_query = normalize("\u00e9")
    assert decomposed_query == "E\u0301"

def test_fuzzy_threshold_effect():
    loose = list(find_chars("grnning", fuzzy=True, threshold=0.5, verbose=False))
    strict = list(find_chars("grnning", fuzzy=True, threshold=0.9, verbose=False))
    assert len(loose) >= len(strict)

def test_fuzzy_threshold_too_strict_returns_none():
    results = list(find_chars("grnning", fuzzy=True, threshold=0.95, verbose=False))
    assert results == [] or all("GRINNING" in line for line in results)

def test_fuzzy_threshold_default_matches_explicit():
    default = list(find_chars("grnning", fuzzy=True, verbose=False))
    explicit = list(find_chars("grnning", fuzzy=True, threshold=0.7, verbose=False))
    assert default == explicit

def test_empty_query_returns_nothing():
    results = list(find_chars("", verbose=False))
    assert results == []

def test_non_string_query_raises_typeerror():
    with pytest.raises(TypeError):
        list(find_chars(123, verbose=False))

def test_large_batch_query_execution():
    queries = ["arrow", "face", "hand", "circle", "star", "square"]
    for query in queries:
        results = list(find_chars(query, verbose=False))
        assert isinstance(results, list)
        assert len(results) > 0