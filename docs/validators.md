# Validators

This document explains the role, architecture, and usage of the `validators.py` module in the **CharFinder** project. The `validators` module plays a central role in ensuring that user inputs (CLI arguments, environment variables, and programmatic values) are validated, normalized, and resolved consistently across both the CLI and core APIs.

---

## Purpose

The `validators.py` module exists to:

* Centralize all validation logic for fuzzy algorithms, match modes, thresholds, color output modes, and more.
* Avoid duplication of validation rules across CLI and core components.
* Provide safe fallbacks and default values.
* Normalize inputs with user-friendly aliases and consistent types.
* Enable reusability in testing, CLI, core, and diagnostics.

---

## Responsibilities

The module validates and resolves values for the following:

* Fuzzy matching algorithm (`FuzzyAlgorithm`)
* Fuzzy matching mode (`FuzzyMatchMode`)
* Exact match mode (`ExactMatchMode`)
* Color mode (`ColorMode`)
* Match threshold (float between 0.0 and 1.0)
* Hybrid aggregation function (`HybridAggFunc`)

It provides these features:

* Runtime validation with fallback to defaults
* CLI-aware or core-aware source tracking
* Custom `argparse.Action` integration for CLI argument validation
* Resolution of fuzzy algorithm aliases (e.g., "lev" → "levenshtein\_ratio")

---

## Core Structures

### FuzzyConfig (from `constants.py`)

```python
@dataclass
class FuzzyConfig:
    fuzzy_algo: FuzzyAlgorithm
    fuzzy_match_mode: FuzzyMatchMode
    hybrid_weights: HybridWeights
```

This dataclass bundles two validated fields representing a user's fuzzy search configuration.

---

## Key Functions

### 1. `validate_threshold()`

Ensures the threshold is a float between 0.0 and 1.0:

```python
def validate_threshold(value: str | float | None, source: Literal["cli", "core"] = "core") -> float:
```

Raises `ValueError` if the value is invalid.

---

### 2. `validate_fuzzy_algorithm()`

Validates and normalizes the fuzzy algorithm string:

```python
def validate_fuzzy_algorithm(value: str | None, source: Literal["cli", "core"] = "core") -> FuzzyAlgorithm:
```

If an alias is passed (e.g. `"lev"`), it is resolved to the canonical algorithm.

---

### 3. `validate_fuzzy_match_mode()`

Ensures the fuzzy match mode is valid:

```python
def validate_fuzzy_match_mode(value: str | None, source: Literal["cli", "core"] = "core") -> FuzzyMatchMode:
```

Fallbacks to `DEFAULT_FUZZY_MATCH_MODE` if needed.

---

### 4. `validate_exact_match_mode()`

Validates modes such as `"substring"` or `"word-subset"`:

```python
def validate_exact_match_mode(value: str | None, source: Literal["cli", "core"] = "core") -> ExactMatchMode:
```

---

### 5. `validate_color_mode()`

Validates whether terminal color output is enabled, disabled, or auto-detected:

```python
def validate_color_mode(value: str | None, source: Literal["cli", "core"] = "core") -> ColorMode:
```

---

### 6. `validate_hybrid_agg_func()`

Ensures the aggregation method is one of the allowed set (mean, median, etc.):

```python
def validate_hybrid_agg_func(value: str | None, source: Literal["cli", "core"] = "core") -> HybridAggFunc:
```

---

### 7. `resolve_algorithm_name()`

Helper used internally and by the CLI to resolve user aliases like `"lev"` into canonical algorithm names:

```python
def resolve_algorithm_name(name: str) -> FuzzyAlgorithm:
```

Raises `ValueError` if not resolvable.

---

### 8. `FuzzyAlgorithmAction`

A custom `argparse.Action` subclass that validates fuzzy algorithm CLI inputs:

```python
class FuzzyAlgorithmAction(argparse.Action):
```

Can be registered in an `ArgumentParser` to ensure input is resolved and valid at parse time.

---

## Source Awareness

All validation functions accept an optional `source: Literal["cli", "core"]` parameter (default = `"core"`). This allows the validator to:

* Adapt error messages or behavior depending on where the input originates.
* Raise detailed CLI errors or internal exceptions as needed.
* Improve diagnostic messages by including source context.

---

## Constants and Valid Values

The `constants.py` file provides the source of truth for all valid modes, algorithms, and defaults:

* `VALID_COLOR_MODES`
* `VALID_FUZZY_ALGO_NAMES`
* `VALID_EXACT_MATCH_MODES`
* `DEFAULT_*` constants
* `FUZZY_ALGO_ALIASES` for resolving names like `"lev"` or `"token_sort"`

These constants ensure consistent behavior and prevent duplication across the project.

---

## Typing and Protocols

The `types.py` module defines reusable protocols and data structures for validators:

* `FuzzyAlgorithm` / `FuzzyMatchMode` / `ColorMode` etc. as `Literal[...]`
* `FuzzyConfig`, `SearchConfig`, `FuzzyMatchContext`, `MatchDiagnosticsInfo` for grouping parameters and diagnostics

This strict typing helps ensure:

* Mypy and IDE support for early error detection
* Reusability across CLI, core, and test code
* Safe refactoring

---

## Validator Module Dependency Map

The `validators.py` module integrates closely with other components of the CharFinder codebase:

| Dependency                                       | Description                                                                                                       |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| [`constants.py`](../src/charfinder/constants.py) | Provides all valid values, defaults, and environment variable names used in validation.                           |
| [`types.py`](../src/charfinder/types.py)         | Defines reusable dataclasses and Protocols like `FuzzyMatchContext`, `SearchConfig`, and `MatchDiagnosticsInfo`.  |
| `core/` and `cli/` modules                       | Both rely on centralized validation from `validators.py` to ensure consistency and reusability across components. |

These dependencies ensure:

* Shared validation logic across CLI and core layers
* Strict typing and safety via centralized type definitions
* Configurability via project-wide constants

---

## Usage Examples

```python
from charfinder.validators import validate_threshold, validate_fuzzy_algorithm

threshold = validate_threshold("0.8")
algo = validate_fuzzy_algorithm("lev")
```

From CLI:

```bash
charfinder --query "smile" --fuzzy-algo lev --threshold 0.75
```

---

## Summary

The `validators.py` module is foundational to CharFinder's robustness and flexibility. It ensures all user and environment inputs are safe, validated, and consistent. Centralizing validation here ensures:

* CLI and core use the same logic.
* Future features can reuse validation easily.
* Tests and diagnostics remain predictable and reliable.
