# Basic Chatbot Tutorial

Build a complete chatbot from scratch using lex-helper, progressing from simple responses to advanced features like session management, error handling, and testing.

## What You'll Build

By the end of this tutorial, you'll have created a **Travel Assistant Bot** with:

- Multiple intent handlers (greeting, booking, help)
- Type-safe session attributes for user context
- Robust error handling and validation
- Channel-aware responses
- Comprehensive test suite
- Proper project organization

**Estimated time:** 45-60 minutes

## Prerequisites

- Completed [installation guide](../getting-started/installation.md) and [quick start](../getting-started/quick-start.md)
- Basic understanding of Python and AWS Lambda
- Familiarity with [core concepts](../guides/core-concepts.md)

## Step 1: Project Setup

Let's create a well-organized project structure for our travel assistant bot.

### 1.1 Create Project Structure

```bash
mkdir travel-assistant-bot
cd travel-assistant-bot

# Create the main package structure
mkdir -p src/travel_bot/{intents,utils,tests}
touch src/travel_bot/__init__.py
touch src/travel_bot/intents/__init__.py
touch src/travel_bot/utils/__init__.py
touch src/travel_bot/tests/__init__.py

# Create configuration files
touch requirements.txt
touch lambda_function.py
```

### 1.2 Install Dependencies

Create `requirements.txt`:

```txt
lex-helper>=0.0.2
pydantic>=2.0.0
pytest>=7.0.0
pytest-mock>=3.10.0
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 1.3 Create Session Attributes

Create `src/travel_bot/session_attributes.py`:

```python
from pydantic import Field
from lex_helper import SessionAttributes


class TravelBotSessionAttributes(SessionAttributes):
    """
    Session attributes for the Travel Assistant Bot.

    These attributes persist across conversation turns and help
    maintain context about the user's travel preferences and booking state.
    """

    # User preferences
    preferred_destination: str = Field(
        default="",
        description="User's preferred travel destination"
    )
    travel_dates: str = Field(
        default="",
        description="Preferred travel dates"
    )
    budget_range: str = Field(
        default="",
        description="User's budget range for travel"
    )

    # Conversation state
    greeting_count: int = Field(
        default=0,
        description="Number of times user has been greeted"
    )
    booking_step: str = Field(
        default="",
        description="Current step in the booking process"
    )

    # Error handling
    consecutive_errors: int = Field(
        default=0,
        description="Count of consecutive errors for recovery"
    )
```

## Step 2: Create Your First Intent Handler

Let's start with a simple greeting intent that demonstrates basic lex-helper patterns.

### 2.1 Greeting Intent

Create `src/travel_bot/intents/greeting.py`:

```python
from lex_helper import LexPlainText, LexRequest, LexResponse, dialog
from ..session_attributes import TravelBotSessionAttributes


def handler(lex_request: LexRequest[TravelBotSessionAttributes]) -> LexResponse[TravelBotSessionAttributes]:
    """
    Handle greeting intents with personalized responses.

    This handler demonstrates:
    - Accessing session attributes
    - Modifying session state
    - Returning different responses based on context
    """

    # Access session attributes
    session_attrs = lex_request.sessionState.sessionAttributes

    # Increment greeting count
    session_attrs.greeting_count += 1

    # Personalize response based on greeting count
    if session_attrs.greeting_count == 1:
        message = "Hello! Welcome to Travel Assistant. I can help you plan your next adventure. What would you like to do today?"
    elif session_attrs.greeting_count <= 3:
        message = f"Hello again! This is visit #{session_attrs.greeting_count}. How can I assist with your travel plans?"
    else:
        message = "You're becoming a regular! How can I help you with your travel needs today?"

    return dialog.close(
        messages=[LexPlainText(content=message)],
        lex_request=lex_request,
    )
```

### 2.2 Help Intent

Create `src/travel_bot/intents/help.py`:

```python
from lex_helper import LexPlainText, LexRequest, LexResponse, dialog
from ..session_attributes import TravelBotSessionAttributes


