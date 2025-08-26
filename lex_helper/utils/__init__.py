# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""General utility functions."""

from lex_helper.utils.add_to_list import add_to_list
from lex_helper.utils.string import (
    extract_numbers,
    find_digit,
    is_valid_email,
    snake_to_camel,
    split_full_name,
    title_to_snake,
)
from lex_helper.utils.type_conversion import (
    safe_float,
    safe_int,
    safe_str,
    str_to_bool,
    to_dict,
    to_list,
)
from lex_helper.utils.validation import (
    are_types_valid,
    has_required_keys,
    is_numeric,
    is_valid_length,
    is_value_set,
    is_within_range,
)

__all__ = [
    # String utilities
    'extract_numbers',
    'find_digit',
    'is_valid_email',
    'snake_to_camel',
    'split_full_name',
    'title_to_snake',
    
    # Type conversion utilities
    'safe_float',
    'safe_int',
    'safe_str',
    'str_to_bool',
    'to_dict',
    'to_list',
    
    # Validation utilities
    'are_types_valid',
    'has_required_keys',
    'is_numeric',
    'is_valid_length',
    'is_value_set',
    'is_within_range',
    
    # Add to list
    'add_to_list',
]
