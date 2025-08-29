# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Type conversion utilities."""

from typing import Any


def str_to_bool(value: str) -> bool:
    """Convert a string to a boolean value.

    Args:
        value: String to convert

    Returns:
        Boolean value

    Example:
        >>> str_to_bool("true")
        True
        >>> str_to_bool("yes")
        True
        >>> str_to_bool("0")
        False
    """
    return value.lower() in ("true", "yes", "1", "on", "t", "y")


def safe_int(value: Any, default: int | None = None) -> int | None:
    """Safely convert a value to integer.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Integer value or default if conversion fails

    Example:
        >>> safe_int("123")
        123
        >>> safe_int("abc", default=0)
        0
    """
    try:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            return int(float(value))
        return default
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float | None = None) -> float | None:
    """Safely convert a value to float.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value or default if conversion fails

    Example:
        >>> safe_float("12.34")
        12.34
        >>> safe_float("abc", default=0.0)
        0.0
    """
    try:
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value)
        return default
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """Safely convert a value to string.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        String value or default if conversion fails

    Example:
        >>> safe_str(123)
        '123'
        >>> safe_str(None, default="N/A")
        'N/A'
    """
    try:
        if value is None:
            return default
        return str(value)
    except Exception:
        return default


def to_list(value: Any) -> list[Any]:
    """Convert a value to a list.

    Args:
        value: Value to convert

    Returns:
        List containing the value, or empty list if value is None

    Example:
        >>> to_list(123)
        [123]
        >>> to_list([1, 2, 3])
        [1, 2, 3]
        >>> to_list(None)
        []
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def to_dict(value: Any) -> dict[str, Any]:
    """Convert a value to a dictionary.

    Args:
        value: Value to convert

    Returns:
        Dictionary representation of the value

    Example:
        >>> to_dict({"a": 1})
        {'a': 1}
        >>> to_dict([("a", 1), ("b", 2)])
        {'a': 1, 'b': 2}
    """
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, (list, tuple)) and all(isinstance(item, tuple) and len(item) == 2 for item in value):  # type: ignore
        return dict(value)
    if hasattr(value, "__dict__"):
        return value.__dict__
    return {}
