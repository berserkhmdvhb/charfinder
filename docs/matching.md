# Matching Logic in CharFinder

This document provides a deep technical reference for the core matching behavior in **CharFinder**. It explains exact and fuzzy matching logic, CLI argument influence, default behavior, scoring algorithms, hybrid logic, diagnostics, and result representations.

---

## 1. Overview

CharFinder searches Unicode character names using **exact** and/or **fuzzy** matching. The process is governed by a `SearchConfig` structure and influenced by CLI arguments or API parameters. Normalization is always applied, ensuring robust and consistent comparisons across character names.

---

## 2. Matching Flow

### Default Flow

```mermaid
graph TD
    A[Input Query] --> B[Normalize (NFC + uppercase)]
    B --> C{Exact match?}
    C -- Yes --> D[Return exact match(es)]
    D --> E{--prefer-fuzzy + --fuzzy?}
    E -- Yes --> F[Also perform fuzzy matching]
    E -- No --> G[Done]
    C -- No --> H{--fuzzy enabled?}
    H -- Yes --> I[Perform fuzzy matching]
    H -- No --> G
```

---

## 3. CLI Arguments Affecting Matching

| Argument                                     | Description                                                          |
| -------------------------------------------- | -------------------------------------------------------------------- |
| `--fuzzy`                                    | Enables fallback to fuzzy matching if exact match fails.             |
| `--prefer-fuzzy`                             | Also returns fuzzy matches even if exact matches were found.         |
| `--threshold FLOAT`                          | Minimum fuzzy score \[0.0, 1.0] to accept a match (default: `0.65`). |
| `--exact-match-mode {substring,word-subset}` | Exact match strategy. Default: `word-subset`.                        |
| `--fuzzy-match-mode {first,all,hybrid}`      | Fuzzy match strategy. Default: `first`.                              |
| `--fuzzy-algo ALGO`                          | Selects fuzzy algorithm. Default: `token_subset_ratio`.              |
| `--hybrid-agg-fn {mean,median,max,min}`      | Aggregation function in hybrid mode. Default: `mean`.                |

---

## 4. Exact Matching

### Modes

| Mode          | CLI Option                                 | Description                                                      |
| ------------- | ------------------------------------------ | ---------------------------------------------------------------- |
| `substring`   | `--exact-match-mode substring`             | Query must be a literal substring of the name.                   |
| `word-subset` | `--exact-match-mode word-subset` (default) | All query words must appear in the name (order does not matter). |

---

## 5. Fuzzy Matching

### Match Modes

| Mode     | CLI Option                           | Description                                                               |
| -------- | ------------------------------------ | ------------------------------------------------------------------------- |
| `first`  | `--fuzzy-match-mode first` (default) | Return only the best match above the threshold.                           |
| `all`    | `--fuzzy-match-mode all`             | Return all matches scoring above the threshold.                           |
| `hybrid` | `--fuzzy-match-mode hybrid`          | Score using multiple algorithms, aggregate results, then apply threshold. |

### Available Algorithms (`--fuzzy-algo`)

| Algorithm            | Description                                                            |
| -------------------- | ---------------------------------------------------------------------- |
| `simple_ratio`       | SequenceMatcher-based ratio (fast character overlap).                  |
| `normalized_ratio`   | Normalized ratio accounting for case and space differences.            |
| `levenshtein_ratio`  | Edit-distance based similarity (more expensive).                       |
| `token_sort_ratio`   | Token-based sort before comparison (handles word reordering well).     |
| `token_subset_ratio` | Token subset matching; penalizes extra or missing words (new default). |
| `hybrid_score`       | Internal use; combines multiple scores with weights.                   |

### Hybrid Mode Details

If `--fuzzy-match-mode hybrid` is selected:

* The following algorithms are used:

  * `token_sort_ratio`
  * `simple_ratio`
  * `normalized_ratio`
  * `levenshtein_ratio`

* **Weights** applied to each algorithm:

| Algorithm           | Weight |
| ------------------- | ------ |
| `token_sort_ratio`  | 0.55   |
| `simple_ratio`      | 0.15   |
| `normalized_ratio`  | 0.15   |
| `levenshtein_ratio` | 0.15   |

* Final score is computed using the aggregation function defined by `--hybrid-agg-fn`:

  * Options: `mean` (default), `median`, `max`, `min`

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

### Internal Tuple: `MatchTuple`

```python
(code: int, char: str, name: str, score: float | None)
```

### Public Dict: `CharMatch`

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

When `--debug` is enabled:

* A diagnostic block is printed showing:

  * Whether fuzzy matching was used
  * Chosen algorithms and mode
  * Threshold and scoring function
  * Aggregation details (for hybrid mode)
* Additionally, `--verbose` may show skipped characters and internal scores for transparency.

---

## 9. Summary Matrix

| Match Path             | Exact Mode         | Fuzzy Mode | Algorithms Used                    | Aggregation     |
| ---------------------- | ------------------ | ---------- | ---------------------------------- | --------------- |
| Exact only             | substring / subset | -          | -                                  | -               |
| Exact → Fuzzy fallback | substring / subset | first/all  | user-selected or default           | -               |
| Exact → Fuzzy fallback | substring / subset | hybrid     | weighted combination of algorithms | mean/median/... |
| Prefer fuzzy           | any                | any        | fuzzy run even if exact succeeds   | as above        |

---

## 10. References

* [`core/finders.py`](../src/charfinder/core/finders.py)
* [`core/handlers.py`](../src/charfinder/core/handlers.py)
* [`fuzzymatchlib.py`](../src/charfinder/fuzzymatchlib.py)
* [`utils/formatter.py`](../src/charfinder/utils/formatter.py)
* [`types.py`](../src/charfinder/types.py)
* [`constants.py`](../src/charfinder/constants.py)
* [`validators.py`](../src/charfinder/validators.py)
* [`cli/cli_main.py`](../src/charfinder/cli/cli_main.py)
