.PHONY: help install install-dev format format-check mypy ruff lint test test-fast coverage coverage-xml check-all precommit precommit-run build clean publish publish-test upload-coverage

help:
	@echo "CharFinder Makefile Commands:"
	@echo "  install            Install package only"
	@echo "  install-dev        Install dev dependencies"
	@echo "  format             Format code using black"
	@echo "  format-check       Check formatting using black --check"
	@echo "  mypy               Run type checking (excludes *.ipynb)"
	@echo "  ruff               Run Ruff linter (excludes *.ipynb)"
	@echo "  lint               Run static checks (ruff + mypy)"
	@echo "  test               Run all tests with pytest"
	@echo "  test-fast          Run failing or last tests quickly"
	@echo "  coverage           Run tests with coverage report"
	@echo "  coverage-xml       Run tests with coverage report and generate coverage.xml"
	@echo "  check-all          Run format-check, mypy, ruff, and test"
	@echo "  precommit          Install pre-commit hook"
	@echo "  precommit-run      Run all pre-commit hooks"
	@echo "  build              Build package for distribution"
	@echo "  clean              Remove build artifacts"
	@echo "  publish-test       Upload to TestPyPI"
	@echo "  publish            Upload to PyPI"
	@echo "  upload-coverage    Upload coverage to Coveralls"

install:
	pip install -e .

install-dev:
	pip install --upgrade pip
	pip install -e .[dev]

format:
	black src tests

format-check:
	black --check src tests

mypy:
	mypy src tests --exclude '.*\.ipynb'

ruff:
	ruff check src tests --exclude '*.ipynb'

lint: ruff mypy

test:
	pytest tests --maxfail=1 -v

test-fast:
	pytest --lf -x -v

coverage:
	pytest --cov=charfinder --cov-report=term

coverage-xml:
	pytest --cov=charfinder --cov-report=term --cov-report=xml

check-all: format-check mypy ruff test

precommit:
	pre-commit install

precommit-run:
	pre-commit run --all-files

upload-coverage:
	coveralls

build:
	python -m build

clean:
	python -c "import shutil, glob; [shutil.rmtree(p, ignore_errors=True) for p in ['dist', 'build'] + glob.glob('*.egg-info')]"

publish-test:
	twine upload --repository testpypi dist/*

publish:
	twine check dist/*
	twine upload dist/*