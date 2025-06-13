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
