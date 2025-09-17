# Your First Chatbot

Build your first complete chatbot using lex-helper with detailed explanations of each component. This comprehensive tutorial will teach you best practices for structuring, testing, and deploying a production-ready chatbot.

## What You'll Build

By the end of this tutorial, you'll have created a **Personal Assistant Bot** that can:

- ✅ Handle multiple intents (greetings, weather, reminders, help)
- ✅ Manage complex session state and user preferences
- ✅ Provide error handling and fallback responses
- ✅ Support different response channels (SMS, web, voice)
- ✅ Include comprehensive testing
- ✅ Follow production-ready patterns

**Estimated time:** 30-45 minutes

## Learning Objectives

By completing this tutorial, you'll understand:

- **Project Structure** - How to organize a lex-helper project for maintainability
- **Intent Patterns** - Common patterns for handling different types of intents
- **Session Management** - Advanced session attribute usage and persistence
- **Error Handling** - Graceful error handling and user experience
- **Testing Strategies** - How to test your chatbot logic
- **Channel Awareness** - Adapting responses for different channels

## Prerequisites

- ✅ Completed [Quick Start Guide](quick-start.md)
- ✅ Basic understanding of Amazon Lex concepts (intents, slots, fulfillment)
- ✅ Familiarity with Python classes and type hints

## Project Setup

### 1. Create Project Structure

Let's create a well-organized project structure:

```bash
mkdir personal-assistant-bot
cd personal-assistant-bot

# Create directory structure
mkdir intents utils tests
touch handler.py session_attributes.py
touch intents/__init__.py utils/__init__.py tests/__init__.py

# Create configuration files
touch requirements.txt .env
```

Your structure should look like:
```
personal-assistant-bot/
├── intents/
│   └── __init__.py
├── utils/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── handler.py
├── session_attributes.py
├── requirements.txt
└── .env
```

### 2. Define Requirements

```text
# requirements.txt
lex-helper>=0.1.0
boto3>=1.26.0
python-dotenv>=1.0.0
pytest>=7.0.0
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Step 1: Advanced Session Attributes

Create comprehensive session attributes that demonstrate real-world usage:

```python
# session_attributes.py
from datetime import datetime
from typing import List, Optional
from pydantic import ConfigDict, Field
from lex_helper import SessionAttributes

class UserPreferences(SessionAttributes):
    """User preferences sub-model."""

    preferred_name: str = Field(default="", description="User's preferred name")
    timezone: str = Field(default="UTC", description="User's timezone")
    notification_enabled: bool = Field(default=True, description="Whether notifications are enabled")

class PersonalAssistantSessionAttributes(SessionAttributes):
    """
    Comprehensive session attributes for a personal assistant bot.

    This demonstrates advanced session management patterns including:
    - Nested models for organization
    - Different data types (strings, integers, booleans, lists, dates)
    - Default values and validation
    - Clear documentation
    """

    model_config = ConfigDict(extra="allow")

    # User Information
    user_preferences: UserPreferences = Field(
        default_factory=UserPreferences,
        description="User's personal preferences"
    )

    # Conversation State
    current_flow: str = Field(
        default="",
        description="Current conversation flow (e.g., 'weather_inquiry', 'reminder_setup')"
    )

    last_intent: str = Field(
        default="",
        description="The last successfully handled intent"
    )

    conversation_count: int = Field(
        default=0,
        description="Number of interactions in this session"
    )

    # Context and Memory
    mentioned_topics: List[str] = Field(
        default_factory=list,
        description="Topics mentioned in this conversation"
    )

    pending_reminders: List[str] = Field(
        default_factory=list,
        description="Reminders waiting to be set"
    )

    # Error Handling
    consecutive_errors: int = Field(
        default=0,
        description="Number of consecutive errors for fallback logic"
    )

    last_error_intent: str = Field(
        default="",
        description="Intent that last caused an error"
    )

    # Timestamps
    session_start_time: Optional[str] = Field(
        default=None,
        description="When this session started (ISO format)"
    )

    last_activity_time: Optional[str] = Field(
        default=None,
        description="Last activity timestamp (ISO format)"
    )

    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity_time = datetime.utcnow().isoformat()
        if not self.session_start_time:
            self.session_start_time = self.last_activity_time

    def add_topic(self, topic: str) -> None:
        """Add a topic to the mentioned topics list."""
        if topic and topic not in self.mentioned_topics:
            self.mentioned_topics.append(topic)

    def reset_error_count(self) -> None:
        """Reset the consecutive error count."""
        self.consecutive_errors = 0
        self.last_error_intent = ""

    def increment_error_count(self, intent_name: str) -> None:
        """Increment the error count for an intent."""
        self.consecutive_errors += 1
        self.last_error_intent = intent_name
