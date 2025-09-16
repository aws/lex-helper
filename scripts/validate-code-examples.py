#!/usr/bin/env python3
"""
Code example validator for lex-helper documentation.
Validates Python code snippets in markdown files for syntax correctness.
"""

import argparse
import ast
import re
import subprocess
import sys
import tempfile
from pathlib import Path


class CodeExampleValidator:
    """Validate code examples in documentation."""

    def __init__(self):
        self.errors: list[tuple[str, int, str, str]] = []
        self.warnings: list[tuple[str, str]] = []
        self.stats = {
            "files_checked": 0,
            "code_blocks_found": 0,
            "code_blocks_validated": 0,
            "syntax_errors": 0,
            "import_errors": 0,
        }

    def extract_code_blocks(self, content: str, file_path: str) -> list[tuple[str, int, str, str | None]]:
        """Extract code blocks from markdown content."""
        code_blocks = []

        # Pattern to match fenced code blocks with optional language (handles indentation)
        pattern = r"```(\w+)?\n(.*?)\n\s*```"

        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1) or "text"
            code = match.group(2)

            # Find line number of the code block
            lines_before = content[: match.start()].count("\n")
            line_number = lines_before + 1

            code_blocks.append((language, line_number, code, file_path))

        return code_blocks

    def validate_python_syntax(self, code: str, file_path: str, line_number: int) -> bool:
        """Validate Python code syntax."""
        try:
            # Try to parse the code as Python AST
            ast.parse(code)
            return True
        except SyntaxError as e:
            error_line = line_number + (e.lineno - 1 if e.lineno else 0)
            self.errors.append((file_path, error_line, "syntax_error", f"Python syntax error: {e.msg} at line {e.lineno}"))
            self.stats["syntax_errors"] += 1
            return False
        except Exception as e:
            self.errors.append((file_path, line_number, "parse_error", f"Failed to parse Python code: {e}"))
            return False

    def validate_python_imports(self, code: str, file_path: str, line_number: int) -> bool:
        """Validate that imports in Python code are available."""
        try:
            # Extract import statements
            tree = ast.parse(code)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            # Check if imports are available
            for import_name in imports:
                # Skip standard library and common packages
                if self._is_standard_library(import_name):
                    continue

                # Skip lex_helper imports (our own package)
                if import_name.startswith("lex_helper"):
                    continue

                # Try to import
                try:
                    __import__(import_name)
                except ImportError:
                    self.warnings.append((file_path, f"Import '{import_name}' not available (line {line_number})"))
                    self.stats["import_errors"] += 1

            return True

        except Exception as e:
            self.warnings.append((file_path, f"Error checking imports: {e}"))
            return False

    def _is_standard_library(self, module_name: str) -> bool:
        """Check if module is part of Python standard library."""
        # Common standard library modules
        stdlib_modules = {
            "os",
            "sys",
            "json",
            "yaml",
            "typing",
            "pathlib",
            "datetime",
            "collections",
            "itertools",
            "functools",
            "operator",
            "re",
            "math",
            "random",
            "string",
            "time",
            "uuid",
            "urllib",
            "http",
            "email",
            "html",
            "xml",
            "csv",
            "sqlite3",
            "logging",
            "unittest",
            "asyncio",
            "concurrent",
            "threading",
            "multiprocessing",
            "subprocess",
            "tempfile",
            "shutil",
            "glob",
            "fnmatch",
            "argparse",
            "configparser",
            "io",
            "base64",
            "hashlib",
            "hmac",
            "secrets",
            "ssl",
            "socket",
        }

        # Check if it's a known stdlib module or submodule
        root_module = module_name.split(".")[0]
        return root_module in stdlib_modules

    def validate_shell_syntax(self, code: str, file_path: str, line_number: int) -> bool:
        """Validate shell script syntax."""
        try:
            # Write code to temporary file and check with bash -n
            with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
                f.write(code)
                temp_path = f.name

            try:
                result = subprocess.run(["bash", "-n", temp_path], capture_output=True, text=True, timeout=5)

                if result.returncode != 0:
                    self.errors.append(
                        (file_path, line_number, "shell_syntax_error", f"Shell syntax error: {result.stderr.strip()}")
                    )
                    return False

                return True

            finally:
                Path(temp_path).unlink(missing_ok=True)

        except subprocess.TimeoutExpired:
            self.warnings.append((file_path, f"Shell syntax check timed out (line {line_number})"))
            return False
        except Exception as e:
            self.warnings.append((file_path, f"Error checking shell syntax: {e}"))
            return False

    def validate_yaml_syntax(self, code: str, file_path: str, line_number: int) -> bool:
        """Validate YAML syntax."""
        try:
            import yaml

            yaml.safe_load(code)
            return True
        except yaml.YAMLError as e:
            self.errors.append((file_path, line_number, "yaml_syntax_error", f"YAML syntax error: {e}"))
            return False
        except ImportError:
            self.warnings.append((file_path, "PyYAML not available for YAML validation"))
            return True

    def validate_json_syntax(self, code: str, file_path: str, line_number: int) -> bool:
        """Validate JSON syntax."""
        try:
            import json

            json.loads(code)
            return True
        except json.JSONDecodeError as e:
            self.errors.append(
                (file_path, line_number, "json_syntax_error", f"JSON syntax error: {e.msg} at line {e.lineno}")
            )
            return False

    def validate_code_block(self, language: str, code: str, file_path: str, line_number: int) -> bool:
        """Validate a single code block based on its language."""
        self.stats["code_blocks_validated"] += 1

        # Skip empty code blocks
        if not code.strip():
            return True

        # Skip code blocks that are clearly examples or pseudo-code
        skip_markers = [
            "# example",
            "# pseudo",
            "# placeholder",
            "...",
            "# todo",
            "# fixme",
            "# note:",
            "# warning:",
            "pass  # implementation",
            "pass  # your implementation",
            "# your code here",
            "# implementation details",
            "→",
            "←",
            "↑",
            "↓",  # Arrow characters often used in docs
            "!ref",
            "!getatt",  # CloudFormation intrinsic functions
        ]

        code_lower = code.lower()
        if any(marker in code_lower for marker in skip_markers):
            return True

        # Skip code blocks that look like incomplete function definitions
        lines = code.strip().split("\n")
        if len(lines) > 1:
            # Check if it's a function/class definition without implementation
            first_line = lines[0].strip()
            if (
                first_line.startswith(("def ", "class ", "async def "))
                and first_line.endswith(":")
                and len([line for line in lines[1:] if line.strip() and not line.strip().startswith("#")]) == 0
            ):
                return True

        language = language.lower() if language else ""

        if language in ["python", "py"]:
            success = self.validate_python_syntax(code, file_path, line_number)
            if success:
                self.validate_python_imports(code, file_path, line_number)
            return success

        elif language in ["bash", "sh", "shell"]:
            return self.validate_shell_syntax(code, file_path, line_number)

        elif language in ["yaml", "yml"]:
            return self.validate_yaml_syntax(code, file_path, line_number)

        elif language == "json":
            return self.validate_json_syntax(code, file_path, line_number)

        else:
            # For other languages, just check if it's not empty
            return True

    def validate_file(self, file_path: Path) -> None:
        """Validate code examples in a single file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.warnings.append((str(file_path), f"Error reading file: {e}"))
            return

        self.stats["files_checked"] += 1

        # Extract and validate code blocks
        code_blocks = self.extract_code_blocks(content, str(file_path))
        self.stats["code_blocks_found"] += len(code_blocks)

        for language, line_number, code, _ in code_blocks:
            self.validate_code_block(language, code, str(file_path), line_number)

    def validate_directory(self, directory: Path, patterns: list[str]) -> None:
        """Validate code examples in all matching files in directory."""
        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    self.validate_file(file_path)

    def report_results(self) -> bool:
        """Report results and return True if no errors."""
        print("\n" + "=" * 60)
        print("CODE VALIDATION RESULTS")
        print("=" * 60)

        print("\nSTATISTICS:")
        print(f"  Files checked: {self.stats['files_checked']}")
        print(f"  Code blocks found: {self.stats['code_blocks_found']}")
        print(f"  Code blocks validated: {self.stats['code_blocks_validated']}")
        print(f"  Syntax errors: {self.stats['syntax_errors']}")
        print(f"  Import warnings: {self.stats['import_errors']}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for file_path, warning in self.warnings:
                print(f"  {file_path}: {warning}")

        if self.errors:
            print(f"\n❌ CODE ERRORS ({len(self.errors)}):")

            # Group errors by file
            errors_by_file: dict[str, list[tuple[int, str, str]]] = {}
            for file_path, line_number, error_type, message in self.errors:
                if file_path not in errors_by_file:
                    errors_by_file[file_path] = []
                errors_by_file[file_path].append((line_number, error_type, message))

            for file_path, file_errors in errors_by_file.items():
                print(f"\n  {file_path}:")
                for line_number, error_type, message in sorted(file_errors):
                    print(f"    Line {line_number} ({error_type}): {message}")

        print("\nSUMMARY:")
        print(f"  Code errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")

        if len(self.errors) == 0:
            print("\n✅ All code examples are valid!")
            return True
        else:
            print(f"\n❌ Found {len(self.errors)} code errors")
            return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Validate code examples in documentation")
    parser.add_argument("paths", nargs="+", help="Files or directories to check")
    parser.add_argument(
        "--patterns", nargs="+", default=["*.md", "*.rst"], help="File patterns to check (only used for directories)"
    )

    args = parser.parse_args()

    validator = CodeExampleValidator()

    for path_str in args.paths:
        path = Path(path_str)
        if not path.exists():
            print(f"Error: Path {path} does not exist")
            return 1

        if path.is_file():
            # Validate individual file
            validator.validate_file(path)
        elif path.is_dir():
            # Validate directory with patterns
            validator.validate_directory(path, args.patterns)
        else:
            print(f"Error: {path} is neither a file nor directory")
            return 1

    success = validator.report_results()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
