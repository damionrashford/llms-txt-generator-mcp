.PHONY: help install install-dev test lint format clean build publish

help: ## Show this help message
	@echo "LLMs.txt Generator Framework - Development Commands"
	@echo "=================================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=llms_txt_generator --cov-report=html --cov-report=term

lint: ## Run linting checks
	flake8 src/ tests/
	mypy src/

format: ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

format-check: ## Check code formatting
	black --check src/ tests/
	isort --check-only src/ tests/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

build: ## Build the package
	python -m build

publish: ## Publish to PyPI (requires twine)
	twine upload dist/*

example: ## Run example generation
	python generate_llms_txt.py https://example.com

example-output: ## Run example with custom output directory
	python generate_llms_txt.py https://example.com ./example_output

server: ## Run the MCP server
	python server.py

server-dev: ## Run the MCP server in development mode
	python -u server.py

check: format-check lint test ## Run all checks (format, lint, test)
