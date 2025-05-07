from typing import Literal

# Valid Inputs
VALID_FUZZY_ALGOS = ('sequencematcher', 'rapidfuzz', 'levenshtein')
VALID_MATCH_MODES = ('single', 'hybrid')

FuzzyAlgorithm = Literal['sequencematcher', 'rapidfuzz', 'levenshtein']
MatchMode = Literal['single', 'hybrid']

# Exit Codes
EXIT_SUCCESS = 0
EXIT_INVALID_USAGE = 1
EXIT_NO_RESULTS = 2
EXIT_CANCELLED = 130
EXIT_ARGPARSE_ERROR = 2

# Output Constants
FIELD_WIDTHS = {
    'code': 10,
    'char': 3,
    'name': 45,
}