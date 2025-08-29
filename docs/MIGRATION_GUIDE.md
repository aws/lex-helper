# Migration Guide: Poetry to uv and Modern Python Tooling

This guide explains the migration from Poetry to uv for dependency management, replacement of flake8/black with Ruff, and implementation of pre-commit hooks and GitHub Actions.

## Overview of Changes

### What Changed
- **Dependency Management**: Poetry → uv
- **Linting**: flake8 → Ruff
- **Formatting**: black → Ruff (unified tool)
- **Pre-commit**: New automated quality checks
- **CI/CD**: GitLab CI → GitHub Actions
- **Configuration**: Consolidated into pyproject.toml

### What Stayed the Same
- **Type Checking**: pyright (unchanged)
- **Testing**: pytest with coverage (unchanged)
- **Python Version**: >= 3.12 (unchanged)
- **Package Structure**: No changes to import paths or APIs

## Quick Start for Existing Developers

### 1. Install uv
```bash
# Install uv (if not already installed)
pip install uv

# Or using homebrew on macOS
brew install uv
```

### 2. Set Up Development Environment
```bash
# Install all dependencies (including dev dependencies)
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install
```

### 3. Verify Setup
```bash
# Run tests to ensure everything works
uv run pytest

# Run code quality checks
uv run ruff check .
uv run ruff format .
```

## Command Migration Reference

### Dependency Management

| Old (Poetry) | New (uv) | Description |
|--------------|----------|-------------|
| `poetry install` | `uv sync` | Install dependencies |
| `poetry install --with dev` | `uv sync --dev` | Install with dev dependencies |
| `poetry add package` | `uv add package` | Add new dependency |
| `poetry add --group dev package` | `uv add --dev package` | Add dev dependency |
| `poetry remove package` | `uv remove package` | Remove dependency |
| `poetry run command` | `uv run command` | Run command in environment |
| `poetry shell` | `uv shell` | Activate virtual environment |
| `poetry lock` | `uv lock` | Update lock file |

### Code Quality

| Old | New | Description |
|-----|-----|-------------|
| `flake8 .` | `uv run ruff check .` | Linting |
| `black .` | `uv run ruff format .` | Formatting |
| `isort .` | `uv run ruff check --select I --fix .` | Import sorting |
| `flake8 . && black . && isort .` | `uv run ruff check --fix . && uv run ruff format .` | All quality checks |

### Testing

| Old (Poetry) | New (uv) | Description |
|--------------|----------|-------------|
| `poetry run pytest` | `uv run pytest` | Run tests |
| `poetry run pytest --cov` | `uv run pytest --cov=lex_helper` | Run with coverage |

## Development Workflow

### Daily Development
```bash
# Start development session
uv sync --dev

# Make your changes...

# Run quality checks (or let pre-commit handle it)
uv run ruff check --fix .
uv run ruff format .

# Run tests
uv run pytest

# Commit (pre-commit hooks will run automatically)
git commit -m "Your changes"
```

### Pre-commit Hooks
Pre-commit hooks now run automatically on every commit:
- **Ruff linting** with auto-fix
- **Ruff formatting**
- **Pyright type checking**
- **Basic file checks** (trailing whitespace, YAML validation, etc.)

To run pre-commit manually:
```bash
# Run on staged files
uv run pre-commit run

# Run on all files
uv run pre-commit run --all-files

# Skip hooks for emergency commits (not recommended)
git commit --no-verify -m "Emergency fix"
```

## CI/CD Migration: GitLab CI to GitHub Actions

### What Changed
- **Pipeline Configuration**: `.gitlab-ci.yml` → `.github/workflows/ci.yml`
- **Workflow Syntax**: GitLab CI YAML → GitHub Actions YAML
- **Caching**: GitLab cache → GitHub Actions cache with uv integration
- **Artifacts**: GitLab artifacts → GitHub Actions artifacts
- **Release**: GitLab releases → GitHub releases with PyPI trusted publishing

### GitHub Actions Workflows

The new GitHub Actions setup includes:

1. **Main CI Workflow** (`.github/workflows/ci.yml`):
   - Linting and formatting checks
   - Testing across Python 3.12 and 3.13
   - Package building
   - Automated PyPI releases on tags

2. **Pre-commit Workflow** (`.github/workflows/pre-commit.yml`):
   - Additional quality checks
   - Runs pre-commit hooks in CI

3. **Test Release Workflow** (`.github/workflows/test-release.yml`):
   - Manual TestPyPI releases for testing
   - Triggered via GitHub Actions UI
   - Includes installation testing

### Key Features
- **Trusted Publishing**: No API tokens needed for PyPI releases
- **Matrix Testing**: Tests across multiple Python versions
- **Caching**: Efficient dependency caching with uv
- **Artifacts**: Build artifacts stored for 30 days
- **Coverage**: Automatic coverage reporting to Codecov

## Configuration Changes

### pyproject.toml Structure
The new pyproject.toml follows PEP 621 standards:

```toml
[project]
# Standard project metadata
name = "lex-helper"
dependencies = [...]

[project.optional-dependencies]
dev = [...]  # Development dependencies

[tool.ruff]
# Unified linting and formatting configuration

[tool.pyright]
# Type checking (unchanged)
```

### Removed Files
- `.flake8` - Configuration moved to `[tool.ruff]`
- `poetry.lock` - Replaced with `uv.lock`
- `.gitlab-ci.yml` - Replaced with GitHub Actions workflows

