# Channel Formatting

Learn how lex-helper automatically formats chatbot responses for different communication channels without requiring any changes to your intent handlers.

## Overview

Different communication channels have unique constraints and capabilities. SMS has character limits and no rich media support, while web chat supports images and interactive buttons. The lex-helper library provides **completely automatic** channel-aware formatting that happens transparently - your intent handlers remain clean and channel-neutral.

## Key Design Philosophy

**🎯 Core Principle: Intent handlers should be channel-neutral**

- Write your intent handlers once, they work everywhere
- No conditional channel logic in your business code
- All channel-specific formatting happens automatically in the framework
- Clean separation between business logic and presentation

## How It Works

### Automatic Channel Detection and Formatting

The lex-helper framework automatically:

1. **Detects the channel** from the incoming Lex event
2. **Applies appropriate formatting** using channel-specific formatters
3. **Returns the optimized response** without any code changes needed

```python
def handle_booking_confirmation(lex_helper):
    # Write your handler once - works for ALL channels
    card = LexImageResponseCard(
        imageResponseCard=ImageResponseCard(
            title="Booking Confirmed!",
            subtitle="Flight AA123 - NYC to LAX",
            imageUrl="https://example.com/confirmation.jpg",
            buttons=[
                Button(text="View Details", value="view_details"),
                Button(text="Modify", value="modify"),
                Button(text="Cancel", value="cancel")
            ]
        )
    )

    # This SAME code produces:
    # - Rich card with image and buttons on Lex web interface
    # - Text-only format on SMS: "Booking Confirmed! | Flight AA123 - NYC to LAX | Options: View Details, Modify, Cancel"
    return lex_helper.close(card)
```

### Supported Channels

- **Lex**: Default Lex console and web interfaces (rich formatting)
- **SMS**: Text messaging with automatic simplification
- **Custom**: Extensible framework for additional channels

## Channel-Specific Behavior

### SMS Channel Formatting

The SMS channel automatically handles these transformations:

#### URL Auto-Enhancement
```python
# Your handler code (channel-neutral):
message = LexPlainText(content="Check status at booking.example.com/status")

# SMS output automatically adds https://
# Result: "Check status at https://booking.example.com/status"
```

#### Image Card Simplification
```python
# Your handler code (channel-neutral):
card = LexImageResponseCard(
    imageResponseCard=ImageResponseCard(
        title="Flight Options",
        subtitle="Choose your preferred flight",
        imageUrl="https://example.com/image.jpg",
        buttons=[
            Button(text="Morning Flight", value="morning"),
            Button(text="Evening Flight", value="evening")
        ]
    )
)

# SMS output (automatic):
# "Flight Options | Choose your preferred flight | https://example.com/image.jpg | Options: Morning Flight, Evening Flight"
```

#### Custom Payload Handling
```python
# Your handler code (channel-neutral):
payload = LexCustomPayload(content={
    "type": "carousel",
    "text": "Choose an option",
    "items": [...]
})

# SMS output extracts text or shows fallback:
# "Choose an option" or "Message received"
```

### Lex Channel Formatting

The Lex channel preserves rich formatting:

#### Rich Media Support
- Images display properly
- Buttons are interactive with proper value handling
- Custom payloads are preserved
- Multiple message types supported

#### Special Lex Handling
The framework automatically handles Lex-specific requirements:
- Adds PlainText message before ImageResponseCard (Lex requirement)
- Preserves button values for proper intent routing
- Maintains session attributes properly

## Best Practices

### Write Channel-Neutral Handlers

✅ **Good: Channel-neutral code**
```python
def handle_flight_status(lex_helper):
    # Single implementation works everywhere
    status_card = LexImageResponseCard(
        imageResponseCard=ImageResponseCard(
            title=f"Flight {flight_number}",
            subtitle=f"Status: {status}",
            imageUrl=flight_image_url,
            buttons=[
                Button(text="Get Updates", value="updates"),
                Button(text="Change Flight", value="change")
            ]
        )
    )
    return lex_helper.close(status_card)
```

