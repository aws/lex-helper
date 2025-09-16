#!/usr/bin/env python3
"""
Accessibility checker for lex-helper documentation.
Validates HTML for WCAG compliance and accessibility best practices.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: BeautifulSoup4 is required for accessibility checking")
    print("Install with: pip install beautifulsoup4")
    sys.exit(1)


class AccessibilityChecker:
    """Check HTML files for accessibility compliance."""

    def __init__(self):
        self.errors: list[tuple[str, str, str, str]] = []
        self.warnings: list[tuple[str, str, str]] = []
        self.stats = {
            "files_checked": 0,
            "images_checked": 0,
            "links_checked": 0,
            "headings_checked": 0,
            "forms_checked": 0,
        }

    def check_images(self, soup: BeautifulSoup, file_path: str) -> None:
        """Check image accessibility."""
        images = soup.find_all("img")
        self.stats["images_checked"] += len(images)

        for img in images:
            # Check for alt attribute
            if not img.get("alt"):
                self.errors.append(
                    (
                        file_path,
                        "image_alt_missing",
                        f"Image missing alt attribute: {img.get('src', 'unknown')}",
                        "Add descriptive alt text for screen readers",
                    )
                )
            elif not img.get("alt").strip():
                self.errors.append(
                    (
                        file_path,
                        "image_alt_empty",
                        f"Image has empty alt attribute: {img.get('src', 'unknown')}",
                        "Provide descriptive alt text or use alt='' for decorative images",
                    )
                )

            # Check for very long alt text
            alt_text = img.get("alt", "")
            if len(alt_text) > 125:
                self.warnings.append(
                    (
                        file_path,
                        "image_alt_long",
                        f"Alt text is very long ({len(alt_text)} chars): {img.get('src', 'unknown')}",
                    )
                )

            # Check for redundant alt text
            if alt_text.lower().startswith(("image of", "picture of", "photo of")):
                self.warnings.append(
                    (file_path, "image_alt_redundant", f"Alt text contains redundant phrase: {img.get('src', 'unknown')}")
                )

    def check_links(self, soup: BeautifulSoup, file_path: str) -> None:
        """Check link accessibility."""
        links = soup.find_all("a", href=True)
        self.stats["links_checked"] += len(links)

        for link in links:
            href = link.get("href", "")
            link_text = link.get_text(strip=True)

            # Check for empty link text
            if not link_text:
                # Check if link contains an image with alt text
                img = link.find("img")
                if img and img.get("alt"):
                    continue  # Image alt text serves as link text

                # Skip code line number links (common in documentation)
                if href.startswith("#__codelineno-"):
                    continue

                # Skip certain navigation links that are handled by JavaScript
                if href in ["javascript:void(0)", "#"]:
                    continue

                # Skip theme-related icon links (common in MkDocs Material theme)
                if self._is_theme_icon_link(href, link):
                    continue

                self.errors.append(
                    (
                        file_path,
                        "link_text_missing",
                        f"Link missing text: {href}",
                        "Add descriptive text or aria-label for screen readers",
                    )
                )

            # Check for generic link text
            generic_texts = {"click here", "read more", "more", "here", "link"}
            if link_text.lower() in generic_texts:
                self.warnings.append((file_path, "link_text_generic", f"Generic link text '{link_text}': {href}"))

            # Check for links that open in new window without indication
            if link.get("target") == "_blank":
                if "external" not in link.get("class", []) and not link.get("aria-label"):
                    self.warnings.append(
                        (file_path, "link_new_window", f"Link opens in new window without indication: {href}")
                    )

            # Check for very long link text
            if len(link_text) > 100:
                self.warnings.append(
                    (file_path, "link_text_long", f"Link text is very long ({len(link_text)} chars): {href}")
                )

    def check_headings(self, soup: BeautifulSoup, file_path: str) -> None:
        """Check heading structure and accessibility."""
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        self.stats["headings_checked"] += len(headings)

        if not headings:
            self.warnings.append((file_path, "no_headings", "Page has no headings for structure"))
            return

        # Check heading hierarchy
        prev_level = 0
        h1_count = 0

        for heading in headings:
            level = int(heading.name[1])
            heading_text = heading.get_text(strip=True)

            # Count H1 tags
            if level == 1:
                h1_count += 1

            # Check for empty headings
            if not heading_text:
                self.errors.append(
                    (file_path, "heading_empty", f"Empty {heading.name.upper()} heading", "Provide descriptive heading text")
                )
                continue

            # Check heading hierarchy (skip first heading)
            if prev_level > 0 and level > prev_level + 1:
                self.warnings.append(
                    (file_path, "heading_hierarchy", f"Heading level jumps from H{prev_level} to H{level}: '{heading_text}'")
                )

            prev_level = level

        # Check for multiple H1 tags
        if h1_count > 1:
            self.warnings.append((file_path, "multiple_h1", f"Page has {h1_count} H1 headings (should have only one)"))
        elif h1_count == 0:
            self.warnings.append((file_path, "no_h1", "Page has no H1 heading"))

    def check_forms(self, soup: BeautifulSoup, file_path: str) -> None:
        """Check form accessibility."""
        forms = soup.find_all("form")
        inputs = soup.find_all(["input", "textarea", "select"])
        self.stats["forms_checked"] += len(forms) + len(inputs)

        for input_elem in inputs:
            input_type = input_elem.get("type", "text")
            input_id = input_elem.get("id")

            # Skip hidden inputs and buttons
            if input_type in ["hidden", "submit", "button", "reset"]:
                continue

            # Skip disabled checkboxes (like task list items)
            if input_elem.has_attr("disabled"):
                continue

            # Skip theme search inputs (they're handled by the theme)
            if self._is_theme_search_input(input_elem):
                continue

            # Check for associated label
            has_label = False

            if input_id:
                # Look for label with for attribute
                label = soup.find("label", attrs={"for": input_id})
                if label:
                    has_label = True

            # Check for aria-label or aria-labelledby
            if input_elem.get("aria-label") or input_elem.get("aria-labelledby"):
                has_label = True

            # Check for placeholder as only label (not recommended)
            if not has_label and input_elem.get("placeholder"):
                self.warnings.append(
                    (
                        file_path,
                        "input_placeholder_only",
                        f"Input uses placeholder as only label: {input_elem.get('name', 'unnamed')}",
                    )
                )
                has_label = True  # Don't double-report

            if not has_label:
                self.errors.append(
                    (
                        file_path,
                        "input_no_label",
                        f"Input missing label: {input_elem.get('name', 'unnamed')}",
                        "Add a label element or aria-label attribute",
                    )
                )

    def check_color_contrast(self, soup: BeautifulSoup, file_path: str) -> None:
        """Check for potential color contrast issues."""
        # This is a basic check - full color contrast checking requires
        # rendering the page and analyzing computed styles

        # Check for inline styles that might indicate color usage
        elements_with_style = soup.find_all(attrs={"style": True})

        for elem in elements_with_style:
            style = elem.get("style", "")

            # Look for color definitions
            if "color:" in style.lower() or "background-color:" in style.lower():
                self.warnings.append((file_path, "inline_color_style", f"Element uses inline color styles: {elem.name}"))

    def check_language(self, soup: BeautifulSoup, file_path: str) -> None:
        """Check for language attributes."""
        html_elem = soup.find("html")

        if html_elem and not html_elem.get("lang"):
            self.errors.append(
                (
                    file_path,
                    "html_no_lang",
                    "HTML element missing lang attribute",
                    "Add lang='en' or appropriate language code to html element",
                )
            )

    def check_page_structure(self, soup: BeautifulSoup, file_path: str) -> None:
        """Check overall page structure."""
        # Check for page title
        title = soup.find("title")
        if not title or not title.get_text(strip=True):
            self.errors.append((file_path, "page_no_title", "Page missing title element", "Add descriptive title element"))

        # Check for main content area
        main = soup.find("main")
        if not main:
            # Look for role="main"
            main_role = soup.find(attrs={"role": "main"})
            if not main_role:
                self.warnings.append((file_path, "no_main_landmark", "Page missing main content landmark"))

        # Check for skip links
        skip_links = soup.find_all("a", href=re.compile(r"^#"))
        skip_link_found = any("skip" in link.get_text().lower() for link in skip_links)

        if not skip_link_found:
            self.warnings.append((file_path, "no_skip_link", "Page missing skip navigation link"))

    def _is_theme_icon_link(self, href: str, link_element) -> bool:
        """Check if this is a theme-related icon link that should be ignored."""
        # Common theme icon link patterns
        theme_patterns = [
            "https://github.com/",
            "https://pypi.org/",
            "https://aws.amazon.com/",
        ]

        # Check if it's a known theme icon link
        if any(pattern in href for pattern in theme_patterns):
            # Check if it has theme-related classes or is in header/footer
            classes = link_element.get("class", [])
            parent_classes = []

            # Check parent elements for theme classes
            parent = link_element.parent
            while parent and parent.name:
                parent_classes.extend(parent.get("class", []))
                parent = parent.parent

            theme_classes = ["md-header", "md-footer", "md-tabs", "md-nav", "md-social"]
            if any(cls in " ".join(classes + parent_classes) for cls in theme_classes):
                return True

        return False

    def _is_generated_table(self, table) -> bool:
        """Check if this is a generated table (like API docs) that should have relaxed rules."""
        # Check for mkdocstrings or other auto-generated content
        parent = table.parent
        while parent and parent.name:
            classes = parent.get("class", [])
            if any("doc" in cls or "mkdocstrings" in cls for cls in classes):
                return True
            parent = parent.parent
        return False

    def _is_theme_search_input(self, input_elem) -> bool:
        """Check if this is a theme search input that should be ignored."""
        # Check for search-related attributes
        input_type = input_elem.get("type", "")
        placeholder = input_elem.get("placeholder", "").lower()
        classes = input_elem.get("class", [])

        # Common search input patterns
        if input_type == "search":
            return True

        if "search" in placeholder:
            return True

        if any("search" in cls for cls in classes):
            return True

        # Check parent elements for search context
        parent = input_elem.parent
        while parent and parent.name:
            parent_classes = parent.get("class", [])
            if any("search" in cls or "md-search" in cls for cls in parent_classes):
                return True
            parent = parent.parent

        return False

    def check_tables(self, soup: BeautifulSoup, file_path: str) -> None:
        """Check table accessibility."""
        tables = soup.find_all("table")

        for table in tables:
            # Skip auto-generated tables (like API documentation)
            if self._is_generated_table(table):
                continue

            # Check for table headers
            headers = table.find_all(["th"])
            if not headers:
                self.warnings.append((file_path, "table_no_headers", "Table missing header cells (th elements)"))

            # Check for table caption
            caption = table.find("caption")
            if not caption:
                self.warnings.append((file_path, "table_no_caption", "Table missing caption element"))

    def check_file(self, file_path: Path) -> None:
        """Check accessibility of a single HTML file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.warnings.append((str(file_path), "file_read_error", f"Error reading file: {e}"))
            return

        self.stats["files_checked"] += 1

        try:
            soup = BeautifulSoup(content, "html.parser")
        except Exception as e:
            self.warnings.append((str(file_path), "parse_error", f"Error parsing HTML: {e}"))
            return

        # Run all accessibility checks
        self.check_language(soup, str(file_path))
        self.check_page_structure(soup, str(file_path))
        self.check_headings(soup, str(file_path))
        self.check_images(soup, str(file_path))
        self.check_links(soup, str(file_path))
        self.check_forms(soup, str(file_path))
        self.check_tables(soup, str(file_path))
        self.check_color_contrast(soup, str(file_path))

    def check_directory(self, directory: Path) -> None:
        """Check accessibility of all HTML files in directory."""
        html_files = list(directory.rglob("*.html"))
        print(f"Checking {len(html_files)} HTML files for accessibility...")

        for file_path in html_files:
            if file_path.is_file():
                self.check_file(file_path)

    def report_results(self) -> bool:
        """Report results and return True if no errors."""
        print("\n" + "=" * 60)
        print("ACCESSIBILITY CHECK RESULTS")
        print("=" * 60)

        print("\nSTATISTICS:")
        print(f"  Files checked: {self.stats['files_checked']}")
        print(f"  Images checked: {self.stats['images_checked']}")
        print(f"  Links checked: {self.stats['links_checked']}")
        print(f"  Headings checked: {self.stats['headings_checked']}")
        print(f"  Form elements checked: {self.stats['forms_checked']}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")

            # Group warnings by type
            warnings_by_type: dict[str, list[tuple[str, str]]] = {}
            for file_path, warning_type, message in self.warnings:
                if warning_type not in warnings_by_type:
                    warnings_by_type[warning_type] = []
                warnings_by_type[warning_type].append((file_path, message))

            for warning_type, type_warnings in warnings_by_type.items():
                print(f"\n  {warning_type.replace('_', ' ').title()}:")
                for file_path, message in type_warnings:
                    print(f"    {file_path}: {message}")

        if self.errors:
            print(f"\n❌ ACCESSIBILITY ERRORS ({len(self.errors)}):")

            # Group errors by type
            errors_by_type: dict[str, list[tuple[str, str, str]]] = {}
            for file_path, error_type, message, suggestion in self.errors:
                if error_type not in errors_by_type:
                    errors_by_type[error_type] = []
                errors_by_type[error_type].append((file_path, message, suggestion))

            for error_type, type_errors in errors_by_type.items():
                print(f"\n  {error_type.replace('_', ' ').title()}:")
                for file_path, message, suggestion in type_errors:
                    print(f"    {file_path}: {message}")
                    print(f"      → {suggestion}")

        print("\nSUMMARY:")
        print(f"  Accessibility errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")

        if len(self.errors) == 0:
            print("\n✅ No critical accessibility errors found!")
            if self.warnings:
                print(f"   Consider addressing {len(self.warnings)} warnings for better accessibility")
            return True
        else:
            print(f"\n❌ Found {len(self.errors)} accessibility errors")
            return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Check accessibility of HTML documentation")
    parser.add_argument("site_dir", help="Directory containing built HTML files")
    parser.add_argument("--fail-on-warnings", action="store_true", help="Fail on warnings as well as errors")

    args = parser.parse_args()

    site_dir = Path(args.site_dir)
    if not site_dir.exists():
        print(f"Error: Site directory {site_dir} does not exist")
        return 1

    checker = AccessibilityChecker()
    checker.check_directory(site_dir)
    success = checker.report_results()

    if not success:
        return 1

    if args.fail_on_warnings and checker.warnings:
        print(f"\n❌ Failing due to {len(checker.warnings)} warnings")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
