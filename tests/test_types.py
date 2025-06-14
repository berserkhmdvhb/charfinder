"""
Test types.py for structural correctness and compatibility.

Covers:
- FuzzyMatchContext and SearchConfig instantiation with valid literals
- CharMatch TypedDict structure
"""

from typing import get_type_hints

import pytest

from charfinder import types


def test_algorithm_fn_type() -> None:
    def dummy_algo(a: str, b: str) -> float:
        return 0.5

    assert isinstance(dummy_algo("a", "b"), float)
    assert callable(dummy_algo)


def test_fuzzy_match_context_fields() -> None:
    ctx = types.FuzzyMatchContext(
        threshold=0.8,
        fuzzy_algo="sequencematcher",
        match_mode="single",
        agg_fn="mean",
        verbose=True,
        use_color=False,
        query="test",
    )

    assert ctx.threshold == 0.8
    assert ctx.fuzzy_algo == "sequencematcher"
    assert ctx.match_mode == "single"
    assert ctx.agg_fn == "mean"
    assert ctx.verbose is True
    assert ctx.use_color is False
    assert ctx.query == "test"


def test_search_config_fields() -> None:
    config = types.SearchConfig(
        fuzzy=True,
        threshold=0.7,
        name_cache=None,
        verbose=True,
        use_color=False,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="single",
        exact_match_mode="word-subset",
        agg_fn="mean",
        prefer_fuzzy=False,
    )

    assert config.fuzzy is True
    assert config.threshold == 0.7
    assert config.name_cache is None
    assert config.verbose is True
    assert config.use_color is False
    assert config.fuzzy_algo == "token_sort_ratio"
    assert config.fuzzy_match_mode == "single"
    assert config.exact_match_mode == "word-subset"
    assert config.agg_fn == "mean"
    assert config.prefer_fuzzy is False


@pytest.mark.parametrize(
    "data",
    [
        {"code": "U+0041", "char": "A", "name": "LATIN CAPITAL LETTER A"},
        {"code": "U+00DF", "char": "ß", "name": "LATIN SMALL LETTER SHARP S", "score": 0.95},
    ],
)
def test_char_match_typeddict(data: dict[str, str | float]) -> None:
    hints = get_type_hints(types.CharMatch, include_extras=True)
    for key in ("code", "char", "name"):
        assert key in data
        assert key in hints
    if "score" in data:
        assert "score" in hints
        assert isinstance(data["score"], float)