❌ **Bad: Channel-specific logic in handlers**
```python
def handle_flight_status(lex_helper):
    # DON'T DO THIS - violates the design principle
    channel = detect_channel_somehow(lex_helper.event)

    if channel == "sms":
        return lex_helper.close(f"Flight {flight_number}: {status}")
    else:
        return lex_helper.close(create_rich_card())
```

### Design for the Richest Experience

Always design your responses for the richest channel (Lex), then let the framework automatically simplify for constrained channels:

```python
def handle_booking_options(lex_helper):
    # Design for rich experience - framework handles simplification
    options_card = LexImageResponseCard(
        imageResponseCard=ImageResponseCard(
            title="Booking Options",
            subtitle="What would you like to do?",
            imageUrl="https://example.com/booking-options.jpg",
            buttons=[
                Button(text="New Booking", value="book_new"),
                Button(text="Modify Existing", value="modify"),
                Button(text="Cancel Booking", value="cancel"),
                Button(text="Check Status", value="status")
            ]
        )
    )
    return lex_helper.close(options_card)
```

### Use Meaningful Button Text

Since SMS shows button text (not values), make button text user-friendly:

```python
# Good: Clear, user-friendly text
Button(text="Morning Flight", value="flight_morning_123")
Button(text="Evening Flight", value="flight_evening_456")

# Avoid: Technical or unclear text
Button(text="Option A", value="opt_a")
Button(text="Select", value="morning")
```

## Testing Channel Formatting

### Unit Testing

Test your handlers without worrying about channels - the framework handles formatting:

```python
def test_booking_confirmation():
    # Test business logic, not channel formatting
    response = handle_booking_confirmation(mock_lex_helper)

    # Verify the response structure
    assert isinstance(response.messages[0], LexImageResponseCard)
    assert "Booking Confirmed" in response.messages[0].imageResponseCard.title
```

### Integration Testing

Test channel formatting separately from business logic:

```python
from lex_helper.channels.channel_formatting import format_for_channel

def test_sms_formatting():
    # Create a standard response
    response = create_test_response_with_image_card()

    # Test SMS formatting
    sms_formatted = format_for_channel(response, "sms")

    # Verify SMS-specific formatting
    assert isinstance(sms_formatted["messages"][0], dict)
    assert "Options:" in sms_formatted["messages"][0]["content"]

def test_lex_formatting():
    # Test Lex formatting preserves rich content
    response = create_test_response_with_image_card()
    lex_formatted = format_for_channel(response, "lex")

    assert "imageResponseCard" in lex_formatted["messages"][0]
```

## Understanding the Implementation

### Channel Formatter Architecture

```python
# The framework automatically:
# 1. Detects channel from Lex event
# 2. Selects appropriate formatter (SMSChannel, LexChannel, etc.)
# 3. Applies channel-specific formatting rules
# 4. Returns optimized response

# You never call this directly - it happens automatically
formatted_response = format_for_channel(response, channel_string="sms")
```

### Current Channel Implementations

**SMS Channel (`SMSChannel`)**:
- Converts image cards to pipe-separated text
- Adds https:// to URLs missing schemes
- Extracts text from custom payloads
- Shows button text only (not values)

**Lex Channel (`LexChannel`)**:
- Preserves all rich formatting
- Handles Lex-specific requirements
- Maintains interactive elements
- Shows button text and values for debugging

## Creating Custom Channels

### Extending the Channel System

If you need to support additional channels, extend the base `Channel` class:

```python
from lex_helper.channels.base import Channel
from lex_helper.core.types import LexBaseResponse, LexMessages, LexPlainText

class SlackChannel(Channel):
    """Custom channel for Slack integration."""

    def format_message(self, message: LexMessages) -> LexBaseResponse:
        if isinstance(message, LexPlainText):
            # Add Slack-specific formatting (e.g., markdown conversion)
            content = message.content or ""
            # Convert bold formatting for Slack
            content = content.replace("**", "*")
            return LexPlainText(content=content)
        return message

    def format_messages(self, messages: list[LexMessages]) -> list[LexBaseResponse]:
        return [self.format_message(msg) for msg in messages]

    def format_image_card(self, card: LexImageResponseCard) -> LexBaseResponse:
        # Convert to Slack block format
        slack_blocks = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": card.imageResponseCard.title}
        }
        return LexCustomPayload(content=slack_blocks)
```

