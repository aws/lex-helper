#!/usr/bin/env python3
"""
Comprehensive test script for lex-helper documentation.
Validates documentation build and runs all quality assurance checks.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(cmd, description, allow_failure=False):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {description} passed")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        if allow_failure:
            print(f"⚠ {description} failed (allowed)")
            print(f"Error: {e.stderr}")
            return False, e.stderr
        else:
            print(f"✗ {description} failed")
            print(f"Error: {e.stderr}")
            return False, e.stderr


def check_dependencies():
    """Check if all required dependencies are available."""
    print("Checking dependencies...")

    required_modules = [
        ("mkdocs", "MkDocs"),
        ("mkdocs_material", "Material theme"),
        ("mkdocstrings", "mkdocstrings"),
        ("bs4", "BeautifulSoup4"),
        ("requests", "requests"),
    ]

    missing = []
    for module, name in required_modules:
        try:
            __import__(module)
            print(f"✓ {name} available")
        except ImportError:
            print(f"✗ {name} missing")
            missing.append(name)

    # Check optional dependencies
    optional_modules = [
        ("enchant", "PyEnchant (for spell checking)"),
    ]

    for module, name in optional_modules:
        try:
            __import__(module)
            print(f"✓ {name} available")
        except ImportError:
            print(f"⚠ {name} missing (optional)")

    if missing:
        print(f"\nMissing required dependencies: {', '.join(missing)}")
        print("Install with: uv sync --group docs")
        return False

    return True


def main():
    """Run comprehensive documentation tests."""

    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("Comprehensive lex-helper documentation testing")
    print("=" * 60)

    overall_success = True
    test_results = []

    # Test 1: Check dependencies
    print("\n1. DEPENDENCY CHECK")
    print("-" * 30)
    if not check_dependencies():
        return False

    # Test 2: Validate mkdocs.yml configuration
    print("\n2. CONFIGURATION VALIDATION")
    print("-" * 30)
    success, output = run_command([sys.executable, "-m", "mkdocs", "config"], "MkDocs configuration validation")
    test_results.append(("Configuration", success))
    if not success:
        overall_success = False

    # Test 3: Build documentation in strict mode
    print("\n3. DOCUMENTATION BUILD")
    print("-" * 30)
    with tempfile.TemporaryDirectory() as temp_dir:
        success, output = run_command(
            [sys.executable, "-m", "mkdocs", "build", "--clean", "--strict", "--site-dir", temp_dir],
            "Documentation build (strict mode)",
        )
        test_results.append(("Build", success))
        if not success:
            overall_success = False
            print("Skipping remaining tests due to build failure")
            return False

        site_dir = temp_dir

        # Test 4: Validate code examples
        print("\n4. CODE EXAMPLE VALIDATION")
        print("-" * 30)
        success, output = run_command(
            [sys.executable, "scripts/validate-code-examples.py", "docs/"], "Code example validation"
        )
        test_results.append(("Code Examples", success))
        if not success:
            overall_success = False

        # Test 5: Check internal links
        print("\n5. LINK CHECKING")
        print("-" * 30)
        success, output = run_command([sys.executable, "scripts/check-links.py", site_dir], "Internal link checking")
        test_results.append(("Internal Links", success))
        if not success:
            overall_success = False

        # Test 6: Check external links (allow failure)
        success, output = run_command(
            [sys.executable, "scripts/check-links.py", site_dir, "--external"], "External link checking", allow_failure=True
        )
        test_results.append(("External Links", success))

        # Test 7: Check accessibility
        print("\n6. ACCESSIBILITY CHECKING")
        print("-" * 30)
        success, output = run_command(
            [sys.executable, "scripts/check-accessibility.py", site_dir], "Accessibility compliance checking"
        )
        test_results.append(("Accessibility", success))
        if not success:
            overall_success = False

        # Test 8: Check spelling (allow failure for now)
        print("\n7. SPELL CHECKING")
        print("-" * 30)
        success, output = run_command(
            [sys.executable, "scripts/check-spelling.py", "docs/"], "Spell checking", allow_failure=True
        )
        test_results.append(("Spelling", success))

    # Test 9: Basic markdown syntax check
    print("\n8. MARKDOWN SYNTAX CHECK")
    print("-" * 30)
    docs_dir = Path("docs")
    if docs_dir.exists():
        md_files = list(docs_dir.rglob("*.md"))
        print(f"Checking {len(md_files)} markdown files...")

        syntax_issues = 0
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                # Basic checks
                if "]((" in content:
                    print(f"⚠ Potential broken link in {md_file}")
                    syntax_issues += 1
                if "![" in content and not content.count("![") == content.count("]("):
                    print(f"⚠ Potential broken image link in {md_file}")
                    syntax_issues += 1
            except Exception as e:
                print(f"⚠ Could not read {md_file}: {e}")
                syntax_issues += 1

        if syntax_issues == 0:
            print("✓ No markdown syntax issues found")
        else:
            print(f"⚠ Found {syntax_issues} potential markdown syntax issues")

        test_results.append(("Markdown Syntax", syntax_issues == 0))

    # Final report
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)

    for test_name, success in test_results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {test_name:<20} {status}")

    print("\nOVERALL RESULT:")
    if overall_success:
        print("✅ All critical tests passed!")
        print("Documentation is ready for deployment.")
    else:
        failed_tests = [name for name, success in test_results if not success]
        print(f"❌ {len(failed_tests)} test(s) failed: {', '.join(failed_tests)}")
        print("Please fix the issues before deploying.")

    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
