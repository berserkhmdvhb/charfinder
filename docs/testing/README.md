# 🧪 Manual Testing Guide – CharFinder

This guide demonstrates how to manually test the CharFinder project via:

- 📟 CLI commands in PowerShell or Bash
- 🐍 Direct Python usage in a Jupyter notebook

> ✅ Make sure you're in the project root and the virtual environment is activated.

---

## ⚙️ Terminal (CLI) Examples

### 🔍 Basic Query

```bash
python src/cli.py -q heart
```

### 🧠 Fuzzy Match (if strict match fails)

```bash
python src/cli.py -q grnning --fuzzy
```

### 🎯 Fuzzy Match with Threshold

```bash
python src/cli.py -q grnning --fuzzy --threshold 0.5
```

### 🚫 Disable Colors (useful for tests or logging)

```bash
python src/cli.py -q heart --no-color
```

### 🤫 Suppress Info Messages (quiet mode)

```bash
python src/cli.py -q heart --quiet
```

---

## 📓 Jupyter Notebook / Python Script Examples

### ▶️ Basic Usage

```python
from core import find_chars

for line in find_chars("heart", verbose=False):
    print(line)
```

### 🧠 Fuzzy Match

```python
list(find_chars("grnning", fuzzy=True, verbose=False))
```

### 🛠 Customize Threshold

```python
list(find_chars("grnning", fuzzy=True, threshold=0.6, verbose=False))
```

---

## 🔁 Rebuild Cache (if needed)

To force regeneration of the Unicode name cache:

```python
from core import build_name_cache
build_name_cache(force_rebuild=True)
```

---

## 🔗 Related

- 🔬 To run automated tests: `pytest tests --disable-warnings -v`
- 📄 Return to main [README.md](../../README.md)