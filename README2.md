[![PyPI](https://img.shields.io/pypi/v/charfinder)](https://pypi.org/project/charfinder/)
[![Python](https://img.shields.io/pypi/pyversions/charfinder)](https://pypi.org/project/charfinder/)
[![License](https://img.shields.io/github/license/berserkhmdvhb/charfinder)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/charfinder/month)](https://pepy.tech/project/charfinder)
[![Tests](https://github.com/berserkhmdvhb/charfinder/actions/workflows/tests.yml/badge.svg)](https://github.com/berserkhmdvhb/charfinder/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/berserkhmdvhb/charfinder/badge.svg?branch=main)](https://coveralls.io/github/berserkhmdvhb/charfinder?branch=main)

# 🔎 charfinder

**charfinder** is a terminal and Python-based tool to search Unicode characters by name—strictly or fuzzily—with normalization, caching, logging, and colorful output.

Ever tried to find an emoji using its name, or more technically, the Unicode character for "shrug" or "grinning face"? `charfinder` helps you locate them effortlessly from the command line or programmatically.

---

## 📚 Table of Contents

- [Demo Video](#-demo-video)
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [For Developers](#-for-developers)
- [Dependencies](#-dependencies)
- [Roadmap](#-roadmap)
- [License](#-license)

---

# 🎥 1. Demo Video

https://github.com/user-attachments/assets/e19b0bbd-d99b-401b-aa29-0092627f376b

---

## ✨ 2. Features

CharFinder is a **feature-rich Unicode character search tool**, designed for both **CLI** and **Python library** usage. It combines exact and fuzzy matching with fast caching, robust environment management, and beautiful CLI output.

### 🔍 Unicode Character Search

* Search Unicode characters by name:

  * **Exact match** (substring or word-subset).
  * **Fuzzy match** with configurable threshold and algorithms.

* Supported fuzzy algorithms:

  * `sequencematcher` (difflib standard library).
  * `rapidfuzz`.
  * `python-Levenshtein`.

* Hybrid fuzzy matching:

  * Combine multiple algorithms with `mean`, `median`, `max`, or `min` aggregation.

### 📉 Unicode Normalization

* All matching is performed after Unicode **NFC normalization**.
* Matching is **case-insensitive** and **accent-insensitive**.
* Alternate names (from `UnicodeData.txt`) are supported.

### 🔄 Caching

* Unicode name cache:

  * Built on first run.
  * Cached locally to JSON file for fast subsequent runs.

* LRU cache:

  * Normalization operations are cached via LRU caching for performance.

### 📊 Logging

* Rotating file logging under `logs/{ENV}/`.

* Console logging:

  * `INFO` level by default.
  * `DEBUG` level with `--debug` flag.

* Each log record includes the current **environment** (DEV, UAT, PROD).

* Logging architecture is clean and test-friendly.

### 🔧 Environment-aware Behavior

* `.env` files are supported with robust resolution:
* Environment-specific behavior:
  * Log directory changes by environment.
  * Test mode activates `.env.test`.

* Cross-ref: [docs/environment\_config.md](docs/environment_config.md).

### 🔊 CLI Features

* Rich CLI with **argcomplete** tab completion.

* Color output:

  * Modes: `auto`, `always`, `never`.
  * Colors used for result rows, headers, log messages.

* Advanced CLI options:

  * `--fuzzy`, `--threshold`, `--fuzzy-algo`, `--fuzzy-match-mode`, `--hybrid-agg-fn`.
  * `--exact-match-mode`.
  * `--color`, `--verbose`, `--debug`.

* Detailed CLI help with examples.

* Cross-ref: [docs/cli\_architecture.md](docs/cli_architecture.md).

### 📚 Python Library Usage

* Import and use core API:

  * `find_chars()` - yields formatted result rows.
  * `find_chars_raw()` - returns structured data (for scripting / JSON output).

* Fully type-annotated.

* No CLI dependencies required in library usage.

* Cross-ref: [docs/core\_logic.md](docs/core_logic.md).

### 🔖 Testability & Quality

* 100% test coverage.

* CLI tested via **subprocess integration tests**.

* Modular `conftest.py` with reusable fixtures.

* Clean `pytest` + `coverage` + `pre-commit` workflow.

* Cross-ref: [docs/unit\_test\_design.md](docs/unit_test_design.md).

### 📑 Modern Packaging & Tooling

* `pyproject.toml` based (PEP 621).

* GitHub Actions CI pipeline:

  * Python 3.10 to 3.13.
  * Lint (Ruff), type-check (MyPy), test, coverage.

* Pre-commit hooks:

  * Black formatting.
  * Ruff linting.
  * Mypy type-checking.

* Easy publishing to PyPI.

* Cross-ref: [docs/logging\_system.md](docs/logging_system.md), [docs/env-logging-scenarios.md](docs/env-logging-scenarios.md).

---

## 3. 📦 Project Structure

CharFinder follows a **clean, layered architecture** to ensure separation of concerns, maintainability, and testability.

The project is structured for ease of contribution and for flexible usage as both:

* A **CLI tool** (`charfinder` command).
* An **importable Python library**.

### 3.1 📂 Structure

```
charfinder/
├── .github/workflows/               # GitHub Actions CI pipeline
├── .pre-commit-config.yaml          # Pre-commit hooks
├── publish/                         # Sample config for PyPI/TestPyPI
├── .env.sample                      # Sample environment variables
├── LICENSE.txt
├── Makefile                         # Automation tasks
├── MANIFEST.in                      # Files to include in sdist
├── pyproject.toml                   # PEP 621 build + deps
├── README.md                        # Project documentation (this file)
├── docs/                            # Detailed documentation (.md files)
├── src/charfinder/                  # Main package code
│   ├── __init__.py                  # Package version marker
│   ├── __main__.py                  # Enables `python -m charfinder`
│   ├── cli/                         # CLI logic (modularized)
│   ├── core/                        # Core Unicode search logic
│   ├── utils/                       # Shared utilities: formatting, logging, normalization
│   ├── constants.py                 # Constants and default values
│   ├── cache.py                     # Caching utilities
│   ├── fuzzymatchlib.py             # Fuzzy matching algorithms
│   ├── settings.py                  # Environment/config management
│   ├── types.py                     # Shared type definitions
│   └── py.typed                     # Marker for type-checking consumers
└── tests/
    ├── cli/                         # CLI test modules
    ├── core/                        # Core logic tests
    ├── test_log.py                  # Logging tests
    ├── test_settings.py             # Settings/config tests
    ├── conftest.py                  # Shared test fixtures
    └── manual/demo.ipynb            # Interactive notebook for manual testing
```

### 3.2 🧱 Architecture

CharFinder implements a **layered architecture** with clear boundaries:

* **CLI Layer**

  * User-facing command line interface.
  * Argument parsing, CLI options, formatted output.
  * Implements `cli_main.py`, `handlers.py`, `formatter.py`, and utilities.

* **Core Layer**

  * Unicode name cache builder.
  * Exact and fuzzy matching logic.
  * Unicode normalization.
  * Pure, reusable business logic.

* **Utilities Layer**

  * Logging system with rotating file handlers.
  * Environment configuration.
  * Type-safe, cached normalization.

* **Tests Layer**

  * Comprehensive unit and CLI tests.
  * 100% coverage enforced.
  * Supports isolated environment behavior during tests.

**Cross-reference:** see [Internals and Architecture](#9-internals-and-architecture) for deeper technical insights, and refer to these detailed documents:

* [docs/cli\_architecture.md](docs/cli_architecture.md)
* [docs/core\_logic.md](docs/core_logic.md)
* [docs/environment\_config.md](docs/environment_config.md)
* [docs/logging\_system.md](docs/logging_system.md)
* [docs/caching.md](docs/caching.md)

---

## 4. 🌐 What is Unicode?

Unicode is the universal standard for encoding text across all writing systems, symbols, and emojis in the world. It assigns a unique code point to every character, ensuring that text is represented consistently across different platforms, languages, and applications.

In other words, Unicode provides the foundation that enables modern software to handle multilingual text and a vast array of symbols reliably.

### Why It Matters for CharFinder

* **Uniform Search Space**: Unicode encompasses over 140,000 characters, making it possible to search and retrieve any symbol, emoji, or letter from a single source.
* **Cross-Language Support**: Whether you search for Latin letters, mathematical symbols, arrows, CJK characters, or ancient scripts, Unicode ensures consistent handling.
* **Emojis & Symbols**: Emojis are part of Unicode and fully supported by CharFinder.

### Normalization in CharFinder

Text normalization is crucial when performing searches across Unicode:

* Different character sequences may visually or semantically represent the same character (e.g. `é` vs `é`).
* Normalization converts these variations to a consistent form before comparison.

**CharFinder** uses **Unicode NFC (Normalization Form C)** by default, which:

* Ensures composed characters are used where possible.
* Provides stable and predictable search behavior.

For example:

| Input Query | Normalized Form (NFC) | Effective Search Behavior |
| ----------- | --------------------- | ------------------------- |
| café        | café (U+00E9)         | Matches correctly         |
| café       | café (U+00E9)         | Matches correctly         |

### Learn More

For deeper insights into Unicode normalization and its impact on search:

* [Unicode® Standard Annex #15 — Unicode Normalization Forms](https://unicode.org/reports/tr15/)
* CharFinder documentation: [docs/normalization.md](docs/normalization.md)

---

## 🎯 5. Exact and Fuzzy Match

CharFinder offers a rich and flexible matching system to search for Unicode characters by name. You can combine exact matching, fuzzy matching, different algorithms, and match modes to suit your needs.

### Matching Modes Overview

| Matching Type | Mode                  | CLI Argument                     | Description                                                                   |
| ------------- | --------------------- | -------------------------------- | ----------------------------------------------------------------------------- |
| Exact         | Substring             | `--exact-match-mode substring`   | Query string must appear as a substring of the character name.                |
| Exact         | Word Subset (default) | `--exact-match-mode word-subset` | All words in the query must appear in the character name (order-independent). |
| Fuzzy         | Single (default)      | `--fuzzy-match-mode single`      | Use a single fuzzy algorithm to compute similarity scores.                    |
| Fuzzy         | Hybrid                | `--fuzzy-match-mode hybrid`      | Combine multiple fuzzy algorithm scores using an aggregation function.        |

### Available Fuzzy Algorithms

You can select the fuzzy matching algorithm using `--fuzzy-algo`:

* `sequencematcher` (Python standard library `difflib.SequenceMatcher`)
* `rapidfuzz` ([RapidFuzz](https://github.com/maxbachmann/RapidFuzz))
* `levenshtein` ([python-Levenshtein](https://github.com/ztane/python-Levenshtein))

### Aggregation Functions (Hybrid Mode)

When using `--fuzzy-match-mode hybrid`, you can select how the algorithm scores are aggregated using `--hybrid-agg-fn`:

* `mean` (default)
* `median`
* `max`
* `min`

### Combination Matrix

| Exact Mode        | Fuzzy Mode | Fuzzy Algo                              | Aggregation Function   |
| ----------------- | ---------- | --------------------------------------- | ---------------------- |
| substring         | -          | -                                       | -                      |
| word-subset       | -          | -                                       | -                      |
| fallback to fuzzy | single     | sequencematcher, rapidfuzz, levenshtein | -                      |
| fallback to fuzzy | hybrid     | Combination of above                    | mean, median, max, min |

### Matching Flow

1. **Exact match first:**

   * CharFinder always tries exact match first (substring or word-subset).
2. **Fuzzy fallback:**

   * If no exact match is found and `--fuzzy` is enabled, fuzzy matching is attempted.
3. **Single vs. Hybrid:**

   * In single mode, one algorithm is used.
   * In hybrid mode, multiple algorithms are used and aggregated.

### Normalization

All matching is performed on Unicode **NFC-normalized** and **uppercased** character names and query strings to ensure consistency.

### Cross-Reference

For a deeper technical dive, see:

* [docs/matching.md](docs/matching.md)
* [docs/core\_logic.md](docs/core_logic.md)

---

## 7. 🚀 Usage

The following usage guide shows how to install, run, and integrate CharFinder both via its command-line interface (CLI) and as a Python library. Whether you are an end user, developer, or automator, CharFinder is designed to fit seamlessly into your workflow.

### 7.1 Installation

#### For Users

##### PyPI (Recommended)

```bash
pip install charfinder
```

##### GitHub (Development Version)

```bash
pip install git+https://github.com/berserkhmdvhb/charfinder.git
```

#### For Developers

##### Clone and Install in Editable Mode

```bash
git clone https://github.com/berserkhmdvhb/charfinder.git
cd charfinder
make develop
```

Alternatively:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .[dev]
```

---

### 7.2 💻 CLI Usage

CharFinder provides a rich CLI for exploring Unicode characters.

#### Basic Example

```bash
charfinder heart
```

Example output:

```bash
U+2764      ❤     HEAVY BLACK HEART  (\u2764)
```

#### Full Help

```bash
charfinder --help
```

#### Common CLI Options

| Option               | Description                                                           |
| -------------------- | --------------------------------------------------------------------- |
| `--fuzzy`            | Enable fuzzy search if no exact matches                               |
| `--threshold`        | Fuzzy match threshold (0.0 to 1.0)                                    |
| `--fuzzy-algo`       | Choose fuzzy algorithm: `sequencematcher`, `rapidfuzz`, `levenshtein` |
| `--fuzzy-match-mode` | Fuzzy match mode: `single` or `hybrid`                                |
| `--exact-match-mode` | Exact match mode: `substring` or `word-subset`                        |
| `--hybrid-agg-fn`    | Aggregation function for hybrid mode: `mean`, `median`, `max`, `min`  |
| `--color`            | Output color mode: `auto`, `always`, `never`                          |
| `--format`           | Output format: `text` or `json`                                       |
| `--verbose`, `-v`    | Enable verbose console output                                         |
| `--debug`            | Enable diagnostic output                                              |
| `--version`          | Show version                                                          |

#### Advanced CLI Tips

* Use `--fuzzy` and `--threshold` for typo tolerance.
* Use `--format json` for scripting and automation.
* Enable diagnostics with `--debug` or by setting `CHARFINDER_DEBUG_ENV_LOAD=1`.

For more details on CLI internals, see [docs/cli\_architecture.md](docs/cli_architecture.md).

---

### 7.3 🐉 Python Library Usage

CharFinder can also be used as a pure Python library:

#### Example: Basic Search

```python
from charfinder.core.core_main import find_chars

for line in find_chars("snowman"):
    print(line)
```

#### Example: Fuzzy Search with Options

```python
from charfinder.core.core_main import find_chars

for line in find_chars(
    "snwmn",
    fuzzy=True,
    threshold=0.6,
    fuzzy_algo="rapidfuzz",
    fuzzy_match_mode="single",
    exact_match_mode="word-subset",
    agg_fn="mean",
):
    print(line)
```

#### Example: Raw Results (for Scripting)

```python
from charfinder.core.core_main import find_chars_raw

results = find_chars_raw("grinning", fuzzy=True, threshold=0.7)

for item in results:
    print(item)
```

For detailed documentation on the core logic and API, see [docs/core\_logic.md](docs/core_logic.md).

---

## 8. Internals and Architecture

CharFinder is designed with a **layered, modular architecture** to ensure clean separation of concerns, testability, and reuse across CLI and Python library usage.

### 8.1. Architecture Overview

The architecture is composed of several logical layers:

1. **Core Logic Layer** (`src/charfinder/core`)

   * Contains business logic for Unicode character search.
   * Implements exact and fuzzy matching.
   * Provides normalized name cache.
   * Independent of CLI and I/O.

2. **CLI Layer** (`src/charfinder/cli`)

   * Implements `charfinder` command-line interface.
   * Provides CLI argument parsing, routing, and output formatting.
   * Manages CLI color output, JSON/text output.

3. **Utilities Layer** (`src/charfinder/utils`)

   * Shared utilities: logging setup, color formatting, Unicode normalization.
   * Used by both core and CLI layers.

4. **Settings Layer** (`src/charfinder/settings.py`)

   * Centralized environment and configuration management.
   * Loads `.env` files or system variables.
   * Supports multi-environment behavior (DEV, UAT, PROD, TEST).

5. **Testing Layer** (`tests/`)

   * Unit tests and CLI integration tests.
   * 100% test coverage.
   * Fixtures for isolated testing.

### 8.2. Key Components

#### Caching

* Unicode name normalization and name cache building is expensive.
* CharFinder implements:

  * An **LRU cache** for normalized name lookup (`cached_normalize`).
  * A persistent **Unicode name cache** (`unicode_name_cache.json`).
  * Cached data can be cleared or rebuilt via API or CLI.

See: [docs/caching.md](docs/caching.md)

#### Environment Management

* CharFinder supports multiple runtime environments:

  * **DEV** (default)
  * **UAT**
  * **PROD**
  * **TEST** (auto-detected via `PYTEST_CURRENT_TEST`)

* Configuration priority chain:

  1. `DOTENV_PATH` override
  2. `.env` in project root
  3. System environment variables

* Verbose debug of `.env` resolution available via `MYPROJECT_DEBUG_ENV_LOAD=1`.

See: [docs/environment\_config.md](docs/environment_config.md)

#### Logging

* Centralized logging using `charfinder` logger.

* Features:

  * Rotating file handler (`logs/{ENV}/charfinder.log`)
  * Console handler with `--debug` and `--verbose` options
  * Multi-environment log filtering
  * Colorized CLI output

* Logger setup is shared between CLI and library.

See: [docs/logging\_system.md](docs/logging_system.md)


## 🧪 9. Testing

CharFinder has a comprehensive test suite covering core logic, CLI integration, caching, environment handling, and logging.

### Running Tests

Run the full test suite:

```bash
make test
```

Run only failed or last tests:

```bash
make test-fast
```

Run tests with coverage:

```bash
make coverage
```

Generate HTML coverage report:

```bash
make coverage-html
```

### Code Quality Enforcement

```bash
make lint-all
```

applys ruff formatting, ruff checking, and mypy statis type check.
It runs all of following commands:

#### Linting and Formatting

```bash
make lint-ruff
```

```bash
nake fmt
```

#### Static Type Checks

```bash
make type-check
```



CharFinder uses **pre-commit** to enforce code quality automatically on each commit.

Set up hooks:

```bash
make precommit
```

Manually run all hooks:

```bash
make precommit-run
```

Hooks include:

* Ruff linting
* MyPy type checking
* Black formatting check
* Check for common errors

### Coverage Policy

* Target: **100% coverage** on all Python files under `src/`.
* CLI integration tests cover all major CLI scenarios via `subprocess.run`.
* Logging behaviors, `.env` loading, and edge cases are all tested.

### Test Layers

* **Unit tests:** test core logic in isolation (core, caching, normalization, settings, utils).
* **CLI integration tests:** test full CLI entrypoint via subprocess.
* **Logging tests:** test rotating logging, suppression, environment filtering.
* **Settings tests:** test different `.env` and environment variable scenarios.

### Test Documentation

See [docs/unit\_test\_design.md](docs/unit_test_design.md) for detailed design of CharFinder's test architecture and testing strategies.



