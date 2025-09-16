# Message Management

Master centralized message management, localization, and internationalization with lex-helper's powerful MessageManager system.

## Overview

The MessageManager provides a centralized, locale-aware system for managing chatbot messages. It supports multiple languages, message templates, dynamic content injection, and automatic fallback mechanisms, making it easy to build globally accessible chatbots.

## Key Features

- **Multi-language Support**: Automatic locale detection and message loading
- **YAML-based Configuration**: Easy-to-manage message files
- **Template System**: Dynamic content injection with variable substitution
- **Automatic Fallback**: Graceful degradation when messages are missing
- **Nested Message Keys**: Organized message hierarchies with dot notation
- **Environment Integration**: Flexible file location configuration

## Getting Started

### Basic Setup

```python
from lex_helper import MessageManager, get_message, set_locale

# Set the locale for your chatbot
set_locale("en_US")

# Get a simple message
greeting = get_message("greeting")
print(greeting)  # "Hello! How can I help you today?"
```

### Message File Structure

Create YAML files in your project directory:

**messages.yaml** (default/fallback):
```yaml
greeting: "Hello! How can I help you today?"
farewell: "Thank you for using our service!"

booking:
  confirmation: "Your booking has been confirmed!"
  cancellation: "Your booking has been cancelled."

error:
  general: "I'm sorry, something went wrong."
  validation: "Please provide valid information."
```

**messages_es_ES.yaml** (Spanish):
```yaml
greeting: "¡Hola! ¿Cómo puedo ayudarte hoy?"
farewell: "¡Gracias por usar nuestro servicio!"

booking:
  confirmation: "¡Tu reserva ha sido confirmada!"
  cancellation: "Tu reserva ha sido cancelada."

error:
  general: "Lo siento, algo salió mal."
  validation: "Por favor, proporciona información válida."
```

## Core Concepts

### Locale Management

The MessageManager automatically handles locale detection and switching:

```python
def lambda_handler(event, context):
    # Extract locale from Lex event
    locale = event.get("bot", {}).get("localeId", "en_US")
    set_locale(locale)

    # All subsequent message calls use this locale
    welcome_msg = get_message("greeting")
    return process_intent(event, welcome_msg)
```

### Nested Message Keys

Use dot notation to organize messages hierarchically:

```python
# Access nested messages
confirmation = get_message("booking.confirmation")
error_msg = get_message("error.validation")

# Deep nesting is supported
specific_error = get_message("error.booking.payment.declined")
```

### Default Values and Fallbacks

Provide fallback messages for robustness:

```python
# With default value
message = get_message("custom.message", "Default message if not found")

# Without default (returns error message)
message = get_message("missing.key")  # "Message not found: missing.key"
```

## Advanced Usage

### Dynamic Message Templates

While MessageManager doesn't include built-in templating, you can easily add it:

```python
def get_templated_message(key: str, **kwargs) -> str:
    """Get message with template variable substitution."""
    template = get_message(key)
    return template.format(**kwargs)

# Usage
welcome = get_templated_message("welcome.user", name="John", points=150)
# From template: "Welcome back, {name}! You have {points} points."
# Result: "Welcome back, John! You have 150 points."
```

### Message File Organization

**messages.yaml**:
```yaml
# User interactions
user:
  welcome: "Welcome, {name}!"
  goodbye: "Goodbye, {name}!"

# Booking flow
booking:
  start: "Let's start your booking process."
  flight_selection: "Please select your preferred flight:"
  confirmation: "Booking confirmed! Reference: {reference}"

# Error handling
error:
  booking:
    no_flights: "No flights available for your dates."
    payment_failed: "Payment processing failed. Please try again."
  system:
    timeout: "Request timed out. Please try again."
    maintenance: "System is under maintenance."
```

### Locale-Specific Customization

**messages_ja_JP.yaml** (Japanese):
```yaml
user:
  welcome: "いらっしゃいませ、{name}様！"
  goodbye: "ありがとうございました、{name}様！"

booking:
  start: "予約手続きを開始いたします。"
  flight_selection: "ご希望のフライトをお選びください："
  confirmation: "予約が確定いたしました！参照番号：{reference}"
```

## Integration Patterns

### With Intent Handlers

