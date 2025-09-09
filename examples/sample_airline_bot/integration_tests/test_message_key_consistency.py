# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Test message key consistency across all locale YAML files.

This test ensures that all message YAML files have exactly the same keys,
preventing missing translations and inconsistent message structures.
"""

from pathlib import Path
from typing import Any

import pytest
import yaml


def flatten_dict(d: dict[str, Any], parent_key: str = "", sep: str = ".") -> set[str]:
    """
    Flatten a nested dictionary and return a set of all keys.

    Args:
        d: Dictionary to flatten
        parent_key: Parent key for nested structures
        sep: Separator for nested keys

    Returns:
        Set of all flattened keys
    """
    keys = set()

    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            keys.update(flatten_dict(v, new_key, sep))
        else:
            keys.add(new_key)

    return keys


def load_yaml_file(file_path: Path) -> dict[str, Any]:
    """
    Load and parse a YAML file.

    Args:
        file_path: Path to the YAML file

    Returns:
        Parsed YAML content as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    try:
        with open(file_path, encoding="utf-8") as file:
            content = yaml.safe_load(file)
            return content if content is not None else {}
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Message file not found: {file_path}") from e
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in {file_path}: {e}") from e


def get_message_files() -> list[Path]:
    """
    Get all message YAML files from the messages directory.

    Returns:
        List of Path objects for message files
    """
    # Get the directory containing this test file
    test_dir = Path(__file__).parent

    # Navigate to the messages directory
    messages_dir = test_dir / "../lambdas/fulfillment_function/src/fulfillment_function/messages"
    messages_dir = messages_dir.resolve()

    if not messages_dir.exists():
        pytest.skip(f"Messages directory not found: {messages_dir}")

    # Find all YAML files that start with "messages"
    message_files = list(messages_dir.glob("messages*.yaml")) + list(messages_dir.glob("messages*.yml"))

    if not message_files:
        pytest.skip(f"No message files found in: {messages_dir}")

    return sorted(message_files)


