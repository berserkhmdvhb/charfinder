# Logging System in CharFinder

CharFinder implements a robust, environment-aware logging system designed to:

* Support console and file logging
* Enable configurable log rotation
* Provide clean, colorized, styled output for terminal use
* Centralize control through environment variables

---

## Overview of Logging Architecture

### Modules Involved

* `utils/logger_setup.py`: Main setup logic for file and console handlers
* `utils/logger_helpers.py`: Custom handlers, filters, and formatters
* `utils/logger_styles.py`: Styled formatting of user-facing messages
* `utils/formatter.py`: Unified logging and echo functions for terminal + logger
* `settings.py`: Reads logging config from `.env` and environment variables
* `constants.py`: Defines default values, log filenames, max size, backup count

---

## Logging Initialization

### `get_logger()` from `logger_setup.py`

Sets up a singleton logger instance, applying the following:

* Log level from environment (default: INFO)
* Console handler (stdout)
* Rotating file handler (`CHARFINDER_LOG_FILE`) with rotation config:

  * Max bytes: `CHARFINDER_LOG_MAX_BYTES` (default 1MB)
  * Backup count: `CHARFINDER_LOG_BACKUP_COUNT` (default 2)
* Style-aware formatter (`SafeFormatter`)
* Optional suppression of logging from `colorama`, `urllib3`, etc.

---

## Custom Components

### `CustomRotatingFileHandler`

A subclass of `RotatingFileHandler` that:

* Customizes file naming strategy
* Provides better diagnostics during rollover

### `EnvironmentFilter`

Injects `env` and `level` into log records for structured formatting.

### `SafeFormatter`

Resilient formatter that:

* Avoids crashes due to missing fields
* Ensures safe substitution of record attributes

---

## Styled Logging and Echoing

### `logger_styles.py`

Defines `format_*()` functions for stylized log output:

* `format_debug()` → \[DEBUG]
* `format_info()` → \[INFO]
* `format_warning()` → \[WARNING]
* `format_error()` → \[ERROR]
* `format_settings()` → \[SETTINGS]
* `format_success()` → \[OK]

These use `colorama` (if enabled) to wrap messages in color codes, making logs user-friendly in terminal mode.

---

## Formatter Utilities: `utils/formatter.py`

### `echo()`

Outputs styled messages to:

* Terminal (via `stream.write`)
* Logger (via dynamic method: info/warning/error/etc.)

Supports:

* `show=True/False` to suppress terminal output
* `log=True/False` to trigger logging
* Optional `log_method` (e.g., "info", "debug")

### `log_optionally_echo()`

Primary use: log to file and optionally print to terminal.

Supports:

* `level` (info, warning, debug, etc.)
* Optional styling (e.g., `format_info()`)
* `show=True` to also print styled terminal output

---

## Color Output Logic

### `should_use_color()`

Determines whether to apply color to terminal output based on:

* `always`: force color
* `never`: suppress color
* `auto`: enable if `sys.stdout` is a TTY

This ensures compatibility across different environments and CI runners.

---

## Environment-Driven Configuration

Key environment variables:

| Variable                      | Default           | Description                               |
| ----------------------------- | ----------------- | ----------------------------------------- |
| `CHARFINDER_LOG_FILE`         | `.charfinder.log` | Log output file                           |
| `CHARFINDER_LOG_MAX_BYTES`    | `1048576`         | Max bytes before log rotation (1MB)       |
| `CHARFINDER_LOG_BACKUP_COUNT` | `2`               | How many backup logs to keep              |
| `CHARFINDER_LOG_LEVEL`        | `INFO`            | Logging level: DEBUG, INFO, WARNING, etc. |
| `CHARFINDER_DEBUG_ENV_LOAD`   | `0`               | If 1, prints diagnostic .env info at load |

These are parsed and validated in `settings.py`.

---

## Suppressing Console Log Noise

In several modules (e.g., `formatter.py` and `logger_helpers.py`), log messages are wrapped in `with suppress_console_logging():` when not intended for the user.

This prevents duplicate or unintended output to terminal from underlying libraries or internal loggers.

---

## Logging Best Practices Followed

* Terminal vs. log separation: styled output for users, clean log files for diagnostics
* Color-safe and UTF-8-safe terminal printing
* Lazy imports to reduce startup overhead
* Configurable via `.env` or OS environment without code change
* Fully testable with log stream capture in test suite

---

## Future Improvements

* Move all color constants to `logger_styles.py` to avoid duplication
* Add `CHARFINDER_LOG_FORMAT` as a future setting to allow user-defined log formats
* Support structured JSON log output for CI/CD systems

---