### New Files
- `uv.lock` - New lock file format
- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `.github/workflows/ci.yml` - Main CI/CD pipeline
- `.github/workflows/pre-commit.yml` - Pre-commit checks

## Performance Improvements

### Speed Comparisons
- **Dependency installation**: ~3-5x faster with uv
- **Linting**: ~10-100x faster with Ruff vs flake8
- **Formatting**: ~10-100x faster with Ruff vs black
- **CI/CD**: Faster builds with GitHub Actions and uv caching
- **Overall development cycle**: Significantly faster

### Resource Usage
- **Memory**: Lower memory usage during linting/formatting
- **Disk**: Smaller virtual environments with uv
- **CPU**: More efficient parallel processing
- **CI Minutes**: Reduced CI time with faster tooling

## Troubleshooting

### Common Issues

#### "uv: command not found"
```bash
# Install uv
pip install uv

# Or using homebrew
brew install uv

# Verify installation
uv --version
```

#### "No such file or directory: poetry.lock"
This is expected - `poetry.lock` has been replaced with `uv.lock`. Run:
```bash
uv sync --dev
```

#### Pre-commit hooks failing
```bash
# Reinstall hooks
uv run pre-commit uninstall
uv run pre-commit install

# Run manually to see detailed errors
uv run pre-commit run --all-files
```

#### Ruff configuration issues
If Ruff behaves differently than expected:
1. Check `[tool.ruff]` configuration in `pyproject.toml`
2. Compare with previous flake8/black settings
3. Use `uv run ruff check --diff .` to see what would change

#### GitHub Actions Issues
If workflows fail:
1. Check workflow syntax in `.github/workflows/`
2. Verify secrets are configured (for PyPI releases)
3. Check Python version compatibility
4. Review workflow logs for specific errors

### Advanced Troubleshooting

#### Dependency Resolution Issues
```bash
# Clear uv cache
uv cache clean

# Force reinstall all dependencies
rm -rf .venv uv.lock
uv sync --dev

# Check for conflicting dependencies
uv tree
```

#### CI/CD Integration Issues
If your CI/CD pipeline fails after migration:

1. **Update CI commands** in GitHub Actions workflows:
   ```yaml
   # Old (GitLab CI with Poetry)
   - poetry install
   - poetry run flake8
   - poetry run black --check
   
   # New (GitHub Actions with uv)
   - name: Install uv
     uses: astral-sh/setup-uv@v3
   - name: Install dependencies
     run: uv sync --dev
   - name: Run linting
     run: uv run ruff check .
   - name: Check formatting
     run: uv run ruff format --check .
   ```

2. **Docker/Container Issues**:
   ```dockerfile
   # Install uv in Docker
   RUN pip install uv
   COPY pyproject.toml uv.lock ./
   RUN uv sync --dev --no-cache
   ```

#### PyPI Release Setup
For automated PyPI releases:
1. **Configure trusted publishing in PyPI project settings**:
   - Go to your PyPI project → Manage → Publishing
   - Add GitHub as a trusted publisher
   - Repository: `your-org/lex-helper`
   - Workflow: `ci.yml`
   - Environment: `release`

2. **Configure trusted publishing in TestPyPI** (for testing):
   - Go to your TestPyPI project → Manage → Publishing
   - Add GitHub as a trusted publisher
   - Repository: `your-org/lex-helper`
   - Workflow: `ci.yml` and `test-release.yml`
   - Environment: `test-release`

3. **No API tokens needed** with trusted publishing

### Getting Help

#### Check Tool Versions
```bash
uv --version
uv run ruff --version
uv run pytest --version
pyright --version
```

#### Verbose Output
```bash
# Verbose uv operations
uv sync --dev --verbose

# Verbose ruff checking
uv run ruff check --verbose .

# Verbose pre-commit
uv run pre-commit run --verbose --all-files
```

#### Reset Environment
If you encounter persistent issues:
```bash
# Remove virtual environment and reinstall
rm -rf .venv
uv sync --dev
uv run pre-commit install
```

## Migration Checklist

- [ ] Install uv: `pip install uv`
- [ ] Install dependencies: `uv sync --dev`
- [ ] Install pre-commit: `uv run pre-commit install`
- [ ] Run tests: `uv run pytest`
- [ ] Run quality checks: `uv run ruff check . && uv run ruff format .`
- [ ] Test pre-commit: `uv run pre-commit run --all-files`
- [ ] Update IDE/editor settings to use new tools
- [ ] Configure GitHub Actions workflows
- [ ] Set up PyPI trusted publishing (for releases)
- [ ] Remove old GitLab CI configuration
- [ ] Update any custom scripts or documentation

## Benefits Realized

### Developer Experience
- **Faster feedback loops** with quicker linting and formatting
- **Unified tooling** - one tool (Ruff) for linting and formatting
- **Automatic quality checks** via pre-commit hooks
- **Better error messages** and suggestions from Ruff
- **Modern CI/CD** with GitHub Actions

### Project Maintenance
- **Simplified configuration** with consolidated pyproject.toml
- **Faster CI/CD** with improved tool performance and GitHub Actions
- **Modern tooling** aligned with Python ecosystem trends
- **Reduced dependencies** with fewer tools to manage
- **Trusted publishing** for secure PyPI releases

### Team Productivity
- **Consistent code quality** enforced automatically
- **Reduced setup time** for new developers
- **Less context switching** between different tools
- **Improved reliability** with better dependency resolution
- **Streamlined releases** with automated GitHub Actions