# Documentation Quality Assurance Scripts

This directory contains scripts for ensuring the quality of the lex-helper documentation. These scripts are used both locally during development and in the CI/CD pipeline.

## Scripts Overview

### Core Testing Scripts

- **`test-docs.py`** - Comprehensive test runner that executes all quality assurance checks
- **`serve-docs.py`** - Development server for live documentation preview

### Quality Assurance Scripts

- **`check-links.py`** - Link checker for internal and external links
- **`check-spelling.py`** - Spell checker with technical dictionary
- **`validate-code-examples.py`** - Code syntax validator for documentation examples
- **`check-accessibility.py`** - Accessibility compliance checker (WCAG)

### Supporting Files

- **`spelling-dictionary.txt`** - Custom dictionary for technical terms

## Usage

### Local Development

Run all quality assurance checks:
```bash
make docs-qa
```

Run individual checks:
```bash
# Test documentation build
python scripts/test-docs.py

# Check links only
python scripts/check-links.py ./site

# Check spelling only
python scripts/check-spelling.py docs/

# Validate code examples only
python scripts/validate-code-examples.py docs/

# Check accessibility only
python scripts/check-accessibility.py ./site
```

### CI/CD Integration

These scripts are automatically run in GitHub Actions:
- On pull requests: All checks run to validate changes
- On main branch pushes: Full quality assurance suite runs before deployment

## Script Details

### check-links.py

Validates all links in the built documentation.

**Features:**
- Internal link validation (checks file existence and anchors)
- External link validation (HTTP status codes)
- Handles relative and absolute paths
- Reports broken links with source file locations

**Usage:**
```bash
# Check internal links only
python scripts/check-links.py ./site

# Check internal and external links
python scripts/check-links.py ./site --external

# Fail on warnings
python scripts/check-links.py ./site --fail-on-warnings
```

### check-spelling.py

Spell checks markdown files with a technical dictionary.

**Features:**
- Uses PyEnchant for spell checking
- Custom dictionary for technical terms
- Skips code blocks and inline code
- Provides spelling suggestions
- Configurable dictionary language

**Usage:**
```bash
# Check spelling in docs directory
python scripts/check-spelling.py docs/

# Use different patterns
python scripts/check-spelling.py docs/ --patterns "*.md" "*.rst"

# Use different dictionary
python scripts/check-spelling.py docs/ --dictionary en_GB
```

**Custom Dictionary:**
Add technical terms to `scripts/spelling-dictionary.txt` to avoid false positives.

### validate-code-examples.py

Validates syntax of code examples in documentation.

**Features:**
- Extracts code blocks from markdown
- Validates Python syntax using AST parsing
- Checks shell script syntax with bash -n
- Validates YAML and JSON syntax
- Reports syntax errors with line numbers

**Usage:**
```bash
# Validate code in docs directory
python scripts/validate-code-examples.py docs/

# Check specific file patterns
python scripts/validate-code-examples.py docs/ --patterns "*.md"
```

### check-accessibility.py

Checks HTML documentation for accessibility compliance.

**Features:**
- WCAG compliance checking
- Image alt text validation
- Link text validation
- Heading structure validation
- Form accessibility checking
- Color contrast warnings
- Language attribute checking

**Usage:**
```bash
# Check accessibility of built site
python scripts/check-accessibility.py ./site

# Fail on warnings as well as errors
python scripts/check-accessibility.py ./site --fail-on-warnings
```

## Dependencies

### Required Dependencies
- `beautifulsoup4` - HTML parsing for link and accessibility checking
- `requests` - HTTP requests for external link checking
- `pyenchant` - Spell checking (requires system enchant library)

### System Dependencies
For spell checking, install system packages:

**Ubuntu/Debian:**
```bash
sudo apt-get install aspell aspell-en libenchant-2-2
```

**macOS:**
```bash
brew install enchant
```

**Windows:**
```bash
# Install via conda or use WSL
conda install enchant
```

## Configuration

### Spell Checking Dictionary

Add technical terms to `scripts/spelling-dictionary.txt`:
```
# Project-specific terms
lex-helper
chatbots
fulfillment

# AWS terms
cloudformation
dynamodb
```

### GitHub Actions Integration

The quality assurance checks are integrated into `.github/workflows/docs.yml`:

- **quality-assurance job**: Runs all QA checks on every push/PR
- **test job**: Runs subset of checks for PR validation
- **build job**: Depends on QA passing before building documentation

## Troubleshooting

### Common Issues

**PyEnchant Installation:**
If PyEnchant fails to install, ensure system enchant library is installed first.

**External Link Timeouts:**
External link checking may timeout for slow sites. This is allowed to fail in CI.

**False Positive Spelling Errors:**
Add legitimate technical terms to the custom dictionary file.

**Code Example Validation:**
Code blocks marked with `# example` or containing `...` are skipped as pseudo-code.

### Performance Considerations

- Link checking can be slow for large sites with many external links
- Spell checking performance depends on dictionary size
- Code validation is fast but may require imports to be available

## Contributing

When adding new quality assurance checks:

1. Create a new script following the existing pattern
2. Add comprehensive error reporting and statistics
3. Include both error and warning categories
4. Add command-line options for flexibility
5. Update this README with usage instructions
6. Add the check to the main test runner and CI/CD pipeline

## Exit Codes

All scripts follow standard exit code conventions:
- `0` - Success (no errors found)
- `1` - Failure (errors found or script error)

Scripts may optionally support `--fail-on-warnings` to treat warnings as failures.
