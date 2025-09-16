#!/usr/bin/env python3
"""
Development server script for lex-helper documentation.
Provides live reload and development utilities.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the MkDocs development server with live reload."""
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Check if dependencies are installed
    try:
        import mkdocs
        import mkdocs_material
        import mkdocstrings
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install documentation dependencies:")
        print("  uv sync --group docs")
        sys.exit(1)
    
    # Run MkDocs serve with development options
    cmd = [
        sys.executable, "-m", "mkdocs", "serve",
        "--dev-addr", "127.0.0.1:8000",
        "--livereload",
        "--watch", "lex_helper/",
        "--watch", "docs/",
        "--watch", "examples/",
    ]
    
    print("Starting MkDocs development server...")
    print("Documentation will be available at: http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nShutting down development server...")
    except subprocess.CalledProcessError as e:
        print(f"Error running MkDocs: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()