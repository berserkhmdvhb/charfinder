[![PyPI](https://img.shields.io/pypi/v/charfinder)](https://pypi.org/project/charfinder/)
[![Python](https://img.shields.io/pypi/pyversions/charfinder)](https://pypi.org/project/charfinder/)
[![License](https://img.shields.io/github/license/berserkhmdvhb/charfinder)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/charfinder/month)](https://pepy.tech/project/charfinder)
[![Tests](https://github.com/berserkhmdvhb/charfinder/actions/workflows/tests.yml/badge.svg)](https://github.com/berserkhmdvhb/charfinder/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/coveralls/github/berserkhmdvhb/charfinder/main?cacheSeconds=300)](https://coveralls.io/github/berserkhmdvhb/charfinder?branch=main)

# 🔎 charfinder

**charfinder** is a modern terminal and Python-based tool for searching and exploring Unicode characters by name — supporting both exact and advanced fuzzy matching — with Unicode normalization, efficient caching, structured logging.

Designed for both technical and non-technical users, CharFinder enables reliable Unicode search in terminals, scripts, automation workflows, and applications. It offers transparency and precise control over matching behavior, making it suitable for developer tooling, data pipelines, chatbots, and messaging interfaces.

---

## 📚 Table of Contents

1. [🎥 Demo Video](#-1-demo-video)
2. [✨ Features](#-2-features)
3. [📦 Project Structure](#3--project-structure)
   * [3.1 📂 Structure](#31--structure)
   * [3.2 🧱 Architecture](#32--architecture)
4. [🌐 Unicode and Normalization](#4--unicode--normalization)
5. [🎯 Matching Engine (Exact & Fuzzy)](#5--matching-engine-exact--fuzzy)
6. [🚀 Usage](#6--usage)

   * [6.1 Installation](#61-installation)
   * [6.2 💻 CLI Usage](#62--cli-usage)
     * [Demo](#demo) 
   * [6.3 🐍 Python Library Usage](#63--python-library-usage)
7. [🧱 Internals and Architecture](#7--internals-and-architecture)

   * [7.1 Architecture Overview](#71-architecture-overview)
   * [7.2 Key Components](#72-key-components)

     * [Caching](#-caching-1)
     * [Environment Management](#%EF%B8%8F-environment-management)
     * [Logging](#-logging-1)
8. [🧪 Testing](#-8-testing)

   * [Running Tests](#running-tests)
   * [Code Quality Enforcement](#code-quality-enforcement)
   * [Coverage Policy](#coverage-policy)
   * [Test Layers](#test-layers)
9. [👨‍💼 Developer Guide](#-9-developer-guide)

   * [🔨 Cloning & Installation](#-cloning--installation)
   * [🔧 Makefile Commands](#-makefile-commands)
   * [🗒️ Onboarding Tips](#-onboarding-tips)
10. [⚡ Performance](#-10-performance)
11. [🚧 Limitations and Known Issues](#-11-limitations-and-known-issues)
12. [📖 Documentation](#-12-documentation)
13. [🧾 License](#-13-license)

---

# 🎥 1. Demo Video

https://github.com/user-attachments/assets/e19b0bbd-d99b-401b-aa29-0092627f376b

To see another demo of CLI usage, see subsection [Demo](#demo)

---

## ✨ 2. Features

CharFinder is a **feature-rich Unicode character search tool**, designed for both **CLI** and **Python library** usage. It combines exact and fuzzy matching with fast caching, robust environment management, and beautiful CLI output.

### 🔍 Unicode Character Search

* Search Unicode characters by name:
  * **Exact match** (`substring` or `word_subset`)
  * **Fuzzy match** with configurable thresholds and algorithms

* Supported fuzzy algorithms:
  * `simple_ratio` — SequenceMatcher-based (from `difflib`)
  * `normalized_ratio` — Normalized variant of `simple_ratio`
  * `levenshtein_ratio` — Based on `python-Levenshtein`
  * `token_sort_ratio` — Word-order invariant (from `rapidfuzz`)
  * `hybrid_score` — Aggregates multiple algorithms

* Hybrid fuzzy matching:
  * Combines multiple algorithms using an aggregation function: `mean`, `median`, `max`, or `min`

### 📉 Unicode Normalization

* All matching is performed after Unicode normalization.
* Matching is case-insensitive, accent-insensitive, and format-insensitive
* Input and character names are normalized using configurable Unicode profiles (`--normalization-profile`)
* Alternate names (from `UnicodeData.txt`) are supported

### 🔄 Caching

* Unicode name cache:
  * Built on first run
  * Stored as a local JSON file for fast reuse

* LRU cache:
  * Internal normalization results are LRU-cached for performance

### 📊 Logging

* Rotating file logs under `logs/{ENV}/`
* Console logging:
  * `INFO` level by default
  * `DEBUG` level with `--debug`
* Each log record includes the current **environment** (`DEV`, `UAT`, `PROD`)
* Logging is modular and test-friendly

### 🔧 Environment-aware Behavior

* `.env` support with layered resolution logic
* Environment-specific behavior:
  * Log directory changes by environment
  * Test mode activates `.env.test`

📚 See [`config_environment.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/config_environment.md)

### 💻 CLI Features

* Rich CLI with **argcomplete** tab completion

* Color output:
  * Modes: `auto`, `always`, `never`
  * Colors used for result rows, headers, and logs

* Advanced CLI options:

  * Matching behavior:
    * `--fuzzy` — Enable fuzzy matching
    * `--threshold` — Set similarity threshold (0.0–1.0)
    * `--fuzzy-algo` — Select fuzzy algorithm (e.g., `token_sort_ratio`)
    * `--fuzzy-match-mode` — Choose fuzzy match mode: `first`, `all`, or `hybrid`
    * `--hybrid-agg-fn` — Set aggregation function: `mean`, `median`, `min`, or `max`
    * `--exact-match-mode` — Specify exact match logic: `word_subset` or `substring`

  * Output control:
    * `--color` — Control color output: `auto`, `always`, or `never`
    * `--verbose` — Display formatted results in the console
    * `--debug` — Enable full diagnostics: dotenv resolution, config state, match algorithms and scores

* Detailed CLI help with examples

📚 See [`cli_architecture.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/cli_architecture.md) and for examples see the subsection [demo](#demo)

### 🐍 Python Library Usage

* Import and use the core API:
  * `find_chars()` — Yields formatted result rows
  * `find_chars_raw()` — Returns structured data (for scripting / JSON)

* Fully type-annotated
* CLI dependencies are not required for library usage

📚 See [`core_logic.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/core_logic.md)

### 🧪 Testability & Quality

* Code quality enforcement:
  * `ruff` (lint & format), `mypy` (type-check)

* High test coverage
* CLI tested via **subprocess integration tests**
* Modular `conftest.py` with reusable fixtures
* Clean `pytest` + `coverage` + `pre-commit` workflow

📚 See [`unit_test_design.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/unit_test_design.md)

### 📑 Modern Packaging & Tooling

* `pyproject.toml`-based (PEP 621)
* GitHub Actions CI pipeline:
  * Python 3.10 to 3.13
  * Lint (Ruff), type-check (MyPy), test, coverage
* Easy publishing to PyPI

---

## 3. 📦 Project Structure

CharFinder follows a **clean, layered architecture** to ensure separation of concerns, maintainability, and testability.

The project is structured for ease of contribution and for flexible usage as both:

* A **CLI tool** (`charfinder` command).
* An **importable Python library**.

### 3.1 📂 Structure

### 3.1 Structure

The project is organized as follows:

```
charfinder/
├── .github/workflows/               # GitHub Actions CI pipeline
├── .pre-commit-config.yaml          # Pre-commit hooks
├── publish/                         # Sample config for PyPI/TestPyPI
├── .env.sample                      # Sample environment variables
├── LICENSE.txt
├── Makefile                         # Automation tasks
├── MANIFEST.in                      # Files to include in sdist
├── pyproject.toml                   # PEP 621 build + dependencies
├── README.md                        # Project documentation (this file)
├── docs/                            # Detailed documentation (.md files)
├── data/                            # Downloaded UnicodeData and cache
│   ├── UnicodeData.txt              # Standard Unicode name definitions
│   └── cache/                       # Local character name cache
├── src/charfinder/                  # Main package code
│   ├── __init__.py                  # Package version marker
│   ├── __main__.py                  # Enables `python -m charfinder`
│   ├── fuzzymatchlib.py             # Fuzzy matching algorithm registry
│   ├── validators.py                # Input validation logic
│   │
│   ├── cli/                         # CLI logic (modularized)
│   │   ├── __init__.py
│   │   ├── args.py                  # CLI argument definitions
│   │   ├── cli_main.py              # CLI main entry point
│   │   ├── diagnostics.py           # Diagnostics and debugging info
│   │   ├── diagnostics_match.py     # Match strategy explanation
│   │   ├── handlers.py              # CLI command handlers
│   │   ├── parser.py                # CLI parser and argument preprocessing
│   │   └── utils_runner.py          # CLI runner and echo utilities
│   │
│   ├── config/                      # Configuration and constants
│   │   ├── __init__.py
│   │   ├── aliases.py               # Alias mappings for fuzzy algorithms
│   │   ├── constants.py             # Default values and valid options
│   │   ├── settings.py              # Environment/config management
│   │   └── types.py                 # Shared type definitions
│   │
│   ├── core/                        # Core Unicode search logic
│   │   ├── __init__.py
│   │   ├── core_main.py             # Public API entry point for core logic
│   │   ├── finders.py               # Output routing and formatting
│   │   ├── handlers.py              # Search coordination and config builder
│   │   ├── matching.py              # Exact and fuzzy matching logic
│   │   ├── name_cache.py            # Unicode name cache builder
│   │   └── unicode_data_loader.py   # UnicodeData.txt loader and parser
│   │
│   ├── utils/                       # Shared utilities
│   │   ├── __init__.py
│   │   ├── formatter.py             # Terminal and log formatting
│   │   ├── logger_helpers.py        # Custom logging helpers
│   │   ├── logger_setup.py          # Logger setup/teardown
│   │   ├── logger_styles.py         # Logging color/style definitions
│   │   └── normalizer.py            # Unicode normalization logic
│
└── tests/                           # Unit, integration, and manual tests
    ├── cli/                         # CLI interface and argument handling tests
    ├── config/                      # Tests for constants, settings, types, aliases
    ├── core/                        # Core Unicode search, cache, and matching logic
    ├── utils/                       # Terminal formatting, normalization, and logger utilities
    ├── helpers/                     # Internal testing utilities (not test files)
    ├── manual/                      # Manual testing and usage examples
    │   └── demo.ipynb               # Interactive demo notebook
    ├── test_fuzzymatchlib.py        # Tests for fuzzy algorithm registry and scoring
    ├── test_validators.py           # Input validation and config resolution logic
    └── conftest.py                  # Shared test fixtures and environment isolation
```



### 3.2 🧱 Architecture

CharFinder implements a **layered architecture** with clear boundaries:

📚 See section [Internals and Architecture](#7--internals-and-architecture), and following documentatoins:

* [docs/cli\_architecture.md](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/cli_architecture.md)
* [docs/core\_logic.md](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/core_logic.md)
* [docs/environment\_config.md](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/config_environment.md)
* [docs/logging\_system.md](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/logging_system.md)
* [docs/caching.md](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/caching.md)

---
## 4. 🌐 Unicode & Normalization

**Unicode** is the global standard for encoding text, defining unique code points for every letter, symbol, emoji, and script. It enables CharFinder to search across more than 140,000 characters—covering everything from Latin letters to CJK ideograms and emojis.

### Why It Matters for CharFinder

* ✅ **Multilingual coverage**: Supports scripts from all major languages and symbol sets.
* ✅ **Emoji and symbol support**: All emoji and symbols are part of Unicode and fully searchable.
* ✅ **Alternate name discovery**: CharFinder indexes official names *and* alternate names (from field 10 of `UnicodeData.txt`) to support queries like `"underscore"`, `"slash"`, or `"period"`.

---

### 🔄 Normalization
### 🔄 Normalization

Characters that look the same can be encoded in different ways. For example:

* `é` (U+00E9) vs. `é` (`e` + U+0301) are visually identical but distinct Unicode sequences.

To ensure consistent matching, CharFinder applies **Unicode normalization, case folding, whitespace cleanup, and optional accent/diacritic stripping** depending on the selected profile.

You can customize this behavior using the `--normalization-profile` CLI argument:

| Profile      | Unicode Form | Strip Accents | Collapse Whitespace | Remove Zero-Width | Transformation Summary                               |
| ------------ | ------------ | ------------- | ------------------- | ----------------- | ---------------------------------------------------- |
| `raw`        | —            | ❌             | ❌                   | ❌                 | No changes                                           |
| `light`      | NFC            | ❌             | ✅                   | ❌                 | Trim + collapse spaces + `.upper()`                  |
| `medium`     | NFKD         | ❌             | ✅                   | ❌                 | `light` + Unicode normalization                      |
| `aggressive` | NFC, NFKD         | ✅             | ✅                   | ✅                 | `medium` + remove diacritics + zero-width characters |

The default profile is **`aggressive`**, which offers the most robust matching by removing visual and encoding differences.

---

#### 🔍 Normalization in Action

| Input                   | Codepoints                           | Normalized | Matches?     |
| ----------------------- | ------------------------------------ | ---------- | ------------ |
| `café`                  | `U+0063 U+0061 U+0066 U+00E9`        | `CAFE`     | ✅            |
| `café`                 | `U+0063 U+0061 U+0066 U+0065 U+0301` | `CAFE`     | ✅            |
| `CAFÉ`                  | `U+0043 U+0041 U+0046 U+00C9`        | `CAFE`     | ✅            |
| `CAFÉ`                 | `U+0043 U+0041 U+0046 U+0045 U+0301` | `CAFE`     | ✅            |
| `𝒸𝒶𝓻é` (italic math) | `U+1D4B8 U+1D4B6 U+1D4FB U+00E9`     | `CARE`     | ✅ (fallback) |
| `ｃａｆｅ́` (fullwidth)     | `U+FF43 U+FF41 U+FF46 U+FF45 U+0301` | `CAFE`     | ✅ (folded)   |

Even though the second input uses a decomposed form (`e` + combining acute), CharFinder normalizes and folds it to ensure a stable match.

---

### 🧪 Terminal Example with Emoji

CharFinder correctly matches Unicode emoji and symbols. For example:

![ex6](https://github.com/user-attachments/assets/e7c781cf-48b1-4e93-b1d6-58e0d5c29d20)

> Note: Composite emoji like `👩‍💻` (woman technologist) are grapheme clusters, not individual Unicode code points, and are not listed in `UnicodeData.txt`. CharFinder focuses on official single-codepoint characters.

📚 See [`unicode_normalization.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/unicode_normalization.md)


---

## 5. 🎯 Matching Engine (Exact + Fuzzy)

CharFinder uses a layered and configurable matching strategy to identify Unicode characters by name. It starts with **exact matching** for speed and precision, then optionally falls back to **fuzzy matching** if no exact hits are found or if `--prefer-fuzzy` is enabled.

### 🔹 Exact Matching

* Fast string comparisons using two match modes `substring` or `word-subset`.
* Controlled via `--exact-match-mode` (default: `word-subset`).
* Ideal for full or partial queries that directly appear in character names.

### 🔸 Fuzzy Matching

Fuzzy matching recovers from typos, partial input, or scrambled tokens. It supports following match modes:

* **Single-algorithm mode** (`--fuzzy-match-mode=single`): uses the algorithm specified by `--fuzzy-algo` (e.g., `token_subset_ratio`, `token_sort_ratio`, `levenshtein_ratio`, etc.)
* **Hybrid mode** (`--fuzzy-match-mode=hybrid`): combines multiple algorithms using weighted scores and an aggregation function (`mean` \[default], `median`, `max`, `min`)
* Controlled via `--fuzzy-match-mode` (default: `hybrid`).
#### Fuzzy control options:

* `--fuzzy`, `--prefer-fuzzy` — enable fallback or hybrid behavior
* `--fuzzy-algo` — select algorithm for single mode
* `--fuzzy-match-mode {single, hybrid}` — control fuzzy strategy
* `--threshold` — set minimum similarity score

> Matching behavior can also be influenced by environment variables. See [sample.env](https://github.com/berserkhmdvhb/charfinder/blob/main/sample.env)

### ⚙️ Normalization

Matching is applied after Unicode normalization, which includes case folding, accent removal, and Unicode normalization. This is configurable via `--normalization-profile`.

📚 See [`matching.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/matching.md) for full logic, algorithm details, and internal representation.

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

#### 👨‍💼 For Developers

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

#### CLI Options

| Option                   | Description                                                                                           |
|--------------------------|-------------------------------------------------------------------------------------------------------|
| `-q`, `--query`          | Provide search query as an option (alternative to positional query)                                   |
| `--fuzzy`                | Enable fuzzy search if no exact matches are found                                                     |
| `--prefer-fuzzy`         | Include fuzzy results even if exact matches are found (hybrid mode)                                   |
| `--threshold`            | Set fuzzy match threshold (0.0 to 1.0); applies to all algorithms                                     |
| `--fuzzy-algo`           | Select fuzzy algorithm: `token_sort_ratio` (default), `simple_ratio`, `normalized_ratio`,  `levenshtein`|
| `--fuzzy-match-mode`     | Fuzzy match mode: `single` (default), `hybrid`                                                        |
| `--hybrid-agg-fn`        | Aggregation function for hybrid mode: `mean` (default), `median`, `max`, `min`                        |
| `--exact-match-mode`     | Exact match strategy: `word-subset` (default), `substring`                                            |
| `--normalization-profile`| Normalization level: `aggressive` (default), `medium`, `light`, `raw`                                 |
| `--format`               | Output format: `text` (default) or `json`                                                             |
| `--color`                | Color output mode: `auto` (default), `always`, `never`                                                |
| `--show-score`           | Display match scores alongside results (enabled by default for JSON output)                           |
| `-v`, `--verbose`        | Enable terminal output (stdout/stderr); defaults to enabled in CLI, disabled in tests                 |
| `--debug`                | Show detailed diagnostics, including config, strategy, and environment                                |
| `--version`              | Show installed version of CharFinder                                                                  |



#### Advanced CLI Tips

* Use `--fuzzy` and `--threshold` for typo tolerance.
* Use `--format json` for scripting and automation.
* Enable diagnostics with `--debug` or by setting `CHARFINDER_DEBUG_ENV_LOAD=1`.


#### Demo

**Basic Example**
![ex1](https://github.com/user-attachments/assets/53e7770f-cb14-4ba7-8157-bc0eeacc19f6)

**Usage of `--verbose` or `-v` flag**

![ex2](https://github.com/user-attachments/assets/ce9914d5-a75a-4fa1-8a84-4eda2c5c6988)


**Usage of `--debug` for diagnostics**

![ex3](https://github.com/user-attachments/assets/bd4b9bd5-1d48-468a-8002-b05dc4b04277)


**Fuzzy Match Example**

![ex4](https://github.com/user-attachments/assets/a74ff5c3-0442-4309-bf52-8ef3824ae1bc)


**Usage `--format` to export JSON Output**

![ex5](https://github.com/user-attachments/assets/2db50733-3e13-4e4e-bc67-6b35884a625b)



📚 See [`cli_architecture.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/cli_architecture.md).

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

📚 See [`core_logic.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/core_logic.md).

---

## 7. 🧱 Internals and Architecture

CharFinder is built with a **layered, modular architecture** designed for clarity, testability, and extensibility. It supports robust CLI interaction and Python API usage.

### 7.1 Architecture Overview

The system is structured into clearly defined layers:

#### 1. **Core Logic Layer** (`core/`)

* Implements the core Unicode search engine: exact/fuzzy matching, scoring, and normalization.
* Fully decoupled from CLI and formatting logic.
* Key modules:

  * `finders.py` — main search orchestrator
  * `matching.py` — scoring logic for fuzzy and exact matches, uses matching library `fuzzymatchlib.py`
  * `name_cache.py` — Unicode name caching, loading, and saving
  * `unicode_data_loader.py` — parses and validates `UnicodeData.txt` and alternate names


📚 See [`core_logic.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/core_logic.md), [`matching.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/matching.md)

#### 2. **Finder API Layer** (`core/core_main.py`)

* Exposes public APIs: `find_chars()`, `find_chars_with_info()`, etc.
* Orchestrates validation, normalization, and config setup
* Consumed by CLI and external Python usage

#### 3. **CLI Layer** (`cli/`)

* Argument parsing (`args.py`, `parser.py`)
* Execution and output routing (`cli_main.py`, `handlers.py`)
* Output formatting (`formatter.py`, `utils_runner.py`)
* Fully testable and modular CLI engine

📚 See [`cli_architecture.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/cli_architecture.md)

#### 4. **Diagnostics Layer** (`cli/diagnostics.py`, `cli/diagnostics_match.py`)

* Provides structured debug output for:

  * Matching decisions, fallback logic, algorithm insights
* Activated via `--debug` or `CHARFINDER_DEBUG_ENV_LOAD=1`

📚 See [`debug_diagnostics.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/debug_diagnostics.md)

#### 5. **Utilities Layer** (`utils/`)

* Shared helpers:

  * `normalizer.py` — normalization, folding, and caching
  * `logger_helpers.py`, `logger_setup.py` — terminal and file-based logging utilities
  * `formatter.py`, `logger_styles.py` — console output styling

#### 6. **Configuration Layer** (`config/`)

* Centralized configuration:

  * `settings.py` — dotenv loading, environment mode detection, paths, log config
  * `constants.py` — global constant values (defaults, exit codes, env var names)
  * `types.py` — shared types and protocols for core and CLI usage
  * `aliases.py` — fuzzy algorithm aliases and canonical name resolution

  📚 See [`config_constants.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/config_constants.md), [`config_environment.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/config_environment.md),  [`config_types_protocols.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/config_types_protocols.md)

#### 7. **Validation Layer** (`validators.py`)

* Core + CLI shared validation
* Ensures consistent input handling:

  * Fuzzy algorithm names, match modes, thresholds, color modes
  * CLI/environment/default priority resolution

📚 See [`validators.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/validators.md)

---

### 7.2 Key Components

#### 🔁 Caching

CharFinder uses layered caching:

* **In-Memory**:

  * `cached_normalize()` — memoizes normalization results for performance

* **Persistent**:

  * `unicode_name_cache.json` stores normalized character name mappings
  * Auto-rebuilt from `UnicodeData.txt` + alternates if missing or outdated

📚 See [`caching.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/caching.md)

---

#### ⚙️ Environment Management

Supports predictable, override-friendly config loading:

* Runtime modes: `DEV`, `UAT`, `PROD`, `TEST`
* Load order:

  1. `DOTENV_PATH` if explicitly set
  2. `.env` from project root
  3. Fallback to system environment

→ Enable `CHARFINDER_DEBUG_ENV_LOAD=1` for detailed trace

📚 See [`config_environment.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/config_environment.md)

---

#### 📋 Logging

Flexible logging system supports development, testing, and production:

* **Rotating file logs** per environment: `logs/{ENV}/charfinder.log`
* **Console output** respects `--verbose` and `--debug`
* **Color detection** adjusts automatically for terminals and scripts
* Logging setup via `setup_logging()` in `logger_setup.py`

📚 See [`logging_system.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/logging_system.md)

---

## 🧪 8. Testing

CharFinder has a comprehensive test suite covering core logic, CLI integration, caching, environment handling, and logging.

**Testing Layer** (`tests/`)
* Unit tests (core, CLI, utils)
* Integration tests (via CLI subprocess)
* Logging behavior tests
* All tests isolated and environment-aware
* High test coverage using `pytest`
* Test isolation enforced via Pytest fixtures and `.env` cleanup

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

Applies Ruff formatting, Ruff checking, and MyPy static type checks.
This runs all of the following commands:

#### Linting and Formatting

```bash
make lint-ruff
```

which is equivalent to 

```bash
ruff check src/ tests/
```

```bash
make fmt
```

which is equivalent to

```bash
ruff format src/ tests/
```

#### Static Type Checks

```bash
make type-check
```

which is equivalent to

```bash
mypy src/ tests/
```

### Coverage Policy

* Target: **100% coverage** on all Python files under `src/`
* CLI integration tests cover all major CLI scenarios via `subprocess.run`
* Logging behaviors, `.env` loading, and edge cases are all tested

### Test Layers

* **Unit tests:** test core logic in isolation (core, caching, normalization, settings, utils)
* **CLI integration tests:** test full CLI entrypoint via subprocess
* **Logging tests:** test rotating logging, suppression, environment filtering
* **Settings tests:** test different `.env` and environment variable scenarios

📚 See [`unit_test_design.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/unit_test_design.md)

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
| `make publish`                              | Upload to PyPI                                               |
| `make upload-coverage`                      | Upload coverage report to Coveralls                          |

#### 📝 Onboarding Tips

* Always use `make develop` to install full dev dependencies.
* Run `make check-all` before pushing changes, or equivalently, run `make lint-all-check` and `make test-coverage`.
* Validate `.env` loading with `make dotenv-debug`.

---


### ⚡ 10. Performance

📚 See [`performance.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/performance.md)

---

## 🚧 11. Limitations and Known Issues

📚 See [`limitations_issues.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/limitations_issues.md)


---

## 📖 12. Documentation

This project includes detailed internal documentation to help both developers and advanced users understand its design, architecture, and internals.

The following documents are located in the [`docs/`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/) directory:

| Document                                                    | Description                                                                                                         |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [`caching.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/caching.md)                             | Explanation of cache layers: Unicode name cache, `cached_normalize()`, performance considerations.                  |
| [`cli_architecture.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/cli_architecture.md)           | Overview of CLI modules, their flow, entry points, and command routing logic.                                       |
| [`config_constants.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/config_constants.md)       |Centralized constants used across the project: default values, valid input sets, exit codes, environment variable names, normalization profiles, hybrid scoring weights, and logging defaults.                         |
| [`config_environment.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/config_environment.md)       | Detailed explanation of environment variable handling and `.env` resolution priorities and scenarios                |
| [`config_types_protocols.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/config_types_protocols.md) | Project-wide types, `Protocol` interfaces, and their role in extensibility and static typing.                     |
| [`core_logic.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/core_logic.md)                       | Core logic and library API (`find_chars`, `find_chars_raw`): processing rules, transformations, architecture.       |
| [`debug_diagnostics.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/debug_diagnostics.md)         | Debug and diagnostic output systems: `--debug`, `CHARFINDER_DEBUG_ENV_LOAD`, dotenv introspection.                  |
| [`logging_system.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/logging_system.md)               | Logging architecture: setup, structured logging, rotating files, and environment-based folders.                     |
| [`matching.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/matching.md)                           | Detailed explanation of exact and fuzzy matching algorithms and options. Includes mode combinations and flowcharts. |
| [`unicode_normalization.md`](docs/unicode_normalization.md) | Unicode normalization explained: what is used (`NFC`), why, and implications for search.                            |
| [`packaging.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/packaging.md)                         | Packaging and publishing: `pyproject.toml`, build tools, versioning strategy, and PyPI release process.             |
| [`unit_test_design.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/unit_test_design.md)           | Testing layers: unit tests, CLI integration tests, coverage strategy.                                               |
| [`validators.md`](https://github.com/berserkhmdvhb/charfinder/blob/main/docs/validators.md)                       | Centralized validation logic shared across CLI and core. Type safety, fallbacks, source-aware behavior.             |

> These documents serve both as **developer onboarding** materials and **technical audit** references.

---

## 🧾 13. License

MIT License © 2025 [berserkhmdvhb](https://github.com/berserkhmdvhb)

