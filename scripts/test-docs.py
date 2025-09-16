#!/usr/bin/env python3
"""
Test script for lex-helper documentation.
Validates documentation build and checks for common issues.
"""

import subprocess
import sys
import os
from pathlib import Path
import tempfile
import shutil

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Run documentation tests."""
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("Testing lex-helper documentation...")
    print("=" * 50)
    
    success = True
    
    # Test 1: Check if dependencies are available
    try:
        import mkdocs
        import mkdocs_material
        import mkdocstrings
        print("✓ All required dependencies are installed")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install documentation dependencies:")
        print("  uv sync --group docs")
        return False
    
    # Test 2: Validate mkdocs.yml configuration
    if not run_command([sys.executable, "-m", "mkdocs", "config"], 
                      "MkDocs configuration validation"):
        success = False
    
    # Test 3: Build documentation in strict mode
    with tempfile.TemporaryDirectory() as temp_dir:
        if not run_command([sys.executable, "-m", "mkdocs", "build", 
                           "--clean", "--strict", "--site-dir", temp_dir], 
                          "Documentation build (strict mode)"):
            success = False
    
    # Test 4: Check for broken internal links (basic check)
    print("Checking for basic markdown syntax issues...")
    docs_dir = Path("docs")
    if docs_dir.exists():
        md_files = list(docs_dir.rglob("*.md"))
        print(f"Found {len(md_files)} markdown files")
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                # Basic checks
                if ']((' in content:
                    print(f"⚠ Potential broken link in {md_file}")
                if '![' in content and not content.count('![') == content.count(']('):
                    print(f"⚠ Potential broken image link in {md_file}")
            except Exception as e:
                print(f"⚠ Could not read {md_file}: {e}")
        
        print("✓ Basic markdown syntax check completed")
    
    print("=" * 50)
    if success:
        print("✓ All documentation tests passed!")
        return True
    else:
        print("✗ Some documentation tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)