def handler(lex_request: LexRequest[TravelBotSessionAttributes]) -> LexResponse[TravelBotSessionAttributes]:
    """
    Provide help information about bot capabilities.
    """

    help_message = """
I'm your Travel Assistant! Here's what I can help you with:

🌍 **Travel Planning**: Get destination recommendations
✈️ **Flight Booking**: Help you find and book flights
🏨 **Hotel Booking**: Find accommodations for your trip
💰 **Budget Planning**: Get cost estimates for your travel

Just tell me what you'd like to do, like:
- "I want to plan a trip to Paris"
- "Help me book a flight"
- "Find hotels in Tokyo"

What would you like to start with?
    """.strip()

    return dialog.close(
        messages=[LexPlainText(content=help_message)],
        lex_request=lex_request,
    )
```

## Step 3: Advanced Intent with Slot Handling

Now let's create a more complex intent that demonstrates slot elicitation and validation.

### 3.1 Travel Planning Intent

Create `src/travel_bot/intents/plan_travel.py`:

```python
from typing import Optional
from lex_helper import Intent, LexPlainText, LexRequest, LexResponse, dialog
from ..session_attributes import TravelBotSessionAttributes


def get_slot_value(slot_name: str, intent: Intent) -> Optional[str]:
    """Helper function to safely get slot values."""
    if intent.slots and slot_name in intent.slots:
        slot = intent.slots[slot_name]
        return slot.value if slot else None
    return None


def validate_destination(destination: str) -> tuple[bool, str]:
    """
    Validate destination input.

    Returns:
        tuple: (is_valid, message)
    """
    if not destination:
        return False, "Please tell me where you'd like to travel."

    # Simple validation - in real implementation, you might check against a database
    invalid_destinations = ["nowhere", "hell", "prison"]
    if destination.lower() in invalid_destinations:
        return False, f"I can't help you travel to {destination}. Please choose a real destination!"

    return True, ""


def validate_travel_dates(dates: str) -> tuple[bool, str]:
    """
    Validate travel dates input.

    Returns:
        tuple: (is_valid, message)
    """
    if not dates:
        return False, "When would you like to travel? Please provide your preferred dates."

    # Basic validation - in production, you'd parse and validate actual dates
    if len(dates) < 3:
        return False, "Please provide more specific travel dates, like 'next month' or 'December 15th'."

    return True, ""


def handler(lex_request: LexRequest[TravelBotSessionAttributes]) -> LexResponse[TravelBotSessionAttributes]:
    """
    Handle travel planning with progressive slot collection and validation.

    This demonstrates:
    - Slot elicitation patterns
    - Input validation
    - Session attribute updates
    - Multi-turn conversation flow
    """

    intent = lex_request.sessionState.intent
    session_attrs = lex_request.sessionState.sessionAttributes

    # Get slot values
    destination = get_slot_value("Destination", intent)
    travel_dates = get_slot_value("TravelDates", intent)
    budget = get_slot_value("Budget", intent)

    # Step 1: Collect destination
    if not destination:
        return dialog.elicit_slot(
            slot_to_elicit="Destination",
            messages=[LexPlainText(content="Where would you like to travel? I can help you plan a trip anywhere in the world!")],
            lex_request=lex_request,
        )

    # Validate destination
    is_valid, error_message = validate_destination(destination)
    if not is_valid:
        return dialog.elicit_slot(
            slot_to_elicit="Destination",
            messages=[LexPlainText(content=error_message)],
            lex_request=lex_request,
        )

    # Step 2: Collect travel dates
    if not travel_dates:
        session_attrs.preferred_destination = destination
        return dialog.elicit_slot(
            slot_to_elicit="TravelDates",
            messages=[LexPlainText(content=f"Great choice! {destination} is wonderful. When are you planning to travel?")],
            lex_request=lex_request,
        )

    # Validate travel dates
    is_valid, error_message = validate_travel_dates(travel_dates)
    if not is_valid:
        return dialog.elicit_slot(
            slot_to_elicit="TravelDates",
            messages=[LexPlainText(content=error_message)],
            lex_request=lex_request,
        )

    # Step 3: Collect budget (optional)
    if not budget:
        session_attrs.travel_dates = travel_dates
        return dialog.elicit_slot(
            slot_to_elicit="Budget",
            messages=[LexPlainText(content="What's your budget range for this trip? (e.g., '$1000-2000' or 'budget-friendly')")],
            lex_request=lex_request,
        )

    # All information collected - provide travel plan
    session_attrs.budget_range = budget
    session_attrs.booking_step = "planning_complete"

    travel_plan = f"""
Perfect! Here's your travel plan summary:

🌍 **Destination**: {destination}
📅 **Travel Dates**: {travel_dates}
💰 **Budget**: {budget}

Based on your preferences, here are my recommendations:

✈️ **Flights**: I recommend booking 2-3 months in advance for the best prices
🏨 **Accommodation**: Consider staying in the city center for easy access to attractions
🎯 **Activities**: I can suggest popular attractions and local experiences

Would you like me to help you with the next step, like finding flights or hotels?
    """.strip()

    return dialog.close(
        messages=[LexPlainText(content=travel_plan)],
        lex_request=lex_request,
    )
