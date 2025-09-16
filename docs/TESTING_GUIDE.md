# Testing Guide for Lex Helper Library

This guide covers comprehensive testing strategies for Lex bots built with the Lex Helper library. For basic setup and usage, see [Installation Guide](getting-started/installation.md) and [Best Practices](BEST_PRACTICES.md).

## Test Helper Functions

```python
import pytest
from lex_helper import dialog, LexPlainText, set_locale, get_message, MessageManager
from your_project.intents.booking_intent import handle_booking_intent
from your_project.session_attributes import CustomSessionAttributes

def create_test_request(intent_name="BookingIntent", slots=None, session_attrs=None):
    """Helper to create test requests"""
    return {
        "sessionId": "test-session",
        "inputTranscript": "test input",
        "sessionState": {
            "sessionAttributes": session_attrs or {},
            "activeContexts": [],
            "intent": {
                "name": intent_name,
                "slots": slots or {},
                "state": "InProgress",
                "confirmationState": "None",
            },
        },
    }
```

## Unit Testing Slot Elicitation

Test that your intent handlers properly elicit required slots:

def test_elicit_missing_slot():
    """Test that missing slots are properly elicited"""
    # Create request without required slot
    request_dict = create_test_request(slots={})
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    response = handle_booking_intent(lex_request)

    # Verify slot elicitation
    assert response.sessionState.dialogAction.type == "ElicitSlot"
    assert response.sessionState.dialogAction.slotToElicit == "destination"
    assert len(response.messages) > 0
    assert isinstance(response.messages[0], LexPlainText)

def test_slot_validation():
    """Test slot value validation"""
    # Create request with invalid slot value
    slots = {"email": {"value": {"originalValue": "invalid-email"}}}
    request_dict = create_test_request(slots=slots)
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    response = handle_booking_intent(lex_request)

    # Should re-elicit the slot
    assert response.sessionState.dialogAction.type == "ElicitSlot"
    assert response.sessionState.dialogAction.slotToElicit == "email"

def test_all_slots_filled():
    """Test behavior when all required slots are filled"""
    slots = {
        "destination": {"value": {"originalValue": "Paris"}},
        "date": {"value": {"originalValue": "2024-01-15"}},
        "email": {"value": {"originalValue": "user@example.com"}}
    }
    request_dict = create_test_request(slots=slots)
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    response = handle_booking_intent(lex_request)

    # Should delegate or close
    assert response.sessionState.dialogAction.type in ["Delegate", "Close"]
```

### Testing Dialog Flow Transitions

Validate multi-turn conversations and intent transitions:

```python
def test_intent_transition():
    """Test transitioning between intents"""
    request_dict = create_test_request()
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    # Simulate transition to authentication
    response = dialog.transition_to_intent(
        intent_name="authenticate",
        lex_request=lex_request,
        messages=[LexPlainText(content="Please authenticate")]
    )

    assert response.sessionState.intent.name == "authenticate"
    assert len(response.messages) > 0
    assert response.messages[0].content == "Please authenticate"

def test_callback_pattern():
    """Test callback pattern for returning to original intent"""
    # Set up callback
    request_dict = create_test_request()
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    lex_request.sessionState.sessionAttributes.callback_handler = "BookingIntent"
    lex_request.sessionState.sessionAttributes.callback_event = json.dumps(lex_request, default=str)

    # Test callback handler
    response = dialog.callback_original_intent_handler(lex_request)

    assert response is not None
    # Verify session attributes were merged properly
```

### Testing Unknown Choice Handling

Validate error handling for invalid user inputs:

```python
def test_unknown_slot_choice_detection():
    """Test detection of unknown slot choices"""
    # Set up previous elicit slot state
    session_attrs = {
        "previous_dialog_action_type": "ElicitSlot",
        "previous_slot_to_elicit": "BookingIntentSlot.DESTINATION"
    }
    request_dict = create_test_request(
        slots={},  # No slot filled (unknown choice)
        session_attrs=session_attrs
    )
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    # Should detect unknown choice
    assert dialog.any_unknown_slot_choices(lex_request) == True

def test_valid_slot_choice():
    """Test that valid choices are not flagged as unknown"""
    session_attrs = {
        "previous_dialog_action_type": "ElicitSlot",
        "previous_slot_to_elicit": "BookingIntentSlot.DESTINATION"
    }
    slots = {"destination": {"value": {"originalValue": "Paris"}}}
    request_dict = create_test_request(slots=slots, session_attrs=session_attrs)
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    # Should not detect unknown choice
    assert dialog.any_unknown_slot_choices(lex_request) == False

def test_error_count_increment():
    """Test that error count increments on unknown choices"""
    session_attrs = {
        "previous_dialog_action_type": "ElicitSlot",
        "previous_slot_to_elicit": "BookingIntentSlot.DESTINATION",
        "error_count": 1
    }
    request_dict = create_test_request(slots={}, session_attrs=session_attrs)
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    dialog.any_unknown_slot_choices(lex_request)

    # Error count should increment
    assert lex_request.sessionState.sessionAttributes.error_count == 2
```

### Integration Testing

Test complete dialog flows end-to-end:

```python
def test_complete_booking_flow():
    """Test complete booking conversation flow"""
    # Step 1: Initial request
    request_dict = create_test_request()
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    response1 = handle_booking_intent(lex_request)
    assert response1.sessionState.dialogAction.type == "ElicitSlot"

    # Step 2: Provide destination
    slots = {"destination": {"value": {"originalValue": "Paris"}}}
    request_dict = create_test_request(slots=slots)
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    response2 = handle_booking_intent(lex_request)
    # Should elicit next slot (date)
    assert response2.sessionState.dialogAction.slotToElicit == "date"

    # Step 3: Complete all slots
    slots = {
        "destination": {"value": {"originalValue": "Paris"}},
        "date": {"value": {"originalValue": "2024-01-15"}},
        "email": {"value": {"originalValue": "user@example.com"}}
    }
    request_dict = create_test_request(slots=slots)
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    response3 = handle_booking_intent(lex_request)
    assert response3.sessionState.dialogAction.type in ["Delegate", "Close"]
