[![PyPI](https://img.shields.io/pypi/v/charfinder)](https://pypi.org/project/charfinder/)
[![Python](https://img.shields.io/pypi/pyversions/charfinder)](https://pypi.org/project/charfinder/)
[![License](https://img.shields.io/github/license/berserkhmdvhb/charfinder)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/charfinder/month)](https://pepy.tech/project/charfinder)
[![Tests](https://github.com/berserkhmdvhb/charfinder/actions/workflows/tests.yml/badge.svg)](https://github.com/berserkhmdvhb/charfinder/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/berserkhmdvhb/charfinder/badge.svg?branch=main)](https://coveralls.io/github/berserkhmdvhb/charfinder?branch=main)

# 🔎 charfinder

**charfinder** is a modern terminal and Python-based tool for searching and exploring Unicode characters by name — supporting both exact and advanced fuzzy matching — with Unicode normalization, efficient caching, structured logging.

Designed for both technical and non-technical users, charfinder enables reliable Unicode search in terminals, scripts, and applications. It can power developer workflows, automation scripts, data pipelines, and user-facing interfaces such as chatbots and messaging apps, while providing transparency and precise control over matching behavior.

---

## 📚 Table of Contents

1. [🎥 Demo Video](#-1-demo-video)
2. [✨ Features](#-2-features)
3. [📦 Project Structure](#3--project-structure)
   * [3.1 📂 Structure](#31--structure)
   * [3.2 🧱 Architecture](#32--architecture)
4. [🌐 What is Unicode?](#4--what-is-unicode)
5. [🎯 Exact and Fuzzy Match](#-5-exact-and-fuzzy-match)

   * [Matching Modes Overview](#matching-modes-overview)
   * [Available Fuzzy Algorithms](#available-fuzzy-algorithms)
   * [Aggregation Functions (Hybrid Mode)](#aggregation-functions-hybrid-mode)
   * [Combination Matrix](#combination-matrix)
   * [Matching Flow](#matching-flow)
   * [Normalization](#normalization)
6. [🚀 Usage](#6--usage)

   * [6.1 Installation](#61-installation)

     * [For Users](#for-users)
     * [For Developers](#for-developers)
   * [6.2 💻 CLI Usage](#62--cli-usage)
   * [6.3 🐍 Python Library Usage](#63--python-library-usage)
7. [🧱 Internals and Architecture](#7--internals-and-architecture)

   * [7.1 Architecture Overview](#71--architecture-overview)
   * [7.2 Key Components](#72--key-components)

     * [Caching](#caching)
     * [Environment Management](#environment-management)
     * [Logging](#logging)
8. [🧪 Testing](#8--testing)

   * [Running Tests](#running-tests)
   * [Code Quality Enforcement](#code-quality-enforcement)
   * [Coverage Policy](#coverage-policy)
   * [Test Layers](#test-layers)
9. [👨‍💼 Developer Guide](#9--developer-guide)

   * [🔨 Cloning & Installation](#--cloning--installation)
   * [🔧 Makefile Commands](#--makefile-commands)
   * [🗒️ Onboarding Tips](#--onboarding-tips)
10. [⚡ Performance](#10--performance)

    * [Key Optimizations](#key-optimizations)
    * [Benchmarks (Informal)](#benchmarks-informal)
    * [Profiling Tips](#profiling-tips)
    * [Future Improvements](#future-improvements)
11. [🚧 Limitations / Known Issues](#11--limitations--known-issues)

    * [Fuzzy Algorithms Scope](#fuzzy-algorithms-scope)
    * [Limitations for Embedding in APIs or External Applications](#limitations-for-embedding-in-apis-or-external-applications)
    * [UnicodeData.txt Updates](#unicodedatattxt-updates)
    * [Limitations of Matching Model](#limitations-of-matching-model)
    * [Known Issues](#known-issues)
    * [Embedding Checklist](#embedding-checklist)
12. [📖 Documentation](#12--documentation)
13. [🧾 License](#13--license)

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

### 💻 CLI Features

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

### 🐍 Python Library Usage

* Import and use core API:

  * `find_chars()` - yields formatted result rows.
  * `find_chars_raw()` - returns structured data (for scripting / JSON output).

* Fully type-annotated.

* No CLI dependencies required in library usage.

* Cross-ref: [docs/core\_logic.md](docs/core_logic.md).

### 🧪 Testability & Quality

* Code quality and enforcement:
  * `ruff` (format/lint), `mypy` (type-check)
   
* High test coverage.

* CLI tested via **subprocess integration tests**.

* Modular `conftest.py` with reusable fixtures.

* Clean `pytest` + `coverage` + `pre-commit` workflow.

* Cross-ref: [docs/unit\_test\_design.md](docs/unit_test_design.md).

### 📑 Modern Packaging & Tooling

* `pyproject.toml` based (PEP 621).

* GitHub Actions CI pipeline:

  * Python 3.10 to 3.13.
  * Lint (Ruff), type-check (MyPy), test, coverage.

* Easy publishing to PyPI.
  
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
│   ├── cache.py                     # Caching utilities
│   ├── constants.py                 # Constants and default values
│   ├── fuzzymatchlib.py             # Fuzzy matching algorithms
│   ├── settings.py                  # Environment/config management
│   ├── types.py                     # Shared type definitions
│   ├── py.typed                     # Marker for type-checking consumers
│   │
│   ├── cli/                         # CLI logic (modularized)
│   │   ├── __init__.py
│   │   ├── args.py                  # CLI argument definitions
│   │   ├── cli_main.py              # CLI main controller
│   │   ├── diagnostics.py           # CLI diagnostics output
│   │   ├── handlers.py              # CLI command handlers
│   │   └── parser.py                # CLI parser and argument preprocessing
│   │
│   ├── core/                        # Core Unicode search logic
│   │   ├── __init__.py
│   │   ├── core_main.py             # Public API functions (find_chars, etc.)
│   │   ├── matching.py              # Exact and fuzzy matching helpers
│   │   ├── name_cache.py            # Unicode name cache builder
│   │   └── unicode_data_loader.py   # UnicodeData.txt loader and parser
│   │
│   ├── utils/                       # Shared utilities
│       ├── __init__.py
│       ├── formatter.py             # Terminal and log message formatting
│       ├── logger_helpers.py        # Custom logging helpers
│       ├── logger_setup.py          # Logging setup and teardown
│       ├── logger_styles.py         # Styling for log output
│       └── normalizer.py            # Unicode normalization utility
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

See section [Internals and Architecture](#9-internals-and-architecture), and following documentatoins:

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


See following:
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

| Match Path             | Exact Match Mode        | Fuzzy Match Mode | Fuzzy Algorithms                        | Aggregation Function   |
| ---------------------- | ----------------------- | ---------------- | --------------------------------------- | ---------------------- |
| Exact only             | substring / word-subset | -                | -                                       | -                      |
| Exact → Fuzzy fallback | substring / word-subset | single           | sequencematcher, rapidfuzz, levenshtein | -                      |
| Exact → Fuzzy fallback | substring / word-subset | hybrid           | Combination of above                    | mean, median, max, min |

**Notes**

- Exact match is always attempted first. If `--fuzzy` is enabled and no exact match is found, fuzzy matching is attempted ("fallback to fuzzy").
- "Fuzzy only" mode is not yet directly supported but may be added in future for advanced use cases.
- The `--exact-match-mode` controls the exact match phase:
  - `substring` → substring matching
  - `word-subset` (default) → all words in query must be present in target name
- The `--fuzzy-match-mode` and `--fuzzy-algo` control the fuzzy phase.
- Hybrid mode combines multiple algorithm scores using the selected aggregation function.

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



See
* [docs/matching.md](docs/matching.md)
* [docs/core\_logic.md](docs/core_logic.md)

---

## 6. 🚀 Usage

The following usage guide shows how to install, run, and integrate CharFinder both via its command-line interface (CLI) and as a Python library. Whether you are an end user, developer, or automator, CharFinder is designed to fit seamlessly into your workflow.

### 6.1 Installation

#### 👤 For Users

##### PyPI (Recommended)

```bash
pip install charfinder
```

##### GitHub (Development Version)

```bash
pip install git+https://github.com/berserkhmdvhb/charfinder.git
```

#### 👨‍💻 For Developers

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

### 6.2 💻 CLI Usage

CharFinder provides a CLI for exploring Unicode characters.

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
| `--format`           | Choose output format: `text` or `json`                                       |
| `--verbose`, `-v`    | Enable verbose console output                                         |
| `--debug`            | Enable diagnostic output                                              |
| `--version`          | Show version                                                          |

#### Advanced CLI Tips

* Use `--fuzzy` and `--threshold` for typo tolerance.
* Use `--format json` for scripting and automation.
* Enable diagnostics with `--debug` or by setting `CHARFINDER_DEBUG_ENV_LOAD=1`.

See [docs/cli\_architecture.md](docs/cli_architecture.md).

---

### 6.3 🐍 Python Library Usage

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

See [docs/core\_logic.md](docs/core_logic.md).

---

## 7. 🧱 Internals and Architecture

CharFinder is designed with a **layered, modular architecture** to ensure clean separation of concerns, testability, and reuse across CLI and Python library usage.

### 7.1. Architecture Overview

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

### 7.2. Key Components

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


## 🧪 8. Testing

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
make fmt
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

See [docs/unit\_test\_design.md](docs/unit_test_design.md)

---

### 👨‍💻 9. Developer Guide

#### 🔨 Cloning & Installation

**For Users:**

```bash
git clone https://github.com/berserkhmdvhb/charfinder.git
cd charfinder
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
make install
```

**For Developers (Contributors):**

```bash
git clone https://github.com/berserkhmdvhb/charfinder.git
cd charfinder
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
make develop
```

#### 🔧 Makefile Commands

| Command                                     | Description                                                  |
| ------------------------------------------- | ------------------------------------------------------------ |
| `make install`                              | Install the package in editable mode                         |
| `make develop`                              | Install with all dev dependencies                            |
| `make fmt`                                  | Auto-format code using Ruff                                  |
| `make fmt-check`                            | Check code formatting (dry run)                              |
| `make lint-ruff`                            | Run Ruff linter                                              |
| `make type-check`                           | Run MyPy static type checker                                 |
| `make lint-all`                             | Run formatter, linter, and type checker                      |
| `make lint-all-check`                       | Dry run: check formatting, lint, and types                   |
| `make test`                                 | Run all tests using Pytest                                   |
| `make test-file FILE=...`                   | Run a single test file or keyword                            |
| `make test-file-function FILE=... FUNC=...` | Run a specific test function                                 |
| `make test-fast`                            | Run only last failed tests                                   |
| `make test-coverage`                        | Run tests and show terminal coverage summary                 |
| `make test-coverage-xml`                    | Run tests and generate XML coverage report                   |
| `make test-cov-html`                        | Run tests with HTML coverage report and open it              |
| `make test-coverage-rep`                    | Show full line-by-line coverage report                       |
| `make test-coverage-file FILE=...`          | Show coverage for a specific file                            |
| `make check-all`                            | Run format-check, lint, and full test suite                  |
| `make test-watch`                           | Auto-rerun tests on file changes                             |
| `make precommit`                            | Install pre-commit hook                                      |
| `make precommit-check`                      | Dry run all pre-commit hooks                                 |
| `make precommit-run`                        | Run all pre-commit hooks                                     |
| `make env-check`                            | Show Python and environment info                             |
| `make env-debug`                            | Show debug-related env info                                  |
| `make env-clear`                            | Unset CHARFINDER\_\* and DOTENV\_PATH environment variables  |
| `make env-show`                             | Show currently set CHARFINDER\_\* and DOTENV\_PATH variables |
| `make env-example`                          | Show example env variable usage                              |
| `make dotenv-debug`                         | Show debug info from dotenv loader                           |
| `make safety`                               | Check dependencies for vulnerabilities                       |
| `make check-updates`                        | List outdated pip packages                                   |
| `make check-toml`                           | Check pyproject.toml for syntax validity                     |
| `make clean-logs`                           | Remove DEV log files                                         |
| `make clean-cache`                          | Remove cache files                                           |
| `make clean-coverage`                       | Remove coverage data                                         |
| `make clean-build`                          | Remove build artifacts                                       |
| `make clean-pyc`                            | Remove .pyc and **pycache** files                            |
| `make clean-all`                            | Remove all build, test, cache, and log artifacts             |
| `make build`                                | Build package for distribution                               |
| `make publish-test`                         | Upload to TestPyPI                                           |
| `make publish-dryrun`                       | Validate and simulate TestPyPI upload (dry run)              |
| `make publish`                              | Upload to PyPI                                               |
| `make upload-coverage`                      | Upload coverage report to Coveralls                          |

#### 📝 Onboarding Tips

* Always use `make develop` to install full dev dependencies.
* Run `make check-all`  before pushing changes, or equivalently, run `make lint-all-check` and `make test-coverage`.
* Validate `.env` loading with `make dotenv-debug`.

---

### ⚡ 10. Performance

`charfinder` is designed with a focus on speed, efficiency, and responsiveness—even when processing the entire Unicode space (1.1M+ code points).

#### Key Optimizations

* **Unicode Name Caching**

  * The Unicode name cache is built once and stored as a local JSON file.
  * On subsequent runs, the cache is loaded instantly, enabling fast lookups.

* **Normalization Caching**

  * The `cached_normalize()` function uses an LRU cache to avoid redundant Unicode normalization calls.
  * This significantly speeds up matching, especially for fuzzy modes where many comparisons are performed.

* **Matching Optimizations**

  * Exact match mode uses fast `in` and set operations.
  * Fuzzy match mode supports multiple optimized algorithms:

    * `rapidfuzz` (fastest)
    * `Levenshtein` (optimized C extension)
    * `SequenceMatcher` (Python stdlib baseline)

* **Efficient CLI Output**

  * Result rows are streamed lazily via generators.
  * Logging and console output are buffered to minimize I/O overhead.

#### Benchmarks (Informal)

| Query                   | Match Mode      | Time (1st run) | Time (cached) |
| ----------------------- | --------------- | -------------- | ------------- |
| `snowman`               | exact           | \~40ms         | \~5ms         |
| `snwmn` (fuzzy)         | fuzzy+rapidfuzz | \~150ms        | \~25ms        |
| `grnning face` (hybrid) | fuzzy+hybrid    | \~200ms        | \~35ms        |

*Tests run on Python 3.12, macOS M2 Pro, full Unicode set.*

#### Profiling Tips

* To profile CLI runs:

  ```bash
  python -m cProfile -m charfinder -q heart --fuzzy
  ```
* To profile library calls:

  ```python
  import cProfile
  cProfile.run("list(find_chars('heart', fuzzy=True))")
  ```

#### Future Improvements

* Smarter pre-filtering to skip unrelated blocks.
* Parallelization of fuzzy matching (via joblib or multiprocessing).
* Optional faster UnicodeData loaders (binary format).
* Support for custom user-provided fuzzy match algorithms (plugin architecture)

---

## 🚧 11. Limitations / Known Issues

While **CharFinder** is a robust and flexible tool, it is important to be aware of the following current limitations and known constraints:

### 🔹 Fuzzy Algorithms Scope

* Currently, **only three fuzzy matching algorithms are supported**:

  * `sequencematcher` (difflib)
  * `rapidfuzz`
  * `levenshtein`

* These are selected for **performance and compatibility** reasons.

* Extending the system to support **custom or additional fuzzy algorithms** (such as Jaro-Winkler, Damerau-Levenshtein, etc.) would require modifying the internal `fuzzymatchlib.py` module and registering the algorithm accordingly.

* For advanced needs, contributions and PRs to add more algorithms are welcome (see [Contributing](#contributing)).

### 🔹 Limitations for Embedding in APIs or External Applications

* While **CharFinder** is designed as a library and CLI, embedding it directly in real-time, high-throughput applications (e.g. messaging apps, chatbots, servers with strict latency constraints) requires careful consideration:

  * The Unicode name cache (`name_cache`) is built at runtime and stored in a JSON file by default:

    * Disk I/O during first run may introduce latency.
    * Caching in-memory for each process is recommended.

  * To optimize embedding scenarios, **you should pre-build the cache once and inject it** into your application process:

    * You can call `build_name_cache()` and persist the result.
    * Later you can pass this cache as the `name_cache` argument to `find_chars()` or `find_chars_raw()`.

  * Without injecting the cache, embedding **may trigger redundant cache building per process**, which is inefficient.

  * The internal cache is not optimized for **distributed or multi-process sharing** out of the box.

    * For large-scale distributed use, consider pre-building the cache and distributing it to your workers.

* The `print_dotenv_debug()` and CLI-based diagnostics output are primarily designed for **terminal users and developers**.

  * If embedding in an app, you may want to adjust or silence these outputs.

### 🔹 UnicodeData.txt Updates

* The project fetches Unicode names from **UnicodeData.txt**.

  * The URL is configurable, but this file should be kept reasonably up-to-date with the Unicode standard.
  * If Unicode evolves (new characters added, names change), ensure you re-run cache building.

* There is no automatic background refresh of the UnicodeData.txt or cache. Manual rebuild is required.

### 🔹 Limitations of Matching Model

* **Exact matching** is limited to:

  * `substring`
  * `word-subset` (word bag subset match)

* **Fuzzy matching**:

  * Currently supports single-algorithm or hybrid scoring with predefined aggregation functions (`mean`, `median`, `max`, `min`).

* **Alternate names**:

  * The alternate names used are limited to what is provided in **UnicodeData.txt field 10** (as parsed by `unicode_data_loader.py`).
  * Other aliases (e.g. from CLDR or additional datasets) are not yet supported.

### 🔹 Known Issues

* On certain platforms, first-time runs may take several seconds while the cache is built.

  * This is expected and logged.

* Unicode normalization is applied uniformly, but in rare cases **visual vs. textual similarity may differ**, especially for symbols.

* There is no support yet for **interactive fuzzy tuning** or learning-based matching (future idea).

* Matching performance scales linearly with the size of the Unicode range:

  * On typical machines, full search takes < 1s.
  * On constrained environments, this may vary.

### 🔹 Embedding Checklist

If you intend to embed CharFinder in a chatbot, server, or app:

* ✅ Pre-build and inject the name cache.
* ✅ Avoid using CLI components or direct terminal output.
* ✅ Optionally silence verbose logs.
* ✅ Test for performance in your target environment.
* ✅ Monitor UnicodeData.txt changes periodically.

---

**Summary:**

CharFinder works well as a CLI and library tool, but for embedding in latency-sensitive or distributed apps, extra precautions are required. The matching pipeline is currently static and not model-based; this is a trade-off between **explainability, reproducibility, and simplicity**.

Advanced embedding features (pre-built cache injection, multi-process sharing, additional algorithm hooks) are planned in future versions.


---

## 📖 12. Documentation

This project includes detailed internal documentation to help both developers and advanced users understand its design, architecture, and internals.

The following documents are located in the [`docs/`](docs/) directory:

| Document                                                    | Description                                                                                                         |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [`cli_architecture.md`](docs/cli_architecture.md)           | Overview of CLI modules, their flow, entry points, and command routing logic.                                       |
| [`core_logic.md`](docs/core_logic.md)                       | Core logic and library API (`find_chars`, `find_chars_raw`): processing rules, transformations, architecture.       |
| [`debug_diagnostics.md`](docs/debug_diagnostics.md)         | Debug and diagnostic output systems: `--debug`, `CHARFINDER_DEBUG_ENV_LOAD`, dotenv introspection.                  |
| [`env-logging-scenarios.md`](docs/env-logging-scenarios.md) | End-to-end `.env` and logging scenarios, edge cases, fallback resolution.                                           |
| [`environment_config.md`](docs/environment_config.md)       | Detailed explanation of environment variable handling and `.env` resolution priorities.                             |
| [`logging_system.md`](docs/logging_system.md)               | Logging architecture: setup, structured logging, rotating files, and environment-based folders.                     |
| [`unit_test_design.md`](docs/unit_test_design.md)           | Testing layers: unit tests, CLI integration tests, coverage strategy.                                               |
| [`normalization.md`](docs/normalization.md)                 | Unicode normalization explained: what is used (`NFC`), why, and implications for search.                            |
| [`matching.md`](docs/matching.md)                           | Detailed explanation of exact and fuzzy matching algorithms and options. Includes mode combinations and flowcharts. |
| [`caching.md`](docs/caching.md)                             | Explanation of cache layers: Unicode name cache, `cached_normalize()`, performance considerations.                  |
| [`roadmap.md`](docs/roadmap.md)                             | Future plans and enhancements.                                                                                      |

> These documents are designed to serve both as **developer onboarding** material and **technical audit** documentation.

---

## 🧾 13. License

MIT License © 2025 [berserkhmdvhb](https://github.com/berserkhmdvhb)

