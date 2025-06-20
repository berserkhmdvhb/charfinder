from typing import Literal

__all__ = [
    "ColorMode",
    "ExactMatchMode",
    "FuzzyAlgorithm",
    "FuzzyMatchMode",
    "HybridAggFunc",
    "NormalizationForm",
    "NormalizationProfile",
    "OutputFormat",
]


# Literal-based type aliases
FuzzyAlgorithm = Literal[
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
NormalizationProfile = Literal["raw", "light", "medium", "aggressive"]
ShowScore = Literal["true", "1", "yes", "false", "0", "no"]
