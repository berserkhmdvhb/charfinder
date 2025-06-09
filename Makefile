.PHONY: all help install develop \
        fmt fmt-check lint-ruff type-check lint-all lint-all-check \
        test test-file test-file-function test-fast testing \
        test-coverage test-coverage-xml test-cov-html test-coverage-rep test-coverage-file clean-coverage \
        check-all test-watch \
        precommit precommit-run precommit-check \
        env-check env-debug env-clear env-show dotenv-debug env-example \
        safety check-updates check-toml \
        build clean clean-pyc clean-all \
        publish publish-test publish-dryrun upload-coverage

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
PYTHON := python

# -------------------------------------------------------------------
# Default
# -------------------------------------------------------------------
all: help

# -------------------------------------------------------------------
# Help
# -------------------------------------------------------------------
help::
	@echo "Available Makefile commands:"
	@echo ""
	@echo "  install                Install the package in editable mode"
	@echo "  develop                Install with all dev dependencies"
	@echo ""
	@echo "  fmt                    Auto-format code using Ruff"
	@echo "  fmt-check              Check code formatting (dry run)"
	@echo "  lint-ruff              Run Ruff linter"
	@echo "  type-check             Run MyPy static type checker"
	@echo "  lint-all               Run formatter, linter, and type checker"
	@echo "  lint-all-check         Dry run: check formatting, lint, and types"
	@echo ""
	@echo "  test                   Run all tests using Pytest"
	@echo "  test-file              Run a single test file or keyword with FILE=... (e.g. make test-file FILE=tests/cli/test_main.py)"
	@echo "  test-file-function     Run a specific test function with FILE=... FUNC=... (e.g. make test-file-function FILE=tests/test_settings.py FUNC=test_no_dotenv_file)"
	@echo "  test-fast              Run only last failed tests"
	@echo ""
	@echo "  test-coverage          Run tests and show terminal coverage summary"
	@echo "  test-coverage-xml      Run tests and generate XML coverage report"
	@echo "  test-cov-html          Run tests with HTML coverage report and open it"
	@echo "  test-coverage-rep      Show full line-by-line coverage report"
	@echo "  test-coverage-file     Show coverage for a specific file: FILE=... (e.g. make test-coverage-file FILE=src/charfinder/cli/cli_main.py)"
	@echo "  clean-coverage         Erase cached coverage data"
	@echo ""
	@echo "  test-watch             Auto-rerun tests on file changes"
	@echo "  check-all              Run format-check, lint, and full test suite"
	@echo ""
	@echo "  precommit              Install pre-commit hook"
	@echo "  precommit-check        Dry run all pre-commit hooks"
	@echo "  precommit-run          Run all pre-commit hooks"
	@echo ""
	@echo "  env-check              Show Python and environment info"
	@echo "  env-debug              Show debug-related env info"
	@echo "  env-clear              Unset CHAFRINDER_* and DOTENV_PATH environment variables"
	@echo "  env-show               Show currently set CHAFRINDER_* and DOTENV_PATH variables"
	@echo "  env-example            Show example env variable usage"
	@echo "  dotenv-debug           Show debug info from dotenv loader"
	@echo ""
	@echo "  safety                 Check dependencies for vulnerabilities"
	@echo "  check-updates          List outdated pip packages"
	@echo "  check-toml             Check pyproject.toml for syntax validity"
	@echo ""
	@echo "  build                  Build package for distribution"
	@echo "  clean                  Remove build artifacts"
	@echo "  clean-pyc              Remove .pyc and __pycache__ files"
	@echo "  clean-all              Remove all build, test, and log artifacts"
	@echo ""
	@echo "  publish-test           Upload to TestPyPI"
	@echo "  publish-dryrun         Validate and simulate TestPyPI upload (dry run)"
	@echo "  publish                Upload to PyPI"
	@echo "  upload-coverage        Upload coverage report to Coveralls"

# -------------------------------------------------------------------
# Install & Development
# -------------------------------------------------------------------
install:
	$(PYTHON) -m pip install -e .

develop:
	$(PYTHON) -m pip install -e .[dev]

# -------------------------------------------------------------------
# Formatting
# -------------------------------------------------------------------
fmt:
	ruff format src/ tests/

fmt-check:
	ruff format --check src/ tests/

# -------------------------------------------------------------------
# Linting / Type Checking
# -------------------------------------------------------------------
lint-ruff:
	ruff check src/ tests/

type-check:
	mypy src/

lint-all: fmt lint-ruff type-check

lint-all-check: fmt-check lint-ruff type-check

# -------------------------------------------------------------------
# Testing
# -------------------------------------------------------------------
test:
	$(PYTHON) -m pytest tests/ -v

test-file:
	@$(PYTHON) -c "import sys; f = '$(FILE)'; sys.exit(0) if f else (print('Usage: make test-file FILE=path/to/file.py'), sys.exit(1))"
	$(PYTHON) -m pytest $(FILE) -v