```

## Step 4: Error Handling and Recovery

Let's add robust error handling to make our bot more resilient.

### 4.1 Create Error Handling Utilities

Create `src/travel_bot/utils/error_handling.py`:

```python
from lex_helper import LexPlainText, LexRequest, LexResponse, dialog
from ..session_attributes import TravelBotSessionAttributes


def handle_error_with_recovery(
    lex_request: LexRequest[TravelBotSessionAttributes],
    error_message: str,
    max_errors: int = 3
) -> LexResponse[TravelBotSessionAttributes]:
    """
    Handle errors with progressive recovery strategies.

    Args:
        lex_request: The current Lex request
        error_message: The error message to display
        max_errors: Maximum consecutive errors before escalation

    Returns:
        LexResponse with appropriate recovery action
    """

    session_attrs = lex_request.sessionState.sessionAttributes
    session_attrs.consecutive_errors += 1

    if session_attrs.consecutive_errors >= max_errors:
        # Escalate to human or reset conversation
        escalation_message = """
I'm having trouble understanding. Let me transfer you to a human agent, or you can:

- Type "help" to see what I can do
- Type "start over" to begin fresh
- Try rephrasing your request

How would you like to proceed?
        """.strip()

        # Reset error count after escalation
        session_attrs.consecutive_errors = 0

        return dialog.close(
            messages=[LexPlainText(content=escalation_message)],
            lex_request=lex_request,
        )

    # Progressive error messages
    if session_attrs.consecutive_errors == 1:
        recovery_message = f"{error_message} Could you please try rephrasing that?"
    elif session_attrs.consecutive_errors == 2:
        recovery_message = f"{error_message} Let me try to help differently. What specifically would you like to do?"
    else:
        recovery_message = f"{error_message} I'm still having trouble. Type 'help' to see what I can assist with."

    return dialog.close(
        messages=[LexPlainText(content=recovery_message)],
        lex_request=lex_request,
    )


def reset_error_count(session_attrs: TravelBotSessionAttributes) -> None:
    """Reset error count when user provides valid input."""
    session_attrs.consecutive_errors = 0
```

### 4.2 Fallback Intent with Error Recovery

Create `src/travel_bot/intents/fallback_intent.py`:

```python
from lex_helper import LexRequest, LexResponse
from ..session_attributes import TravelBotSessionAttributes
from ..utils.error_handling import handle_error_with_recovery


def handler(lex_request: LexRequest[TravelBotSessionAttributes]) -> LexResponse[TravelBotSessionAttributes]:
    """
    Handle unrecognized user input with helpful recovery.

    This demonstrates:
    - Graceful error handling
    - Progressive error recovery
    - User guidance and assistance
    """

    error_message = """
I didn't quite understand that. I'm a travel assistant and I can help you with:

• Planning trips and getting destination advice
• Finding flights and travel information
• Hotel recommendations
• Budget planning for your travels
    """.strip()

    return handle_error_with_recovery(
        lex_request=lex_request,
        error_message=error_message,
        max_errors=3
    )
