# ---------------------------------------------------------------------
# cli/
# ---------------------------------------------------------------------

# handlers.py

MSG_ERROR_UNKNOWN_VERSION = "unknown (not installed)"
MSG_ERROR_UNEXPECTED_EXCEPTION = "An unexpected error occurred: {error}. See logs for details."
MSG_ERROR_EMPTY_QUERY = "Query must not be empty."
MSG_INFO_SEARCH_CANCELLED = "Search cancelled by user."


# utils_runner.py

MSG_INFO_ENVIRONMENT = "Using environment: {env}"
MSG_WARNING_PROD_ENV = "You are running in PROD environment!"
MSG_INFO_CLI_STARTED = "CharFinder {version} CLI started"
MSG_INFO_QUERY_FINISHED = "Processing finished. Query: '{query}'"
MSG_WARNING_INTERRUPTED = "Execution interrupted by user."
MSG_ERROR_UNHANDLED_EXCEPTION = "Unhandled error during CLI execution"
MSG_ERROR_EXCEPTION_DETAIL = "Error: {error}"


# diagnostics.py

MSG_DEBUG_SECTION_START = "=== DEBUG DIAGNOSTICS ==="
MSG_DEBUG_SECTION_END = "=== END DEBUG DIAGNOSTICS ==="
MSG_DEBUG_PARSED_ARGS = "Parsed args:"
MSG_DEBUG_ARG_ITEM = "{key:<20} = {value}"
MSG_DEBUG_ENV_VAR = "{env_var} = {value}"
MSG_DEBUG_DOTENV_LOADED_FILES = "Loaded .env file(s):"

MSG_DEBUG_DOTENV_START = "=== DOTENV DEBUG ==="
MSG_DEBUG_DOTENV_END = "=== END DOTENV DEBUG ==="
MSG_DEBUG_NO_DOTENV_FOUND = "No .env file found or resolved."
MSG_DEBUG_OS_ENV_ONLY = "Environment variables may only be coming from the OS."
MSG_DEBUG_DOTENV_SELECTED = "Selected .env file: {path}"
MSG_DEBUG_DOTENV_EMPTY = ".env file exists but is empty or contains no key-value pairs."
MSG_DEBUG_DOTENV_READ_ERROR = "Failed to read .env file: {error}"
MSG_DEBUG_DOTENV_ITEM = "{key:<20} = {value}"
MSG_DEBUG_NORMALIZED_QUERY_TOKENS = "Normalized query tokens = {tokens}"

# diagnostics_match.py

MSG_DEBUG_MATCH_SECTION_START = "=== MATCH STRATEGY ==="
MSG_DEBUG_MATCH_SECTION_END = "=== END MATCH STRATEGY ==="

MSG_DEBUG_EXACT_EXECUTED = "Exact match strategy executed."
MSG_DEBUG_EXACT_MODE = "Exact match mode: {mode!r}"

MSG_DEBUG_FUZZY_EXECUTED = "Fuzzy match strategy executed."
MSG_DEBUG_FUZZY_MODE = "Fuzzy match mode: {mode!r}"
MSG_DEBUG_FUZZY_ALGO = "Fuzzy algorithm: {algo!r}"
MSG_DEBUG_HYBRID_AGG_FN = "Aggregation function: {agg_fn!r}"
MSG_DEBUG_HYBRID_ALGOS_HEADER = "Fuzzy algorithms used:"
MSG_DEBUG_HYBRID_ALGO_WEIGHT = "{algo:<22} (weight={weight})"

MSG_DEBUG_FUZZY_NOT_REQUESTED = "Fuzzy matching was not requested."
MSG_DEBUG_PREFER_FUZZY_USED_EXACT = "Fuzzy was preferred but exact match was used."
MSG_DEBUG_FUZZY_SKIPPED_DUE_TO_EXACT = "Fuzzy requested but skipped due to exact match success."


# ---------------------------------------------------------------------
# config/
# ---------------------------------------------------------------------

# settings.py

MSG_WARNING_INVALID_ENV_INT = "Invalid int for '{env_var!r}' = '{value!r}'; using default {default}"
MSG_WARNING_DOTENV_PATH_MISSING = 'DOTENV_PATH is set to "{path}" but the file does not exist.'
MSG_INFO_NO_DOTENV_LOADED = "No .env file loaded — using system env or defaults."


