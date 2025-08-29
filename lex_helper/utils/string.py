# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""String manipulation utilities."""

import re


def title_to_snake(text: str) -> str:
    """Convert a title case string to snake case.

    Args:
        text: Title case string to convert

    Returns:
        Snake case string

    Example:
        >>> title_to_snake("HelloWorld")
        'hello_world'
        >>> title_to_snake("API Response")
        'api_response'
    """
    # Insert underscore between camelCase
    text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    # Insert underscore between lowercase and uppercase
    text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
    # Convert to lowercase
    return text.lower()


def snake_to_camel(text: str) -> str:
    """Convert a snake case string to camel case.

    Args:
        text: Snake case string to convert

    Returns:
        Camel case string

    Example:
        >>> snake_to_camel("hello_world")
        'helloWorld'
        >>> snake_to_camel("api_response")
        'apiResponse'
    """
    components = text.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def split_full_name(full_name: str) -> tuple[str, str]:
    """Split a full name into first name and last name.

    Args:
        full_name: Full name to split

    Returns:
        Tuple of (first_name, last_name)

    Example:
        >>> split_full_name("John Doe")
        ('John', 'Doe')
        >>> split_full_name("Mary Jane Smith")
        ('Mary', 'Jane Smith')
    """
    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    elif len(parts) == 2:
        return parts[0], parts[1]
    else:
        return parts[0], " ".join(parts[1:])


def find_digit(text: str) -> str:
    """Find the first digit in a string.

    Args:
        text: String to search for digits

    Returns:
        First digit found or empty string if no digits

    Example:
        >>> find_digit("abc123def")
        '1'
        >>> find_digit("no digits")
        ''
    """
    match = re.search(r"\d", text)
    return match.group() if match else ""


def extract_numbers(text: str) -> list[str]:
    """Extract all numbers from a string.

    Args:
        text: String to extract numbers from

    Returns:
        List of numbers found as strings

    Example:
        >>> extract_numbers("Room 123, Price: $45.67")
        ['123', '45.67']
    """
    return re.findall(r"\d+(?:\.\d+)?", text)


def is_valid_email(email: str) -> bool:
    """Check if string is a valid email address.

    Args:
        email: String to validate as email

    Returns:
        True if valid email, False otherwise

    Example:
        >>> is_valid_email("user@example.com")
        True
        >>> is_valid_email("invalid.email")
        False
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))
