# Development Guide

This guide covers common development tasks and workflows for the Lex Helper library.

## Development Environment Setup

### Initial Setup
```bash
# Install uv (Python package manager)
pip install uv

# Install all dependencies including development tools
uv sync --dev

# Install pre-commit hooks for automated code quality
uv run pre-commit install

# Verify setup by running tests
uv run pytest
```

### IDE Configuration

#### VS Code
Recommended extensions:
- Python
- Pylance (for type checking)
- Ruff (for linting and formatting)

Settings for `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": false,
    "python.formatting.provider": "none",
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": true,
            "source.organizeImports.ruff": true
        }
    },
    "python.analysis.typeCheckingMode": "strict"
}
```

#### PyCharm
1. Set Python interpreter to `.venv/bin/python`
2. Install Ruff plugin
3. Configure Ruff as the default formatter
4. Enable type checking in Python settings

## Common Development Tasks

### Running Tests
```bash
# Run all tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov=lex_helper

# Run tests with detailed coverage report
uv run pytest --cov=lex_helper --cov-report=html

# Run specific test file
uv run pytest tests/test_handler.py

# Run tests matching a pattern
uv run pytest -k "test_dialog"

# Run tests in verbose mode
uv run pytest -v
```

### Code Quality Checks
```bash
# Lint code (check for issues)
uv run ruff check .

# Lint and auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Check specific files
uv run ruff check lex_helper/core/handler.py

# Show what would be formatted (dry run)
uv run ruff format --diff .
```

### Type Checking
```bash
# Run type checking
pyright

# Type check specific files
pyright lex_helper/core/handler.py

# Type check with verbose output
pyright --verbose
```

### Pre-commit Hooks
```bash
# Run pre-commit on staged files
uv run pre-commit run

# Run pre-commit on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff

# Update hook versions
uv run pre-commit autoupdate
```

### Dependency Management
```bash
# Add new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Remove dependency
uv remove package-name

# Update dependencies
uv sync

# Show dependency tree
uv tree

# Export requirements (for compatibility)
uv export --format requirements-txt > requirements.txt
```

## Project Structure

### Core Components
```
lex_helper/
├── __init__.py           # Main exports
├── core/                 # Core functionality
│   ├── handler.py        # Main LexHelper class
│   ├── types.py          # Pydantic models
│   ├── dialog.py         # Dialog utilities
│   └── ...
├── channels/             # Channel-specific formatting
├── formatters/           # Text and response formatters
├── utils/                # Utility functions
└── exceptions/           # Custom exceptions
```

### Testing Structure
```
tests/
├── test_handler.py       # Handler tests
├── test_utils.py         # Utility tests
├── test_*.py             # Other test files
└── sample_lex_request.py # Test data
```

## Code Style Guidelines

### Python Code Style
- **Line length**: 125 characters
- **Quote style**: Double quotes for strings
- **Import organization**: Automatic with Ruff
- **Type hints**: Required for all public APIs
- **Docstrings**: Google style for public functions

### Example Code Style
```python
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from lex_helper.core.types import LexRequest, LexResponse


class ExampleModel(BaseModel):
    """Example model with proper type hints and docstrings.
    
    Args:
        name: The name field with validation
        count: Optional count with default value
    """
    name: str = Field(..., description="Name field")
    count: Optional[int] = Field(default=0, description="Count field")

    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return results.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Processed data dictionary
            
        Raises:
            ValueError: If data is invalid
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        return {"processed": True, "original": data}
```

## Testing Guidelines

### Test Structure
```python
import pytest
from unittest.mock import Mock, patch

from lex_helper import LexHelper, Config
from lex_helper.core.types import LexRequest


class TestLexHelper:
    """Test class for LexHelper functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.config = Config()
        self.lex_helper = LexHelper(config=self.config)
    
    def test_handler_success(self):
        """Test successful handler execution."""
        # Arrange
        event = {"key": "value"}
        context = Mock()
        
        # Act
        result = self.lex_helper.handler(event, context)
        
        # Assert
        assert result is not None
        assert "statusCode" in result
    
    @patch("lex_helper.core.handler.some_external_call")
    def test_handler_with_mock(self, mock_external):
        """Test handler with mocked external dependencies."""
        # Arrange
        mock_external.return_value = "mocked_result"
        
        # Act & Assert
        # ... test implementation
```