```

## Step 2: Utility Functions

Create utility functions to support your intents:

```python
# utils/helpers.py
from typing import Optional
from datetime import datetime
import re

def extract_name_from_input(user_input: str) -> Optional[str]:
    """
    Extract a name from user input using common patterns.

    Examples:
    - "My name is John" -> "John"
    - "I'm Sarah" -> "Sarah"
    - "Call me Mike" -> "Mike"
    """
    patterns = [
        r"my name is (\w+)",
        r"i'm (\w+)",
        r"call me (\w+)",
        r"i am (\w+)",
    ]

    user_input_lower = user_input.lower()

    for pattern in patterns:
        match = re.search(pattern, user_input_lower)
        if match:
            return match.group(1).title()

    return None

def format_time_greeting() -> str:
    """Return a time-appropriate greeting."""
    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 22:
        return "Good evening"
    else:
        return "Good night"

def is_business_hours() -> bool:
    """Check if it's currently business hours (9 AM - 5 PM)."""
    hour = datetime.now().hour
    return 9 <= hour < 17

def format_list_response(items: list, conjunction: str = "and") -> str:
    """
    Format a list into a natural language string.

    Examples:
    - ["apple"] -> "apple"
    - ["apple", "banana"] -> "apple and banana"
    - ["apple", "banana", "cherry"] -> "apple, banana, and cherry"
    """
    if not items:
        return ""
    elif len(items) == 1:
        return str(items[0])
    elif len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    else:
        return f"{', '.join(items[:-1])}, {conjunction} {items[-1]}"
```

## Step 3: Intent Handlers

Now let's create comprehensive intent handlers that demonstrate different patterns:

### Welcome Intent

```python
# intents/welcome_intent.py
from lex_helper import LexRequest, LexResponse, LexPlainText, dialog
from session_attributes import PersonalAssistantSessionAttributes
from utils.helpers import format_time_greeting, extract_name_from_input

def handler(lex_request: LexRequest[PersonalAssistantSessionAttributes]) -> LexResponse[PersonalAssistantSessionAttributes]:
    """
    Handle welcome/greeting intents.

    This intent demonstrates:
    - Session state initialization
    - Personalized responses based on session history
    - Context-aware greetings
    """

    session_attrs = lex_request.sessionState.sessionAttributes
    session_attrs.update_activity()
    session_attrs.conversation_count += 1
    session_attrs.current_flow = "greeting"
    session_attrs.last_intent = "WelcomeIntent"
    session_attrs.add_topic("greeting")

    # Try to extract name from user input
    user_input = lex_request.inputTranscript or ""
    extracted_name = extract_name_from_input(user_input)
    if extracted_name and not session_attrs.user_preferences.preferred_name:
        session_attrs.user_preferences.preferred_name = extracted_name

    # Create personalized greeting
    time_greeting = format_time_greeting()

    if session_attrs.user_preferences.preferred_name:
        if session_attrs.conversation_count == 1:
            message = f"{time_greeting}, {session_attrs.user_preferences.preferred_name}! Welcome back to your personal assistant."
        else:
            message = f"Hello again, {session_attrs.user_preferences.preferred_name}!"
    else:
        message = f"{time_greeting}! I'm your personal assistant. What's your name?"

    # Add helpful context
    if session_attrs.conversation_count == 1:
        message += " I can help you with weather, reminders, and general questions. What would you like to do?"

    return dialog.close(
        messages=[LexPlainText(content=message)],
        lex_request=lex_request,
        fulfillment_state="Fulfilled"
    )
