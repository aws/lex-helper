# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest

from lex_helper.utils import safe_float, safe_int


@pytest.mark.parametrize(
    "convert, value", [(safe_int, float("inf")), (safe_int, float("-inf")), (safe_int, "1e1000"), (safe_float, 10**400)]
)
@pytest.mark.parametrize("default", [None, -7])
def test_safe_numeric_conversion_returns_default_on_overflow(convert, value, default):
    assert convert(value, default=default) == default
