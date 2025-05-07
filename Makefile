.PHONY: help install test lint build clean publish publish-test coverage format check

help:
	@echo "CharFinder Makefile Commands:"
	@echo "  install        Install package and dev dependencies"
	@echo "  test           Run all tests with pytest"
	@echo "  coverage       Run tests with coverage report in terminal"
	@echo "  lint           Run basic syntax checks"
	@echo "  format         Format code using black"
	@echo "  check          Check formatting with black --check"
	@echo "  build          Build the distribution (wheel and sdist)"
	@echo "  clean          Remove build artifacts"
	@echo "  publish-test   Upload to TestPyPI (safe dry run)"
	@echo "  publish        Upload to PyPI (requires credentials)"

install:
	pip install -e .[dev]

test:
	pytest tests --maxfail=1 -v

coverage:
	pytest --cov=charfinder --cov-report=term

lint:
	python -m py_compile src/charfinder/*.py

format:
	black src tests

check:
	black --check src tests

build:
	python -m build

clean:
	python -c "import shutil, glob; [shutil.rmtree(p, ignore_errors=True) for p in ['dist', 'build'] + glob.glob('*.egg-info')]"

publish-test:
	twine upload --repository testpypi dist/*

publish:
	twine check dist/*
	twine upload dist/*