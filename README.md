![CLI](https://img.shields.io/badge/CLI-Terminal%20Tool-blue)
![Language](https://img.shields.io/badge/Language-Python%203.10+-yellow)
![Unicode](https://img.shields.io/badge/Unicode-NFKD%20Search-green)

# 🔎 charfinder

**charfinder** is a command-line and Python-based tool for searching Unicode characters by name.  
It supports strict and fuzzy matching, Unicode normalization, and a local cache for performance.

## ✨ Features

- 🔍 Search Unicode characters by name (strict or fuzzy match)
- 📚 Uses Unicode NFKD normalization for accurate results
- 🚀 Fast name-based lookup using a local cache (`unicode_name_cache.json`)
- 🌈 Colorized CLI output (optional)
- ✅ Includes full unit tests with `pytest`

---

## 📂 Project Structure

```
charfinder/
├── src/
│   ├── cli.py            # CLI interface
│   └── core.py           # Main logic (normalization, search, cache)
├── tests/
│   ├── test_cli.py       # CLI integration tests
│   └── test_lib.py       # Library unit tests
├── unicode_name_cache.json  # Cached Unicode name mapping (auto-generated)
├── pyproject.toml        # Build system and dependencies
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### Using `git`:

```bash
git clone https://github.com/yourusername/charfinder.git
cd charfinder
python -m venv .venv
.venv\Scripts\activate  # or source .venv/bin/activate on Linux/macOS
pip install .
```

Or directly install with:

```bash
pip install git+https://github.com/yourusername/charfinder.git
```

---

## 🚀 Usage

### 🖥 CLI Mode

Run from the terminal:

```bash
python src/cli.py -q "heart"
```

Optional flags:

- `--fuzzy` → enable fuzzy search
- `--threshold` → set fuzzy match threshold (default `0.7`)
- `--quiet` → suppress logs
- `--no-color` → disable colored output

Example:

```bash
python src/cli.py -q "grnning" --fuzzy --threshold 0.6
```

### 🐍 Library Mode

Use it directly in Python:

```python
from core import find_chars

for line in find_chars("snowman"):
    print(line)
```

---

## 🧪 Running Tests

Run all unit tests using:

```bash
pytest tests --disable-warnings -v
```

Make sure to activate your virtual environment first.
For manual tests and having visibility on outputs, visit the page [testing](docs/testing/README.md).

---

## 📦 Dependencies

Managed with [PEP 621](https://peps.python.org/pep-0621/) via `pyproject.toml`.

Key packages:

- `colorama`
- `pytest`

Install with:

```bash
pip install -e .[dev]
```

---

## 🛠 Roadmap

| Feature                                       | Status |
|-----------------------------------------------|--------|
| Strict Unicode search                         | ✅     |
| Fuzzy search (difflib)                        | ✅     |
| Unicode normalization (NFKD)                  | ✅     |
| Local cache for performance                   | ✅     |
| CLI options: threshold, quiet                 | ✅     |
| Type hints + logging                          | ✅     |
| Pytest coverage                               | ✅     |
| `pyproject.toml` support                      | ✅     |
| Display fuzzy match's scores in output        | 🔜     |
| Equip with multiple fuzzy matching alg.s      | 🔜     |
| CLI autocomplete support                      | 🔜     |

---