# ---------------------------------------------------------------------
# core/
# ---------------------------------------------------------------------

# handlers.py

MSG_ERROR_QUERY_TYPE = "Query must be a string."
MSG_ERROR_QUERY_EMPTY = "Query string must not be empty."
MSG_ERROR_INVALID_ALGORITHM = "Invalid fuzzy algorithm: {error}"
MSG_INFO_MATCH_FOUND = "Found {n} match(es) for normalized query: '{query}'"
MSG_INFO_MATCH_NOT_FOUND = "No matches found for query: '{query}'"
MSG_DEBUG_REMOVED_DUPLICATE_FUZZY = (
    "Removed {removed_count} duplicate fuzzy match(es) already present in exact results."
)


# matching.py

MSG_UNKNOWN_EXACT_MODE = "Unknown exact match mode: {mode}"
MSG_NO_SCORE_COMPUTED = "Skipped char '{char}' (U+{code:04X}) — no valid score computed."
MSG_FUZZY_START = "No exact match found for '{query}', trying fuzzy..."
MSG_FUZZY_SETTINGS = "[FUZZY] settings: threshold={threshold}, agg_fn={agg_fn}"
MSG_EXACT_CHECKING = "[EXACT] Checking char U+{code:04X}: norm_name='{name}' alt_norm='{alt}'"
MSG_EXACT_MATCH = "[EXACT] query='{query}' matched in {field} for char '{char}'"
MSG_SUBSET_CHECKING = "[EXACT] Checking subset: query_words={query} name_words={name}"
MSG_SUBSET_MATCH = "[EXACT] (subset) for char '{char}'"


# name_cache.py

MSG_INFO_LOAD_SUCCESS = 'Loaded Unicode name cache from: "{path}"'
MSG_ERROR_WRITE_FAIL = "Failed to write cache after multiple attempts."
MSG_INFO_WRITE_SUCCESS = 'Cache written to: "{path}"'
MSG_INFO_REBUILD = "Rebuilding Unicode name cache. This may take a few seconds..."
MSG_ERROR_INVALID_PATH_TYPE = "cache_file_path must be a valid Path object. Got {type}"
MSG_ERROR_INVALID_CACHE_PATH = "Cache file path does not exist. Got {path}"
MSG_WARNING_WRITE_RETRY = (
    "Failed to write cache (attempt {attempt}/{max_attempts}). Retrying in {delay}s..."
)


# unicode_data_loader.py

MSG_ERROR_VALIDATION_FAILED = "Validation failed: {error!s}"
MSG_ERROR_INVALID_URL = "Invalid URL: {url}"
MSG_ERROR_UNSUPPORTED_URL_SCHEME = (
    "Invalid URL scheme '{scheme}' in: {url}. Only HTTP/HTTPS are allowed."
)
MSG_INFO_DOWNLOAD_SUCCESS = 'Downloaded and cached "UnicodeData.txt" from {url}'
MSG_WARNING_DOWNLOAD_FAILED = (
    'Error downloading "UnicodeData.txt": {error}. No local fallback found.'
)
MSG_INFO_LOAD_LOCAL_FILE = 'Loaded "UnicodeData.txt" from local file: {path}'
MSG_WARNING_READ_FAILED = "Failed to read file {path}: {error}"
MSG_WARNING_MALFORMED_LINE = "Skipping malformed line (too few fields): {line}"
MSG_WARNING_INVALID_CODE = "Skipping invalid entry for code {code_hex}: {error}"


# ---------------------------------------------------------------------
# utils/
# ---------------------------------------------------------------------

# formatter.py

MSG_ERROR_ECHO_LOG_METHOD_REQUIRED = "log_method must be provided if log=True"
MSG_ERROR_ECHO_INVALID_LOG_METHOD = "Invalid log_method: {method}. Valid options: {valid_options}"
MSG_DEBUG_FORMAT_MATCH_ERROR = "[Error formatting match: {error!r}] → {match!r}"


# logger_helpers.py

