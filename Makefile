.PHONY: install clean clean-media clean-cards clean-test test test-cov lint format format-check lint-fix check help

.DEFAULT_GOAL := install

install:  ## Install the CLI tool globally
	uv tool install .

check:  ## Run all checks (lint, format-check, test)
	@$(MAKE) lint
	@$(MAKE) format-check
	@uv run pytest tests/ -q

format:  ## Format code with ruff
	uv run ruff format .

format-check:  ## Check if code is formatted
	uv run ruff format --check .

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

lint:  ## Run ruff linter
	uv run ruff check .

lint-fix:  ## Run ruff linter with auto-fix
	uv run ruff check --fix .

reinstall:  ## Reinstall the CLI tool (useful after code changes)
	uv tool install --force .

uninstall:  ## Uninstall the CLI tool
	uv tool uninstall ankicard

clean-media:  ## Remove generated media files (audio and images)
	rm -rf anki_media/
	@echo "Cleaned media files"

clean-cards:  ## Remove generated Anki card files
	rm -rf anki_cards/
	@echo "Cleaned card files"

clean-test:  ## Remove test and coverage artifacts
	rm -rf .pytest_cache/ htmlcov/ .coverage
	@echo "Cleaned test artifacts"

clean:  ## Remove all generated files (media, cards, and test artifacts)
	@$(MAKE) clean-media
	@$(MAKE) clean-cards
	@$(MAKE) clean-test

test:  ## Run all tests
	uv run pytest tests/ -v

test-cov:  ## Run tests with coverage report
	uv run pytest tests/ --cov=src/ankicard --cov-report=term-missing

version:  ## Show installed version
	ankicard --version
