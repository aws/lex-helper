# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from typing import cast

import fulfillment_function.utils as utils

from lex_helper import (
    LexCustomPayload,
    LexImageResponseCard,
    LexPlainText,
    LexResponse,
    SessionAttributes,
)


def assert_contains_message(response: LexResponse, text: str) -> None:
    # This verifies that the response contains the message
    received_messages = response.messages
    received_messages_content: list[str] = []
    for message in received_messages:  # type: ignore
        if isinstance(message, LexCustomPayload):
            continue
        if hasattr(message, "imageResponseCard"):
            image_response_card = cast(LexImageResponseCard, message)
            received_messages_content.append(image_response_card.imageResponseCard.title)
        else:
            plaintext_card = cast(LexPlainText, message)
            if plaintext_card.content:
                received_messages_content.append(plaintext_card.content)
    assert text in received_messages_content, f"Expected message {text} not found in {received_messages_content}"


def assert_contains_response_code(
    response: LexResponse,
    intent_name: str,
    response_code: str,
    session_attributes: SessionAttributes | None = None,
):
    # This verifies that the response contains the response code (pulling from AEM)
    expected_messages = utils.create_response(
        intent=intent_name, response_code=response_code, session_attributes=session_attributes
    )
    if isinstance(expected_messages[0], LexPlainText) and expected_messages[0].content == response_code:
        raise ValueError(f"Response code {response_code} not found in AEM for intent {intent_name}")
    received_messages = response.messages

    # Get just the content of expected_messages
    expected_messages_content: list[str] = [
        message.content for message in expected_messages if isinstance(message, LexPlainText) and message.content
    ]

    # Get just the content of received_messages.  If a message is an LexImageResponseCard, we want to get the title
    received_messages_content = []
    for message in received_messages:
        if hasattr(message, "imageResponseCard"):
            received_messages_content.append(message.imageResponseCard.title)  # type: ignore
        else:
            received_messages_content.append(message.content)  # type: ignore
    # Ensure that all expected_messages_content are in received_messages_content
    for expected_message in expected_messages_content:
        assert expected_message in received_messages_content, (
            f"Expected message {expected_message} not found in {received_messages_content}"
        )
