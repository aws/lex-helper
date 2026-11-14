# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest

from lex_helper.utils import safe_int


@pytest.mark.parametrize(
    "value, expected",
    [
        ("9007199254740993", 9007199254740993),
        ("-9007199254740993", -9007199254740993),
        ("9223372036854775807", 9223372036854775807),
        ("12.9", 12),
        ("-12.9", -12),
        ("1e3", 1000),
    ],
)
def test_safe_int_preserves_integer_literal_precision(value, expected):
    assert safe_int(value) == expected
