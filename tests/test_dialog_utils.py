# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Optional

from lex_helper import Intent, LexPlainText, LexSlot, SessionAttributes, dialog


class TestSlot(LexSlot):
    NEW_SLOT = "new_slot"


class TestSessionAttributes(SessionAttributes):
    test_value: str = "test"


def create_test_request(
    intent_name: str = "TestIntent",
    slots: Optional[dict[str, Any]] = None,
    session_attributes: Optional[dict[str, Any]] = None,
    active_contexts: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Helper function to create test requests"""
    return {
        "sessionId": "test-session",
        "inputTranscript": "test input",
        "sessionState": {
            "sessionAttributes": session_attributes or {},
            "activeContexts": active_contexts or [],
            "intent": {
                "name": intent_name,
                "slots": slots or {},
                "state": "InProgress",
                "confirmationState": "None",
            },
        },
    }


def test_get_intent():
    """Test getting intent from request"""
    request_dict = create_test_request(intent_name="TestIntent")
    request = dialog.parse_lex_request(request_dict, TestSessionAttributes())
    intent = dialog.get_intent(request)
    assert isinstance(intent, Intent)
    assert intent.name == "TestIntent"


def test_get_slot():
    """Test getting slot value"""
    slots = {"test_slot": {"value": {"originalValue": "test_value"}}}
    request_dict = create_test_request(slots=slots)
    request = dialog.parse_lex_request(request_dict, TestSessionAttributes())
    slot_value = dialog.get_slot("test_slot", dialog.get_intent(request))
    assert slot_value == "test_value"


def test_get_slot_missing():
    """Test getting missing slot"""
    request_dict = create_test_request()
    request = dialog.parse_lex_request(request_dict, TestSessionAttributes())
    slot_value = dialog.get_slot("nonexistent_slot", dialog.get_intent(request))
    assert slot_value is None


def test_set_slot():
    """Test setting slot value"""
    request_dict = create_test_request()
    request = dialog.parse_lex_request(request_dict, TestSessionAttributes())
    intent = dialog.get_intent(request)
    dialog.set_slot(TestSlot.NEW_SLOT, "new_value", intent)
    assert dialog.get_slot(TestSlot.NEW_SLOT, intent) == "new_value"


def test_get_active_contexts():
    """Test getting active contexts"""
    active_contexts = [
        {
            "name": "test_context",
            "contextAttributes": {"key": "value"},
            "timeToLive": {"timeToLiveInSeconds": 600, "turnsToLive": 1},
        }
    ]
    request_dict = create_test_request(active_contexts=active_contexts)
    request = dialog.parse_lex_request(request_dict, TestSessionAttributes())
    contexts = dialog.get_active_contexts(request)
    assert contexts is not None
    assert len(contexts) == 1
    assert contexts[0]["name"] == "test_context"


def test_remove_context():
    """Test removing context"""
    active_contexts = [
        {
            "name": "test_context",
            "contextAttributes": {},
            "timeToLive": {"timeToLiveInSeconds": 600, "turnsToLive": 1},
        }
    ]
    request_dict = create_test_request(active_contexts=active_contexts)
    request = dialog.parse_lex_request(request_dict, TestSessionAttributes())
    contexts = dialog.remove_context(request.sessionState.activeContexts, "test_context")
    assert contexts is not None
    assert len(contexts) == 0


def test_close():
    """Test closing dialog"""
    request_dict = create_test_request()
    request = dialog.parse_lex_request(request_dict, TestSessionAttributes())
    response = dialog.close(request, [LexPlainText(content="Test message")])
    assert isinstance(response.messages[0], LexPlainText)
    assert response.messages[0].content == "Test message"
    assert response.sessionState.intent.state == "Fulfilled"


def test_delegate():
    """Test delegating dialog"""
    request_dict = create_test_request()
    request = dialog.parse_lex_request(request_dict, TestSessionAttributes())
    response = dialog.delegate(request)
    assert response.sessionState.dialogAction is not None
    assert response.sessionState.dialogAction.type == "Delegate"


def test_elicit_intent():
    """Test eliciting intent"""
    request_dict = create_test_request()
    request = dialog.parse_lex_request(request_dict, TestSessionAttributes())
    response = dialog.elicit_intent([LexPlainText(content="What would you like to do?")], request)
    assert isinstance(response.messages[0], LexPlainText)
    assert response.messages[0].content == "What would you like to do?"
    assert response.sessionState.dialogAction is not None
    assert response.sessionState.dialogAction.type == "ElicitIntent"


def test_elicit_slot():
    """Test eliciting slot"""
    request_dict = create_test_request()
    request = dialog.parse_lex_request(request_dict, TestSessionAttributes())
    response = dialog.elicit_slot("test_slot", [LexPlainText(content="What is the value?")], request)
    assert isinstance(response.messages[0], LexPlainText)
    assert response.messages[0].content == "What is the value?"
    assert response.sessionState.dialogAction is not None
    assert response.sessionState.dialogAction.type == "ElicitSlot"
    assert response.sessionState.dialogAction.slotToElicit == "test_slot"


def test_get_slot_value():
    """Test getting slot value with preferences"""
    slot = {
        "value": {
            "originalValue": "original",
            "interpretedValue": "interpreted",
            "resolvedValues": ["resolved1", "resolved2"],
        }
    }
    assert dialog.get_slot_value(slot) == "interpreted"  # Default preference
    assert dialog.get_slot_value(slot, preference="originalValue") == "original"
    assert dialog.get_slot_value(slot, preference="interpretedValue") == "interpreted"



def test_parse_lex_request():
    """Test parsing Lex request"""
    request_dict = create_test_request(
        intent_name="TestIntent",
        session_attributes={"test_value": "custom"},
    )
    request = dialog.parse_lex_request(request_dict, TestSessionAttributes())
    assert request.sessionState.intent.name == "TestIntent"
    assert request.sessionState.sessionAttributes.test_value == "custom"


def test_transition_to_intent(monkeypatch):
    """Test transition_to_intent prepends messages correctly"""
    # Create test request
    request_dict = create_test_request(intent_name="SourceIntent")
    request = dialog.parse_lex_request(request_dict, TestSessionAttributes())
    
    # Create input messages
    input_messages = [LexPlainText(content="Input message 1"), LexPlainText(content="Input message 2")]
    
    # Create mock response from call_handler_for_file
    handler_messages = [LexPlainText(content="Handler message")]
    handler_response = dialog.LexResponse(
        sessionState=request.sessionState,
        messages=handler_messages,
        requestAttributes={}
    )
    
    # Mock call_handler_for_file to return our mock response
    def mock_call_handler_for_file(intent_name, lex_request, **kwargs):
        assert intent_name == "TargetIntent"
        return handler_response
    
    monkeypatch.setattr(dialog, "call_handler_for_file", mock_call_handler_for_file)
    
    # Call transition_to_intent
    response = dialog.transition_to_intent(
        intent_name="TargetIntent",
        lex_request=request,
        messages=input_messages
    )
    
    # Verify the messages are combined correctly
    assert len(response.messages) == 3
    assert response.messages[0].content == "Input message 1"
    assert response.messages[1].content == "Input message 2"
    assert response.messages[2].content == "Handler message"