```

### Testing Session Attributes

Validate session state management:

```python
def test_session_attribute_persistence():
    """Test that session attributes persist across turns"""
    session_attrs = {"user_name": "John", "visit_count": 1}
    request_dict = create_test_request(session_attrs=session_attrs)
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    # Modify session attributes
    lex_request.sessionState.sessionAttributes.visit_count += 1

    response = handle_booking_intent(lex_request)

    # Verify attributes are maintained
    assert response.sessionState.sessionAttributes.user_name == "John"
    assert response.sessionState.sessionAttributes.visit_count == 2

def test_session_attribute_merging():
    """Test session attribute merging in callback scenarios"""
    # Create original request with callback data
    original_attrs = {"user_name": "John", "booking_id": "123"}
    callback_event = json.dumps(create_test_request(session_attrs=original_attrs), default=str)

    # Create current request with additional attributes
    current_attrs = {
        "callback_event": callback_event,
        "callback_handler": "BookingIntent",
        "auth_token": "abc123"
    }
    request_dict = create_test_request(session_attrs=current_attrs)
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    response = dialog.callback_original_intent_handler(lex_request)

    # Both original and current attributes should be present
    assert hasattr(response.sessionState.sessionAttributes, 'user_name')
    assert hasattr(response.sessionState.sessionAttributes, 'auth_token')
```

### Testing Message Handling

Validate message creation and formatting:

```python
def test_message_loading():
    """Test loading messages from JSON"""
    messages_json = '''[
        {"contentType": "PlainText", "content": "Hello!"},
        {"contentType": "ImageResponseCard", "imageResponseCard": {"title": "Test"}}
    ]'''

    messages = dialog.load_messages(messages_json)

    assert len(messages) == 2
    assert isinstance(messages[0], LexPlainText)
    assert messages[0].content == "Hello!"

def test_message_prepending():
    """Test that messages are properly prepended in transitions"""
    request_dict = create_test_request()
    lex_request = dialog.parse_lex_request(request_dict, CustomSessionAttributes())

    input_messages = [LexPlainText(content="Transition message")]

    # Mock the handler to return a response with messages
    def mock_handler(intent_name, lex_request):
        return dialog.LexResponse(
            sessionState=lex_request.sessionState,
            messages=[LexPlainText(content="Handler message")],
            requestAttributes={}
        )

    # Test message prepending
    response = dialog.transition_to_intent(
        intent_name="test_intent",
        lex_request=lex_request,
        messages=input_messages
    )

    # Input messages should come first
    assert len(response.messages) >= 1
    assert response.messages[0].content == "Transition message"
```

### Testing Message Management

Test localized messages and MessageManager functionality:

```python
def test_message_loading():
    """Test loading messages for different locales"""
    # Test English messages
    set_locale("en_US")
    greeting = get_message("greeting")
    assert "Hello" in greeting

    # Test Spanish messages
    set_locale("es_ES")
    spanish_greeting = get_message("greeting")
    assert "Hola" in spanish_greeting

    # Test fallback to default
    fallback_message = get_message("nonexistent.key", "Default message")
    assert fallback_message == "Default message"

def test_locale_override():
    """Test locale override in get_message"""
    set_locale("en_US")

    # Get message in current locale
    english_msg = get_message("greeting")

    # Override locale for specific message
    spanish_msg = get_message("greeting", locale="es_ES")

    assert english_msg != spanish_msg
    assert "Hello" in english_msg
    assert "Hola" in spanish_msg

def test_message_manager_singleton():
    """Test MessageManager singleton behavior"""
    manager1 = MessageManager()
    manager2 = MessageManager()

    assert manager1 is manager2

    # Test that locale changes affect all instances
    manager1.set_locale("fr_FR")
    french_msg = manager2.get_message("greeting")
    assert "Bonjour" in french_msg or "greeting" in french_msg  # fallback

def test_nested_message_keys():
    """Test nested message key access"""
    set_locale("en_US")

    # Test nested key access
    agent_confirmation = get_message("agent.confirmation")
    error_general = get_message("error.general")

    assert agent_confirmation != "Message not found: agent.confirmation"
    assert error_general != "Message not found: error.general"
```

### Running Tests

Use pytest to run your tests:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_dialog_flows.py

# Run with coverage
pytest --cov=your_project tests/

# Run tests with verbose output
pytest -v tests/
```

### Test Organization

Structure your tests to match your intent organization:

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_dialog_flows.py     # Dialog flow tests
├── test_slot_validation.py  # Slot validation tests
├── test_session_management.py # Session attribute tests
└── intents/
    ├── test_booking_intent.py
    ├── test_welcome_intent.py
    └── test_fallback_intent.py
```

### Best Practices for Testing

1. **Use fixtures** for common test data and setup
2. **Test edge cases** like empty inputs, invalid data, and error conditions
3. **Mock external dependencies** to isolate your bot logic
4. **Test across channels** by simulating different request attributes
5. **Validate error handling** and fallback behaviors
6. **Test session state** persistence and transitions
7. **Use descriptive test names** that explain the scenario being tested

This comprehensive testing approach ensures your Lex bot handles all dialog scenarios correctly and provides a reliable user experience.
