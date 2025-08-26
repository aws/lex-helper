# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Union

from lex_helper import (
    Intent,
    LexBaseResponse,
    LexMessages,
    LexPlainText,
    LexResponse,
    PlainText,
    SessionAttributes,
    SessionState,
    format_for_channel,
)


def test_format_for_channel_sms():
    sample_response_with_href = get_sample_lex_response(
        LexPlainText(content="Next message is a hyperlink"),
        LexPlainText(content="https://examplehyperlink"),
    )
    formatted_for_sms = format_for_channel(
        response=sample_response_with_href, channel_string="sms"
    )
    received_messages = formatted_for_sms["messages"]
    expected_messages = [
        {"content": "Next message is a hyperlink", "contentType": "PlainText"},
        {"content": "https://examplehyperlink", "contentType": "PlainText"},
    ]

    assert received_messages == expected_messages


def get_sample_lex_response(
    *args: Union[
        LexBaseResponse,
        PlainText,
    ],
) -> LexResponse[SessionAttributes]:
    messages: LexMessages = [card for card in args]

    return LexResponse(
        sessionState=SessionState(
            activeContexts=[],
            sessionAttributes=SessionAttributes(),
            intent=Intent(
                name="formatting_test",
                slots={},
                state="Fulfilled",
                confirmationState="None",
            ),
        ),
        requestAttributes={},
        messages=messages,
    )
