#!/usr/bin/env python3
"""
Spell checker for lex-helper documentation.
Validates spelling in markdown and HTML files with technical term dictionary.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from enchant.checker import SpellChecker

except ImportError:
    print("Error: pyenchant is required for spell checking")
    print("Install with: pip install pyenchant")
    sys.exit(1)


class DocumentationSpellChecker:
    """Spell checker for documentation files."""

    def __init__(self, dictionary_lang: str = "en_US"):
        self.dictionary_lang = dictionary_lang
        self.custom_words = self._load_custom_dictionary()
        self.errors: list[tuple[str, int, str, str]] = []
        self.warnings: list[tuple[str, str]] = []

    def _load_custom_dictionary(self) -> set[str]:
        """Load custom dictionary with technical terms."""
        # Technical terms specific to lex-helper and AWS
        custom_words = {
            # AWS Services and Terms
            "aws",
            "lex",
            "lambda",
            "bedrock",
            "boto3",
            "botocore",
            "cloudformation",
            "cloudwatch",
            "dynamodb",
            "s3",
            "iam",
            "vpc",
            "api",
            "apis",
            "sdk",
            "cli",
            "arn",
            "arns",
            "json",
            "yaml",
            "yml",
            "http",
            "https",
            "url",
            "urls",
            "uri",
            "uris",
            "uuid",
            "uuids",
            "oauth",
            "jwt",
            "ssl",
            "tls",
            "cdn",
            # Programming Terms
            "python",
            "pip",
            "pypi",
            "virtualenv",
            "venv",
            "conda",
            "poetry",
            "uv",
            "pytest",
            "unittest",
            "mock",
            "mocking",
            "async",
            "await",
            "asyncio",
            "pydantic",
            "dataclass",
            "dataclasses",
            "enum",
            "enums",
            "typing",
            "mypy",
            "pylint",
            "flake8",
            "ruff",
            "pre-commit",
            "github",
            "ci",
            "cd",
            "dockerfile",
            "docker",
            "kubernetes",
            "k8s",
            "helm",
            "terraform",
            # lex-helper Specific Terms
            "lex-helper",
            "lexhelper",
            "chatbot",
            "chatbots",
            "nlp",
            "nlu",
            "asr",
            "tts",
            "intent",
            "intents",
            "slot",
            "slots",
            "utterance",
            "utterances",
            "fulfillment",
            "disambiguation",
            "anthropic",
            "claude",
            "llm",
            "llms",
            "ai",
            "ml",
            "generative",
            "conversational",
            # Documentation Terms
            "mkdocs",
            "mkdocstrings",
            "markdown",
            "md",
            "html",
            "css",
            "javascript",
            "js",
            "typescript",
            "ts",
            "npm",
            "node",
            "webpack",
            "babel",
            "eslint",
            "prettier",
            "gitlab",
            "bitbucket",
            "readme",
            "changelog",
            "gui",
            "ui",
            "ux",
            "frontend",
            "backend",
            # Common Technical Abbreviations
            "config",
            "configs",
            "env",
            "vars",
            "param",
            "params",
            "arg",
            "args",
            "func",
            "fn",
            "obj",
            "str",
            "int",
            "bool",
            "dict",
            "list",
            "tuple",
            "regex",
            "regexp",
            "utf",
            "ascii",
            "unicode",
            "base64",
            "sha",
            "md5",
            "gzip",
            "zip",
            "tar",
            "gz",
            "xml",
            "csv",
            "tsv",
            "sql",
            "nosql",
            # Business/Domain Terms
            "serverless",
            "microservices",
            "devops",
            "sre",
            "monitoring",
            "observability",
            "telemetry",
            "metrics",
            "logging",
            "tracing",
            "scalability",
            "availability",
            "reliability",
            "performance",
            "optimization",
            "caching",
            "load",
            "balancer",
            "proxy",
            # Version/Release Terms
            "semver",
            "versioning",
            "deprecation",
            "migration",
            "upgrade",
            "downgrade",
            "rollback",
            "hotfix",
            "patch",
            "minor",
            "major",
            "alpha",
            "beta",
            "rc",
            "stable",
            "lts",
            # File Extensions and Formats
            "py",
            "pyc",
            "pyo",
            "pyd",
            "so",
            "dll",
            "exe",
            "sh",
            "bat",
            "ps1",
            "toml",
            "ini",
            "cfg",
            "conf",
            "log",
            "txt",
            "rst",
            "pdf",
            "png",
            "jpg",
            "jpeg",
            "gif",
            "svg",
            "ico",
            "woff",
            "ttf",
            "eot",
        }

        # Load additional words from custom dictionary file if it exists
        custom_dict_file = Path(__file__).parent / "spelling-dictionary.txt"
        if custom_dict_file.exists():
            try:
                with open(custom_dict_file, encoding="utf-8") as f:
                    for line in f:
                        word = line.strip().lower()
                        if word and not word.startswith("#"):
                            custom_words.add(word)
            except Exception as e:
                self.warnings.append(("custom dictionary", f"Error loading custom dictionary: {e}"))

        return custom_words

    def _is_code_block(self, text: str, position: int) -> bool:
        """Check if position is within a code block."""
        # Simple heuristic: check for code fences around the position
        lines_before = text[:position].split("\n")

        # Count code fences before and after
        fences_before = sum(1 for line in lines_before if line.strip().startswith("```"))

        # If odd number of fences before, we're in a code block
        return fences_before % 2 == 1

    def _should_skip_word(self, word: str) -> bool:
        """Check if word should be skipped from spell checking."""
        # Skip very short words
        if len(word) < 3:
            return True

        # Skip words that are all uppercase (likely acronyms)
        if word.isupper() and len(word) > 1:
            return True

        # Skip words with numbers
        if any(c.isdigit() for c in word):
            return True

        # Skip words with underscores or hyphens (likely code)
        if "_" in word or "-" in word:
            return True

        # Skip words that look like file paths or URLs
        if "/" in word or "\\" in word or "." in word:
            return True

        return False

    def check_file(self, file_path: Path) -> None:
        """Check spelling in a single file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.warnings.append((str(file_path), f"Error reading file: {e}"))
            return

        # Create spell checker
        try:
            checker = SpellChecker(self.dictionary_lang)

            # Add custom words to personal word list
            for word in self.custom_words:
                checker.dict.add(word)

        except Exception as e:
            self.warnings.append((str(file_path), f"Error creating spell checker: {e}"))
            return

        # Remove code blocks and inline code from markdown
        if file_path.suffix == ".md":
            # Remove fenced code blocks
            content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
            # Remove inline code
            content = re.sub(r"`[^`]+`", "", content)
            # Remove links
            content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", content)
            # Remove image references
            content = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", content)

        # Check spelling
        checker.set_text(content)

        for error in checker:
            word = error.word

            # Skip words that shouldn't be checked
            if self._should_skip_word(word):
                continue

            # Get line number
            lines_before = content[: error.wordpos].count("\n")
            line_number = lines_before + 1

            # Get suggestions
            suggestions = checker.suggest()[:5]  # Limit to 5 suggestions

            self.errors.append(
                (str(file_path), line_number, word, ", ".join(suggestions) if suggestions else "no suggestions")
            )

    def check_directory(self, directory: Path, patterns: list[str]) -> None:
        """Check spelling in all matching files in directory."""
        files_checked = 0

        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    self.check_file(file_path)
                    files_checked += 1

        print(f"Checked {files_checked} files for spelling errors")

    def report_results(self) -> bool:
        """Report results and return True if no errors."""
        print("\n" + "=" * 60)
        print("SPELL CHECK RESULTS")
        print("=" * 60)

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for file_path, warning in self.warnings:
                print(f"  {file_path}: {warning}")

        if self.errors:
            print(f"\n❌ SPELLING ERRORS ({len(self.errors)}):")

            # Group errors by file
            errors_by_file: dict[str, list[tuple[int, str, str]]] = {}
            for file_path, line_number, word, suggestions in self.errors:
                if file_path not in errors_by_file:
                    errors_by_file[file_path] = []
                errors_by_file[file_path].append((line_number, word, suggestions))

            for file_path, file_errors in errors_by_file.items():
                print(f"\n  {file_path}:")
                for line_number, word, suggestions in sorted(file_errors):
                    print(f"    Line {line_number}: '{word}' → {suggestions}")

        print("\nSUMMARY:")
        print(f"  Spelling errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")

        if len(self.errors) == 0:
            print("\n✅ No spelling errors found!")
            return True
        else:
            print(f"\n❌ Found {len(self.errors)} spelling errors")
            return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Check spelling in documentation")
    parser.add_argument("directory", help="Directory to check")
    parser.add_argument("--patterns", nargs="+", default=["*.md", "*.rst"], help="File patterns to check")
    parser.add_argument("--dictionary", default="en_US", help="Dictionary language")

    args = parser.parse_args()

    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        return 1

    checker = DocumentationSpellChecker(args.dictionary)
    checker.check_directory(directory, args.patterns)
    success = checker.report_results()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
