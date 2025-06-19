from typing import Literal

# Literal-based type aliases
FuzzyAlgorithm = Literal[
    "sequencematcher",
    "rapidfuzz",
    "levenshtein_ratio",
    "simple_ratio",
    "normalized_ratio",
    "token_sort_ratio",
    "hybrid_score",
]

ExactMatchMode = Literal["substring", "word-subset"]
FuzzyMatchMode = Literal["single", "hybrid"]
ColorMode = Literal["auto", "always", "never"]
HybridAggFunc = Literal["mean", "median", "max", "min"]
OutputFormat = Literal["text", "json"]
NormalizationForm = Literal["NFC", "NFD", "NFKC", "NFKD"]
