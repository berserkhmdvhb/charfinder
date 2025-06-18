# Core Logic Architecture (`charfinder.core`)

This document describes the internal architecture and logic of the `charfinder.core` package, which encapsulates the main business logic behind character search, name matching, and Unicode data handling. Unlike CLI components that focus on user interaction, the `core` modules provide reusable, tested, and validated functionality that powers both interactive and programmatic usage.

---

## Overview

The core package is responsible for:

* Loading and parsing Unicode character names and alternate names.
* Building and managing the Unicode name cache.
* Performing both exact and fuzzy matching over Unicode data.
* Structuring configuration and result types for search logic.

---

## Mermaid Diagram: Core Logic Flow

```mermaid
flowchart TD
    %% ===========================
    %% Input Layer
    %% ===========================
    Q[query (str)]
    CFG[SearchConfig (dataclass)]
    CACHE[NameCache (dict)]

    subgraph Inputs
        Q
        CFG
        CACHE
    end

    %% ===========================
    %% Matching Logic Layer
    %% ===========================
    MATCHTYPE{Fuzzy?}
    EXACT[find_exact_matches()]
    FUZZY[find_fuzzy_matches()]

    subgraph Matching
        MATCHTYPE
        EXACT
        FUZZY
    end

    Q --> MATCHTYPE
    CFG --> MATCHTYPE
    CACHE --> MATCHTYPE

    MATCHTYPE -- No --> EXACT
    MATCHTYPE -- Yes --> FUZZY

    EXACT --> MR[MatchResult (exit_code, diagnostics)]
    FUZZY --> MR

    %% ===========================
    %% Handler Logic
    %% ===========================
    RUN[_run_query_and_return()]

    subgraph CoreHandler
        RUN
    end

    MR --> RUN

    %% ===========================
    %% Output Layer
    %% ===========================
    TEXT[Text Output]
    JSON[JSON Output]

    subgraph Output
        TEXT
        JSON
    end

    RUN --> TEXT
    RUN --> JSON
```

---

## Module Breakdown

### 1. `core/unicode_data_loader.py`

#### Responsibilities:

* Fetch or load the UnicodeData.txt file (either from URL or disk).
* Parse raw lines into alternate name mappings.
* Validate URL and file paths.

#### Key Functions:

* `load_alternate_names()` – Main entry point for loading alt names with fallback.
* `validate_files_and_url()` – Ensures path and URL validity.
* `download_and_cache_unicode_data()` – Downloads and writes Unicode data locally.
* `load_unicode_data_from_file()` – Reads UnicodeData.txt from disk.
* `parse_unicode_data()` – Converts file content into `{char: alt_name}` dict.

#### Output:

```python
Dict[str, str]  # Example: {"A": "LATIN CAPITAL LETTER A"}
```

---

### 2. `core/name_cache.py`

#### Responsibilities:

* Load and build a multi-source name cache including alternate names.
* Write and read cache from disk.
* Retry on failure, normalize keys.

#### Key Elements:

* `CacheIOOptions` / `BuildCacheOptions` – Typed configuration for cache behavior.
* `build_name_cache()` – Main entry to build a Unicode name cache.
* `_load_existing_cache()` – Reads JSON cache file.
* `_save_cache_with_retries()` – Saves cache to disk with retry logic.

#### Output:

```python
NameCache = Dict[str, Dict[str, str]]  # {'A': {'name': ..., 'alt_name': ...}}
```

---

### 3. `core/matching.py`

#### Responsibilities:

* Perform character name comparisons.
* Compute exact or fuzzy match scores.
* Normalize, validate, and skip malformed data.

#### Key Functions:

* `find_exact_matches()` – Simple exact prefix/substring search.
* `find_fuzzy_matches()` – Fuzzy search using `fuzzymatchlib`.
* `compute_similarity()` – Delegates to `AlgorithmFn` from `types.py`.

#### Data Flow:

* Takes `SearchConfig` and `NameCache`
* Returns list of `CharMatch` results (with optional scores)

---

### 4. `core/finders.py`

#### Responsibilities:

* Entry point to core matching logic.
* Wraps both exact and fuzzy matching functions.
* Chooses appropriate strategy based on config.

#### Key Functions:

* `find_chars()` – User-facing API.
* `find_chars_with_info()` – Also returns diagnostics.
* `find_chars_raw()` – Internal core interface.

#### Output:

```python
List[CharMatch]
# Or (List[CharMatch], MatchDiagnosticsInfo) when using diagnostics
```

---

### 5. `core/handlers.py`

#### Responsibilities:

* Formats search results for final consumption.
* Wraps finder logic and builds `MatchResult` dataclass.

#### Key Functions:

* `_run_query_and_return()` – Calls `find_chars_with_info()` and wraps output.
* `MatchResult` – Combines exit code and optional `MatchDiagnosticsInfo`

---

### 6. `core/core_main.py`

#### Responsibilities:

* Thin wrapper that validates inputs and delegates to `finders.py`.
* May be removed in favor of using `finders.py` directly.

#### Functions:

* `find_chars()`, `find_chars_raw()`, `find_chars_with_info()` – All delegated to `finders.py`

---

## Core Data Types (from `types.py`)

### Key Dataclasses

* `SearchConfig`: User-defined or CLI-resolved settings.
* `FuzzyMatchContext`: Contextual settings for scoring.
* `MatchDiagnosticsInfo`: Used for `--debug` CLI output.
* `MatchResult`: Final result of a search.

### Protocols

* `MatchFunc`, `EchoFunc`, `FormatterFunc`, `DiagnosticFormatter`, `UnicodeDataLoader`

---

## Summary

The `charfinder.core` package forms the backbone of the application’s logic. It takes care of everything from data ingestion and cache management to scoring and result generation. It is cleanly separated from CLI logic and can be reused in API backends, batch processing scripts, or test harnesses without modification.

The architectural design emphasizes modularity, testability, and configurability, making it easy to extend or plug in new functionality (e.g., alternate data sources, hybrid fuzzy algorithms, or custom output handlers).
