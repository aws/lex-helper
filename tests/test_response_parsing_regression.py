# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from pydantic import ValidationError

from lex_helper.core.types import LexCustomPayload, LexImageResponseCard, LexPlainText, parse_lex_response


@pytest.mark.parametrize(
    "data, expected_type",
    [
        ({"contentType": "PlainText", "content": "hello"}, LexPlainText),
        ({"contentType": "ImageResponseCard", "imageResponseCard": {"title": "hello"}}, LexImageResponseCard),
        ({"contentType": "CustomPayload", "content": "hello"}, LexCustomPayload),
        ({"contentType": "CustomPayload", "content": {"text": "hello"}}, LexCustomPayload),
    ],
)
def test_parse_all_supported_response_types(data, expected_type):
    assert isinstance(parse_lex_response(data), expected_type)


@pytest.mark.parametrize("data", [{}, {"contentType": "unknown", "content": "hello"}])
def test_parse_invalid_response_reports_validation_error(data):
    with pytest.raises(ValidationError):
        parse_lex_response(data)