```python
from lex_helper import LexHelper, get_message

class BookingIntent:
    def __init__(self, lex_helper: LexHelper):
        self.lex_helper = lex_helper

    def handle_booking_start(self):
        message = get_message("booking.start")
        return self.lex_helper.elicit_slot(
            slot_to_elicit="departure_city",
            message=message
        )

    def handle_booking_confirmation(self, reference: str):
        message = get_templated_message(
            "booking.confirmation",
            reference=reference
        )
        return self.lex_helper.close(message)
```

### With Session Attributes

```python
from lex_helper.core.session_attributes import SessionAttributes

class MySessionAttributes(SessionAttributes):
    user_name: str = ""
    preferred_language: str = "en_US"

def handle_personalized_greeting(lex_helper):
    session = lex_helper.session_attributes

    # Set locale from user preference
    set_locale(session.preferred_language)

    # Get personalized message
    if session.user_name:
        message = get_templated_message(
            "user.welcome",
            name=session.user_name
        )
    else:
        message = get_message("user.welcome.anonymous")

    return lex_helper.close(message)
```

### Environment Configuration

Configure message file locations using environment variables:

```python
import os

# Set custom message directory
os.environ["MESSAGES_YAML_PATH"] = "/opt/lambda/messages"

# MessageManager will look for files in this directory first
set_locale("en_US")  # Loads from /opt/lambda/messages/messages_en_US.yaml
```

## File Location Strategy

MessageManager searches for message files in this order:

1. **Custom path** from `MESSAGES_YAML_PATH` environment variable
2. **Current working directory**
3. **Common subdirectories**: `messages/`, `config/`, `resources/`, `data/`
4. **Relative paths** from current directory

### Recommended Project Structure

```
your-lambda-function/
├── lambda_function.py
├── messages/
│   ├── messages.yaml           # Default English
│   ├── messages_es_ES.yaml     # Spanish (Spain)
│   ├── messages_fr_FR.yaml     # French (France)
│   ├── messages_ja_JP.yaml     # Japanese
│   └── messages_de_DE.yaml     # German
├── intents/
│   └── ...
└── requirements.txt
```

## Best Practices

### Message Key Naming

Use consistent, hierarchical naming conventions:

```yaml
# Good: Hierarchical and descriptive
user:
  greeting:
    first_time: "Welcome to our service!"
    returning: "Welcome back!"

booking:
  flight:
    search_prompt: "Where would you like to go?"
    no_results: "No flights found for your criteria."

# Avoid: Flat, unclear naming
msg1: "Some message"
error_thing: "Error occurred"
```

### Error Message Strategy

Provide helpful, actionable error messages:

```yaml
error:
  validation:
    email: "Please provide a valid email address (e.g., user@example.com)"
    phone: "Please provide a valid phone number (e.g., +1-555-123-4567)"
    date: "Please provide a date in MM/DD/YYYY format"

  booking:
    no_availability: "No flights available. Try different dates or destinations."
    payment_declined: "Payment was declined. Please check your card details or try a different payment method."
```

### Locale-Specific Considerations

Consider cultural differences in your messages:

```yaml
# US English - Direct and informal
greeting: "Hi! How can I help you?"
booking_success: "Great! Your flight is booked."

# Japanese - More formal and polite
greeting: "いらっしゃいませ。どのようなご用件でしょうか？"
booking_success: "ありがとうございます。フライトのご予約が完了いたしました。"

# German - Formal but efficient
greeting: "Guten Tag! Wie kann ich Ihnen helfen?"
booking_success: "Perfekt! Ihr Flug ist gebucht."
```

## Testing Message Management

### Unit Testing

```python
import pytest
from lex_helper import MessageManager, get_message, set_locale

class TestMessageManager:
    def setup_method(self):
        # Reset MessageManager state
        MessageManager._messages = {}
        MessageManager._current_locale = "en_US"

    def test_basic_message_retrieval(self):
        set_locale("en_US")
        message = get_message("greeting", "Default greeting")
        assert message is not None

    def test_locale_switching(self):
        # Test English
        set_locale("en_US")
        en_message = get_message("greeting")

        # Test Spanish
        set_locale("es_ES")
        es_message = get_message("greeting")

        assert en_message != es_message

    def test_nested_keys(self):
        message = get_message("booking.confirmation")
        assert "booking" not in message  # Should be the actual message, not the key

    def test_fallback_behavior(self):
        # Test with non-existent key
        message = get_message("nonexistent.key", "Fallback message")
        assert message == "Fallback message"
```

