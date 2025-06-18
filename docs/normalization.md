# Unicode Normalization in CharFinder

CharFinder ensures **reliable and consistent search behavior** through Unicode normalization. This normalization guarantees that both Unicode character names and user-provided search queries are processed in a standardized form, improving exact and fuzzy matching accuracy.

---

## Overview

* All character names are normalized **at cache build time**.
* User input queries are normalized **at search time**.
* Normalization includes:

  * Applying a Unicode normalization form (default: **NFC**)
  * Converting all text to **uppercase**

Normalization enables accurate matching even when users:

* Input characters with different accent compositions
* Use alternate name representations
* Provide lowercase or mixed-case queries

---

## What Is Unicode Normalization?

Unicode normalization is a standard way of transforming Unicode strings so that equivalent strings have a **unique binary representation**. This is critical because many characters can be encoded in multiple ways (e.g., accented letters).

CharFinder uses the [`unicodedata.normalize`](https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize) function with the `NFC` form by default, which:

* Composes characters into their canonical combined form.
* Preserves compatibility with most standard inputs (e.g., keyboard entry, official names).

---

## Where Normalization Happens

### ✅ Cache Build Time

In `core/name_cache.py`, during the execution of `build_name_cache()`, every official and alternate character name is normalized:

```python
normalized = normalize(name)  # applies NFC + upper()
```

These normalized names are stored under the `"normalized"` and `"alternate_normalized"` keys in the cache.

### ✅ Search Time (User Query)

In `core/handlers.py`, the input query is normalized **before** matching:

```python
normalized_query = normalize(query)
```

This ensures that the user query is compared fairly against the normalized name cache.

---

## Implementation Details

### Source

Normalization is implemented in:

* **`utils/normalizer.py`**:

```python
def normalize(text: str, form: Literal["NFC", "NFD", "NFKC", "NFKD"] = DEFAULT_NORMALIZATION_FORM) -> str:
    normalized_text = unicodedata.normalize(form, text)
    return normalized_text.upper()
```

* Default form is configurable via `DEFAULT_NORMALIZATION_FORM` in `constants.py`

---

## Why Normalization Matters

Without normalization:

* The same character (e.g., é vs. e + ́) may not match
* Fuzzy match scores may be inaccurate
* Substring or exact matching can fail on composed/decomposed text

With normalization:

* Matching is **deterministic**
* Typing style and accent encoding are neutralized
* Cache and query representations align

---

## Configuration & Extensibility

* Normalization form is adjustable (NFC, NFD, NFKC, NFKD) via internal constants.
* If desired, future CLI flags could expose this form as a user-facing option.

---

## Summary

| Aspect              | Normalization Applied | Notes                           |
| ------------------- | --------------------- | ------------------------------- |
| Character names     | Yes (during caching)  | Normalized once and saved       |
| Alternate names     | Yes (if present)      | Normalized alongside main name  |
| Search query        | Yes (at runtime)      | Ensures accurate lookup         |
| Matching operations | Always on normalized  | Enables exact/fuzzy comparisons |

Normalization is **foundational** to CharFinder's matching reliability. All major components (cache builder, matchers, CLI) depend on consistent normalized input and name data.