```

### Weather Intent

```python
# intents/weather_intent.py
from lex_helper import LexRequest, LexResponse, LexPlainText, dialog
from session_attributes import PersonalAssistantSessionAttributes

def handler(lex_request: LexRequest[PersonalAssistantSessionAttributes]) -> LexResponse[PersonalAssistantSessionAttributes]:
    """
    Handle weather inquiry intents.

    This intent demonstrates:
    - Slot validation and elicitation
    - Multi-turn conversations
    - Error handling for missing information
    """

    session_attrs = lex_request.sessionState.sessionAttributes
    session_attrs.update_activity()
    session_attrs.current_flow = "weather_inquiry"
    session_attrs.last_intent = "WeatherIntent"
    session_attrs.add_topic("weather")

    # Get the city slot
    city_slot = dialog.get_slot("City", lex_request.sessionState.intent)

    if not city_slot or not city_slot.value:
        # Elicit the city if not provided
        return dialog.elicit_slot(
            slot_to_elicit="City",
            messages=[LexPlainText(content="Which city would you like to know the weather for?")],
            lex_request=lex_request
        )

    city = city_slot.value.interpretedValue

    # In a real implementation, you would call a weather API here
    # For this tutorial, we'll simulate a response
    weather_response = f"The weather in {city} is currently sunny with a temperature of 72°F. Perfect day to go outside!"

    # Add personalized touch
    if session_attrs.user_preferences.preferred_name:
        weather_response = f"Here you go, {session_attrs.user_preferences.preferred_name}! " + weather_response

    return dialog.close(
        messages=[LexPlainText(content=weather_response)],
        lex_request=lex_request,
        fulfillment_state="Fulfilled"
    )
```

### Reminder Intent

```python
# intents/reminder_intent.py
from lex_helper import LexRequest, LexResponse, LexPlainText, dialog
from session_attributes import PersonalAssistantSessionAttributes

def handler(lex_request: LexRequest[PersonalAssistantSessionAttributes]) -> LexResponse[PersonalAssistantSessionAttributes]:
    """
    Handle reminder creation intents.

    This intent demonstrates:
    - Complex slot management
    - Session state persistence
    - Multi-step workflows
    """

    session_attrs = lex_request.sessionState.sessionAttributes
    session_attrs.update_activity()
    session_attrs.current_flow = "reminder_setup"
    session_attrs.last_intent = "ReminderIntent"
    session_attrs.add_topic("reminders")

    # Get required slots
    reminder_text_slot = dialog.get_slot("ReminderText", lex_request.sessionState.intent)
    reminder_time_slot = dialog.get_slot("ReminderTime", lex_request.sessionState.intent)

    # Elicit reminder text if missing
    if not reminder_text_slot or not reminder_text_slot.value:
        return dialog.elicit_slot(
            slot_to_elicit="ReminderText",
            messages=[LexPlainText(content="What would you like me to remind you about?")],
            lex_request=lex_request
        )

    # Elicit reminder time if missing
    if not reminder_time_slot or not reminder_time_slot.value:
        return dialog.elicit_slot(
            slot_to_elicit="ReminderTime",
            messages=[LexPlainText(content="When would you like to be reminded?")],
            lex_request=lex_request
        )

    reminder_text = reminder_text_slot.value.interpretedValue
    reminder_time = reminder_time_slot.value.interpretedValue

    # Store the reminder (in a real app, you'd save to a database)
    reminder = f"{reminder_text} at {reminder_time}"
    session_attrs.pending_reminders.append(reminder)

    # Create confirmation message
    message = f"Perfect! I've set a reminder for '{reminder_text}' at {reminder_time}."

    if session_attrs.user_preferences.preferred_name:
        message += f" I'll make sure to remind you, {session_attrs.user_preferences.preferred_name}!"

    return dialog.close(
        messages=[LexPlainText(content=message)],
        lex_request=lex_request,
        fulfillment_state="Fulfilled"
    )
