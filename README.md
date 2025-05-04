![PackageDev](https://img.shields.io/badge/Package%20Development|%20Unit%20Tests%20-blue)
![CLI](https://img.shields.io/badge/CLI-Terminal%20Tool-blue)
![Language](https://img.shields.io/badge/Language-Python%203.8%2B-yellow)

# 🔎 charfinder

**charfinder** is a command-line and Python-based tool for searching Unicode characters by name.  
It supports strict and fuzzy matching (with multiple algorithms), Unicode normalization, logging, colored CLI output, and a local cache for performance.

---

## ✨ Features

- 🔍 Search Unicode characters by name (strict or fuzzy match)
- ⚡ Supports multiple fuzzy matching algorithms: SequenceMatcher, RapidFuzz, Levenshtein
- 📚 Unicode NFKD normalization for accurate comparison
- 💾 Caches all Unicode names to speed up repeated lookups
- 🧪 Full unit + CLI tests via `pytest`
- 🖥 CLI color support with `colorama`
- 📦 PEP 621 compliant (`pyproject.toml`)

---

## 📂 Project Structure

```
charfinder/
├── src/
│   └── charfinder/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py         # CLI interface
│       └── core.py        # Search logic, normalization, caching
├── tests/
│   ├── test_cli.py        # CLI tests (subprocess-based)
│   ├── test_lib.py        # Library tests (direct function calls)
│   └── manual/demo.ipynb  # Interactive notebook demo
├── unicode_name_cache.json  # Auto-generated cache
├── pyproject.toml         # Build config & dependencies
├── Makefile               # Development workflow automation
└── README.md              # This file
```

---

## ⚙️ Installation

```bash
git clone https://github.com/yourusername/charfinder.git
cd charfinder
python -m venv .venv
.venv\Scripts\activate    # or source .venv/bin/activate
pip install -e .[dev]     # includes test + dev tools
```

Or install directly via:

```bash
pip install git+https://github.com/yourusername/charfinder.git
```

---

## 🚀 Usage

### 🖥 CLI Mode

Run via installed CLI:

```bash
charfinder -q heart
```

Or directly (if running from source):

```bash
python -m charfinder -q heart
```

Optional flags:

- `--fuzzy` → enable fuzzy search fallback
- `--threshold` → fuzzy threshold (0.0–1.0, default: `0.7`)
- `--fuzzy-algo` → `sequencematcher`, `rapidfuzz`, `levenshtein`
- `--match-mode` → `single` or `hybrid`
- `--quiet` → suppress logging
- `--color` → `auto`, `never`, `always`

Example:

```bash
charfinder -q grnning --fuzzy --threshold 0.6 --fuzzy-algo rapidfuzz
```

### 🐍 Python Library Mode

```python
from charfinder.core import find_chars

for line in find_chars("snowman"):
    print(line)
```

---

## 🧪 Testing

### Unit & CLI Tests

```bash
pytest tests -v
```

### Manual Notebook

Use [`demo.ipynb`](https://github.com/berserkhmdvhb/charfinder/blob/main/tests/manual/demo.ipynb) for CLI + core function exploration.

---

## 📦 Dependencies

- `colorama`
- `argcomplete`
- `rapidfuzz`
- `python-Levenshtein`
- `pytest` (for dev/test)

Install them via:

```bash
pip install -e .[dev]
```

---

## 🛠 Development & Build

The Makefile includes common commands:

```bash
make help         # Show all targets
make install      # Install with dev dependencies
make test         # Run all tests
make build        # Build distribution
make publish-test # Upload to TestPyPI
make publish      # Upload to PyPI (requires config)
```

---

## 📌 Roadmap

| Feature                                       | Status |
|-----------------------------------------------|--------|
| Strict Unicode search                         | ✅     |
| Unicode normalization (NFKD)                  | ✅     |
| Local cache for performance                   | ✅     |
| Fuzzy search (difflib / rapidfuzz / Levenshtein) | ✅  |
| CLI options: quiet, color, threshold          | ✅     |
| Type hints + logging                          | ✅     |
| Pytest CLI + lib test coverage                | ✅     |
| `pyproject.toml` packaging                    | ✅     |
| CLI via `charfinder` entry point              | ✅     |
| Fuzzy score shown in output                   | ✅     |
| `demo.ipynb` manual test interface            | ✅     |
| Hybrid fuzzy matching mode                    | ✅     |
| Containerize with Docker                     | 🔜     |

---