### Registering Custom Channels

Add your custom channel to the channel registry:

```python
# In your custom channel_formatting.py or by extending the existing one
def _get_channel(channel_string: str) -> Channel:
    channels = {
        "sms": SMSChannel,
        "lex": LexChannel,
        "slack": SlackChannel,  # Add your custom channel
        "teams": TeamsChannel,  # Another custom channel
    }
    channel = channels.get(channel_string.lower(), LexChannel)
    return channel()
```

## Troubleshooting

### Common Issues

#### Channel Not Detected Correctly
The framework automatically detects the channel from the Lex event. If you need to override this:

```python
# The framework handles this automatically, but for debugging:
# Check the event structure to understand channel detection
logger.info(f"Event structure: {json.dumps(event, indent=2)}")
```

#### Rich Content Not Displaying
If rich content isn't showing properly:

1. **Verify your message structure** - ensure proper `LexImageResponseCard` format
2. **Check the channel** - SMS will always convert to text
3. **Test with Lex console** first to verify rich formatting works

#### Custom Payloads Not Working
```python
# Ensure custom payloads are properly structured
payload = LexCustomPayload(content={
    "text": "Fallback text for SMS",  # Always include fallback text
    "rich_content": {...}  # Rich content for capable channels
})
```

### Debugging Channel Formatting

```python
# Enable debug logging to see channel formatting in action
import logging
logging.getLogger("lex_helper").setLevel(logging.DEBUG)

# The framework will log:
# - Channel detection
# - Formatting decisions
# - Final response structure
```

## Performance Considerations

### Automatic Optimization

The channel formatting system is designed for performance:

- **Lazy loading**: Channels are instantiated only when needed
- **Minimal overhead**: Simple message types pass through quickly
- **Efficient copying**: Uses Pydantic's efficient model copying

### Memory Usage

- Channel formatters are stateless and lightweight
- No persistent state between requests
- Automatic garbage collection of temporary objects

## Migration from Manual Channel Handling

### Before: Manual Channel Logic
```python
def handle_response(lex_helper):
    # DON'T DO THIS - old pattern
    if is_sms_channel(lex_helper.event):
        return lex_helper.close("Simple text response")
    else:
        return lex_helper.close(create_rich_card())
```

### After: Channel-Neutral Code
```python
def handle_response(lex_helper):
    # DO THIS - let the framework handle channels
    card = LexImageResponseCard(
        imageResponseCard=ImageResponseCard(
            title="Response Title",
            subtitle="Response details",
            buttons=[Button(text="Action", value="action")]
        )
    )
    return lex_helper.close(card)
```

### Migration Steps

1. **Remove channel detection logic** from your handlers
2. **Convert to rich message types** (LexImageResponseCard, etc.)
3. **Test with multiple channels** to verify automatic formatting
4. **Simplify your code** by removing channel-specific branches

## Related Topics

- [Message Management](message-management.md) - Learn about localization and message templates
- [Intent Handling](intent-handling.md) - Understand how intents work with formatted responses
- [Core Concepts](core-concepts.md) - Fundamental lex-helper concepts
- [Examples](../examples/index.md) - See channel formatting in action

---

*This page is part of the comprehensive lex-helper documentation. [Learn about message management →](message-management.md)*

## Best Practices

### Design for the Lowest Common Denominator

Always ensure your core message works on SMS, then enhance for richer channels:

```python
def handle_accessible_response(lex_helper):
    # Core message that works everywhere
    base_message = "Flight AA123 departs 3:30 PM Gate B12"

    # Enhanced for rich channels
    card = LexImageResponseCard(
        imageResponseCard=ImageResponseCard(
            title="Flight Departure",
            subtitle=base_message,
            imageUrl="https://example.com/gate-map.jpg",
            buttons=[
                Button(text="Get Directions", value="directions"),
                Button(text="Set Reminder", value="reminder")
            ]
        )
    )

    return lex_helper.close(card)
```

### URL and Link Handling

