# Environment and Logging Scenarios

This document outlines how CharFinder handles **environment configuration** and **logging setup** across different environments (DEV, UAT, PROD, TEST). It reflects the current design in `settings.py`, providing insight into dotenv resolution, environment detection, and dynamic logging paths.

## Overview

CharFinder separates configuration from code by using environment variables and `.env` files. This approach ensures flexible, testable, and secure deployment across different environments (DEV, UAT, PROD, TEST).

---

## 1. Configuration Flow (Environment Resolution)

CharFinder supports a robust but minimal configuration strategy. It prioritizes **explicit user overrides** while maintaining safe fallbacks to default `.env` or system variables. The main configuration flow is implemented in `settings.py`.

### 🔁 Resolution Order

The following logic is used to resolve environment settings:

1. `DOTENV_PATH` (environment variable) — explicit override
2. `.env` (project root) — default fallback if exists
3. System environment — fallback for all undefined vars

A debug flag `CHARFINDER_DEBUG_ENV_LOAD=1` can be used to emit detailed output during resolution (e.g., missing file warnings).

### 📦 Detected Environment (CHARFINDER\_ENV)

The environment is determined by `CHARFINDER_ENV`, which defaults to `DEV`.

* `DEV`, `UAT`, `PROD`, and `TEST` are recognized
* `TEST` can also be inferred if `PYTEST_CURRENT_TEST` is set

Environment-specific logic is implemented via:

```python
get_environment()
is_dev(), is_uat(), is_prod(), is_test_mode(), is_test()
```

---

## 2. Environment Priority Table

The table below summarizes how `.env` and environment variables are resolved:

| Priority | Source                | Loaded When                           | Purpose / Notes                             | Git Tracked? | Overrides Others? |
| -------- | --------------------- | ------------------------------------- | ------------------------------------------- | ------------ | ----------------- |
| 1️⃣      | `DOTENV_PATH` env var | Set explicitly                        | Force use of specific `.env` file           | ❌            | ✅                 |
| 2️⃣      | `.env` in root dir    | File exists and `DOTENV_PATH` not set | Main project config file (default fallback) | ✅            | ✅ (if present)    |
| 3️⃣      | System Environment    | No `.env` file found                  | Final fallback for all values               | N/A          | ✅                 |

🧪 If `CHARFINDER_ENV=TEST` or `PYTEST_CURRENT_TEST` is set, **test mode** is activated.

🔍 If `CHARFINDER_DEBUG_ENV_LOAD=1` is set, you’ll see debug output (e.g., warnings about missing `.env` paths).

---

## 3. Logging Behavior by Environment

The log system is configured dynamically based on the current environment. Logs are stored under `logs/{ENV}/`, such as `logs/DEV/`, `logs/PROD/`, etc.

### Paths and Rotation:

* `get_log_dir()` returns the correct log path.
* Log files are subject to rotation, using these env-controlled settings:

  * `CHARFINDER_LOG_MAX_BYTES` (default: 1\_000\_000 bytes)
  * `CHARFINDER_LOG_BACKUP_COUNT` (default: 5)

These are resolved using the `safe_int()` utility to guard against invalid values.

---

## 4. Related Modules

* [`settings.py`](../charfinder/settings.py): core environment logic
* [`logger_setup.py`](../charfinder/utils/logger_setup.py): initializes logging handlers
* [`env-logging-scenarios.md`](./env-logging-scenarios.md): end-to-end .env and logging scenarios, edge cases, fallback resolution.
* [`logging_system.md`](./logging_system.md): implementation and formatter details for logging

---

## 5. Summary

CharFinder uses a lightweight, explicit-first environment strategy:

* `.env` is optional but supported
* Users can override via `DOTENV_PATH`
* Logging is environment-aware and rotatable
* Debug output available via `CHARFINDER_DEBUG_ENV_LOAD`

This setup enables consistent behavior in development, production, and test environments, while preserving developer flexibility and test isolation.