```

### Help Intent

```python
# intents/help_intent.py
from lex_helper import LexRequest, LexResponse, LexPlainText, dialog
from session_attributes import PersonalAssistantSessionAttributes
from utils.helpers import format_list_response

def handler(lex_request: LexRequest[PersonalAssistantSessionAttributes]) -> LexResponse[PersonalAssistantSessionAttributes]:
    """
    Handle help requests.

    This intent demonstrates:
    - Context-aware help based on conversation history
    - Dynamic response generation
    - User guidance and onboarding
    """

    session_attrs = lex_request.sessionState.sessionAttributes
    session_attrs.update_activity()
    session_attrs.current_flow = "help"
    session_attrs.last_intent = "HelpIntent"
    session_attrs.add_topic("help")

    # Base capabilities
    capabilities = [
        "check the weather for any city",
        "set reminders for you",
        "have conversations and answer questions",
        "remember your preferences"
    ]

    # Create personalized help message
    if session_attrs.user_preferences.preferred_name:
        greeting = f"Hi {session_attrs.user_preferences.preferred_name}! "
    else:
        greeting = "Hi there! "

    message = greeting + f"I can help you {format_list_response(capabilities)}."

    # Add context-specific help
    if session_attrs.mentioned_topics:
        message += f"\n\nWe've talked about {format_list_response(session_attrs.mentioned_topics)} so far."

    if session_attrs.pending_reminders:
        reminder_count = len(session_attrs.pending_reminders)
        message += f"\n\nYou have {reminder_count} pending reminder{'s' if reminder_count != 1 else ''}."

    message += "\n\nWhat would you like to do?"

    return dialog.close(
        messages=[LexPlainText(content=message)],
        lex_request=lex_request,
        fulfillment_state="Fulfilled"
    )
```

### Fallback Intent

```python
# intents/fallback_intent.py
from lex_helper import LexRequest, LexResponse, LexPlainText, dialog
from session_attributes import PersonalAssistantSessionAttributes

def handler(lex_request: LexRequest[PersonalAssistantSessionAttributes]) -> LexResponse[PersonalAssistantSessionAttributes]:
    """
    Handle fallback when no intent matches or errors occur.

    This intent demonstrates:
    - Error tracking and recovery
    - Escalating help based on error frequency
    - Graceful degradation of user experience
    """

    session_attrs = lex_request.sessionState.sessionAttributes
    session_attrs.update_activity()
    session_attrs.increment_error_count("FallbackIntent")
    session_attrs.current_flow = "fallback"
    session_attrs.last_intent = "FallbackIntent"

    # Escalate help based on consecutive errors
    if session_attrs.consecutive_errors == 1:
        message = "I'm not sure I understood that. Could you try rephrasing your request?"

    elif session_attrs.consecutive_errors == 2:
        message = "I'm still having trouble understanding. I can help with weather, reminders, or general questions. What would you like to do?"

    elif session_attrs.consecutive_errors >= 3:
        message = "I apologize for the confusion. Let me help you get back on track. Here's what I can do:\n\n"
        message += "• Say 'weather in [city]' to get weather information\n"
        message += "• Say 'remind me to [task] at [time]' to set reminders\n"
        message += "• Say 'help' for more options\n\n"
        message += "What would you like to try?"

        # Reset error count after providing comprehensive help
        session_attrs.reset_error_count()

    else:
        message = "I didn't catch that. Could you please try again?"

    return dialog.close(
        messages=[LexPlainText(content=message)],
        lex_request=lex_request,
        fulfillment_state="Failed"
    )