```

## Step 5: Main Lambda Handler

Create the main `lambda_function.py`:

```python
from typing import Any
from lex_helper import Config, LexHelper
from src.travel_bot.session_attributes import TravelBotSessionAttributes


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Main Lambda handler for the Travel Assistant Bot.

    This demonstrates:
    - Proper lex-helper configuration
    - Custom session attributes
    - Automatic exception handling
    - Package-based intent routing
    """

    # Configure lex-helper with our custom session attributes
    config = Config(
        session_attributes=TravelBotSessionAttributes(),
        package_name="src.travel_bot",  # Points to our intent handlers
        auto_handle_exceptions=True,    # Automatically handle exceptions
        error_message="I encountered an error. Please try again or type 'help' for assistance."
    )

    # Initialize and run the handler
    lex_helper = LexHelper(config=config)
    return lex_helper.handler(event, context)
```

## Step 6: Testing Your Chatbot

Let's create comprehensive tests to ensure our bot works correctly.

### 6.1 Basic Unit Tests

Create `src/travel_bot/tests/test_greeting.py`:

```python
import pytest
from unittest.mock import Mock
from lex_helper import LexRequest, Intent, SessionState
from ..intents.greeting import handler
from ..session_attributes import TravelBotSessionAttributes


def create_mock_request(greeting_count: int = 0) -> LexRequest[TravelBotSessionAttributes]:
    """Helper to create mock Lex requests for testing."""

    session_attrs = TravelBotSessionAttributes(greeting_count=greeting_count)

    mock_request = Mock(spec=LexRequest)
    mock_request.sessionState = Mock(spec=SessionState)
    mock_request.sessionState.sessionAttributes = session_attrs
    mock_request.sessionState.intent = Mock(spec=Intent)

    return mock_request


def test_first_greeting():
    """Test first-time greeting response."""

    request = create_mock_request(greeting_count=0)
    response = handler(request)

    # Check that greeting count was incremented
    assert request.sessionState.sessionAttributes.greeting_count == 1

    # Check response contains welcome message
    assert "Welcome to Travel Assistant" in response.messages[0].content


def test_repeat_greeting():
    """Test repeat greeting response."""

    request = create_mock_request(greeting_count=2)
    response = handler(request)

    # Check that greeting count was incremented
    assert request.sessionState.sessionAttributes.greeting_count == 3

    # Check response acknowledges repeat visit
    assert "visit #3" in response.messages[0].content


def test_frequent_visitor():
    """Test frequent visitor greeting."""

    request = create_mock_request(greeting_count=5)
    response = handler(request)

    # Check response for frequent visitors
    assert "becoming a regular" in response.messages[0].content
```

### 6.2 Integration Tests

Create `src/travel_bot/tests/test_integration.py`:

```python
import pytest
from unittest.mock import Mock, patch
from lex_helper import Config, LexHelper
from ..session_attributes import TravelBotSessionAttributes


@pytest.fixture
def lex_helper():
    """Create a configured LexHelper for testing."""
    config = Config(
        session_attributes=TravelBotSessionAttributes(),
        package_name="src.travel_bot",
        auto_handle_exceptions=True
    )
    return LexHelper(config=config)


def create_lex_event(intent_name: str, slots: dict = None, session_attrs: dict = None):
    """Create a mock Lex event for testing."""
    return {
        "sessionState": {
            "intent": {
                "name": intent_name,
                "slots": slots or {},
                "state": "InProgress"
            },
            "sessionAttributes": session_attrs or {}
        },
        "inputTranscript": "test input",
        "bot": {
            "name": "TravelBot",
            "version": "1.0"
        }
    }


def test_greeting_flow(lex_helper):
    """Test complete greeting conversation flow."""

    # Create greeting event
    event = create_lex_event("greeting")
    context = Mock()

    # Process the event
    response = lex_helper.handler(event, context)

    # Verify response structure
    assert "sessionState" in response
    assert "messages" in response
    assert len(response["messages"]) > 0

    # Verify session attributes were updated
    session_attrs = response["sessionState"]["sessionAttributes"]
    assert session_attrs["greeting_count"] == "1"


def test_travel_planning_flow(lex_helper):
    """Test travel planning conversation flow."""

    # Start travel planning
    event = create_lex_event("plan_travel")
    context = Mock()

    response = lex_helper.handler(event, context)

    # Should ask for destination
    assert any("where would you like to travel" in msg["content"].lower()
              for msg in response["messages"])

    # Provide destination
    event = create_lex_event(
        "plan_travel",
        slots={"Destination": {"value": "Paris"}}
    )

    response = lex_helper.handler(event, context)

    # Should ask for travel dates
    assert any("when are you planning" in msg["content"].lower()
              for msg in response["messages"])


def test_error_handling(lex_helper):
    """Test error handling and recovery."""

    # Trigger fallback intent
    event = create_lex_event("FallbackIntent")
    context = Mock()

    response = lex_helper.handler(event, context)

    # Should provide helpful error message
    assert any("didn't quite understand" in msg["content"].lower()
              for msg in response["messages"])
```

### 6.3 Running Tests

Create a simple test runner script `run_tests.py`:

```python
import pytest
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([
        "src/travel_bot/tests/",
        "-v",
        "--tb=short",
        "--color=yes"
    ])
```

Run your tests:

```bash
python run_tests.py
```

## Step 7: Channel-Aware Responses

Let's add channel-specific formatting to make our bot work well across different platforms.

### 7.1 Enhanced Response Formatting

Create `src/travel_bot/utils/response_formatter.py`:

```python
from typing import List
from lex_helper import LexPlainText, LexRequest
from lex_helper.channels import format_for_channel


def create_channel_aware_response(
    content: str,
    lex_request: LexRequest,
    use_markdown: bool = True
) -> List[LexPlainText]:
    """
    Create responses optimized for different channels.

    Args:
        content: The message content
        lex_request: Current Lex request for channel detection
        use_markdown: Whether to use markdown formatting

    Returns:
        List of formatted messages
    """

    # Format content for the specific channel
    formatted_content = format_for_channel(
        content=content,
        lex_request=lex_request,
        use_markdown=use_markdown
    )

    return [LexPlainText(content=formatted_content)]


def create_travel_summary_response(
    destination: str,
    dates: str,
    budget: str,
    lex_request: LexRequest
) -> List[LexPlainText]:
    """Create a formatted travel summary response."""

    # Rich formatting for web/app channels
    rich_content = f"""
