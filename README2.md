# 🔎 CharFinder

[![PyPI](https://img.shields.io/pypi/v/charfinder)](https://pypi.org/project/charfinder/)
[![Python](https://img.shields.io/pypi/pyversions/charfinder)](https://pypi.org/project/charfinder/)
[![License](https://img.shields.io/github/license/berserkhmdvhb/charfinder)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/charfinder/month)](https://pepy.tech/project/charfinder)
[![Tests](https://github.com/berserkhmdvhb/charfinder/actions/workflows/tests.yml/badge.svg)](https://github.com/berserkhmdvhb/charfinder/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/berserkhmdvhb/charfinder/badge.svg?branch=main)](https://coveralls.io/github/berserkhmdvhb/charfinder?branch=main)

---

**CharFinder** is a powerful and flexible tool to search Unicode characters by name, with both **exact** and **fuzzy** matching, Unicode normalization, caching, environment-aware logging, and a clean CLI and Python API.

Whether you're trying to find `SNOWMAN` (\u2603), `GRINNING FACE`, or "some heart emoji", CharFinder helps you locate and inspect Unicode characters effortlessly.

* Works as both **CLI** and **importable Python library**
* Designed with a clean and testable architecture
* Professional-level CLI with colored output, JSON output, and full debug support
* Full test coverage and modular codebase

---

# 🎥 Demo Video

[https://github.com/user-attachments/assets/e19b0bbd-d99b-401b-aa29-0092627f376b](https://github.com/user-attachments/assets/e19b0bbd-d99b-401b-aa29-0092627f376b)

---

# 💡 Features

* 🔍 Search Unicode characters by name (**exact** or **fuzzy**)
* 🔋 Multiple fuzzy matching algorithms:

  * `sequencematcher` (Python stdlib)
  * `rapidfuzz`
  * `python-Levenshtein`
* 💥 Hybrid fuzzy scoring with aggregation (mean, median, max, min)
* 🌐 Unicode normalization (NFC) and case-folding for accurate comparisons
* 🔄 Caching of normalized names and repeated lookups
* 📁 Local disk cache for Unicode name data
* 💨 Fast performance even on full Unicode range
* 📃 Structured logging with per-environment folders
* 🌟 Colorized CLI output with `colorama`
* 🎉 JSON output support for scripting
* 🔢 Configurable via `.env` or environment variables
* 🔖 Full test suite with 100% coverage
* 📆 GitHub Actions CI + Coveralls
* 🎓 Modern `pyproject.toml` (PEP 621) packaging

---

# 📅 Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)

   * [CLI Usage](#cli-usage)
   * [Python Library Usage](#python-library-usage)
4. [What is Unicode?](#what-is-unicode)
5. [Project Structure](#project-structure)

   * [Structure](#structure)
   * [Architecture](#architecture)
6. [Exact and Fuzzy Match](#exact-and-fuzzy-match)
7. [Caching](#caching)
8. [Environment and Configuration Management](#environment-and-configuration-management)
9. [Logging System](#logging-system)
10. [Internals and Architecture](#internals-and-architecture)
11. [Testing](#testing)
12. [Developer Guide](#developer-guide)
13. [Performance](#performance)
14. [Further Documentation and References](#further-documentation-and-references)
15. [Limitations / Known Issues](#limitations--known-issues)
16. [License](#license)

---

# 📦 Installation

### For Users

```bash
pip install charfinder
```

### For Developers

```bash
git clone https://github.com/berserkhmdvhb/charfinder.git
cd charfinder
make develop
```

---

# 🚀 Usage

## CLI Usage

```bash
charfinder heart
charfinder snowman
charfinder --fuzzy --threshold 0.6 --fuzzy-algo rapidfuzz heart
```

### Example

```bash
$ charfinder snowman
CODE       CHAR NAME                                    
------------------------------------------------------
U+2603     ☃   SNOWMAN  (\u2603)
```

### Help

```bash
charfinder --help
```

## Python Library Usage

```python
from charfinder.core.core_main import find_chars

for line in find_chars("snowman"):
    print(line)

# Fuzzy search
find_chars("snwmn", fuzzy=True, threshold=0.6, fuzzy_algo="rapidfuzz")
```

---

# 🌐 What is Unicode?

Unicode is the universal character encoding standard, defining more than 150,000 characters used worldwide.

CharFinder allows you to search for Unicode characters by their **official name**, using:

* Unicode normalization (NFC)
* Case-folding for case-insensitive comparison

More details: [docs/unicode.md](docs/unicode.md)

---

# 📂 Project Structure

## Structure

```text
charfinder/
├── src/charfinder/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli/
│   ├── core/
│   ├── utils/
│   ├── constants.py
│   ├── settings.py
│   ├── cache.py
│   ├── fuzzymatchlib.py
│   ├── types.py
├── tests/
├── docs/
├── .github/workflows/
├── Makefile
├── pyproject.toml
├── README.md
```

## Architecture

See: [docs/architecture.md](docs/architecture.md)

---

# 🔄 Exact and Fuzzy Match

CharFinder supports powerful combinations of exact and fuzzy match modes.

| Match Type | Argument             | Modes                      |
| ---------- | -------------------- | -------------------------- |
| Exact      | `--exact-match-mode` | `substring`, `word-subset` |
| Fuzzy      | `--fuzzy-match-mode` | `single`, `hybrid`         |

### Fuzzy Matching Algorithms

| Algorithm         | Argument       |
| ----------------- | -------------- |
| `sequencematcher` | `--fuzzy-algo` |
| `rapidfuzz`       | `--fuzzy-algo` |
| `levenshtein`     | `--fuzzy-algo` |

### Hybrid Aggregation Functions

| Aggregation Function | Argument `--hybrid-agg-fn` |
| -------------------- | -------------------------- |
| `mean` (default)     | `mean`                     |
| `median`             | `median`                   |
| `max`                | `max`                      |
| `min`                | `min`                      |

More details and flowchart: [docs/matching.md](docs/matching.md)

---

# 🔁 Caching

* LRU caching is used for Unicode normalization.
* Unicode name cache is built once and stored as JSON.
* Cache path configurable via `.env`.

See: [docs/caching.md](docs/caching.md)

---

# 📥 Environment and Configuration Management

* Environment controlled via `CHARFINDER_ENV`: `DEV`, `UAT`, `PROD`.
* `.env` files loaded dynamically.
* Supports debug output of dotenv loading.

See: [docs/environment\_config.md](docs/environment_config.md)

---

# 🔊 Logging System

* Rotating file logs in `logs/{ENV}/`
* Console logging (colorized)
* Full support for suppressing console output during tests

See: [docs/logging\_system.md](docs/logging_system.md)

---

# 🔢 Internals and Architecture

Covers detailed module-level architecture and flow:

* CLI layer
* Core matching layer
* Caching layer
* Utilities

See: [docs/architecture.md](docs/architecture.md)

---

# 🔧 Testing

```bash
make test
make coverage
make check-all
```

Full test coverage enforced. CLI integration tested via subprocess.

See: [docs/unit\_test\_design.md](docs/unit_test_design.md)

---

# 📚 Developer Guide

```bash
git clone https://github.com/berserkhmdvhb/charfinder.git
cd charfinder
make develop
```

See Makefile for available commands.

See: [docs/developer\_guide.md](docs/developer_guide.md)

---

# 🏃️ Performance

* LRU cache (`cached_normalize`) prevents redundant normalization
* Unicode name cache dramatically speeds up repeated lookups
* Fuzzy matching optimized by hybrid scoring

More: [docs/caching.md](docs/caching.md)

---

# 📚 Further Documentation and References

* [docs/architecture.md](docs/architecture.md)
