# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest

from lex_helper import Intent, LexCustomPayload, LexResponse, SessionAttributes, SessionState, format_for_channel


@pytest.mark.parametrize("channel", ["lex", "sms"])
@pytest.mark.parametrize("content", ["hello", {"text": "hello"}, {"message": "hello"}])
def test_format_custom_payload_through_public_api(channel, content):
    response = LexResponse(
        sessionState=SessionState(intent=Intent(name="Test"), sessionAttributes=SessionAttributes()),
        messages=[LexCustomPayload(content=content)],
        requestAttributes={},
    )

    result = format_for_channel(response, channel)

    assert result["messages"] == [{"content": "hello", "contentType": "CustomPayload"}]
    assert response.messages[0].content == content
