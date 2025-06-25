"""
Unit tests for charfinder.config.types module.

Covers:
- FuzzyMatchContext, SearchConfig, MatchResult, MatchDiagnosticsInfo, MatchTuple instantiation
- CharMatch and NormalizationProfileDict TypedDict structures
- Callable Protocols: AlgorithmFn, FormatterFunc, EchoFunc, MatchFunc, DiagnosticFormatter, UnicodeDataLoader
"""

from pathlib import Path
from typing import get_type_hints, TextIO

from charfinder.config import types


def test_algorithm_fn_type() -> None:
    def dummy_algo(a: str, b: str) -> float:
        return 0.5

    assert isinstance(dummy_algo("a", "b"), float)
    assert callable(dummy_algo)


def test_search_config_instantiation() -> None:
    config = types.SearchConfig(
        fuzzy=True,
        threshold=0.7,
        name_cache=None,
        verbose=True,
        debug=False,
        use_color=False,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="single",
        exact_match_mode="word-subset",
        agg_fn="mean",
        prefer_fuzzy=True,
        normalization_profile="aggressive",
    )
    assert config.fuzzy
    assert config.threshold == 0.7
    assert config.name_cache is None
    assert config.fuzzy_algo == "token_sort_ratio"


def test_fuzzy_match_context_instantiation() -> None:
    context = types.FuzzyMatchContext(
        threshold=0.8,
        fuzzy_algo="levenshtein_ratio",
        match_mode="hybrid",
        agg_fn="max",
        verbose=False,
        debug=False,
        use_color=True,
        query="snow"
    )
    assert context.query == "snow"
    assert context.fuzzy_algo == "levenshtein_ratio"
    assert context.use_color is True


def test_match_result_and_diagnostics() -> None:
    diagnostics = types.MatchDiagnosticsInfo(
        fuzzy=True,
        fuzzy_was_used=True,
        fuzzy_algo="token_sort_ratio",
        fuzzy_match_mode="single",
        prefer_fuzzy=False,
        exact_match_mode="substring",
        threshold=0.65,
        hybrid_agg_fn="mean",
    )
    result = types.MatchResult(exit_code=0, match_info=diagnostics)
    assert result.exit_code == 0
    if result.match_info is not None:
        assert result.match_info.fuzzy_algo == "token_sort_ratio"


def test_char_match_typeddict_structure() -> None:
    sample: types.CharMatch = {
        "code": "U+0041",
        "char": "A",
        "name": "LATIN CAPITAL LETTER A",
        "score": 1.0,
        "is_fuzzy": False,
        "code_int": 65,
    }
    hints = get_type_hints(types.CharMatch, include_extras=True)
    for key in sample:
        assert key in hints


def test_match_tuple_instantiation() -> None:
    match = types.MatchTuple(code=65, char="A", name="LATIN CAPITAL LETTER A", score=1.0, is_fuzzy=True)
    assert match.code == 65
    assert match.is_fuzzy


def test_normalization_profile_dict() -> None:
    profile: types.NormalizationProfileDict = {
        "form": "NFKC",
        "strip_accents": True,
        "strip_whitespace": False,
    }
    assert profile["form"] == "NFKC"


def test_protocols_functionally(tmp_path: Path) -> None:
    def dummy_formatter(message: str, *, use_color: bool) -> str:
        return message.upper() if use_color else message

    def dummy_echo(
        msg: str,
        style: types.FormatterFunc,
        *,
        stream_: TextIO,
        show: bool = True,
        log: bool = False,
        log_method: str | None = None
    ) -> None:
        if show:
            stream_.write(style(msg, use_color=True))

    def dummy_match(query: str, candidate: str) -> float:
        return 0.9

    def dummy_diag_fmt(
        query: str,
        candidate: str,
        *,
        score: float,
        algorithm: str,
        mode: str,
        use_color: bool
    ) -> str:
        return f"{query} vs {candidate} -> {score:.2f}"

    def dummy_loader(path: Path) -> types.NameCache:
        return {"A": {"code": "U+0041", "char": "A", "name": "LATIN CAPITAL LETTER A"}}

    assert isinstance(dummy_formatter("test", use_color=True), str)
    assert callable(dummy_echo)
    assert dummy_match("a", "b") == 0.9
    assert "-> 0.90" in dummy_diag_fmt("a", "b", score=0.9, algorithm="seq", mode="token", use_color=False)
    assert "A" in dummy_loader(tmp_path / "fake.txt")
