# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Validation utilities."""

from typing import Any


def is_value_set(value: Any) -> bool:
    """Check if a value is set (not None and not empty).

    Args:
        value: Value to check

    Returns:
        True if value is set, False otherwise

    Example:
        >>> is_value_set(None)
        False
        >>> is_value_set("")
        False
        >>> is_value_set(0)
        True
        >>> is_value_set([])
        False
    """
    if value is None:
        return False
    if isinstance(value, str | list | dict | set | tuple):
        return bool(value)
    return True


def is_numeric(value: Any) -> bool:
    """Check if a value is numeric.

    Args:
        value: Value to check

    Returns:
        True if value is numeric, False otherwise

    Example:
        >>> is_numeric(123)
        True
        >>> is_numeric("123")
        True
        >>> is_numeric("12.34")
        True
        >>> is_numeric("abc")
        False
    """
    if isinstance(value, int | float):
        return True
    if isinstance(value, str):
        try:
            float(value)
            return True
        except ValueError:
            return False
    return False


def is_within_range(
    value: int | float,
    min_value: int | float | None = None,
    max_value: int | float | None = None,
) -> bool:
    """Check if a numeric value is within a specified range.

    Args:
        value: Value to check
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)

    Returns:
        True if value is within range, False otherwise

    Example:
        >>> is_within_range(5, 0, 10)
        True
        >>> is_within_range(15, 0, 10)
        False
    """
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def has_required_keys(data: dict[str, Any], required_keys: list[str]) -> bool:
    """Check if a dictionary has all required keys.

    Args:
        data: Dictionary to check
        required_keys: List of required keys

    Returns:
        True if all required keys are present, False otherwise

    Example:
        >>> has_required_keys({"name": "John", "age": 30}, ["name"])
        True
        >>> has_required_keys({"name": "John"}, ["name", "age"])
        False
    """
    return all(key in data for key in required_keys)


def is_valid_length(
    value: str | list[Any] | dict[str, Any],
    min_length: int | None = None,
    max_length: int | None = None,
) -> bool:
    """Check if a value's length is within specified bounds.

    Args:
        value: Value to check length of
        min_length: Minimum allowed length (inclusive)
        max_length: Maximum allowed length (inclusive)

    Returns:
        True if length is valid, False otherwise

    Example:
        >>> is_valid_length("test", 2, 6)
        True
        >>> is_valid_length([1, 2, 3], max_length=2)
        False
    """
    length = len(value)
    if min_length is not None and length < min_length:
        return False
    if max_length is not None and length > max_length:
        return False
    return True


def are_types_valid(values: list[Any], expected_type: type) -> bool:
    """Check if all values in a list are of the expected type.

    Args:
        values: List of values to check
        expected_type: Expected type of values

    Returns:
        True if all values are of expected type, False otherwise

    Example:
        >>> are_types_valid([1, 2, 3], int)
        True
        >>> are_types_valid([1, "2", 3], int)
        False
    """
    return all(isinstance(value, expected_type) for value in values)
