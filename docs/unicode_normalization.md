# 🌐 Unicode & Normalization in CharFinder

CharFinder ensures **reliable and consistent search behavior** through deep integration with the Unicode standard and careful normalization of input and data. This page explains what Unicode is, why it matters, and how CharFinder handles normalization to guarantee robust and accurate matching.

---

## 1. What Is Unicode?

**Unicode** is the universal standard for encoding text and symbols used across all languages and digital platforms. Every character—letters, emojis, mathematical symbols, currency signs—has a unique **code point**.

For example:
- `A` → U+0041
- `€` → U+20AC
- `😄` → U+1F604

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

- `café` (with `é` as U+00E9) vs. `café` (`e` + combining acute accent U+0301)

These forms **look identical** but are different byte-wise and won't match without normalization.

---

## 3. Normalization in CharFinder

CharFinder applies normalization at all key stages of operation, enabling deterministic and encoding-agnostic search results.

### Overview

* Character names are normalized **at cache build time**
* User input queries are normalized **at search time**
* Normalization steps:
  - Apply a **Unicode normalization form** (default: **NFKD**)
  - Convert to **uppercase**

This ensures accurate matching even when:

- Users input differently encoded diacritics or composed forms
- Names contain symbols or non-ASCII characters
- Queries vary in case or formatting

---

## 4. Where Normalization Happens

### ✅ Cache Build Time

In `core/name_cache.py`, during `build_name_cache()`:

```python
normalized = normalize(name)  # applies NFKD + upper()
```

This affects both:
- `"normalized"`: the official Unicode name
- `"alternate_normalized"`: any alternate name defined for a character

These normalized values are stored for fast lookup.

### ✅ Search Time (User Query)

In `core/handlers.py`, the input is normalized before matching:

```python
normalized_query = normalize(query)
```

This ensures query strings are directly comparable to the normalized cache.

---
## 5. Implementation Details

CharFinder applies normalization consistently across both **cache building** and **search queries**. The logic is implemented in `utils/normalizer.py`:

```python
def normalize(text: str, form: Literal["NFC", "NFD", "NFKC", "NFKD"] = DEFAULT_NORMALIZATION_FORM) -> str:
    normalized_text = unicodedata.normalize(form, text)
    text_without_accents = STRIP_ACCENTS_RE.sub("", normalized_text)
    cleaned_text = text_without_accents.strip().upper()
    return cleaned_text
```

### 🔧 Step-by-Step: How Normalization Works

The normalization process includes the following steps:

