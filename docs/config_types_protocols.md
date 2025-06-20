# Types and Protocols

This document outlines the role of project-wide type definitions and `Protocol` interfaces in **CharFinder**. The `types.py` module defines structured data classes and typing contracts that ensure correctness, flexibility, and testability across all components of the project.

---

## Purpose

The `types.py` module provides:

* **Shared types** for configurations and match results.
* **Dataclasses** for structured grouping of parameters.
* **TypedDicts** for match data representations.
* **Protocol interfaces** to define contract-based expectations for plugins, formatters, and match algorithms.
* **Callable aliases** for internal logic like match scoring functions.

These definitions enable static type checking, reduce boilerplate, and improve developer productivity with IDE auto-completion and refactor safety.

---

## Core Structures and Type Categories

### ✅ **Callable Type Aliases**

```python
AlgorithmFn = Callable[[str, str], float]
NameCache = dict[str, dict[str, str]]
```

* Used to represent fuzzy match functions and the Unicode name cache structure.

---

### ✅ **Dataclasses**

#### `FuzzyMatchContext`

Represents runtime parameters for fuzzy matching:

```python
@dataclass
class FuzzyMatchContext:
    threshold: float
    fuzzy_algo: FuzzyAlgorithm
    match_mode: FuzzyMatchMode
    agg_fn: HybridAggFunc
    verbose: bool
    use_color: bool
    query: str
```

#### `SearchConfig`

Configuration used during a character search:

```python
@dataclass
class SearchConfig:
    fuzzy: bool
    threshold: float
    name_cache: NameCache | None
    verbose: bool
    use_color: bool
    fuzzy_algo: FuzzyAlgorithm
    fuzzy_match_mode: FuzzyMatchMode
    exact_match_mode: str
    agg_fn: HybridAggFunc
    prefer_fuzzy: bool
```

#### `MatchDiagnosticsInfo`

Used in `--debug` mode to provide diagnostic output:

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
```

#### `MatchResult`

Encapsulates search results and exit code:

```python
@dataclass
class MatchResult:
    exit_code: int
    match_info: MatchDiagnosticsInfo | None = None
```

---

### ✅ **TypedDicts**

#### `CharMatch`

Returned for each character that matches a query:

```python
class CharMatch(TypedDict):
    code: str
    char: str
    name: str
    score: NotRequired[float | None]
    is_fuzzy: NotRequired[bool]
```

---

### ✅ **NamedTuple**

```python
class MatchTuple(NamedTuple):
    code: int
    char: str
    name: str
    score: float | None
```

This is a simpler, positional representation of a match result used for compatibility with older components.

---

### ✅ **Protocols**

Protocols define callable contracts for pluggable behaviors and testable interfaces.

#### `FormatterFunc`

```python
class FormatterFunc(Protocol):
    def __call__(self, message: str, *, use_color: bool) -> str: ...
```

Used for consistent styling of messages in CLI or logs.

#### `EchoFunc`

```python
class EchoFunc(Protocol):
    def __call__(self, msg: str, style: Callable[[str], str], *, stream_: object, show: bool = True, log: bool = False, log_method: str | None = None) -> None: ...
```

Allows injection of echo-style functions in testable, flexible ways.

#### `MatchFunc`

```python
class MatchFunc(Protocol):
    def __call__(self, query: str, candidate: str) -> float: ...
```

Abstract match function used for pluggable scoring implementations.

#### `DiagnosticFormatter`

```python
class DiagnosticFormatter(Protocol):
    def __call__(self, query: str, candidate: str, *, score: float, algorithm: str, mode: str, use_color: bool) -> str: ...
```

Used to generate detailed match diagnostics.

#### `UnicodeDataLoader`

```python
class UnicodeDataLoader(Protocol):
    def __call__(self, file_path: Path) -> NameCache: ...
```

Pluggable interface for Unicode data loading functions.

---

## Integration with `constants.py`

Most types in this module depend on `Literal[...]` types defined in [`constants.py`](../src/charfinder/constants.py):

* `FuzzyAlgorithm`
* `FuzzyMatchMode`
* `ExactMatchMode`
* `ColorMode`
* `HybridAggFunc`

These ensure consistent values and autocompletion across the project.

---

## Dependency Map

| Dependency         | Purpose                                                                                  |
| ------------------ | ---------------------------------------------------------------------------------------- |
| `constants.py`     | Provides all `Literal[...]` values for algorithm names, modes, and output settings.      |
| `validators.py`    | Uses many of the types (e.g., `FuzzyConfig`, `MatchDiagnosticsInfo`) to validate inputs. |
| `core/` and `cli/` | Consume `SearchConfig`, `MatchResult`, `EchoFunc`, and other interfaces across modules.  |
| `diagnostics.py`   | Uses `DiagnosticFormatter`, `MatchDiagnosticsInfo`, and echo-related interfaces.         |

---

## Benefits of Centralized Typing

* Static analysis with **MyPy** and IDEs.
* Easy refactoring and extension.
* Ensures correct usage across CLI, core, and test layers.
* Improves testability via pluggable `Protocol` interfaces.
* Clarifies contracts for formatter, diagnostics, and loaders.

---

## Summary

The `types.py` module defines a robust foundation for type safety, diagnostics, formatting, and search configuration. By using standard structures and `Protocol`s, it enhances the project's maintainability, testing, and clarity across CLI and programmatic APIs.