### Test Coverage
- Aim for >90% test coverage
- Test both success and error paths
- Include edge cases and boundary conditions
- Mock external dependencies (AWS services, etc.)

## CI/CD with GitHub Actions

### Workflows
The project uses GitHub Actions for continuous integration:

1. **Main CI Workflow** (`.github/workflows/ci.yml`):
   - Runs on push to main/develop branches and pull requests
   - Linting and formatting checks with Ruff
   - Testing across Python 3.12 and 3.13
   - Package building and artifact storage
   - Automated PyPI releases on version tags

2. **Pre-commit Workflow** (`.github/workflows/pre-commit.yml`):
   - Additional quality assurance
   - Runs all pre-commit hooks in CI environment

### Workflow Triggers
- **Push to main/develop**: Full CI pipeline
- **Pull requests**: Full CI pipeline
- **Version tags** (`v*`): Full CI + PyPI release

### Local Testing
Before pushing, ensure your changes pass CI:
```bash
# Run the same checks as CI
uv run ruff check .
uv run ruff format --check .
uv run pytest --cov=lex_helper
uv run pre-commit run --all-files
```

## Release Process

### Version Management
Versions are managed in `pyproject.toml`:
```toml
[project]
version = "0.0.9"
```

### Testing Releases with TestPyPI

Before releasing to production PyPI, you can test releases using TestPyPI:

#### Option 1: Manual TestPyPI Release
1. Go to GitHub Actions → "Test Release" workflow
2. Click "Run workflow"
3. Enter a test version (e.g., `0.1.0-test.1`)
4. The workflow will:
   - Build the package with the test version
   - Publish to TestPyPI
   - Test installation from TestPyPI

#### Option 2: Release Candidate Tags
1. Create a release candidate tag: `git tag v0.1.0-rc.1`
2. Push the tag: `git push --tags`
3. GitHub Actions will automatically publish to TestPyPI

### Creating a Production Release
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with new features and fixes
3. Run full test suite: `uv run pytest`
4. Run quality checks: `uv run pre-commit run --all-files`
5. Commit changes: `git commit -am "Release v0.0.9"`
6. Create git tag: `git tag v0.0.9`
7. Push changes and tag: `git push && git push --tags`
8. GitHub Actions will automatically build and release to PyPI

### Release Types
- **Production releases**: Tags like `v1.0.0` → PyPI
- **Release candidates**: Tags like `v1.0.0-rc.1` → TestPyPI
- **Manual test releases**: Use "Test Release" workflow → TestPyPI

### PyPI Release Setup
The project uses PyPI trusted publishing:
- No API tokens required
- Configured in PyPI and TestPyPI project settings
- Automatic releases based on tag patterns
- Secure and maintainable

### Testing TestPyPI Installations
After publishing to TestPyPI, you can test the installation:
```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ lex-helper==0.1.0-test.1

# Test basic functionality
python -c "import lex_helper; print('Import successful')"
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure all dependencies are installed
uv sync --dev

# Check Python path
uv run python -c "import sys; print(sys.path)"
```

#### Test Failures
```bash
# Run tests with verbose output
uv run pytest -v -s

# Run specific failing test
uv run pytest tests/test_handler.py::TestLexHelper::test_specific_method -v
```

#### Pre-commit Issues
```bash
# Reinstall hooks
uv run pre-commit uninstall
uv run pre-commit install

# Run with verbose output
uv run pre-commit run --verbose --all-files
```

#### Type Checking Errors
```bash
# Run pyright with verbose output
pyright --verbose

# Check specific file
pyright lex_helper/core/handler.py
```

### Performance Optimization

#### Profiling Tests
```bash
# Install profiling tools
uv add --dev pytest-profiling

# Run tests with profiling
uv run pytest --profile
```

#### Memory Usage
```bash
# Install memory profiling
uv add --dev memory-profiler

# Profile memory usage
uv run python -m memory_profiler your_script.py
```

## Contributing

### Before Submitting Changes
1. Run full test suite: `uv run pytest`
2. Run code quality checks: `uv run pre-commit run --all-files`
3. Update documentation if needed
4. Add tests for new functionality
5. Update type hints for new code

### Code Review Checklist
- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Type hints are present and correct
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact considered

## Additional Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pre-commit Documentation](https://pre-commit.com/)