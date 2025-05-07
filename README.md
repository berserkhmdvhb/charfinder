[![PyPI](https://img.shields.io/pypi/v/charfinder)](https://pypi.org/project/charfinder/)
[![Python](https://img.shields.io/pypi/pyversions/charfinder)](https://pypi.org/project/charfinder/)
[![License](https://img.shields.io/github/license/berserkhmdvhb/charfinder)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/charfinder/month)](https://pepy.tech/project/charfinder)
![Tests](https://github.com/berserkhmdvhb/charfinder/actions/workflows/tests.yml/badge.svg)
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

- 🔍 Search Unicode characters by name (strict or fuzzy match)
- ⚡ Multiple fuzzy matching algorithms:
  - `difflib.SequenceMatcher` (standard lib)
  - [`rapidfuzz`](https://github.com/maxbachmann/RapidFuzz)
  - [`python-Levenshtein`](https://github.com/ztane/python-Levenshtein)
- 📚 Unicode NFKD normalization for accurate comparison
- 💾 Local cache to speed up repeated lookups
- 🎨 CLI color support via `colorama`
- 🧪 Full test suite: unit tests + CLI tests via `pytest`
- 🐍 Usable both as CLI and as Python library
- 📦 Modern `pyproject.toml`-based packaging (PEP 621)

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
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── core.py
│   └── fuzzymatchlib.py
├── tests/
│   ├── test_cli.py
│   ├── test_lib.py
│   ├── test_fuzzymatchlib.py
│   └── manual/demo.ipynb
├── Makefile
├── pyproject.toml
├── unicode_name_cache.json  # auto-generated
└── README.md
```

---

## 🧪 Testing

```bash
pytest tests -v
# or:
make test
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

### Makefile Commands

| Command         | Description                    |
|----------------|--------------------------------|
| `make install` | Install with dev dependencies  |
| `make test`    | Run all tests                  |
| `make build`   | Build distribution             |
| `make publish-test` | Upload to TestPyPI       |
| `make publish` | Upload to PyPI (requires login)|

---

## 📦 Dependencies

- [`colorama`](https://pypi.org/project/colorama/)
- [`argcomplete`](https://pypi.org/project/argcomplete/)
- [`rapidfuzz`](https://pypi.org/project/rapidfuzz/)
- [`python-Levenshtein`](https://pypi.org/project/python-Levenshtein/)
- `pytest` for development

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
