#!/usr/bin/env python3
"""
Lightweight documentation quality check for pre-commit hooks.
Only runs essential checks that are fast and relevant for commit-time validation.
"""

import argparse
import subprocess
import sys


def run_command(cmd, description, allow_failure=False):
    """Run a command and handle errors."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, shell=True)
        print(f"✅ {description} passed")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        if allow_failure:
            print(f"⚠️  {description} failed (allowed)")
            print(f"Output: {e.stdout}")
            print(f"Error: {e.stderr}")
            return False, e.stderr
        else:
            print(f"❌ {description} failed")
            print(f"Output: {e.stdout}")
            print(f"Error: {e.stderr}")
            return False, e.stderr


def main():
    """Run lightweight documentation checks for pre-commit."""
    parser = argparse.ArgumentParser(description="Pre-commit documentation quality checks")
    parser.add_argument("files", nargs="*", help="Files to check (from pre-commit)")
    parser.add_argument("--skip-build", action="store_true", help="Skip documentation build")

    args = parser.parse_args()

    print("📚 Running documentation quality checks for pre-commit...")
    print("=" * 60)

    overall_success = True

    # Check 1: Validate code examples in changed markdown files
    if args.files:
        md_files = [f for f in args.files if f.endswith(".md") and f.startswith("docs/")]
        if md_files:
            print(f"Checking code examples in {len(md_files)} changed files...")
            success, _ = run_command(
                f"uv run python scripts/validate-code-examples.py {' '.join(md_files)}", "Code example validation"
            )
            if not success:
                overall_success = False

    # Check 2: Quick documentation build test (only if mkdocs.yml or many docs changed)
    if not args.skip_build:
        build_needed = False
        if args.files:
            # Check if mkdocs.yml changed or if many doc files changed
            if any("mkdocs.yml" in f for f in args.files):
                build_needed = True
            elif len([f for f in args.files if f.endswith(".md") and f.startswith("docs/")]) > 5:
                build_needed = True
        else:
            build_needed = True

        # Skip build tests in pre-commit environment to avoid dependency issues
        # Full documentation build and link checks are performed in CI
        if build_needed:
            print("🔍 Documentation build test...")
            print("⚠️  Skipping documentation build test in pre-commit environment")
            print("💡 Full documentation build and link checks run in CI")

    print("=" * 60)
    if overall_success:
        print("✅ All documentation quality checks passed!")
        print("💡 Tip: Run 'make docs-qa' for comprehensive checks")
    else:
        print("❌ Some documentation quality checks failed!")
        print("🔧 Fix the issues above or run 'make docs-qa' for detailed analysis")

    return 0 if overall_success else 1


if __name__ == "__main__":
    sys.exit(main())