**🌍 Your Travel Plan**

**Destination:** {destination}
**Travel Dates:** {dates}
**Budget:** {budget}

**Next Steps:**
• ✈️ Find flights
• 🏨 Book accommodation
• 🎯 Plan activities

Would you like help with any of these?
    """.strip()

    # Simple formatting for SMS
    simple_content = f"""
Your Travel Plan:
Destination: {destination}
Dates: {dates}
Budget: {budget}

Next: flights, hotels, or activities?
    """.strip()

    # Choose format based on channel
    channel = getattr(lex_request, 'channel', 'web')
    content = simple_content if channel == 'sms' else rich_content

    return create_channel_aware_response(content, lex_request)
```

## Step 8: Deployment and Testing

### 8.1 Create Deployment Package

Create `deploy.py`:

```python
import zipfile
import os
from pathlib import Path


def create_deployment_package():
    """Create a deployment package for AWS Lambda."""

    # Create deployment zip
    with zipfile.ZipFile('travel-bot-deployment.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:

        # Add main handler
        zipf.write('lambda_function.py')

        # Add source code
        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    zipf.write(file_path)

        # Add requirements (you'd typically use a layer for this)
        # zipf.write('requirements.txt')

    print("✅ Deployment package created: travel-bot-deployment.zip")
    print("📦 Package size:", os.path.getsize('travel-bot-deployment.zip'), "bytes")


if __name__ == "__main__":
    create_deployment_package()
```

### 8.2 Local Testing Script

Create `test_locally.py`:

```python
import json
from lambda_function import lambda_handler


def test_greeting():
    """Test greeting intent locally."""

    event = {
        "sessionState": {
            "intent": {
                "name": "greeting",
                "slots": {},
                "state": "ReadyForFulfillment"
            },
            "sessionAttributes": {}
        },
        "inputTranscript": "hello",
        "bot": {
            "name": "TravelBot",
            "version": "1.0"
        }
    }

    response = lambda_handler(event, None)
    print("🤖 Bot Response:")
    print(json.dumps(response, indent=2))
    return response


def test_travel_planning():
    """Test travel planning intent locally."""

    event = {
        "sessionState": {
            "intent": {
                "name": "plan_travel",
                "slots": {},
                "state": "InProgress"
            },
            "sessionAttributes": {}
        },
        "inputTranscript": "I want to plan a trip",
        "bot": {
            "name": "TravelBot",
            "version": "1.0"
        }
    }

    response = lambda_handler(event, None)
    print("🤖 Bot Response:")
    print(json.dumps(response, indent=2))
    return response


if __name__ == "__main__":
    print("🧪 Testing Travel Assistant Bot locally...\n")

    print("=" * 50)
    print("TEST 1: Greeting Intent")
    print("=" * 50)
    test_greeting()

    print("\n" + "=" * 50)
    print("TEST 2: Travel Planning Intent")
    print("=" * 50)
    test_travel_planning()

    print("\n✅ Local testing complete!")
```

Run local tests:

```bash
python test_locally.py
```

## What You've Accomplished

Congratulations! You've built a comprehensive travel assistant chatbot that demonstrates:

### ✅ Core lex-helper Features
- **Intent routing** with automatic handler discovery
- **Type-safe session attributes** for maintaining conversation state
- **Slot elicitation** with validation and error handling
- **Progressive conversation flows** with multi-turn interactions

### ✅ Best Practices
- **Proper project organization** with clear separation of concerns
- **Comprehensive error handling** with recovery strategies
- **Input validation** and user guidance
- **Channel-aware responses** for different platforms

### ✅ Testing and Quality
- **Unit tests** for individual intent handlers
- **Integration tests** for complete conversation flows
- **Local testing tools** for development and debugging
- **Deployment packaging** for AWS Lambda

### ✅ Advanced Patterns
- **Session state management** for context preservation
- **Progressive error recovery** with escalation strategies
- **Flexible response formatting** for different channels
- **Modular code organization** for maintainability

## Next Steps

Now that you've mastered the basics, you're ready to explore more advanced topics:

1. **[Airline Bot Walkthrough](airline-bot.md)** - Learn advanced patterns from a real-world example
2. **[Multi-language Support](multi-language.md)** - Add internationalization to your bot
3. **[Production Deployment](production-deployment.md)** - Deploy your bot with best practices
4. **[Smart Disambiguation](../guides/smart-disambiguation.md)** - Handle ambiguous user input intelligently

## Troubleshooting

### Common Issues

**Import errors when testing locally:**
```bash
# Make sure your Python path includes the src directory
export PYTHONPATH="${PYTHONPATH}:./src"
```

**Session attributes not persisting:**
- Ensure you're returning the modified session attributes in your response
- Check that your session attribute class inherits from `SessionAttributes`

**Intent handlers not found:**
- Verify your package name in the Config matches your directory structure
- Ensure all `__init__.py` files are present
- Check that handler functions are named `handler`

**Slot elicitation not working:**
- Verify slot names match exactly between your Lex bot and your code
- Check that you're using `dialog.elicit_slot()` correctly
- Ensure your intent state is set to "InProgress"

---

*This tutorial is part of the comprehensive lex-helper documentation. Ready for more advanced patterns? Continue with the [Airline Bot Walkthrough →](airline-bot.md)*
