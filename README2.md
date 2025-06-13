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

# 🎥 Demo Video

https://github.com/user-attachments/assets/e19b0bbd-d99b-401b-aa29-0092627f376b

---

## ✨ Features

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

  * `DOTENV_PATH` override.
  * `.env.override`, `.env`, `.env.local`, `.env.test`.

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

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install charfinder
```

### From GitHub (Development Version)

```bash
pip install git+https://github.com/berserkhmdvhb/charfinder.git
```

---

## 🚀 Usage

### 🖥 CLI Mode

```bash
charfinder -q heart
```

Example:

```bash
$ charfinder -q snowman
☃  U+2603  SNOWMAN
```

Show all options:

```bash
charfinder --help
```

You can also run directly from source:

```bash
python -m charfinder -q smile
```

#### Common CLI Options

| Option            | Description                                                 |
|-------------------|-------------------------------------------------------------|
| `--fuzzy`         | Enable fuzzy match fallback                                 |
| `--threshold`     | Fuzzy match threshold (0.0–1.0, default: `0.7`)             |
| `--fuzzy-algo`    | `sequencematcher`, `rapidfuzz`, or `levenshtein`           |
| `--match-mode`    | `single` or `hybrid` (aggregated fuzzy scoring)            |
| `--quiet`         | Suppress logging                                           |
| `--color`         | `auto`, `never`, or `always`                               |
| `--help`          | Show command-line help and usage info                     |
| `--version`       | Show installed version of `charfinder`                    |

🧠 Use `--match-mode hybrid` to combine all 3 algorithms by averaging their scores.

Example:

```bash
charfinder -q grnning --fuzzy --threshold 0.6 --fuzzy-algo rapidfuzz
```

### 🐍 Python Library Mode

```python
from charfinder.core import find_chars

for line in find_chars("snowman"):
    print(line)

# Enable fuzzy search with threshold and algorithm
find_chars("snwmn", fuzzy=True, threshold=0.6, fuzzy_algo="rapidfuzz")
```

---

## 📂 Project Structure

```
charfinder/
├── src/charfinder/
│   ├── __init__.py               ← Package marker
│   ├── __main__.py               ← Enables `python -m charfinder` entry point
│   ├── cli.py                    ← Argument parsing and CLI integration
│   ├── core.py                   ← Core logic: search, normalize, cache
│   ├── fuzzymatchlib.py          ← Fuzzy algorithm dispatcher
│   ├── constants.py              ← Constants, enums, and default settings
│   └── py.typed                  ← Marker for type-checking consumers
├── tests/
│   ├── test_cli.py               ← CLI integration tests via subprocess
│   ├── test_lib.py               ← Tests for core `find_chars` function
│   ├── test_fuzzymatchlib.py     ← Tests for fuzzy similarity scoring logic
│   └── manual/demo.ipynb         ← Notebook for interactive exploration
├── .github/
│   └── workflows/tests.yml       ← GitHub Actions workflow (CI/CD)
├── .pre-commit-config.yaml       ← Hook definitions: lint, format, type-check
├── Makefile                      ← Automation for common dev tasks
├── pyproject.toml                ← PEP 621 config + dependencies
├── MANIFEST.in                   ← Includes additional files in distributions
├── LICENSE.txt                   ← MIT license
├── unicode_name_cache.json       ← Auto-generated at runtime; not tracked in Git
└── README.md                     ← Project documentation (this file)
```

---

## 🧪 Testing

```bash
# Run the full test suite with detailed output
make test

# Re-run only failed or last tests for quicker feedback
make test-fast

# Run tests and show coverage report in the terminal
make coverage

# Run all style and type checks
make check-all

