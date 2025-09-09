# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from examples.basic_handler.handler import lambda_handler
from lex_helper import Config, LexHelper, SessionAttributes


class TestSessionAttributes(SessionAttributes):
    current_weather: str = "sunny"
    test_value: str = "test"


def create_test_event(
    intent_name: str = "BookHotel",
    slots: dict[str, Any] | None = None,
    session_attributes: dict[str, Any] | None = None,
    input_transcript: str = "test",
) -> dict[str, Any]:
    """Helper function to create test events with customizable parameters"""
    return {
        "sessionId": "test",
        "bot": {
            "name": "test",
            "aliasId": "test",
            "version": "test",
            "localeId": "en_US",
        },
        "inputTranscript": input_transcript,
        "inputMode": "test",
        "invocationSource": "test",
        "messageVersion": "test",
        "transcriptions": [],
        "responseContentType": "test",
        "sessionState": {
            "sessionAttributes": session_attributes or {"current_weather": "sunny"},
            "activeContexts": [],
            "intent": {
                "name": intent_name,
                "slots": slots or {},
                "state": "Fulfilled",
                "confirmationState": "None",
            },
        },
    }


def test_basic_handler():
    """Test basic handler functionality with default event"""
    event = create_test_event()
    context = {}
    response = lambda_handler(event, context)
    assert response["messages"][0]["content"] == "Hello, it sure is sunny today!  Good luck booking a hotel!"


def test_handler_with_custom_session_attributes():
    """Test handler with custom session attributes"""
    config = Config(session_attributes=TestSessionAttributes(), package_name="examples.basic_handler")
    lex_helper = LexHelper(config=config)

    event = create_test_event(session_attributes={"current_weather": "rainy", "test_value": "custom"})
    context = {}

    response = lex_helper.handler(event, context)
    assert "rainy" in response["messages"][0]["content"]


def test_handler_with_slots():
    """Test handler with slot values"""
    event = create_test_event(
        intent_name="BookHotel",
        slots={"location": {"value": {"originalValue": "New York"}}},
    )
    context = {}

    response = lambda_handler(event, context)
    assert response["sessionState"]["intent"]["slots"]["location"]["value"]["originalValue"] == "New York"


def test_handler_with_unknown_intent():
    """Test handler behavior with unknown intent"""
    event = create_test_event(intent_name="UnknownIntent")
    context = {}

    # With auto exception handling enabled, this should return an error response instead of raising
    response = lambda_handler(event, context)

    # Should return a valid error response
    assert isinstance(response, dict)
    assert "sessionState" in response
    assert "messages" in response
    assert response["sessionState"]["dialogAction"]["type"] == "Close"


def test_handler_with_active_contexts():
    """Test handler with active contexts"""
    event = create_test_event()
    event["sessionState"]["activeContexts"] = [
        {
            "name": "test_context",
            "contextAttributes": {},
            "timeToLive": {"timeToLiveInSeconds": 600, "turnsToLive": 1},
        }
    ]
    context = {}

    response = lambda_handler(event, context)
    assert "transition_to_exit" in [ctx["name"] for ctx in response["sessionState"]["activeContexts"]]


def test_handler_session_attribute_persistence():
    """Test that session attributes persist through the handler"""
    event = create_test_event(session_attributes={"current_weather": "cloudy", "persistent_value": "should_remain"})
    context = {}

    response = lambda_handler(event, context)
    assert response["sessionState"]["sessionAttributes"]["persistent_value"] == "should_remain"


def test_handler_input_validation():
    """Test handler input validation"""
    invalid_event = {"invalid": "event"}
    context = {}

    # With auto exception handling enabled, this should return an error response instead of raising
    response = lambda_handler(invalid_event, context)

    # Should return a valid error response
    assert isinstance(response, dict)
    assert "sessionState" in response
    assert "messages" in response
    assert response["sessionState"]["dialogAction"]["type"] == "Close"


def test_handler_response_format():
    """Test handler response format compliance"""
    event = create_test_event()
    context = {}

    response: dict[str, Any] = lambda_handler(event, context)
    messages: list[dict[str, Any]] = response["messages"]

    # Verify response structure
    assert "messages" in response
    assert "sessionState" in response
    assert isinstance(messages, list)
    assert all(isinstance(msg, dict) for msg in messages)
    assert all(isinstance(msg.get("content"), str) for msg in messages)