MSG_WARNING_DELETE_OLD_LOG_FAILED = "Failed to delete old log file: {path}"
MSG_WARNING_DELETE_ROLLOVER_TARGET_FAILED = "Failed to delete rollover target: {path}"
MSG_WARNING_DELETE_EXISTING_ROLLOVER_FAILED = "Failed to delete existing rollover log: {path}"

# logger_setup.py

MSG_INFO_LOGGING_INITIALIZED = (
    'Logging initialized. Log file: "{path}" (maxBytes={max_bytes}, backupCount={backup_count})'
)


# normalizer.py

MSG_ERROR_NORMALIZATION_FAILED = "Error normalizing text: {error}"


# ---------------------------------------------------------------------
# root/
# ---------------------------------------------------------------------

# fuuzymatchlib.py

MSG_ERROR_AGG_FN_UNEXPECTED = "Unexpected aggregation function: {agg_fn!r}"
MSG_ERROR_UNSUPPORTED_ALGO_INPUT = (
    "Invalid fuzzy algorithm. Got: '{name}'. Valid options: {valid_options}"
)
MSG_ERROR_ALGO_NOT_FOUND = (
    "Invalid fuzzy algorithm. It's missing from registry FUZZY_ALGORITHM_REGISTRY. Got: {algorithm}"
)

# validators.py

MSG_ERROR_INVALID_THRESHOLD = "Invalid threshold used."
MSG_ERROR_INVALID_THRESHOLD_TYPE = "Threshold must be a float or int."
MSG_ERROR_INVALID_NAME = "Normalized name must be a non-empty string. Got {value!r}"
MSG_ERROR_EXPECTED_BOOL = "Expected a boolean value. Got {type}"
MSG_ERROR_EXPECTED_DICT = "Expected a dictionary for name cache."
MSG_ERROR_EXPECTED_DICT_KEY = (
    "Expected string keys in name cache dictionary. Found key of type {type} for key: {key}"
)
MSG_ERROR_EXPECTED_DICT_VAL = (
    "Expected dictionary values in name cache. Found value of types {type} for key: {key}"
)
MSG_ERROR_EXPECTED_PATH = "Expected a Path object for cache file"
MSG_ERROR_MISSING_FUZZY_ALGO_VALUE = "Missing fuzzy algorithm value."
MSG_ERROR_EMPTY_FUZZY_ALGO_LIST = "Empty list of fuzzy algorithm values."
MSG_ERROR_INVALID_OUTPUT_FORMAT = (
    "Invalid output format. Got {format}. Valid options: {valid_options}"
)
MSG_ERROR_INVALID_AGG_FUNC = (
    "Invalid aggregation function for hybrid mode. Got {func}. Valid options: {valid_options}"
)
MSG_ERROR_ENV_INVALID_THRESHOLD = "Invalid {env_var} env var: {value!r}. Using default."
MSG_ERROR_INVALID_COLOR_MODE_WITH_VALUE = (
    "Invalid color mode. Got: {value}. Valid options: {valid_options}"
)
MSG_ERROR_INVALID_FUZZY_MATCH_MODE = (
    "Invalid fuzzy match mode. Got {value}. Valid options: {valid_options}"
)
MSG_ERROR_INVALID_EXACT_MATCH_MODE = (
    "Invalid exact match mode. Got {value}. Valid options: {valid_options}"
)
MSG_ERROR_FILE_NOT_FOUND = "The file {path} does not exist."
MSG_ERROR_EXPECTED_NAME_CACHE_DICT = "Expected name_cache to be a dict."
MSG_ERROR_INVALID_NAME_CACHE_ENTRY_TYPE = "Invalid entry for {key!r}: expected a dict."
MSG_ERROR_MISSING_NAME_CACHE_KEYS = (
    "Missing required keys in name_cache entry for {key!r}. "
    "Expected keys: 'original', 'normalized'."
)
MSG_ERROR_INVALID_NORMALIZATION_PROFILE = (
    "Invalid normalization profile. Got '{value}' from {source}. Valid options: {valid_options}."
)
MSG_ERROR_INVALID_SHOW_SCORE_VALUE = (
    "Invalid value for --show-score. Got {value}. Valid options: {valid_options}"
)