### Integration Testing

```python
def test_message_integration_with_lex():
    """Test MessageManager integration with LexHelper."""
    from lex_helper import LexHelper, Config
    from lex_helper.core.session_attributes import SessionAttributes

    # Mock Lex event with locale
    event = {
        "bot": {"localeId": "es_ES"},
        "sessionState": {"sessionAttributes": {}}
    }

    config = Config(
        session_attributes=SessionAttributes(),
        package_name="test.intents"
    )

    lex_helper = LexHelper(config=config)

    # Set locale from event
    locale = event["bot"]["localeId"]
    set_locale(locale)

    # Get localized message
    message = get_message("greeting")

    # Verify Spanish message is returned
    assert "Hola" in message or "¡" in message
```

## Troubleshooting

### Common Issues

#### Messages Not Loading

```python
# Problem: Message files not found
# Solution: Check file paths and naming

import logging
logging.basicConfig(level=logging.INFO)

# Enable MessageManager logging to see file search paths
set_locale("en_US")  # Check logs for file search attempts
```

#### Locale Not Switching

```python
# Problem: Locale changes not taking effect
# Solution: Ensure proper locale setting

# Wrong: Setting locale after getting messages
message = get_message("greeting")
set_locale("es_ES")  # Too late!

# Correct: Set locale first
set_locale("es_ES")
message = get_message("greeting")
```

#### Missing Nested Keys

```python
# Problem: Nested key not found
message = get_message("booking.flight.confirmation")

# Solution: Check YAML structure
# Ensure proper nesting:
# booking:
#   flight:
#     confirmation: "Your flight is confirmed!"
```

### Debugging Tips

```python
def debug_message_loading():
    """Debug message loading issues."""
    # Check all loaded messages
    all_messages = MessageManager.get_all_messages()
    print(f"Loaded locales: {list(all_messages.keys())}")

    for locale, messages in all_messages.items():
        print(f"\n{locale} messages:")
        for key, value in messages.items():
            print(f"  {key}: {value}")

    # Test specific key
    test_key = "booking.confirmation"
    message = get_message(test_key, "KEY_NOT_FOUND")
    print(f"\nTest key '{test_key}': {message}")
```

## Performance Considerations

### Message Caching

MessageManager automatically caches loaded messages:

```python
# First call loads from file
set_locale("en_US")  # Loads messages.yaml

# Subsequent calls use cached messages
message1 = get_message("greeting")  # From cache
message2 = get_message("farewell")  # From cache

# Force reload if needed
MessageManager.reload_messages()
```

### Memory Usage

For Lambda functions, consider message file size:

```yaml
# Good: Organized, reasonable size
# messages.yaml (5KB)
# messages_es_ES.yaml (5KB)

# Consider splitting large files:
# messages/
#   common.yaml          # Shared messages
#   booking.yaml         # Booking-specific
#   support.yaml         # Support messages
#   errors.yaml          # Error messages
```

## Migration from Hardcoded Messages

### Before: Hardcoded Messages

```python
def handle_booking_intent(lex_helper):
    if success:
        return lex_helper.close("Your booking has been confirmed!")
    else:
        return lex_helper.close("Sorry, booking failed. Please try again.")
```

### After: MessageManager

```python
def handle_booking_intent(lex_helper):
    if success:
        message = get_message("booking.confirmation")
        return lex_helper.close(message)
    else:
        message = get_message("booking.error")
        return lex_helper.close(message)
```

### Migration Strategy

1. **Extract existing messages** to YAML files
2. **Replace hardcoded strings** with `get_message()` calls
3. **Add locale support** by creating additional YAML files
4. **Test thoroughly** with different locales

## Related Topics

- [Channel Formatting](channel-formatting.md) - Learn how messages are formatted for different channels
- [Multi-language Tutorial](../tutorials/multi-language.md) - Step-by-step internationalization guide
- [Session Attributes](session-attributes.md) - Managing user state and preferences
- [Examples](../examples/index.md) - See message management in action

---

*This page is part of the comprehensive lex-helper documentation. [Learn about error handling →](error-handling.md)*
