import pytest
from charfinder.fuzzymatchlib import compute_similarity
from charfinder.constants import VALID_FUZZY_ALGOS, VALID_MATCH_MODES


def test_similarity_exact_match() -> None:
    assert compute_similarity('smile', 'smile') == 1.0


def test_similarity_case_insensitive() -> None:
    assert compute_similarity('SmIlE', 'smile') == 1.0


def test_similarity_algorithms_produce_floats() -> None:
    for algo in VALID_FUZZY_ALGOS:
        score = compute_similarity('smile', 'smlie', algorithm=algo)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


def test_similarity_hybrid_average_range() -> None:
    if 'hybrid' in VALID_MATCH_MODES:
        score = compute_similarity('smile', 'smyle', mode='hybrid')
        assert 0.0 <= score <= 1.0


def test_similarity_invalid_algorithm_raises() -> None:
    with pytest.raises(ValueError):
        compute_similarity('smile', 'smyle', algorithm='unknown')  # type: ignore


def test_similarity_invalid_match_mode_raises() -> None:
    with pytest.raises(ValueError):
        compute_similarity('smile', 'smyle', mode='ensemble')  # type: ignore