class TestMessageKeyConsistency:
    """Test cases for message key consistency across locales."""

    def test_all_message_files_have_same_keys(self):
        """Test that all message YAML files have exactly the same keys."""
        message_files = get_message_files()

        if len(message_files) < 2:
            pytest.skip("Need at least 2 message files to test consistency")

        # Load all message files and extract their keys
        file_keys = {}
        file_contents = {}

        for file_path in message_files:
            try:
                content = load_yaml_file(file_path)
                keys = flatten_dict(content)
                file_keys[file_path.name] = keys
                file_contents[file_path.name] = content
            except Exception as e:
                pytest.fail(f"Failed to load {file_path.name}: {e}")

        # Compare all files against the first one (reference)
        reference_file = message_files[0].name
        reference_keys = file_keys[reference_file]

        errors = []

        for file_name, keys in file_keys.items():
            if file_name == reference_file:
                continue

            # Find missing keys (in reference but not in current file)
            missing_keys = reference_keys - keys
            if missing_keys:
                errors.append(f"❌ {file_name} is missing keys: {sorted(missing_keys)}")

            # Find extra keys (in current file but not in reference)
            extra_keys = keys - reference_keys
            if extra_keys:
                errors.append(f"❌ {file_name} has extra keys: {sorted(extra_keys)}")

        # If there are errors, provide detailed report
        if errors:
            error_report = [
                "Message key consistency check failed!",
                f"Reference file: {reference_file}",
                f"Total keys in reference: {len(reference_keys)}",
                "",
                "Issues found:",
            ]
            error_report.extend(errors)

            # Add summary of all keys for debugging
            error_report.extend(["", "All keys in reference file:", *[f"  - {key}" for key in sorted(reference_keys)]])

            pytest.fail("\n".join(error_report))

    def test_message_files_are_valid_yaml(self):
        """Test that all message files contain valid YAML."""
        message_files = get_message_files()

        for file_path in message_files:
            try:
                content = load_yaml_file(file_path)
                assert isinstance(content, dict), f"{file_path.name} should contain a dictionary at root level"
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {file_path.name}: {e}")
            except Exception as e:
                pytest.fail(f"Failed to load {file_path.name}: {e}")

    def test_message_files_not_empty(self):
        """Test that all message files contain actual content."""
        message_files = get_message_files()

        for file_path in message_files:
            content = load_yaml_file(file_path)

            assert content, f"{file_path.name} is empty or contains only null values"

            # Check that it has at least some nested structure
            keys = flatten_dict(content)
            assert len(keys) > 0, f"{file_path.name} contains no message keys"

    def test_required_message_categories_exist(self):
        """Test that all message files contain required message categories."""
        message_files = get_message_files()

        # Define required top-level categories that should exist in all files
        required_categories = {
            "general",  # General messages like errors, goodbye, etc.
            "greeting",  # Greeting messages
            "book_flight",  # Flight booking messages
            "cancel_flight",  # Flight cancellation messages
        }

        for file_path in message_files:
            content = load_yaml_file(file_path)

            existing_categories = set(content.keys())
            missing_categories = required_categories - existing_categories

            if missing_categories:
                pytest.fail(f"{file_path.name} is missing required message categories: {sorted(missing_categories)}")

    def test_no_placeholder_values(self):
        """Test that message files don't contain placeholder values."""
        message_files = get_message_files()

        # Common placeholder patterns that shouldn't exist in production
        placeholder_patterns = [
            "TODO",
            "FIXME",
            "PLACEHOLDER",
            "TBD",
            "XXX",
            "{{",  # Unprocessed template variables
            "}}",
        ]

        for file_path in message_files:
            content = load_yaml_file(file_path)

            # Convert entire content to string for searching
            content_str = yaml.dump(content, default_flow_style=False)

            found_placeholders = []
            for pattern in placeholder_patterns:
                if pattern in content_str.upper():
                    found_placeholders.append(pattern)

            if found_placeholders:
                pytest.fail(
                    f"{file_path.name} contains placeholder values: {found_placeholders}. "
                    f"All messages should be properly translated."
                )

    def test_message_parameter_consistency(self):
        """Test that messages with parameters have consistent parameter usage."""
        message_files = get_message_files()

        if len(message_files) < 2:
            pytest.skip("Need at least 2 message files to test parameter consistency")

        # Load all files
        all_contents = {}
        for file_path in message_files:
            all_contents[file_path.name] = load_yaml_file(file_path)

        # Get reference file
        reference_file = message_files[0].name
        reference_content = all_contents[reference_file]

        errors = []

        def extract_parameters(text: str) -> set[str]:
            """Extract parameter names from message text like {param_name}."""
            import re

            return set(re.findall(r"\{(\w+)\}", text))

        def check_parameters_recursive(ref_dict: dict, other_dict: dict, path: str = ""):
            """Recursively check parameter consistency."""
            for key, ref_value in ref_dict.items():
                current_path = f"{path}.{key}" if path else key

                if key not in other_dict:
                    continue  # Missing key will be caught by other test

                other_value = other_dict[key]

                if isinstance(ref_value, dict) and isinstance(other_value, dict):
                    check_parameters_recursive(ref_value, other_value, current_path)
                elif isinstance(ref_value, str) and isinstance(other_value, str):
                    ref_params = extract_parameters(ref_value)
                    other_params = extract_parameters(other_value)

                    if ref_params != other_params:
                        missing = ref_params - other_params
                        extra = other_params - ref_params

                        error_parts = []
                        if missing:
                            error_parts.append(f"missing: {sorted(missing)}")
                        if extra:
                            error_parts.append(f"extra: {sorted(extra)}")

                        errors.append(f"Parameter mismatch in {current_path}: {', '.join(error_parts)}")

        # Check each file against reference
        for file_name, content in all_contents.items():
            if file_name == reference_file:
                continue

            check_parameters_recursive(reference_content, content)

        if errors:
            error_report = [
                "Message parameter consistency check failed!",
                f"Reference file: {reference_file}",
                "",
                "Parameter mismatches found:",
            ]
            error_report.extend([f"  - {error}" for error in errors])

            pytest.fail("\n".join(error_report))


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])
