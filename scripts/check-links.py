#!/usr/bin/env python3
"""
Link checker for lex-helper documentation.
Validates internal and external links in the built documentation.
"""

import argparse
import sys
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup


class LinkChecker:
    """Check links in HTML documentation."""

    def __init__(self, site_dir: Path, check_external: bool = False, config_file: Path = None):
        self.site_dir = Path(site_dir)
        self.check_external = check_external
        self.internal_links: set[str] = set()
        self.external_links: set[str] = set()
        self.broken_links: list[tuple[str, str, str]] = []
        self.warnings: list[tuple[str, str, str]] = []
        self.config = self._load_config(config_file)

    def collect_links(self) -> None:
        """Collect all links from HTML files."""
        html_files = list(self.site_dir.rglob("*.html"))
        print(f"Scanning {len(html_files)} HTML files for links...")

        for html_file in html_files:
            try:
                with open(html_file, encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")

                # Find all links
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    self._process_link(href, html_file)

                # Find all images
                for img in soup.find_all("img", src=True):
                    src = img["src"]
                    self._process_link(src, html_file)

            except Exception as e:
                self.warnings.append((str(html_file), "", f"Error reading file: {e}"))

    def _load_config(self, config_file: Path = None) -> dict:
        """Load configuration from YAML file."""
        if config_file is None:
            config_file = Path(__file__).parent / "qa-config.yaml"

        try:
            if config_file.exists():
                with open(config_file) as f:
                    return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")

        # Return default config
        return {
            "links": {
                "safe_external_patterns": [
                    "../README.md",
                    "README.md",
                    "CONTRIBUTING.md",
                    "CHANGELOG.md",
                    "LICENSE",
                    "LICENSE.md",
                    ".env",
                    "requirements.txt",
                    "package.json",
                    "pyproject.toml",
                ],
                "ignore_broken_links_in": ["404.html", "error.html"],
            }
        }

    def _is_safe_external_reference(self, url: str, source_file: str) -> bool:
        """Check if this is a safe external reference that should be ignored."""
        # Get patterns from config
        safe_patterns = self.config.get("links", {}).get("safe_external_patterns", [])
        ignore_files = self.config.get("links", {}).get("ignore_broken_links_in", [])

        # Check if URL matches any safe pattern
        for pattern in safe_patterns:
            if pattern in url:
                return True

        # Skip links in files where broken links are expected
        for ignore_file in ignore_files:
            if ignore_file in source_file:
                return True

        return False

    def _process_link(self, url: str, source_file: Path) -> None:
        """Process a single link."""
        # Skip certain URLs
        if (
            url.startswith("mailto:")
            or url.startswith("tel:")
            or url.startswith("javascript:")
            or url.startswith("#")
            or not url.strip()
        ):
            return

        if url.startswith("http://") or url.startswith("https://"):
            self.external_links.add((url, str(source_file)))
        else:
            # Internal link - resolve relative to current file
            if url.startswith("/"):
                # Absolute path from site root
                target_path = self.site_dir / url.lstrip("/")
            else:
                # Relative path
                target_path = source_file.parent / url

            # Handle anchors
            if "#" in url:
                url_part, anchor = url.split("#", 1)
                if url_part:
                    target_path = (
                        source_file.parent / url_part
                        if not url_part.startswith("/")
                        else self.site_dir / url_part.lstrip("/")
                    )
            else:
                anchor = None

            self.internal_links.add((str(target_path), str(source_file), anchor, url))

    def check_internal_links(self) -> None:
        """Check internal links."""
        print(f"Checking {len(self.internal_links)} internal links...")

        for target_path, source_file, anchor, original_url in self.internal_links:
            target = Path(target_path)

            # Skip external file references that are expected to be missing
            if self._is_safe_external_reference(original_url, source_file):
                continue

            # If it's a directory, look for index.html
            if target.is_dir():
                target = target / "index.html"

            # If no extension, try .html
            if not target.suffix and not target.is_dir():
                target = target.with_suffix(".html")

            if not target.exists():
                self.broken_links.append((source_file, original_url, f"Target not found: {target}"))
                continue

            # Check anchor if present
            if anchor and target.suffix == ".html":
                try:
                    with open(target, encoding="utf-8") as f:
                        content = f.read()
                        soup = BeautifulSoup(content, "html.parser")

                    # Look for element with id or name matching anchor
                    anchor_element = soup.find(attrs={"id": anchor}) or soup.find(attrs={"name": anchor})
                    if not anchor_element:
                        # Also check for heading with matching text (common in MkDocs)
                        heading_text = anchor.replace("-", " ").replace("_", " ")
                        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
                        found_heading = any(heading_text.lower() in heading.get_text().lower() for heading in headings)
                        if not found_heading:
                            self.warnings.append((source_file, original_url, f"Anchor not found: #{anchor}"))

                except Exception as e:
                    self.warnings.append((source_file, original_url, f"Error checking anchor: {e}"))

    def check_external_links(self) -> None:
        """Check external links."""
        if not self.check_external:
            return

        print(f"Checking {len(self.external_links)} external links...")

        session = requests.Session()
        session.headers.update({"User-Agent": "lex-helper-docs-link-checker/1.0"})

        for url, source_file in self.external_links:
            try:
                response = session.head(url, timeout=10, allow_redirects=True)
                if response.status_code >= 400:
                    self.broken_links.append((source_file, url, f"HTTP {response.status_code}"))
            except requests.exceptions.RequestException as e:
                self.warnings.append((source_file, url, f"Request failed: {e}"))

    def report_results(self) -> bool:
        """Report results and return True if no broken links."""
        print("\n" + "=" * 60)
        print("LINK CHECK RESULTS")
        print("=" * 60)

        if self.broken_links:
            print(f"\n❌ BROKEN LINKS ({len(self.broken_links)}):")
            for source_file, url, error in self.broken_links:
                print(f"  {source_file}")
                print(f"    → {url}")
                print(f"    ✗ {error}")
                print()

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for source_file, url, warning in self.warnings:
                print(f"  {source_file}")
                if url:
                    print(f"    → {url}")
                print(f"    ⚠ {warning}")
                print()

        total_links = len(self.internal_links) + len(self.external_links)
        broken_count = len(self.broken_links)
        warning_count = len(self.warnings)

        print("\nSUMMARY:")
        print(f"  Total links checked: {total_links}")
        print(f"  Broken links: {broken_count}")
        print(f"  Warnings: {warning_count}")

        if broken_count == 0:
            print("\n✅ All links are working!")
            return True
        else:
            print(f"\n❌ Found {broken_count} broken links")
            return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Check links in documentation")
    parser.add_argument("site_dir", help="Path to built documentation site")
    parser.add_argument("--external", action="store_true", help="Check external links")
    parser.add_argument("--fail-on-warnings", action="store_true", help="Fail on warnings")
    parser.add_argument("--config", type=Path, help="Path to QA configuration file")

    args = parser.parse_args()

    site_dir = Path(args.site_dir)
    if not site_dir.exists():
        print(f"Error: Site directory {site_dir} does not exist")
        return 1

    checker = LinkChecker(site_dir, check_external=args.external, config_file=args.config)
    checker.collect_links()
    checker.check_internal_links()
    checker.check_external_links()

    success = checker.report_results()

    if not success:
        return 1

    if args.fail_on_warnings and checker.warnings:
        print(f"\n❌ Failing due to {len(checker.warnings)} warnings")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