test-file-function:
	@$(PYTHON) -c "import sys; f = '$(FILE)'; func = '$(FUNC)'; sys.exit(0) if f and func else (print('Usage: make test-file-function FILE=path/to/file.py FUNC=function_name'), sys.exit(1))"
	$(PYTHON) -m pytest $(FILE)::$(FUNC) -v

test-fast:
	$(PYTHON) -m pytest --lf -x -v

test-coverage:
	$(PYTHON) -m pytest --cov=charfinder --cov-report=term --cov-fail-under=95

test-coverage-xml:
	$(PYTHON) -m pytest --cov=charfinder --cov-report=term --cov-report=xml

test-cov-html:
	$(PYTHON) -m pytest --cov=charfinder --cov-report=html
	$(PYTHON) -c "import webbrowser; webbrowser.open('htmlcov/index.html')"

test-coverage-rep:
	coverage report -m

test-coverage-file:
	@$(PYTHON) -c "import sys; f = '$(FILE)'; sys.exit(0) if f else (print('Usage: make test-coverage-file FILE=path/to/file.py'), sys.exit(1))"
	coverage report -m $(FILE)

clean-coverage:
	coverage erase

testing: test-cov-html

check-all: lint-all-check test-coverage

test-watch:
	ptw --runner "$(PYTHON) -m pytest -v" tests/

# -------------------------------------------------------------------
# Pre-commit Hooks
# -------------------------------------------------------------------
precommit:
	pre-commit install

precommit-check:
	pre-commit run --all-files --hook-stage manual --verbose --show-diff-on-failure --color always --config .pre-commit-config.yaml

precommit-run:
	pre-commit run --all-files

# -------------------------------------------------------------------
# Environment & Debugging
# -------------------------------------------------------------------
env-check:
	@echo "Python: $$(python --version)"
	@$(PYTHON) -c "import sys; print('Virtualenv:', sys.executable)"
	@echo "Environment: $${CHARFINDER_ENV:-not set}"

env-debug:
	@echo "Debug: $${CHARFINDER_DEBUG_ENV_LOAD:-not set}"

env-clear:
	@echo "Clearing selected CHARFINDER_* and DOTENV_PATH environment variables..."
	@$(PYTHON) -c "import os; vars = ['CHARFINDER_ENV', 'CHARFINDER_LOG_MAX_BYTES', 'CHARFINDER_LOG_BACKUP_COUNT', 'CHARFINDER_LOG_LEVEL', 'CHARFINDER_DEBUG_ENV_LOAD', 'DOTENV_PATH']; [print(f'  Unsetting {v}') or os.environ.pop(v, None) for v in vars if v in os.environ]"

env-show:
	@echo "Currently set CHARFINDER_* and DOTENV_PATH environment variables:"
	@$(PYTHON) -c "import os; [print(f'  {k}={v}') for k, v in os.environ.items() if k.startswith('CHARFINDER_') or k == 'DOTENV_PATH']"

env-example:
	@echo "Example usage:"
	@echo "  export CHARFINDER_ENV=dev"
	@echo "  export CHARFINDER_DEBUG_ENV_LOAD=1"

dotenv-debug:
	@echo "==> Debugging dotenv loading via print_dotenv_debug()"
	$(PYTHON) -c "import logging; logging.basicConfig(level=logging.INFO); from charfinder.settings import print_dotenv_debug; print_dotenv_debug()"

# -------------------------------------------------------------------
# Security & Dependency Management
# -------------------------------------------------------------------
safety:
	safety scan

check-updates:
	$(PYTHON) -m pip list --outdated

check-toml:
	@$(PYTHON) -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb')); print('pyproject.toml syntax is valid')"

# -------------------------------------------------------------------
# Build & Distribution
# -------------------------------------------------------------------
build:
	$(PYTHON) -m build

clean:
	$(PYTHON) -c "import shutil, glob; [shutil.rmtree(p, ignore_errors=True) for p in ['dist', 'build'] + glob.glob('*.egg-info')]"

clean-pyc:
	@echo "Removing .pyc and __pycache__ files..."
	$(PYTHON) -c "import pathlib, shutil; [p.unlink() for p in pathlib.Path('.').rglob('*.pyc')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"

clean-all: clean clean-pyc
	@echo "Removing logs and cache files..."
	$(PYTHON) -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.log')]"
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in map(pathlib.Path, ['.pytest_cache', '.mypy_cache', '.ruff_cache', 'htmlcov']) if p.exists()]"
	$(PYTHON) -c "import pathlib; [p.unlink() for p in map(pathlib.Path, ['.coverage', 'coverage.xml']) if p.exists()]"

publish-test:
	twine check dist/*
	twine upload --repository testpypi dist/*

publish-dryrun:
	twine check dist/*
	twine upload --repository testpypi --skip-existing --non-interactive dist/*

publish:
	twine check dist/*
	twine upload dist/*

upload-coverage:
	coveralls