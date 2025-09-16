# Quick Start

Get up and running with lex-helper in under 10 minutes with a working chatbot example. This guide will walk you through creating a simple greeting bot that demonstrates the core concepts of lex-helper.

## What You'll Build

By the end of this guide, you'll have:

- ✅ A working chatbot that handles greetings
- ✅ Type-safe session attribute management
- ✅ Proper intent handling structure
- ✅ A foundation for building more complex bots

**Estimated time:** 5-10 minutes

## Prerequisites

- ✅ Completed [installation guide](installation.md)
- ✅ AWS credentials configured
- ✅ Basic understanding of Python and AWS Lambda

## Step 1: Create Session Attributes

First, define your session attributes using Pydantic models for type safety:

```python
# session_attributes.py
from pydantic import ConfigDict, Field
from lex_helper import SessionAttributes

class MySessionAttributes(SessionAttributes):
    """Custom session attributes for our greeting bot."""

    model_config = ConfigDict(extra="allow")

    user_name: str = Field(
        default="",
        description="The user's name"
    )
    greeting_count: int = Field(
        default=0,
        description="Number of times user has been greeted"
    )
    last_intent: str = Field(
        default="",
        description="The last intent that was triggered"
    )
```

!!! info "API Reference"
    Learn more about [`SessionAttributes`](../api/core.md#type-definitions) in the API documentation.

!!! tip "Why Pydantic?"
    Using Pydantic models gives you:
    - **Type safety** - catch errors before runtime
    - **IDE autocomplete** - better development experience
    - **Validation** - automatic data validation
    - **Documentation** - self-documenting code

## Step 2: Create the Main Handler

Create your Lambda handler that will route requests to the appropriate intent handlers:

```python
# handler.py
from typing import Any
from lex_helper import Config, LexHelper
from session_attributes import MySessionAttributes

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Main Lambda handler for the greeting bot.

    This function:
    1. Configures lex-helper with custom session attributes
    2. Sets the package name for intent discovery
    3. Delegates request handling to the appropriate intent
    """

    # Configure lex-helper
    config = Config(
        session_attributes=MySessionAttributes(),
        package_name="intents"  # Where to find intent handlers
    )

    # Initialize lex-helper
    lex_helper = LexHelper(config=config)

    # Handle the request - lex-helper will automatically
    # route to the correct intent handler
    return lex_helper.handler(event, context)
```

!!! info "API Reference"
    - [`Config`](../api/core.md#lex_helper.core.handler.Config) - Configuration options for lex-helper
    - [`LexHelper`](../api/core.md#lex_helper.core.handler.LexHelper) - Main handler class
    - [`LexHelper.handler`](../api/core.md#lex_helper.core.handler.LexHelper.handler) - Primary entry point method

## Step 3: Create Intent Handlers

Create the `intents` directory and add your first intent handler:

```bash
mkdir intents
touch intents/__init__.py
```

Now create a greeting intent handler:

```python
# intents/greeting_intent.py
from lex_helper import LexRequest, LexResponse, LexPlainText, dialog
from session_attributes import MySessionAttributes

def handler(lex_request: LexRequest[MySessionAttributes]) -> LexResponse[MySessionAttributes]:
    """
    Handle greeting intents like "Hello", "Hi", "Good morning".

    This handler:
    1. Increments the greeting counter
    2. Personalizes the response if we know the user's name
    3. Returns a friendly greeting
    """

    # Access session attributes with full type safety
    session_attrs = lex_request.sessionState.sessionAttributes

    # Increment greeting count
    session_attrs.greeting_count += 1
    session_attrs.last_intent = "GreetingIntent"

    # Create personalized response
    if session_attrs.user_name:
        message = f"Hello again, {session_attrs.user_name}! This is greeting #{session_attrs.greeting_count}."
    else:
        message = f"Hello! Nice to meet you. This is greeting #{session_attrs.greeting_count}. What's your name?"

    # Return response using dialog utilities
    return dialog.close(
        messages=[LexPlainText(content=message)],
        lex_request=lex_request,
        fulfillment_state="Fulfilled"
    )
```

!!! info "API Reference"
    - [`LexRequest`](../api/core.md#type-definitions) - Typed request object
    - [`LexResponse`](../api/core.md#type-definitions) - Typed response object
    - [`LexPlainText`](../api/core.md#type-definitions) - Plain text message type
    - [`dialog.close`](../api/core.md#lex_helper.core.dialog.close) - Close dialog with fulfillment

Let's add another intent to capture the user's name:

```python
# intents/capture_name_intent.py
from lex_helper import LexRequest, LexResponse, LexPlainText, dialog
from session_attributes import MySessionAttributes

def handler(lex_request: LexRequest[MySessionAttributes]) -> LexResponse[MySessionAttributes]:
    """
    Handle intents that capture the user's name.

    This handler:
    1. Extracts the name from the 'Name' slot
    2. Stores it in session attributes
    3. Provides a personalized response
    """

    # Get the name from the slot
    name_slot = dialog.get_slot("Name", lex_request.sessionState.intent)

    if not name_slot or not name_slot.value:
        # If no name provided, ask for it
        return dialog.elicit_slot(
            slot_to_elicit="Name",
            messages=[LexPlainText(content="I'd love to know your name! What should I call you?")],
            lex_request=lex_request
        )

    # Store the name in session attributes
    session_attrs = lex_request.sessionState.sessionAttributes
    session_attrs.user_name = name_slot.value.interpretedValue
    session_attrs.last_intent = "CaptureNameIntent"

    # Respond with personalized greeting
    message = f"Nice to meet you, {session_attrs.user_name}! I'll remember your name for our conversation."

    return dialog.close(
        messages=[LexPlainText(content=message)],
        lex_request=lex_request,
        fulfillment_state="Fulfilled"
    )
```

## Step 4: Test Your Handler Locally

Create a simple test to verify your handler works:

```python
# test_handler.py
import json
from handler import lambda_handler

# Sample Lex event (simplified)
sample_event = {
    "sessionState": {
        "intent": {
            "name": "GreetingIntent",
            "state": "ReadyForFulfillment"
        },
        "sessionAttributes": {}
    },
    "inputTranscript": "Hello"
}

# Test the handler
response = lambda_handler(sample_event, None)
print("Response:", json.dumps(response, indent=2))
```

Run the test:
```bash
python test_handler.py
```

You should see a response with a greeting message!

## Step 5: Project Structure

Your final project structure should look like this:

```
my-greeting-bot/
├── intents/
│   ├── __init__.py
│   ├── greeting_intent.py
│   └── capture_name_intent.py
├── handler.py
├── session_attributes.py
└── test_handler.py
```

## Key Concepts Demonstrated

This quick start introduced several important lex-helper concepts:

### 1. **Type-Safe Session Attributes**
```python
# Instead of this (error-prone):
user_name = event['sessionState']['sessionAttributes'].get('userName', '')

# You write this (type-safe):
user_name = session_attrs.user_name
```

### 2. **Automatic Intent Routing**
- lex-helper automatically finds and calls the right intent handler
- No need for complex if/elif chains
- Each intent lives in its own file for better organization

### 3. **Dialog Utilities**
```python
# Easy dialog management
dialog.close(messages=[...], lex_request=lex_request)
dialog.elicit_slot(slot_to_elicit="Name", messages=[...], lex_request=lex_request)
```

### 4. **Clean Response Building**
```python
# Simple, readable response creation
LexPlainText(content="Hello, world!")
```

## What's Next?

Congratulations! You've built your first lex-helper chatbot. Here's what to explore next:

### Immediate Next Steps
1. **[Your First Chatbot](first-chatbot.md)** - Build a more comprehensive bot with multiple intents
2. **[Core Concepts](../guides/core-concepts.md)** - Understand lex-helper's architecture in depth

### Advanced Features to Explore
- **[Smart Disambiguation](../guides/smart-disambiguation.md)** - Handle ambiguous user input
- **[Bedrock Integration](../guides/bedrock-integration.md)** - Add AI-powered responses
- **[Channel Formatting](../guides/channel-formatting.md)** - Support multiple channels (SMS, web, voice)
- **[Message Management](../guides/message-management.md)** - Internationalization and localization

### Real-World Examples
- **[Basic Chatbot Tutorial](../tutorials/basic-chatbot.md)** - Step-by-step comprehensive tutorial
- **[Airline Bot Example](../tutorials/airline-bot.md)** - Production-ready patterns
- **[Code Examples](../examples/index.md)** - Common patterns and use cases

## Troubleshooting

### Common Issues

**Issue: "Module not found" error**
```bash
# Make sure you're in the right directory and virtual environment is activated
pwd
which python
pip list | grep lex-helper
```

**Issue: Intent handler not found**
```python
# Check that your intent name matches the file name
# GreetingIntent -> greeting_intent.py
# CaptureNameIntent -> capture_name_intent.py
```

**Issue: Session attributes not persisting**
```python
# Make sure you're modifying the session attributes object
session_attrs = lex_request.sessionState.sessionAttributes
session_attrs.user_name = "John"  # ✅ Correct

# Not creating a new object
session_attrs = MySessionAttributes(user_name="John")  # ❌ Wrong
```

### Getting Help

- **[Troubleshooting Guide](../advanced/troubleshooting.md)** - Common issues and solutions
- **[Community Support](../community/support.md)** - Get help from the community
- **[GitHub Issues](https://github.com/aws/lex-helper/issues)** - Report bugs or request features

---

*Ready for a more comprehensive tutorial? Continue to [Your First Chatbot](first-chatbot.md) →*
