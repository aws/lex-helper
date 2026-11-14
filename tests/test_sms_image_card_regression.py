# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest

from lex_helper import (
    Button,
    ImageResponseCard,
    Intent,
    LexImageResponseCard,
    LexResponse,
    SessionAttributes,
    SessionState,
    format_for_channel,
)


@pytest.mark.parametrize("card_count", [1, 2])
def test_sms_image_cards_use_the_channel_text_renderer(card_count):
    card = LexImageResponseCard(
        imageResponseCard=ImageResponseCard(
            title="Test Card",
            subtitle="Details",
            imageUrl="https://example.com/image.jpg",
            buttons=[Button(text="Book", value="book")],
        )
    )
    response = LexResponse(
        sessionState=SessionState(intent=Intent(name="Test"), sessionAttributes=SessionAttributes()),
        messages=[card.model_copy(deep=True) for _ in range(card_count)],
        requestAttributes={},
    )

    result = format_for_channel(response, "sms")

    expected = {"contentType": "PlainText", "content": "Test Card | Details | https://example.com/image.jpg | Options: Book"}
    assert result["messages"] == [expected] * card_count