# Or run individual checks
make lint                # ruff + mypy
make format-check        # black format check (skips .ipynb)
make format              # auto-format with black
```

**Pre-commit hooks**

```bash
make precommit       # install pre-commit hook
make precommit-run   # manually run hooks on all files
```

For manual exploration, see: [`demo.ipynb`](https://github.com/berserkhmdvhb/charfinder/blob/main/tests/manual/demo.ipynb)

---

## 🛠 For Developers

```bash
git clone https://github.com/berserkhmdvhb/charfinder.git
cd charfinder
make install
```

If `make` is unavailable:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .[dev]
```

---


### Makefile Commands

| Command            | Description                                                         |
|--------------------|---------------------------------------------------------------------|
| `help`             | Show this help text with a list of available commands               |
| `install`          | Install the package in editable mode (no dev dependencies)          |
| `install-dev`      | Upgrade pip and install package + all dev dependencies              |
| `format`           | Reformat all Python files using `black`                             |
| `format-check`     | Check formatting using `black --check` (non-invasive)               |
| `mypy`             | Type-check source & tests (excludes `*.ipynb`)                      |
| `ruff`             | Lint source & tests with `ruff` (excludes `*.ipynb`)                |
| `lint`             | Run static checks: `ruff` + `mypy`                                  |
| `test`             | Run the full test suite (`pytest tests --maxfail=1 -v`)             |
| `test-fast`        | Run only failed or last tests quickly (`pytest --lf -x -v`)         |
| `coverage`         | Run tests with coverage report in the terminal                      |
| `coverage-xml`     | Run tests with coverage and output `coverage.xml` (for CI tools)   |
| `check-all`        | Run `format-check`, `mypy`, `ruff`, and then `test`                 |
| `precommit`        | Install Git pre-commit hooks (`pre-commit install`)                 |
| `precommit-run`    | Run all configured pre-commit hooks locally                         |
| `build`            | Build sdist & wheel via `python -m build`                           |
| `clean`            | Remove build artifacts (`dist/`, `build/`, `*.egg-info/`)           |
| `publish-test`     | Upload distributions to TestPyPI                                    |
| `publish`          | Check & upload distributions to PyPI                                |
| `upload-coverage`  | Send coverage report to Coveralls                                   |


## 📦 Dependencies

**Runtime**

- [`argcomplete`](https://pypi.org/project/argcomplete/)
- [`colorama`](https://pypi.org/project/colorama/)
- [`python-Levenshtein`](https://pypi.org/project/python-Levenshtein/)
- [`rapidfuzz`](https://pypi.org/project/rapidfuzz/)

**Development**

- [`black`](https://pypi.org/project/black/)
- [`build`](https://pypi.org/project/build/)
- [`coverage`](https://pypi.org/project/coverage/)
- [`coveralls`](https://pypi.org/project/coveralls/) *(Python < 3.13 only)*
- [`mypy`](https://pypi.org/project/mypy/)
- [`pre-commit`](https://pypi.org/project/pre-commit/)
- [`pytest`](https://pypi.org/project/pytest/)
- [`pytest-cov`](https://pypi.org/project/pytest-cov/)
- [`ruff`](https://pypi.org/project/ruff/)
- [`twine`](https://pypi.org/project/twine/)


Install all with:

```bash
pip install -e .[dev]
```

---

## 📌 Roadmap

| Feature                              | Status |
|--------------------------------------|--------|
| Strict Unicode name matching         | ✅     |
| Unicode normalization (NFKD)         | ✅     |
| Caching for fast repeated lookup     | ✅     |
| Fuzzy search with 3 algorithms       | ✅     |
| CLI: quiet mode, color modes         | ✅     |
| Type hints, logging, clean code      | ✅     |
| Unit tests + CLI test coverage       | ✅     |
| `charfinder` CLI entry point         | ✅     |
| Fuzzy score shown in results         | ✅     |
| `demo.ipynb` interactive interface   | ✅     |
| Hybrid fuzzy matching strategy       | ✅     |
| Docker container support             | 🔜     |
| JSON output format (for scripting)   | 🔜     |

---

## 🧾 License

MIT License © 2025 [berserkhmdvhb](https://github.com/berserkhmdvhb)