1. **Apply Unicode Normalization Form**:

   * The default form is `NFKD` (Normalization Form Compatibility Decomposed).
   * This decomposes characters such as:

     * Ligatures (`ﬁ` → `f` + `i`)
     * Superscripts (`²     - Superscripts (`\xb2`→`2\`)
     * Roman numerals (`Ⅷ` → `VIII`)
     * Full-width characters (`Ａ` → `A`)
     * Accented letters (`é` → `e` + combining acute)

2. **Strip Accents**:

   * All combining marks (e.g., U+0301 COMBINING ACUTE ACCENT) are removed using a regular expression that filters characters by Unicode category (`Mn`).

3. **Trim Whitespace**:

   * Leading and trailing whitespace is removed with `.strip()`.

4. **Convert to Uppercase**:

   * The result is converted to uppercase to ensure case-insensitive, canonical matching.

These steps ensure that:

* `café` (U+00E9) and `café` (`e` + U+0301) normalize identically.
* Compatibility glyphs like `ﬁ`, superscript digits, and full-width forms reduce to simple ASCII equivalents.
* Matching is robust regardless of how the input is entered or encoded.

### 🔐 Centralized & Configurable

* Normalization is centrally handled by `normalize()` in `utils/normalizer.py`.
* The default normalization form (`NFKD`) is defined in `DEFAULT_NORMALIZATION_FORM` in `constants.py`.
* This setup ensures consistency, configurability, and testability across all stages of cache building and search.

### ✨ Supported Normalization Forms

| Form | Description                                       |
| ---- | ------------------------------------------------- |
| NFC  | Canonical composed                                |
| NFD  | Canonical decomposed                              |
| NFKC | Compatibility composed (e.g., ligature = letters) |
| NFKD | Compatibility decomposed (**CharFinder default**) |

CharFinder uses **NFKD** because it maximizes compatibility and decomposes characters to their simplest searchable form, matching typical keyboard input and file encodings.


---

## 6. Why Normalization Matters

Without normalization:

* Input like `é` and `e + ́` don’t match.
* Fuzzy scores become inconsistent.
* Substring or exact match logic fails.

With normalization:

* Search behavior is **stable and predictable**
* All inputs are **uniformly preprocessed**
* Matching is **robust across platforms and languages**

---

## 7. Real-World Example

| Input Query | Code Points             | Normalized Form (NFKD + upper) | Matches? |
|-------------|-------------------------|----------------------------------|----------|
| café        | `U+0063 U+0061 U+0066 U+00E9`        | `CAFÉ`       | ✅       |
| café       | `U+0063 U+0061 U+0066 U+0065 U+0301` | `CAFÉ`       | ✅       |



Thanks to NFC normalization and uppercasing, both queries match identically.

Other special characters:

| Input Query   | Code Points                            | Normalized Form (NFKD + upper) | Matches? |
|---------------|----------------------------------------|----------------------------------|----------|
| ﬁ             | U+FB01                                | FI                               | ✅       |
| Ⅷ           | U+2167                              | VIII                               | ✅       |
| full-width A  | U+FF21                                | A                                | ✅       |
| superscript 2 | U+00B2                                | 2                                | ✅       |
| ①             | U+2460                                | 1                                | ✅       |
| Å (angstrom)  | U+212B                                | Å                                | ✅       |


---

## 8. Summary Table

| Aspect              | Normalization Applied | Notes                           |
|---------------------|-----------------------|---------------------------------|
| Character names     | ✅ (during caching)    | Normalized once and persisted   |
| Alternate names     | ✅ (if available)      | Same treatment as official names |
| Search query        | ✅ (at runtime)        | Normalized before comparison    |
| Matching operations | ✅ Always on normalized input | Ensures correct fuzzy scoring  |

---

## 9. Configuration & Extensibility

Normalization behavior is internally configurable:

- Default form: via `DEFAULT_NORMALIZATION_FORM` constant.
- Future roadmap: expose normalization form as CLI flag (e.g., `--norm-form`).

---
## Enhancing Discoverability with Alternate Names (Field 10)

### Problem: What Users Type ≠ Official Unicode Names

Many users fail to find characters because they search with intuitive or informal terms rather than official Unicode names. For instance:

```bash
$ charfinder --query underscore
No matches found for query: 'underscore'

$ charfinder --query period
No matches found for query: 'period'
```

This happens because:

* `U+005F` is officially named **"LOW LINE"**, not "underscore"
* `U+002E` is officially named **"FULL STOP"**, not "period"
* `U+002F` is officially named **"SOLIDUS"**, not "slash"

Yet "underscore", "period", and "slash" are the most common user terms.

### Solution: Use Unicode Index Field 10 (Alternate Name)

To bridge this gap, CharFinder uses **field 10** of the `UnicodeData.txt` file—an alternate name field rarely used by default tools.

| Character | Codepoint | Official Name | Field 10 (Alternate Name) |
| --------- | --------- | ------------- | ------------------------- |
| `.`       | U+002E    | FULL STOP     | PERIOD                    |
| `/`       | U+002F    | SOLIDUS       | SLASH                     |
| `_`       | U+005F    | LOW LINE      | SPACING UNDERSCORE        |

With field 10 integrated, CharFinder allows:

* ✅ `--query underscore` → `U+005F`
* ✅ `--query period` → `U+002E`
* ✅ `--query slash` → `U+002F`

These alternate names are merged into the name cache used for both exact and fuzzy search.

### Behavior: Loading UnicodeData.txt

CharFinder dynamically loads the alternate names from `UnicodeData.txt`. The logic is as follows:

1. **Attempt to download** from a remote Unicode URL.
2. If download **succeeds**, the file is **cached locally**.
3. If download **fails**, CharFinder attempts to **read from the local path**.
4. If both steps fail, alternate names are not used.

#### Configurable Environment Variables

To support custom paths or offline setups, CharFinder allows injection of two environment variables:

```bash
# Optional custom settings
UNICODE_DATA_URL=https://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt
UNICODE_DATA_FILE_PATH=data/UnicodeData.txt
```

* `UNICODE_DATA_URL`: Where to download the Unicode database from (default is the official Unicode URL).
* `UNICODE_DATA_FILE_PATH`: Where to store or read the file locally.

These values are validated before use. If the URL is invalid or the file is missing, warnings are shown, but the tool continues gracefully.

### Parsing Logic (from unicode\_data\_loader.py)

```python
fields = line.split(";")
if len(fields) >= EXPECTED_MIN_FIELDS:
    alt_name = fields[ALT_NAME_INDEX].strip()
    if alt_name:
        char = chr(int(fields[0], 16))
        alt_names[char] = alt_name
```

* `ALT_NAME_INDEX = 10`
* Hex codepoint (Field 0) is converted into a Unicode character.
* Malformed lines or invalid hex codes are logged and skipped.

### Benefits of Field 10 Support

| Benefit                    | Description                                               |
| -------------------------- | --------------------------------------------------------- |
| Enhanced search terms      | Supports common terms like "period" and "underscore"      |
| Complements official names | Alternate names are additive, not replacements            |
| Improves discoverability   | Especially useful for punctuation and symbolic characters |
| Graceful fallback          | Works even when download fails, if local file exists      |

### Reference Links

* [UnicodeData.txt – Unicode.org](https://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt)
* [Fluent Python by Luciano Ramalho](https://www.fluentpython.com)
* [CharFinder Source – unicode\_data\_loader.py](../../charfinder/core/unicode_data_loader.py)


---

## 11. Summary
Normalization is a **foundational mechanism** in CharFinder. It ensures:

- That exact and fuzzy matches behave consistently
- That queries written in different styles or systems still work
- That the Unicode universe remains navigable and predictable

Whether you're searching for `é`, `𝔈`, `⅀`, or `🧠` — normalization makes it all work.

> **CharFinder: Unicode-aware, normalized, multilingual.**


---

## 12. Further Reading

- 🔤 Python's [`unicodedata.normalize()`](https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize)
- 📘 [Unicode® Standard Annex #15 — Unicode Normalization Forms](https://unicode.org/reports/tr15/)
- 📚 [CharFinder documentation: docs/caching.md](./caching.md)




