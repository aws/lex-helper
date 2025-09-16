# Makefile for lex-helper documentation development

.PHONY: help docs-serve docs-build docs-test docs-clean docs-install

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

docs-install: ## Install documentation dependencies
	uv sync --group docs

docs-serve: ## Start the documentation development server with live reload
	@echo "Starting documentation development server..."
	@echo "Visit http://127.0.0.1:8000 to view the documentation"
	uv run python scripts/serve-docs.py

docs-build: ## Build the documentation
	uv run mkdocs build --clean

docs-test: ## Test the documentation build and check for issues
	uv run python scripts/test-docs.py

docs-clean: ## Clean the documentation build directory
	rm -rf site/

docs-deploy: ## Deploy documentation to GitHub Pages (for maintainers)
	uv run mkdocs gh-deploy --clean

# Development shortcuts
serve: docs-serve ## Alias for docs-serve
build: docs-build ## Alias for docs-build
test: docs-test ## Alias for docs-test