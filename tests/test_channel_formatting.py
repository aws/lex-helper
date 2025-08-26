# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from lex_helper import (
    Button,
    ImageResponseCard,
    Intent,
    LexImageResponseCard,
    LexPlainText,
    LexResponse,
    SessionAttributes,
    SessionState,
    format_for_channel,
)


class TestSessionAttributes(SessionAttributes):
    test_value: str = "test"


def create_test_response(
    messages: list[Any],
    session_attributes: TestSessionAttributes | None = None,
) -> LexResponse[TestSessionAttributes]:
    if session_attributes is None:
        session_attributes = TestSessionAttributes()
    """Helper function to create test responses"""
    return LexResponse(
        sessionState=SessionState(
            sessionAttributes=session_attributes,
            intent=Intent(name="TestIntent"),
            activeContexts=None,
        ),
        messages=messages,
        requestAttributes={},
    )


def test_format_plain_text_lex():
    """Test formatting plain text message for Lex channel"""
    message = LexPlainText(content="Test message")
    response = create_test_response([message])
    
    formatted = format_for_channel(response, "lex")
    
    assert formatted["messages"][0]["contentType"] == "PlainText"
    assert formatted["messages"][0]["content"] == "Test message"


def test_format_plain_text_sms():
    """Test formatting plain text message for SMS channel"""
    message = LexPlainText(content="Test message")
    response = create_test_response([message])
    
    formatted = format_for_channel(response, "sms")
    
    assert formatted["messages"][0]["contentType"] == "PlainText"
    assert formatted["messages"][0]["content"] == "Test message"


def test_format_image_card_lex():
    """Test formatting image card for Lex channel"""
    image_card = ImageResponseCard(
        title="Test Card",
        subtitle="Test Subtitle",
        imageUrl="https://example.com/image.jpg",
        buttons=[
            Button(text="Button 1", value="value1"),
            Button(text="Button 2", value="value2"),
        ],
    )
    message = LexImageResponseCard(
        imageResponseCard=image_card,
        contentType="ImageResponseCard",
    )
    response = create_test_response([message])
    
    formatted = format_for_channel(response, "lex")
    
    # Lex requires a PlainText message before ImageResponseCard
    assert len(formatted["messages"]) == 2
    assert formatted["messages"][0]["contentType"] == "PlainText"
    assert formatted["messages"][0]["content"] == "Test Card"
    assert formatted["messages"][1]["contentType"] == "ImageResponseCard"
    assert formatted["messages"][1]["imageResponseCard"]["buttons"][0]["text"] == "Button 1"
    assert formatted["messages"][1]["imageResponseCard"]["buttons"][1]["text"] == "Button 2"


def test_format_image_card_sms():
    """Test formatting image card for SMS channel"""
    image_card = ImageResponseCard(
        title="Test Card",
        subtitle="Test Subtitle",
        imageUrl="https://example.com/image.jpg",
        buttons=[
            Button(text="Button 1", value="value1"),
            Button(text="Button 2", value="value2"),
        ],
    )
    message = LexImageResponseCard(
        imageResponseCard=image_card,
        contentType="ImageResponseCard",
    )
    response = create_test_response([message])
    
    formatted = format_for_channel(response, "sms")
    
    # SMS formats image cards as plain text
    assert formatted["messages"][0]["contentType"] == "PlainText"
    assert "Test Card" in formatted["messages"][0]["content"]



def test_format_multiple_messages():
    """Test formatting multiple messages"""
    messages = [
        LexPlainText(content="Message 1"),
        LexPlainText(content="Message 2"),
        LexImageResponseCard(
            imageResponseCard=ImageResponseCard(
                title="Test Card",
                subtitle="Test Subtitle",
                buttons=[Button(text="Button", value="value")],
            )
        ),
    ]
    response = create_test_response(messages)
    
    formatted = format_for_channel(response, "lex")
    
    assert len(formatted["messages"]) == 3
    assert formatted["messages"][0]["content"] == "Message 1"
    assert formatted["messages"][1]["content"] == "Message 2"
    assert formatted["messages"][2]["contentType"] == "ImageResponseCard"


def test_format_with_session_attributes():
    """Test formatting with session attributes"""
    message = LexPlainText(content="Test message")
    session_attrs = TestSessionAttributes(test_value="custom")
    response = create_test_response([message], session_attrs)
    
    formatted = format_for_channel(response, "lex")
    
    assert formatted["sessionState"]["sessionAttributes"]["test_value"] == "custom"


def test_invalid_channel():
    """Test formatting with invalid channel defaults to Lex"""
    message = LexPlainText(content="Test message")
    response = create_test_response([message])
    
    formatted = format_for_channel(response, "invalid_channel")
    
    assert formatted["messages"][0]["contentType"] == "PlainText"
    assert formatted["messages"][0]["content"] == "Test message"


