# 🌐 Unicode & Normalization in CharFinder

CharFinder ensures **reliable and consistent search behavior** through deep integration with the Unicode standard and careful normalization of input and data. This page explains what Unicode is, why it matters, and how CharFinder handles normalization to guarantee robust and accurate matching.

---

## 1. What Is Unicode?

**Unicode** is the universal standard for encoding text and symbols used across all languages and digital platforms. Every character—letters, emojis, mathematical symbols, currency signs—has a unique **code point**.

For example:

* `A` → U+0041
* `€` → U+20AC
* `😄` → U+1F604

### Why It Matters for CharFinder

Unicode provides the foundation that enables CharFinder to:

* 🌍 **Support all languages**: Latin, Greek, Cyrillic, Hebrew, Arabic, CJK, and more.
* 🧠 **Enable smart queries**: Tolerant of casing, accents, and visual variants.
* 🔣 **Recognize everything**: Symbols, emojis, math operators, and ancient scripts.
* 💡 **Normalize input and data**: Resolve encoding inconsistencies for stable matching.

---

## 2. What Is Unicode Normalization?

Unicode normalization transforms text into a **standardized binary form**, resolving the fact that some characters can be encoded in multiple ways.

For instance:

* `café` (with `é` as U+00E9) vs. `café` (`e` + combining acute accent U+0301)

These forms **look identical** but are different byte-wise and won't match without normalization.

---

## 3. Normalization in CharFinder

CharFinder applies normalization at all key stages of operation, enabling deterministic and encoding-agnostic search results.

### Overview

* Character names are normalized **at cache build time**
* User input queries are normalized **at search time**
* Normalization includes:

  * Apply a **Unicode normalization form**
  * Optional **accent stripping**
  * Optional **whitespace stripping**
  * Convert to **uppercase**

This ensures accurate matching even when:

* Users input differently encoded diacritics or composed forms
* Names contain symbols or non-ASCII characters
* Queries vary in case or formatting

---

## 4. Normalization Profiles

To support different use cases, CharFinder introduces the `--normalization-profile` argument (CLI) and `normalization_profile` option (core API). This provides **preset normalization behaviors** optimized for varying levels of strictness.

### 🔧 Preset Levels

| Level        | Unicode Normalization Form | Strip Accents | Strip Whitespace      | Transformation Summary             |
| ------------ | ------------ | ------------- | --------------------- | ---------------------------------- |
| `raw`        | NFC          | False         | False                 | NFC + `.upper()` (no stripping)    |
| `light`      | NFC          | False         | (unspecified → False) | NFC + `.upper()`                   |
| `medium`     | NFKD         | False         | (unspecified → False) | NFKD + `.upper()`                  |
| `aggressive` | NFKD         | True          | (unspecified → False) | NFKD + remove accents + `.upper()` |


### Normalization Forms

| Form | Description                                       |
| ---- | ------------------------------------------------- |
| NFC  | Canonical composed                                |
| NFD  | Canonical decomposed                              |
| NFKC | Compatibility composed (e.g., ligature = letters) |
| NFKD | Compatibility decomposed                          |

### 🎯 Choosing a Profile

The default profile is **`aggressive`**, which maximizes matchability by:

* Using NFKD normalization (decomposes characters)
* Removing diacritics (accents)
* Ensuring case-insensitivity

You can override the profile using:

```bash
charfinder --query cafe --normalization-profile=light
```

Or programmatically:

```python
find_chars("cafe", normalization_profile="light")
```

---

## 5. Where Normalization Happens

### ✅ Cache Build Time

In `core/name_cache.py`, during `build_name_cache()`:

```python
normalized = normalize(name)  # uses aggressive profile by default
```

This affects both:

* `"normalized"`: the official Unicode name
* `"alternate_normalized"`: any alternate name defined for a character

These normalized values are stored for fast lookup.

### ✅ Search Time (User Query)

In `core/handlers.py`, the input is normalized using the selected profile:

```python
normalized_query = normalize(query, profile="medium")
```

This ensures query strings are directly comparable to the normalized cache.

---

## 6. Implementation Details

CharFinder applies normalization consistently across both **cache building** and **search queries**. The logic is implemented in `utils/normalizer.py` and driven by a selected **normalization profile**.

```python
def normalize(text: str, profile: str = DEFAULT_NORMALIZATION_PROFILE) -> str:
    # Resolve form, accent, and whitespace behavior from profile
    ...
    text = unicodedata.normalize(form, text)
    if strip_accents:
        text = STRIP_ACCENTS_RE.sub("", text)
    if strip_whitespace:
        text = text.strip()
    return text.upper()
```

