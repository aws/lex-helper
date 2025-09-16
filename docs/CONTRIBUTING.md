# Contributing to lex-helper

Thank you for your interest in contributing to lex-helper! This guide will help you get started with development and ensure your contributions meet our quality standards.

## 🚀 Quick Start

### 1. Development Setup

```bash
# Clone the repository
git clone https://github.com/aws/lex-helper.git
cd lex-helper

# Install dependencies with uv
uv sync --group docs --group dev

# Install pre-commit hooks
pre-commit install
```

### 2. Pre-commit Quality Checks

We use pre-commit hooks to maintain code and documentation quality. The hooks will automatically run when you commit changes and include:

#### Code Quality Checks
- **Ruff** - Linting and formatting (replaces flake8 + black)
- **Pyright** - Type checking
- **Pytest** - Test suite execution

#### Documentation Quality Checks
- **Code Example Validation** - Ensures all code snippets are syntactically correct
- **Documentation Build Test** - Verifies docs build successfully
- **Link Integrity Check** - Validates internal and external links
- **Basic Accessibility Check** - Ensures WCAG compliance

### 3. Running Checks Manually

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run specific hooks
pre-commit run ruff --all-files
pre-commit run docs-quality-check --all-files

# Run comprehensive documentation QA
make docs-qa

# Run individual documentation checks
python scripts/validate-code-examples.py docs/
python scripts/check-links.py ./site
python scripts/check-accessibility.py ./site
```

## 📝 Documentation Contributions

### Writing Guidelines

1. **Code Examples Must Be Valid**
   - All Python code snippets must be syntactically correct
   - Use comments for incomplete code: `# Example implementation`
   - Add implementation stubs: `pass  # Implementation details`

2. **Link Integrity**
   - All internal links must work
   - External links are checked but won't fail builds
   - Use relative paths for internal documentation links

3. **Accessibility Standards**
   - Images must have descriptive alt text
   - Tables should have headers and captions when appropriate
   - Headings should follow proper hierarchy (H1 → H2 → H3)

### Documentation Structure

```
docs/
├── getting-started/     # New user guides
├── guides/             # Feature-specific guides
├── tutorials/          # Step-by-step tutorials
├── api/               # API reference
├── advanced/          # Advanced topics
├── examples/          # Code examples
├── community/         # Community resources
└── migration/         # Migration guides
```

### Testing Documentation Changes

```bash
# Quick validation (runs in pre-commit)
python scripts/pre-commit-docs-check.py docs/your-file.md

# Comprehensive validation
make docs-qa

# Local development server
make docs-serve
```

## 🧪 Code Contributions

### Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write code following our style guidelines
   - Add comprehensive type hints
   - Include docstrings for public APIs

3. **Add Tests**
   ```bash
   # Run tests
   uv run pytest

   # Run with coverage
   uv run pytest --cov=lex_helper
   ```

4. **Update Documentation**
   - Update relevant documentation files
   - Add code examples for new features
   - Update API documentation if needed

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

   Pre-commit hooks will automatically run and validate your changes.

### Code Style Guidelines

We use **Ruff** for both linting and formatting:

```bash
# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

**Key Style Points:**
- Use type hints for all function parameters and return values
- Follow PEP 8 naming conventions
- Maximum line length: 125 characters
- Use double quotes for strings
- Add docstrings for all public functions and classes

### Type Checking

We use **Pyright** for type checking:

```bash
# Run type checking
uv run pyright lex_helper/
```

**Type Checking Guidelines:**
- All public APIs must have complete type annotations
- Use typing module for complex types
- Prefer modern syntax: `list[str]` over `List[str]`
- Use Union types: `Union[T, None]` instead of `Optional[T]`

## 🔧 Quality Assurance

### Automated Checks

Our QA system includes:

1. **Pre-commit Hooks** - Run on every commit
2. **GitHub Actions** - Run on every push/PR
3. **Manual Commands** - For comprehensive testing

### Quality Standards

- **Zero tolerance** for syntax errors in code examples
- **All links must work** (except safe external references)
- **Accessibility compliance** (WCAG guidelines)
- **Type safety** with comprehensive type hints
- **Test coverage** for new functionality

### Troubleshooting Common Issues

#### Pre-commit Hook Failures

```bash
# If hooks fail, fix the issues and re-commit
git add .
git commit -m "fix: address pre-commit issues"

# Skip hooks only in emergencies
git commit --no-verify -m "emergency: skip hooks"
```

#### Documentation Build Failures

```bash
# Check for syntax errors in markdown
python scripts/validate-code-examples.py docs/

# Check for broken links
make docs-qa

# Debug specific issues
mkdocs build --clean --verbose
```

#### Type Checking Failures

```bash
# Run type checking with detailed output
uv run pyright lex_helper/ --verbose

# Fix common issues:
# - Add missing type hints
# - Import required types from typing module
# - Use proper generic syntax
```

## 📋 Pull Request Process

1. **Ensure All Checks Pass**
   - Pre-commit hooks pass
   - All tests pass
   - Documentation builds successfully
   - No type checking errors

2. **Write a Clear Description**
   - Explain what the change does
   - Reference any related issues
   - Include testing instructions

3. **Request Review**
   - Add appropriate reviewers
   - Respond to feedback promptly
   - Update documentation as needed

4. **Merge Requirements**
   - All CI checks must pass
   - At least one approving review
   - Up-to-date with main branch

## 🆘 Getting Help

- **Documentation Issues**: Run `make docs-qa` for detailed analysis
- **Code Issues**: Check the test suite with `uv run pytest -v`
- **General Questions**: Open a GitHub issue with the `question` label

## 🎯 Quality Metrics

We maintain high quality standards:

- **Code Coverage**: >90% for core functionality
- **Type Coverage**: 100% for public APIs
- **Documentation**: All features must be documented
- **Accessibility**: WCAG 2.1 AA compliance
- **Performance**: No regressions in benchmarks

Thank you for contributing to lex-helper! 🚀