```

## Step 4: Enhanced Main Handler

Create a robust main handler with error handling:

```python
# handler.py
import logging
from typing import Any
from lex_helper import Config, LexHelper
from session_attributes import PersonalAssistantSessionAttributes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Enhanced Lambda handler with comprehensive error handling and logging.

    This handler demonstrates:
    - Proper logging for debugging and monitoring
    - Error handling and recovery
    - Configuration management
    - Performance considerations
    """

    try:
        # Log the incoming request (be careful with sensitive data in production)
        logger.info(f"Processing request for intent: {event.get('sessionState', {}).get('intent', {}).get('name', 'Unknown')}")

        # Configure lex-helper
        config = Config(
            session_attributes=PersonalAssistantSessionAttributes(),
            package_name="intents"
        )

        # Initialize lex-helper
        lex_helper = LexHelper(config=config)

        # Process the request
        response = lex_helper.handler(event, context)

        # Log successful processing
        logger.info("Request processed successfully")

        return response

    except Exception as e:
        # Log the error
        logger.error(f"Error processing request: {str(e)}", exc_info=True)

        # Return a graceful error response
        return {
            "sessionState": {
                "dialogAction": {
                    "type": "Close"
                },
                "intent": {
                    "name": event.get('sessionState', {}).get('intent', {}).get('name', 'Unknown'),
                    "state": "Failed"
                }
            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
                }
            ]
        }
```

## Step 5: Testing Your Chatbot

Create comprehensive tests to ensure your chatbot works correctly:

```python
# tests/test_intents.py
import pytest
from unittest.mock import Mock
from lex_helper import LexRequest
from session_attributes import PersonalAssistantSessionAttributes

# Import your intent handlers
from intents.welcome_intent import handler as welcome_handler
from intents.weather_intent import handler as weather_handler
from intents.help_intent import handler as help_handler

class TestWelcomeIntent:
    """Test the welcome intent handler."""

    def test_first_time_user(self):
        """Test welcome for a new user."""
        # Create mock request
        session_attrs = PersonalAssistantSessionAttributes()
        lex_request = Mock(spec=LexRequest)
        lex_request.sessionState.sessionAttributes = session_attrs
        lex_request.inputTranscript = "Hello"

        # Call handler
        response = welcome_handler(lex_request)

        # Verify response
        assert response.sessionState.dialogAction.type == "Close"
        assert "Good" in response.messages[0].content  # Should include time-based greeting
        assert session_attrs.conversation_count == 1
        assert session_attrs.last_intent == "WelcomeIntent"

    def test_returning_user_with_name(self):
        """Test welcome for a returning user with a known name."""
        # Create mock request with existing session
        session_attrs = PersonalAssistantSessionAttributes()
        session_attrs.user_preferences.preferred_name = "Alice"
        session_attrs.conversation_count = 0  # Will be incremented to 1

        lex_request = Mock(spec=LexRequest)
        lex_request.sessionState.sessionAttributes = session_attrs
        lex_request.inputTranscript = "Hi there"

        # Call handler
        response = welcome_handler(lex_request)

        # Verify personalized response
        assert "Alice" in response.messages[0].content
        assert session_attrs.conversation_count == 1

class TestWeatherIntent:
    """Test the weather intent handler."""

    def test_weather_with_city(self):
        """Test weather request with city provided."""
        # Create mock request with city slot
        session_attrs = PersonalAssistantSessionAttributes()
        lex_request = Mock(spec=LexRequest)
        lex_request.sessionState.sessionAttributes = session_attrs
        lex_request.sessionState.intent = Mock()

        # Mock the city slot
        city_slot = Mock()
        city_slot.value.interpretedValue = "Seattle"

        # Mock dialog.get_slot to return our city
        import intents.weather_intent
        original_get_slot = intents.weather_intent.dialog.get_slot
        intents.weather_intent.dialog.get_slot = Mock(return_value=city_slot)

        try:
            # Call handler
            response = weather_handler(lex_request)

            # Verify response
            assert response.sessionState.dialogAction.type == "Close"
            assert "Seattle" in response.messages[0].content
            assert session_attrs.current_flow == "weather_inquiry"

        finally:
            # Restore original function
            intents.weather_intent.dialog.get_slot = original_get_slot

    def test_weather_without_city(self):
        """Test weather request without city - should elicit slot."""
        # Create mock request without city slot
        session_attrs = PersonalAssistantSessionAttributes()
        lex_request = Mock(spec=LexRequest)
        lex_request.sessionState.sessionAttributes = session_attrs
        lex_request.sessionState.intent = Mock()

        # Mock dialog.get_slot to return None (no city provided)
        import intents.weather_intent
        original_get_slot = intents.weather_intent.dialog.get_slot
        intents.weather_intent.dialog.get_slot = Mock(return_value=None)

        try:
            # Call handler
            response = weather_handler(lex_request)

            # Verify it elicits the city slot
            assert response.sessionState.dialogAction.type == "ElicitSlot"
            assert response.sessionState.dialogAction.slotToElicit == "City"

        finally:
            # Restore original function
            intents.weather_intent.dialog.get_slot = original_get_slot

class TestHelpIntent:
    """Test the help intent handler."""

    def test_help_with_conversation_history(self):
        """Test help with existing conversation context."""
        # Create session with history
        session_attrs = PersonalAssistantSessionAttributes()
        session_attrs.user_preferences.preferred_name = "Bob"
        session_attrs.mentioned_topics = ["weather", "reminders"]
        session_attrs.pending_reminders = ["Buy groceries at 5 PM"]

        lex_request = Mock(spec=LexRequest)
        lex_request.sessionState.sessionAttributes = session_attrs
        lex_request.inputTranscript = "help"

        # Call handler
        response = help_handler(lex_request)

        # Verify contextual help
        assert "Bob" in response.messages[0].content
        assert "weather" in response.messages[0].content
        assert "1 pending reminder" in response.messages[0].content

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

Run your tests:
```bash
python -m pytest tests/ -v
```

## Step 6: Local Testing Script

Create a script to test your bot locally:

```python
# test_bot_locally.py
import json
from handler import lambda_handler

def create_test_event(intent_name: str, input_text: str, slots: dict = None) -> dict:
    """Create a test Lex event."""
    event = {
        "sessionState": {
            "intent": {
                "name": intent_name,
                "state": "ReadyForFulfillment",
                "slots": slots or {}
            },
            "sessionAttributes": {}
        },
        "inputTranscript": input_text,
        "bot": {
            "name": "PersonalAssistantBot",
            "version": "1.0"
        }
    }
    return event

def test_conversation_flow():
    """Test a complete conversation flow."""
    print("🤖 Testing Personal Assistant Bot\n")

    # Test 1: Welcome
    print("Test 1: Welcome Intent")
    event = create_test_event("WelcomeIntent", "Hello")
    response = lambda_handler(event, None)
    print(f"Bot: {response['messages'][0]['content']}\n")

    # Test 2: Weather (without city)
    print("Test 2: Weather Intent (no city)")
    event = create_test_event("WeatherIntent", "What's the weather?")
    response = lambda_handler(event, None)
    print(f"Bot: {response['messages'][0]['content']}\n")

    # Test 3: Weather (with city)
    print("Test 3: Weather Intent (with city)")
    event = create_test_event("WeatherIntent", "Weather in New York", {
        "City": {
            "value": {
                "interpretedValue": "New York"
            }
        }
    })
    response = lambda_handler(event, None)
    print(f"Bot: {response['messages'][0]['content']}\n")

    # Test 4: Help
    print("Test 4: Help Intent")
    event = create_test_event("HelpIntent", "help")
    response = lambda_handler(event, None)
    print(f"Bot: {response['messages'][0]['content']}\n")

    # Test 5: Fallback
    print("Test 5: Fallback Intent")
    event = create_test_event("FallbackIntent", "asdfghjkl")
    response = lambda_handler(event, None)
    print(f"Bot: {response['messages'][0]['content']}\n")

if __name__ == "__main__":
    test_conversation_flow()
```

Run the local test:
```bash
python test_bot_locally.py
```

## Key Concepts Explained

### 1. **Session State Management**

```python
# Session attributes persist across the conversation
session_attrs.user_preferences.preferred_name = "Alice"
session_attrs.conversation_count += 1
session_attrs.add_topic("weather")
```

### 2. **Intent Organization**

Each intent handler follows a consistent pattern:
- Update session state
- Validate and process slots
- Generate appropriate response
- Handle errors gracefully

### 3. **Error Handling Strategy**

```python
# Track consecutive errors for escalating help
session_attrs.increment_error_count("FallbackIntent")

# Provide increasingly helpful responses
if session_attrs.consecutive_errors >= 3:
    # Provide comprehensive help and reset counter
    pass  # Implementation details
```

### 4. **Type Safety Benefits**

```python
# Type-safe access to session attributes
user_name: str = session_attrs.user_preferences.preferred_name
count: int = session_attrs.conversation_count

# IDE autocomplete and error detection
# session_attrs.user_preferences.  # <- IDE shows available fields
```

## Production Considerations

### 1. **Environment Configuration**

```python
# .env file for local development
AWS_REGION=us-east-1
LOG_LEVEL=INFO
WEATHER_API_KEY=your_api_key_here
```

### 2. **Logging and Monitoring**

```python
import logging
logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Processing {intent_name} for user {user_id}")
logger.error(f"Error in {intent_name}: {str(e)}")
```

### 3. **Security Best Practices**

- Never log sensitive user data
- Use IAM roles instead of hardcoded credentials
- Validate all user inputs
- Implement rate limiting

### 4. **Performance Optimization**

- Keep Lambda functions warm
- Minimize cold start time
- Use connection pooling for databases
- Cache frequently accessed data

## Next Steps

Congratulations! You've built a comprehensive chatbot with lex-helper. Here's what to explore next:

### Immediate Enhancements
1. **[Message Management](../guides/message-management.md)** - Add internationalization
2. **[Channel Formatting](../guides/channel-formatting.md)** - Optimize for different channels
3. **[Smart Disambiguation](../guides/smart-disambiguation.md)** - Handle ambiguous input

### Advanced Features
1. **[Bedrock Integration](../guides/bedrock-integration.md)** - Add AI-powered responses
2. **[Testing Strategies](../advanced/testing.md)** - Comprehensive testing approaches
3. **[Production Deployment](../tutorials/production-deployment.md)** - Deploy to AWS

### Real-World Examples
1. **[Airline Bot Tutorial](../tutorials/airline-bot.md)** - Complex multi-turn conversations
2. **[Advanced Patterns](../examples/advanced-patterns.md)** - Production-ready patterns
3. **[AWS Integrations](../examples/integration-examples.md)** - Connect with other AWS services

## Troubleshooting

### Common Issues

**Issue: Intent handler not found**
```bash
# Check file naming convention
# Intent name: "WeatherIntent" -> File: "weather_intent.py"
```

**Issue: Session attributes not persisting**
```python
# Ensure you're modifying the existing object, not creating new ones
session_attrs = lex_request.sessionState.sessionAttributes  # ✅
session_attrs.user_name = "Alice"  # ✅

# Don't create new instances
session_attrs = PersonalAssistantSessionAttributes()  # ❌
```

**Issue: Slots not being elicited properly**
```python
# Make sure slot names match exactly between Lex console and code
dialog.elicit_slot(
    slot_to_elicit="City",  # Must match Lex console exactly
    messages=[LexPlainText(content="Which city?")],
    lex_request=lex_request
)
```

### Getting Help

- **[Advanced Troubleshooting](../advanced/troubleshooting.md)** - Detailed debugging guide
- **[Troubleshooting Guide](../advanced/troubleshooting.md)** - Get help with common issues
- **[GitHub Issues](https://github.com/aws/lex-helper/issues)** - Report bugs or request features

---

*Ready to explore advanced features? Check out the [Core Concepts Guide](../guides/core-concepts.md) →*
