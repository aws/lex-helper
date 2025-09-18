# Makefile for lex-helper documentation development

.PHONY: help docs-serve docs-build docs-test docs-clean docs-install

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

docs-install: ## Install documentation dependencies
	uv sync --group docs

docs-serve: docs-install ## Start the documentation development server with live reload
	@echo "Starting documentation development server..."
	@echo "Visit http://127.0.0.1:8000 to view the documentation"
	uv run python scripts/serve-docs.py

docs-build: ## Build the documentation
	uv run mkdocs build --clean

docs-test: ## Test the documentation build and check for issues
	uv run python scripts/test-docs.py

docs-qa: ## Run comprehensive quality assurance checks
	@echo "Running comprehensive quality assurance checks..."
	@echo "Building documentation..."
	uv run mkdocs build --clean
	@echo "Validating code examples..."
	uv run python scripts/validate-code-examples.py docs/
	@echo "Checking internal links (ignoring safe external references)..."
	uv run python scripts/check-links.py ./site
	@echo "Checking accessibility (ignoring theme-related issues)..."
	-uv run python scripts/check-accessibility.py ./site
	@echo "Checking spelling (warnings allowed)..."
	-uv run python scripts/check-spelling.py docs/
	@echo "Quality assurance checks completed!"

docs-qa-full: ## Run full quality assurance checks including external links
	@echo "Running full quality assurance checks..."
	@echo "Building documentation..."
	uv run mkdocs build --clean
	@echo "Validating code examples..."
	uv run python scripts/validate-code-examples.py docs/
	@echo "Checking internal links..."
	uv run python scripts/check-links.py ./site
	@echo "Checking external links..."
	-uv run python scripts/check-links.py ./site --external
	@echo "Checking accessibility..."
	uv run python scripts/check-accessibility.py ./site
	@echo "Checking spelling..."
	-uv run python scripts/check-spelling.py docs/
	@echo "Full quality assurance checks completed!"

docs-clean: ## Clean the documentation build directory
	rm -rf site/

docs-deploy: ## Deploy documentation to GitHub Pages (for maintainers)
	uv run mkdocs gh-deploy --clean

# Development shortcuts
serve: docs-serve ## Alias for docs-serve
build: docs-build ## Alias for docs-build
test: docs-test ## Alias for docs-test
qa: docs-qa ## Alias for docs-qa
