# Constants

This document outlines all global constants used in **CharFinder**, located in `charfinder/config/constants.py`. These constants define:

* Package metadata and encoding
* Valid modes and algorithms for matching
* Default configuration for normalization and formatting
* CLI and logging behavior
* Unicode data handling expectations

---

## 📦 Package Metadata

| Name               | Value        |
| ------------------ | ------------ |
| `PACKAGE_NAME`     | `charfinder` |
| `DEFAULT_ENCODING` | `utf-8`      |

---

## 🔍 Matching Configuration

### Fuzzy Algorithm Aliases

```python
FUZZY_ALGO_ALIASES = {
    "lev": "levenshtein_ratio",
    "levenshtein": "levenshtein_ratio",
    "simple": "simple_ratio",
    "normalized": "normalized_ratio",
    "tsr": "token_sort_ratio",
    "token_sort": "token_sort_ratio",
    "token_sort_ratio": "token_sort_ratio",
    "hybrid": "hybrid_score",
    "sequencematcher": "sequencematcher",
    "rapidfuzz": "rapidfuzz",
}
```

### Valid Modes and Algorithms

| Category                 | Valid Values                           |
| ------------------------ | -------------------------------------- |
| Fuzzy Match Modes        | `single`, `hybrid`                     |
| Exact Match Modes        | `substring`, `word-subset`             |
| Output Formats           | `text`, `json`                         |
| Color Modes              | `auto`, `never`, `always`              |
| Normalization Forms      | `NFC`, `NFD`, `NFKC`, `NFKD`           |
| Normalization Profiles   | `raw`, `light`, `medium`, `aggressive` |
| Hybrid Aggregation Funcs | `mean`, `median`, `max`, `min`         |

---

## ✅ Defaults

| Constant                        | Default Value      |
| ------------------------------- | ------------------ |
| `DEFAULT_THRESHOLD`             | `0.7`              |
| `DEFAULT_FUZZY_ALGO`            | `token_sort_ratio` |
| `DEFAULT_FUZZY_MATCH_MODE`      | `single`           |
| `DEFAULT_EXACT_MATCH_MODE`      | `word-subset`      |
| `DEFAULT_HYBRID_AGG_FUNC`       | `mean`             |
| `DEFAULT_COLOR_MODE`            | `auto`             |
| `DEFAULT_OUTPUT_FORMAT`         | `text`             |
| `DEFAULT_NORMALIZATION_FORM`    | `NFKD`             |
| `DEFAULT_NORMALIZATION_PROFILE` | `aggressive`       |

---

## 🧪 Normalization Profiles

| Level        | Unicode Form | Strip Accents | Strip Whitespace      | Transformation Summary             |
| ------------ | ------------ | ------------- | --------------------- | ---------------------------------- |
| `raw`        | NFC          | False         | False                 | NFC + `.upper()` (no stripping)    |
| `light`      | NFC          | False         | (unspecified → False) | NFC + `.upper()`                   |
| `medium`     | NFKD         | False         | (unspecified → False) | NFKD + `.upper()`                  |
| `aggressive` | NFKD         | True          | (unspecified → False) | NFKD + remove accents + `.upper()` |

---

## 🧠 Hybrid Algorithm Weights

Used when `--fuzzy-match-mode=hybrid`:

```python
FUZZY_HYBRID_WEIGHTS = {
    "simple_ratio": 0.10,
    "normalized_ratio": 0.10,
    "levenshtein_ratio": 0.10,
    "token_sort_ratio": 0.50,
    "token_subset_ratio": 0.20,
}
```

---

## 📤 Output Formatting

```python
FIELD_WIDTHS = {
    "code": 10,
    "char": 3,
    "name": 45,
}
```

---

## 🚪 Exit Codes

| Constant             | Value | Description                 |
| -------------------- | ----- | --------------------------- |
| `EXIT_SUCCESS`       | `0`   | Execution succeeded         |
| `EXIT_INVALID_USAGE` | `1`   | CLI or argument error       |
| `EXIT_NO_RESULTS`    | `2`   | No matches found            |
| `EXIT_ERROR`         | `3`   | Unexpected runtime error    |
| `EXIT_CANCELLED`     | `130` | KeyboardInterrupt or SIGINT |

---

## 🧾 Logging Configuration

| Constant           | Value                  |
| ------------------ | ---------------------- |
| `LOG_FILE_NAME`    | `charfinder.log`       |
| `LOG_FORMAT`       | `[%(...)] %(message)s` |
| `DEFAULT_LOG_ROOT` | `logs/`                |

Logging methods (as `SimpleNamespace`):

```python
LOG_METHODS = {
    DEBUG = "debug",
    INFO = "info",
    WARNING = "warning",
    ERROR = "error",
    EXCEPTION = "exception",
}
```

---

## 🌍 Environment Variables

| Env Variable Name                  | Purpose                                        |
| ---------------------------------- | ---------------------------------------------- |
| `CHARFINDER_ENV`                   | Environment name (`DEV`, `TEST`, `PROD`, etc.) |
| `CHARFINDER_LOG_MAX_BYTES`         | Log file max size in bytes                     |
| `CHARFINDER_LOG_BACKUP_COUNT`      | Number of rotated log backups                  |
| `CHARFINDER_LOG_LEVEL`             | Log level (e.g. `info`, `debug`)               |
| `CHARFINDER_DEBUG_ENV_LOAD`        | Show environment load debug details            |
| `CHARFINDER_MATCH_THRESHOLD`       | Override default fuzzy threshold               |
| `CHARFINDER_COLOR_MODE`            | Output color override                          |
| `CHARFINDER_NORMALIZATION_PROFILE` | Profile used to normalize input                |

---

## 🔠 Unicode Data Constants

| Constant              | Value | Description                                             |
| --------------------- | ----- | ------------------------------------------------------- |
| `ALT_NAME_INDEX`      | `10`  | Index of alternate name in `UnicodeData.txt` field list |
| `EXPECTED_MIN_FIELDS` | `11`  | Minimum expected fields in `UnicodeData.txt` rows       |
