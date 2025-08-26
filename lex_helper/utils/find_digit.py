# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Optional


def find_digit(s: Optional[str]) -> Optional[int]:
    """Finds the first digit in the given string and returns it."""

    if s is None:
        return None
    for char in s:
        if char.isdigit():
            return int(char)
    return None
