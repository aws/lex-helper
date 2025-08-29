# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from lex_helper.utils.add_to_list import add_to_list
from lex_helper.utils.find_digit import find_digit
from lex_helper.utils.title_to_snake import title_to_snake
from lex_helper.utils.type_conversion import str_to_bool


def test_add_to_list():
    """Test adding items to a list"""
    lst = []
    lst = add_to_list(lst, "item1")
    lst = add_to_list(lst, "item2")
    assert lst == ["item1", "item2"]


def test_find_digit():
    """Test finding digits in strings"""
    assert find_digit("abc123def") == 1
    assert find_digit("no digits") is None
    assert find_digit("multiple 123 456") == 1


def test_title_to_snake():
    """Test converting title case to snake case"""
    assert title_to_snake("HelloWorld") == "hello_world"


def test_str_to_bool():
    """Test string to boolean conversion"""
    assert str_to_bool("true") is True
    assert str_to_bool("True") is True
    assert str_to_bool("false") is False
    assert str_to_bool("False") is False
    assert str_to_bool("1") is True
    assert str_to_bool("0") is False
    assert str_to_bool("invalid") is False