```python
def handle_links_properly(lex_helper):
    # Always provide context for links
    message = LexPlainText(
        content="Check your boarding pass: https://airline.com/boarding/ABC123"
    )
    # SMS: Automatically formats URL
    # Lex: Can be enhanced with buttons
    return lex_helper.close(message)
```

### Button Design Guidelines

```python
def handle_button_best_practices(lex_helper):
    card = LexImageResponseCard(
        imageResponseCard=ImageResponseCard(
            title="What would you like to do?",
            buttons=[
                # Keep button text short and clear
                Button(text="Check In", value="checkin"),
                Button(text="Change Seat", value="seat_change"),
                Button(text="Cancel Trip", value="cancel"),
                # Limit to 3-5 options for best UX
            ]
        )
    )
    return lex_helper.close(card)
```

## Testing Channel Formatting

### Unit Testing Different Channels

```python
import pytest
from lex_helper.channels.channel_formatting import format_for_channel
from lex_helper.core.types import LexResponse, LexPlainText

def test_sms_formatting():
    response = LexResponse(
        messages=[LexPlainText(content="Visit example.com/help")]
    )

    formatted = format_for_channel(response, "sms")

    # Verify SMS-specific formatting
    assert "https://example.com/help" in formatted["messages"][0]["content"]

def test_lex_formatting():
    response = LexResponse(
        messages=[LexImageResponseCard(...)]
    )

    formatted = format_for_channel(response, "lex")

    # Verify rich formatting is preserved
    assert "imageResponseCard" in formatted["messages"][0]
```

### Manual Testing Across Channels

1. **SMS Testing**: Use AWS Connect or test phone numbers
2. **Web Testing**: Lex console and web chat integrations
3. **Voice Testing**: Alexa or phone-based interfaces

## Troubleshooting

### Common Issues

#### Messages Not Formatting Correctly

```python
# Problem: Custom channel not recognized
formatted = format_for_channel(response, "unknown_channel")
# Solution: Falls back to Lex channel formatting

# Problem: Complex objects in custom payload
payload = LexCustomPayload(content=complex_object)
# Solution: Ensure content is serializable
payload = LexCustomPayload(content=str(complex_object))
```

#### Button Values Not Working

```python
# Problem: Button values not preserved
Button(text="Click Me")  # Missing value

# Solution: Always provide values
Button(text="Click Me", value="button_clicked")
```

### Debugging Channel Detection

```python
def debug_channel_formatting(lex_helper):
    # Log the detected channel
    channel = lex_helper.event.get("inputMode", "text")
    lex_helper.logger.info(f"Detected channel: {channel}")

    # Test formatting for specific channel
    test_response = format_for_channel(response, channel)
    lex_helper.logger.info(f"Formatted response: {test_response}")
```

## Creating Custom Channels

### Extending the Channel System

```python
from lex_helper.channels.base import Channel
from lex_helper.core.types import LexBaseResponse, LexMessages, LexPlainText

class SlackChannel(Channel):
    """Custom channel for Slack integration."""

    def format_message(self, message: LexMessages) -> LexBaseResponse:
        if isinstance(message, LexPlainText):
            # Add Slack-specific formatting
            content = message.content
            if content:
                # Convert to Slack markdown
                content = content.replace("**", "*")  # Bold formatting
            return LexPlainText(content=content)
        return message

    def format_messages(self, messages: list[LexMessages]) -> list[LexBaseResponse]:
        return [self.format_message(msg) for msg in messages]
```

### Registering Custom Channels

```python
# In channel_formatting.py, add your channel:
def _get_channel(channel_string: str) -> Channel:
    channels = {
        "sms": SMSChannel,
        "lex": LexChannel,
        "slack": SlackChannel,  # Add custom channel
    }
    channel = channels.get(channel_string.lower(), LexChannel)
    return channel()
```

## Related Topics

- [Message Management](message-management.md) - Learn about localization and message templates
- [Intent Handling](intent-handling.md) - Understand how intents work with formatted responses
- [Core Concepts](core-concepts.md) - Fundamental lex-helper concepts
- [Examples](../examples/index.md) - See channel formatting in action

---

*This page is part of the comprehensive lex-helper documentation. [Learn about message management →](message-management.md)*