### 🔍 How Normalization Profiles Work

Each profile resolves to a set of options (`form`, `strip_accents`, `strip_whitespace`). These are defined centrally and validated before being applied.

The normalization logic includes the following steps:

1. **Apply Unicode Normalization Form**:

   * For example, `NFKD` decomposes characters like:

     * Ligatures (`ﬁ` → `f` + `i`)
     * Superscripts (`²` → `2`)
     * Full-width characters (`Ａ` → `A`)
     * Accented letters (`é` → `e` + combining acute)

2. **Optional Accent Stripping**:

   * If `strip_accents=True`, all combining marks are removed (Unicode category `Mn`).

3. **Optional Whitespace Trimming**:

   * Controlled by the profile or function argument.

4. **Uppercase Conversion**:

   * All normalized results are uppercased for uniformity.

### 🔐 Centralized & Configurable

* Normalization is centrally handled by `normalize()` in `utils/normalizer.py`.
* The default normalization profile (`aggressive`) is defined in `DEFAULT_NORMALIZATION_PROFILE` in `constants.py`.
* This setup ensures consistency, configurability, and testability across all stages of cache building and search.

---

## 7. Why Normalization Matters

Without normalization:

* Input like `é` and `e + ́` don’t match.
* Fuzzy scores become inconsistent.
* Substring or exact match logic fails.

With normalization:

* Search behavior is **stable and predictable**
* All inputs are **uniformly preprocessed**
* Matching is **robust across platforms and languages**

---

## 8. Real-World Example

| Input Query | Code Points                          | Normalized (`aggressive`) | Matches? |
| ----------- | ------------------------------------ | ------------------------- | -------- |
| café        | `U+0063 U+0061 U+0066 U+00E9`        | `CAFE`                    | ✅        |
| café       | `U+0063 U+0061 U+0066 U+0065 U+0301` | `CAFE`                    | ✅        |

Other special characters:

| Input Query   | Code Points | Normalized (`aggressive`) | Matches? |
| ------------- | ----------- | ------------------------- | -------- |
| ﬁ             | U+FB01      | FI                        | ✅        |
| Ⅷ             | U+2167      | VIII                      | ✅        |
| full-width A  | U+FF21      | A                         | ✅        |
| superscript 2 | U+00B2      | 2                         | ✅        |
| ①             | U+2460      | 1                         | ✅        |
| Å (angstrom)  | U+212B      | Å                        | ✅        |

---

## 9. Summary Table

| Aspect              | Normalization Applied        | Notes                             |
| ------------------- | ---------------------------- | --------------------------------- |
| Character names     | ✅ (during caching)           | Based on selected profile         |
| Alternate names     | ✅ (if available)             | Normalized same as official names |
| Search query        | ✅ (at runtime)               | Controlled by profile             |
| Matching operations | ✅ Always on normalized input | Ensures correct fuzzy scoring     |

---

## 10. Configuration & Extensibility

Normalization behavior is fully configurable:

* 🔧 `--normalization-profile` (CLI)
* 🧩 `normalization_profile="..."` (API)
* 🔄 Profiles are resolved and validated centrally
* 🧪 Custom profiles may be supported in the future

Supported profile levels:

* `raw`
* `light`
* `medium`
* `aggressive` (default)

---

## 11. Enhancing Discoverability with Alternate Names (Field 10)

*See [docs/caching.md](./caching.md) for full details.*

CharFinder uses alternate names (Field 10 in `UnicodeData.txt`) to improve discoverability of characters not matched by their official name.

Example:

```bash
charfinder --query underscore
```

Matches:

| Character | Codepoint | Official Name | Alternate Name     |
| --------- | --------- | ------------- | ------------------ |
| `_`       | U+005F    | LOW LINE      | SPACING UNDERSCORE |

---

## 12. Further Reading

* 🌤 Python’s [`unicodedata.normalize()`](https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize)
* 📘 [Unicode® Standard Annex #15 — Unicode Normalization Forms](https://unicode.org/reports/tr15/)
* 📚 [CharFinder documentation: docs/caching.md](./caching.md)

---

## 13. Final Thoughts

Normalization is a **foundational mechanism** in CharFinder. It ensures:

* That exact and fuzzy matches behave consistently
* That queries written in different styles or systems still work
* That the Unicode universe remains navigable and predictable

> **CharFinder: Unicode-aware, normalized, multilingual.**
