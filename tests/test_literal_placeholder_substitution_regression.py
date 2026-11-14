# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest

from lex_helper.formatters import substitute_keys_in_text


@pytest.mark.parametrize("value", [r"C:\new\temp", r"\1", r"\g<missing>", "normal"])
def test_placeholder_values_are_inserted_literally(value):
    result = substitute_keys_in_text("File {path}; again {path}; {unknown}", {"path": value})
    assert result == "File " + value + "; again " + value + "; {unknown}"
