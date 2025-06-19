## ⚡ Performance

`charfinder` is designed with a focus on speed, efficiency, and responsiveness—even when processing the entire Unicode space (1.1M+ code points).

#### Key Optimizations

* **Unicode Name Caching**

  * The Unicode name cache is built once and stored as a local JSON file.
  * On subsequent runs, the cache is loaded instantly, enabling fast lookups.

* **Normalization Caching**

  * The `cached_normalize()` function uses an LRU cache to avoid redundant Unicode normalization calls.
  * This significantly speeds up matching, especially for fuzzy modes where many comparisons are performed.

* **Matching Optimizations**

  * Exact match mode uses fast `in` and set operations.
  * Fuzzy match mode supports multiple optimized algorithms:

    * `rapidfuzz` (fastest)
    * `Levenshtein` (optimized C extension)
    * `SequenceMatcher` (Python stdlib baseline)

* **Efficient CLI Output**

  * Result rows are streamed lazily via generators.
  * Logging and console output are buffered to minimize I/O overhead.

#### Benchmarks (Informal)

| Query                   | Match Mode      | Time (1st run) | Time (cached) |
| ----------------------- | --------------- | -------------- | ------------- |
| `snowman`               | exact           | \~40ms         | \~5ms         |
| `snwmn` (fuzzy)         | fuzzy+rapidfuzz | \~150ms        | \~25ms        |
| `grnning face` (hybrid) | fuzzy+hybrid    | \~200ms        | \~35ms        |

*Tests run on Python 3.12, macOS M2 Pro, full Unicode set.*

#### Profiling Tips

* To profile CLI runs:

  ```bash
  python -m cProfile -m charfinder -q heart --fuzzy
  ```
* To profile library calls:

  ```python
  import cProfile
  cProfile.run("list(find_chars('heart', fuzzy=True))")
  ```

#### Future Improvements

* Smarter pre-filtering to skip unrelated blocks.
* Parallelization of fuzzy matching (via joblib or multiprocessing).
* Optional faster UnicodeData loaders (binary format).
* Support for custom user-provided fuzzy match algorithms (plugin architecture)
