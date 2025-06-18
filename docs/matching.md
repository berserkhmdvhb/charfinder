# Matching Logic in CharFinder

This document provides a deep technical reference for the core matching behavior in **CharFinder**. It explains exact and fuzzy matching logic, CLI argument influence, default behavior, scoring algorithms, modes, hybrid logic, and diagnostic capabilities.

---

## 1. Overview

CharFinder searches Unicode character names using **exact** and/or **fuzzy** matching. This logic is triggered via CLI commands or internal API calls, governed by a `SearchConfig`.

---

## 2. Matching Flow

### Default Flow

1. Normalize query (NFC + uppercase).
2. Attempt **exact match** first using selected mode.
3. If exact matches found:

   * Return exact results.
   * If `--prefer-fuzzy` is set **and** `--fuzzy` is enabled, fuzzy results are also included.
4. If exact matches are **not** found and `--fuzzy` is enabled:

   * Perform fuzzy matching.

---

## 3. CLI Arguments Affecting Matching

| Argument                                     | Description                                                              |
| -------------------------------------------- | ------------------------------------------------------------------------ |
| `--fuzzy`                                    | Enables fallback to fuzzy matching if exact match fails.                 |
| `--prefer-fuzzy`                             | Even if exact match is successful, also return fuzzy matches.            |
| `--threshold FLOAT`                          | Minimum fuzzy score \[0.0, 1.0] to accept a match (default: 0.7).        |
| `--exact-match-mode {substring,word-subset}` | Strategy for exact match. Default: `word-subset`.                        |
| `--fuzzy-match-mode {first,all,hybrid}`      | Strategy for fuzzy match result filtering. Default: `first`.             |
| `--fuzzy-algo ALGO`                          | Specifies fuzzy algorithm (see list below). Default: `token_sort_ratio`. |
| `--hybrid-agg-fn {mean,median,max,min}`      | Aggregation function for hybrid scoring. Default: `mean`.                |

---

## 4. Exact Matching

### Modes

| Mode          | CLI                                        | Description                                                 |
| ------------- | ------------------------------------------ | ----------------------------------------------------------- |
| `substring`   | `--exact-match-mode substring`             | Query is a literal substring of the name.                   |
| `word-subset` | `--exact-match-mode word-subset` (default) | All query words must be present in name, order-independent. |

---

## 5. Fuzzy Matching

### Match Modes

| Mode     | CLI                                  | Description                                                  |
| -------- | ------------------------------------ | ------------------------------------------------------------ |
| `first`  | `--fuzzy-match-mode first` (default) | Return best match (highest score).                           |
| `all`    | `--fuzzy-match-mode all`             | Return all matches above threshold.                          |
| `hybrid` | `--fuzzy-match-mode hybrid`          | Combine multiple algorithm scores into one aggregated score. |

### Available Algorithms (`--fuzzy-algo`)

| Algorithm           | Description                                              |
| ------------------- | -------------------------------------------------------- |
| `simple_ratio`      | Fast character overlap (SequenceMatcher).                |
| `normalized_ratio`  | Character overlap with normalization penalty.            |
| `levenshtein_ratio` | Edit distance normalized score.                          |
| `token_sort_ratio`  | Token-based sorting and comparison (handles reordering). |
| `hybrid_score`      | Internal use only (used automatically in hybrid mode).   |

### Hybrid Mode Details

If `--fuzzy-match-mode hybrid` is set:

* Scores from all core algorithms are computed:

  * `token_sort_ratio`
  * `simple_ratio`
  * `normalized_ratio`
  * `levenshtein_ratio`
* Each is weighted:

| Algorithm           | Weight |
| ------------------- | ------ |
| `token_sort_ratio`  | 0.55   |
| `simple_ratio`      | 0.15   |
| `normalized_ratio`  | 0.15   |
| `levenshtein_ratio` | 0.15   |

* Aggregation is performed using `--hybrid-agg-fn`:

  * `mean` (default), `median`, `min`, or `max`

---

## 6. SearchConfig Object

```python
@dataclass
class SearchConfig:
    fuzzy: bool
    prefer_fuzzy: bool
    threshold: float
    fuzzy_algo: FuzzyAlgorithm
    fuzzy_match_mode: FuzzyMatchMode
    exact_match_mode: ExactMatchMode
    agg_fn: HybridAggFunc
    use_color: bool
    verbose: bool
    name_cache: NameCache | None
```

---

## 7. Result Representation

### Internal Type: `MatchTuple`

```python
(code: int, char: str, name: str, score: float | None)
```

### Public API/CLI Type: `CharMatch`

```python
TypedDict('CharMatch', {
    'code': str,
    'char': str,
    'name': str,
    'score': NotRequired[float]
})
```

Converted using:

```python
from utils.formatter import matchtuple_to_charmatch
```

### Diagnostic Result Wrapper

```python
@dataclass
class MatchDiagnosticsInfo:
    fuzzy: bool
    fuzzy_was_used: bool
    fuzzy_algo: str
    fuzzy_match_mode: str
    prefer_fuzzy: bool
    exact_match_mode: str
    threshold: float
    hybrid_agg_fn: str | None = None

@dataclass
class MatchResult:
    exit_code: int
    match_info: MatchDiagnosticsInfo | None
```

---

## 8. Diagnostic Output (`--debug`)

If `--debug` is used:

* Matching decisions are logged:

  * Was exact or fuzzy used?
  * Which algorithms were selected?
  * What was the threshold and score?
  * Aggregation details (if hybrid)
* Match diagnostics info is displayed as part of the result.

---

## 9. Summary Matrix

| Match Path             | Exact Mode         | Fuzzy Mode | Algorithms Used                        | Aggregation     |
| ---------------------- | ------------------ | ---------- | -------------------------------------- | --------------- |
| Exact only             | substring / subset | -          | -                                      | -               |
| Exact → Fuzzy fallback | substring / subset | first/all  | user-selected or default (token\_sort) | -               |
| Exact → Fuzzy fallback | substring / subset | hybrid     | multiple weighted algorithms           | mean/median/... |
| Prefer fuzzy           | any                | any        | fuzzy run even if exact succeeds       | as above        |

---

## 10. References

* [`core/finders.py`](./core/finders.py)
* [`core/handlers.py`](./core/handlers.py)
* [`utils/formatter.py`](./utils/formatter.py)
* [`types.py`](./types.py)
* [`constants.py`](./constants.py)
* [`validators.py`](./validators.py)
* [`cli/cli_main.py`](./cli/cli_main.py)
