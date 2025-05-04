# Makefile for CharFinder
.PHONY: help install test lint build clean publish publish-test

# Show available commands
help:
	@echo "CharFinder Makefile Commands:"
	@echo "  install        Install package and dev dependencies"
	@echo "  test           Run all tests with pytest"
	@echo "  lint           Run basic syntax checks"
	@echo "  build          Build the distribution (wheel and sdist)"
	@echo "  clean          Remove build artifacts"
	@echo "  publish-test   Upload to TestPyPI (safe dry run)"
	@echo "  publish        Disabled for safety (enable manually)"

# Install dependencies in editable mode + dev
install:
	pip install -e .[dev]

# Run tests
test:
	pytest tests --maxfail=1 -v

# Check syntax only
lint:
	python -m py_compile src/charfinder/*.py

# Build the distribution package
build:
	python -m build

# Clean build artifacts
clean:
	python -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ['dist', 'build']]"
	del /q /s *.egg-info 2>nul || exit 0

# Publish to TestPyPI
publish-test:
	twine upload --repository testpypi dist/*

# Disable accidental PyPI publishing
publish:
	@echo "Publishing to PyPI is disabled. Run 'twine upload dist/*' manually if you're sure."
	@exit 1