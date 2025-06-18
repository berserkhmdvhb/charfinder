# Caching in CharFinder

CharFinder uses an internal **Unicode name cache** to improve search performance and avoid repeated parsing of large Unicode datasets. This cache is especially critical for fuzzy matching, which performs similarity scoring over a large space.

---

## ✨ What Is Cached?

CharFinder builds and stores a cache of Unicode character names (and optional alternate names) in a local JSON file. Each entry includes:

* Code point (e.g. `U+1F600`)
* Character (e.g. `😀`)
* Unicode name (e.g. `GRINNING FACE`)
* Optionally: aliases and fuzzy-friendly keys (normalized)

The cache allows:

* Fast lookup for **exact matches**
* Fast iteration and scoring for **fuzzy matches**

---

## 📂 Default Cache File Location

By default, the cache is stored at:

```bash
<data-root>/data/cache/unicode_name_cache.json
```

Where `<data-root>` is the project root (typically resolved via `get_root_dir()` in `settings.py`).

---

## ⚖️ Environment Variable Overrides

You can override the default cache path by setting:

```bash
CHARFINDER_CACHE_FILE_PATH="custom/path/to/cache.json"
```

CharFinder will resolve this path **relative to the project root**. This allows custom or test-specific cache locations.

Other relevant variables:

* `CHARFINDER_ROOT_DIR_FOR_TESTS` — used to override root path in test mode

---

## ⚙️ When the Cache Is Used

### During Query Resolution

Whenever a search query is handled (via `find_chars`, `find_chars_raw`, etc.):

1. `build_name_cache()` is invoked if no `name_cache` was explicitly passed.
2. The function checks if the cache file exists.
3. If not, it triggers a **build** process and saves the result.

### Cache Build Options

Controlled via `BuildCacheOptions`, with:

* `force_rebuild`: always rebuild cache if `True`
* `retry_attempts`: number of save retries on I/O errors
* `retry_delay`: delay between retries (seconds)

These options are passed internally from `core/finders.py` and not CLI-exposed (yet).

---

## 🚫 What Happens If the Cache Is Missing or Corrupt?

* If the file is **missing**, CharFinder will silently rebuild it.
* If the file is **invalid or fails to parse**, an error will be logged and the user will be informed (with fallback behavior depending on failure).

---

## 🔎 Verbosity and Debugging

To view cache activity, use CLI options or env vars:

* `--verbose`: prints messages when cache is used or built
* `CHARFINDER_DEBUG_ENV_LOAD=1`: prints details about environment settings (if `.env` or `DOTENV_PATH` is set incorrectly)

The log output uses color formatting (if supported) and integrates with CharFinder’s unified logging system.

---

## 🔹 Summary

| Behavior                     | Default                              | Override Mechanism              |
| ---------------------------- | ------------------------------------ | ------------------------------- |
| Cache file path              | `data/cache/unicode_name_cache.json` | `CHARFINDER_CACHE_FILE_PATH`    |
| Root directory               | Based on `__file__` resolution       | `CHARFINDER_ROOT_DIR_FOR_TESTS` |
| Automatic rebuild if missing | Yes                                  | n/a                             |
| Logging                      | Enabled via `--verbose` or `debug`   | n/a                             |

---

## 🎓 Developer Notes

* The cache is always normalized using `normalize()` from `utils.normalizer`.
* Alternate name support is loaded via `load_alternate_names()` in `unicode_data_loader.py`.
* This system is designed for future extension (e.g. per-locale caches, compression, or remote cache sharing).

---

For deeper internals, see:

* `core/name_cache.py`
* `core/finders.py`
* `settings.py`
