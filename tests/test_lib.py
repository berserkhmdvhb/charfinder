import pytest
import os
from core import find_chars, normalize, build_name_cache, CACHE_FILE


def test_strict_match_heart() -> None:
    results = list(find_chars("heart", verbose=False))
    assert any("WHITE HEART SUIT" in line for line in results)
    assert any("U+2661" in line for line in results)

def test_case_insensitive_strict() -> None:
    assert list(find_chars("snowman", verbose=False)) == list(find_chars("SNOWMAN", verbose=False))

def test_accented_match_normalized() -> None:
    assert any("ACUTE" in line for line in find_chars("acute", verbose=False))

def test_strict_vs_fuzzy_fallback() -> None:
    assert list(find_chars("smiel", verbose=False)) == []
    assert list(find_chars("smiel", fuzzy=True, verbose=False)) != []

def test_fuzzy_match_present() -> None:
    assert any("GRINNING" in line for line in find_chars("grnning", fuzzy=True, verbose=False))

def test_fuzzy_does_not_override_strict() -> None:
    assert list(find_chars("heart", verbose=False)) == list(find_chars("heart", fuzzy=True, verbose=False))

def test_output_format_and_score_column() -> None:
    results = list(find_chars("grnning", fuzzy=True, verbose=False))
    assert results[0].startswith("CODE") and "SCORE" in results[0]
    for line in results[2:]:
        assert line.startswith("U+")
        assert len(line.split()) >= 4

def test_output_strict_has_no_score_column() -> None:
    results = list(find_chars("snowman", verbose=False))
    assert all("SCORE" not in line for line in results[:2])

def test_normalization_nfkd() -> None:
    assert normalize("é") == "É"
    assert normalize("café") == "CAFÉ"

def test_cache_file_build_and_exists(tmp_path) -> None:
    test_cache = tmp_path / "test_cache.json"
    assert not test_cache.exists()
    cache = build_name_cache(verbose=False, cache_file=str(test_cache))
    assert test_cache.exists()
    assert isinstance(cache, dict)
    assert all("original" in v and "normalized" in v for v in cache.values())

def test_multiple_strict_matches() -> None:
    results = list(find_chars("arrow", verbose=False))
    assert len(results) > 10
    assert all("ARROW" in line for line in results[2:])

def test_empty_query_returns_nothing() -> None:
    assert list(find_chars("", verbose=False)) == []

def test_invalid_query_type_raises() -> None:
    with pytest.raises(TypeError):
        list(find_chars(123, verbose=False))

def test_fuzzy_threshold_behavior() -> None:
    loose = list(find_chars("grnning", fuzzy=True, threshold=0.5, verbose=False))
    strict = list(find_chars("grnning", fuzzy=True, threshold=0.9, verbose=False))
    assert len(loose) >= len(strict)

def test_fuzzy_score_exact_match() -> None:
    results = list(find_chars("heart", fuzzy=True, verbose=False))
    assert all(line.startswith("U+") for line in results[2:])

def test_default_vs_explicit_threshold() -> None:
    default = list(find_chars("grnning", fuzzy=True, verbose=False))
    explicit = list(find_chars("grnning", fuzzy=True, threshold=0.7, verbose=False))
    assert default == explicit

def test_fuzzy_algorithms_diverge() -> None:
    base_query = "c a T"
    threshold = 0.4

    results = {
        algo: list(find_chars(base_query, fuzzy=True, fuzzy_algo=algo, threshold=threshold, verbose=False))
        for algo in ["rapidfuzz", "sequencematcher", "levenshtein"]
    }

    # Extract all matched Unicode code points (e.g., U+1F600) from each result set
    match_codes = {
        algo: {line.split()[0] for line in lines if line.startswith("U+")}
        for algo, lines in results.items()
    }

    # Compare sets — check if at least one algorithm differs in result set
    code_sets = list(match_codes.values())
    assert any(code_sets[i] != code_sets[j] for i in range(len(code_sets)) for j in range(i + 1, len(code_sets))), (
        f"All fuzzy algorithms returned the same match set for query '{base_query}'."
    )


@pytest.mark.parametrize("query", ["arrow", "face", "star", "hand"])
def test_batch_queries_success(query: str) -> None:
    assert list(find_chars(query, verbose=False))