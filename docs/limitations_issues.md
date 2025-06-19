
## 🚧 Limitations and Known Issues

While **CharFinder** is a robust and flexible tool, it is important to be aware of the following current limitations and known constraints:

### 🔹 Fuzzy Algorithms Scope

CharFinder currently supports five fuzzy matching algorithms:

* `simple_ratio` — based on `difflib.SequenceMatcher`
* `normalized_ratio` — normalized variant of `simple_ratio`
* `levenshtein_ratio` — based on `python-Levenshtein`
* `token_sort_ratio` — word-order invariant, from `rapidfuzz`
* `hybrid_score` — aggregates multiple algorithms using predefined weights

These algorithms are selected for performance, robustness, and compatibility across systems.

The `hybrid_score` mode combines results from multiple algorithms to improve match accuracy. However, the internal weights used for aggregation are **not user-configurable**.

To extend support for additional fuzzy algorithms (e.g., Jaro-Winkler, Damerau-Levenshtein), or to enable weight customization, the internal `fuzzymatchlib.py` module would need to be updated. PRs are welcome (see [Contributing](#contributing)).

### 🔹 Limitations for Embedding in APIs or External Applications

While **CharFinder** is designed as both a library and CLI, embedding it into high-throughput applications (e.g., servers, chatbots) requires extra care:

* The Unicode name cache (`name_cache`) is built at runtime and saved as a local JSON file.
* Without pre-building and injecting the cache, each process may rebuild it unnecessarily, introducing latency.
* For real-time or distributed usage:

  * Pre-build the cache with `build_name_cache()` and inject it as an argument.
  * Avoid using CLI-level diagnostics or console outputs.
  * Cache sharing between processes is not optimized out-of-the-box.

### 🔹 UnicodeData.txt Updates

* CharFinder fetches character names from the Unicode Consortium's **UnicodeData.txt**.
* This file should be updated manually when Unicode standards evolve.
* No automatic refresh mechanism is included. You must manually rebuild the cache.

### 🔹 Limitations of Matching Model

* **Exact matching**:

  * Limited to substring and bag-of-words (word-subset) matches.
* **Fuzzy matching**:

  * Only supports the predefined algorithms listed above.
  * Hybrid scores use predefined aggregation strategies (e.g., mean, median, max) and fixed internal weights.
* **Alternate names**:

  * Only field 10 of UnicodeData.txt is used.
  * No CLDR or extended alias datasets are currently integrated.

### 🔹 Known Issues

* First runs may take several seconds to build the Unicode name cache (logged visibly).
* Unicode normalization can result in differences between visual and textual similarity.
* No support yet for:

  * Learning-based match improvements
  * Interactive fuzzy tuning
* Matching scales linearly with dataset size. While usually <1s, constrained environments may vary.

### 🔹 Embedding Checklist

If embedding CharFinder in a chatbot, server, or interactive app:

* ✅ Pre-build and inject the name cache.
* ✅ Avoid CLI components and stdout printing.
* ✅ Silence or override logging as needed.
* ✅ Benchmark in your production environment.
* ✅ Periodically check and update UnicodeData.txt.

**Summary:**

CharFinder is well-suited for use as both a CLI tool and a Python library. However, when embedding into latency-sensitive or distributed systems, additional considerations are necessary to ensure performance and correctness.

The current matching pipeline is deliberately designed to be static and deterministic—prioritizing **simplicity, reproducibility, and explainability** over dynamic or learning-based behavior.

Support for advanced embedding scenarios (such as pre-injected caches, multi-process sharing, and plugin-based algorithm extension) is planned for future versions.
