# Smart Disambiguation for lex-helper

## Overview

Smart Disambiguation is an intelligent feature in lex-helper that helps resolve ambiguous user input by presenting clear options when Amazon Lex cannot confidently determine the user's intent. Instead of falling back to "I didn't understand," the system analyzes confidence scores and presents relevant choices to guide users to their desired outcome.

## Table of Contents

- [How It Works](#how-it-works)
- [When Disambiguation Triggers](#when-disambiguation-triggers)
- [Configuration](#configuration)
- [Message Localization](#message-localization)
- [Integration](#integration)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## How It Works

### The Problem

Traditional chatbots often respond with generic fallback messages when they can't determine user intent:

```
User: "I need help with my booking"
Bot: "I didn't understand that. Could you please rephrase your request?"
```

### The Solution

Smart Disambiguation analyzes Lex's confidence scores and presents clear options:

```
User: "I need help with my booking"
Bot: "I can help you with a couple of things. Which would you like to do?"
     [Book a Flight] [Change Flight]
```

### Architecture

The disambiguation system consists of three main components:

1. **DisambiguationAnalyzer** - Analyzes confidence scores and determines when to disambiguate
2. **DisambiguationHandler** - Generates user-friendly clarification responses
3. **Handler Pipeline Integration** - Seamlessly integrates with existing lex-helper flow

## When Disambiguation Triggers

Disambiguation triggers in two scenarios:

### 1. Low Confidence Scenario
When the top intent has low confidence and multiple candidates exist:
```python
# Example: All intents have low confidence
{
    "TrackBaggage": 0.25,
    "ChangeFlight": 0.23,
    "CancelFlight": 0.19
}
# Result: Triggers disambiguation
```

### 2. Close Scores Scenario
When multiple intents have similar confidence scores:
```python
# Example: Two intents are very close
{
    "BookFlight": 0.45,
    "ChangeFlight": 0.42,
    "CancelFlight": 0.10
}
# Result: Triggers disambiguation between BookFlight and ChangeFlight
```

### When It Doesn't Trigger
When there's a clear winner:
```python
# Example: Clear winner
{
    "TrackBaggage": 0.75,
    "ChangeFlight": 0.15,
    "Authenticate": 0.10
}
# Result: Proceeds directly to TrackBaggage
```

## Configuration

### Basic Configuration

Enable disambiguation with default settings:

```python
from lex_helper import Config, LexHelper
from lex_helper.core.disambiguation.types import DisambiguationConfig

config = Config(
    session_attributes=MySessionAttributes(),
    enable_disambiguation=True  # Enable with defaults
)

lex_helper = LexHelper(config=config)
```

### Advanced Configuration

Customize disambiguation behavior:

```python
disambiguation_config = DisambiguationConfig(
    # Core thresholds
    confidence_threshold=0.4,      # Trigger when top score < 0.4
    similarity_threshold=0.15,     # Trigger when top scores within 0.15
    max_candidates=2,              # Show max 2 options
    min_candidates=2,              # Need at least 2 candidates

    # Intent groupings for better messages
    custom_intent_groups={
        "booking": ["BookFlight", "ChangeFlight", "CancelFlight"],
        "status": ["FlightDelayUpdate", "TrackBaggage"],
        "account": ["Authenticate"]
    },

    # Custom message keys for localization
    custom_messages={
        # Direct intent pair mappings
        "BookFlight_ChangeFlight": "disambiguation.airline.book_or_change",

        # Intent group mappings
        "disambiguation.booking": "disambiguation.airline.booking_options",

        # General mappings
        "disambiguation.two_options": "disambiguation.airline.two_options"
    }
)

config = Config(
    session_attributes=MySessionAttributes(),
    enable_disambiguation=True,
    disambiguation_config=disambiguation_config
)
```

### Bedrock-Powered Disambiguation

For even more intelligent and contextual disambiguation, enable Amazon Bedrock integration:

```python
from lex_helper.core.disambiguation.types import (
    BedrockDisambiguationConfig,
    DisambiguationConfig
)

# Configure Bedrock for intelligent text generation
bedrock_config = BedrockDisambiguationConfig(
    enabled=True,
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    region_name="us-east-1",
    max_tokens=150,
    temperature=0.3,
    system_prompt=(
        "You are a helpful assistant that creates clear, concise "
        "disambiguation messages for chatbot users. Be friendly and natural."
    ),
    fallback_to_static=True,  # Graceful fallback if Bedrock fails
)

# Configure disambiguation with Bedrock
disambiguation_config = DisambiguationConfig(
    confidence_threshold=0.5,
    max_candidates=2,
    bedrock_config=bedrock_config,  # Enable Bedrock integration
)
```

**Benefits of Bedrock Integration:**
- **Contextual messages**: Acknowledges user's specific input
- **Natural language**: More conversational than static templates
- **Smart button labels**: Generates intuitive action text
- **Adaptive responses**: Tailored to your domain and use case

**Example comparison:**

*Static disambiguation:*
```
User: "I need help with my flight"
Bot: "I can help you with several things. What would you like to do?"
Buttons: ["Book Flight", "Change Flight", "Cancel Flight"]
```

*Bedrock-powered disambiguation:*
```
User: "I need help with my flight"
Bot: "I'd be happy to help with your flight! Are you looking to make changes to an existing booking or book a new flight?"
Buttons: ["Modify existing booking", "Book new flight"]
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `confidence_threshold` | float | 0.6 | Minimum confidence to avoid disambiguation |
| `similarity_threshold` | float | 0.15 | Max difference between top scores to trigger |
| `max_candidates` | int | 3 | Maximum options to show users |
| `min_candidates` | int | 2 | Minimum candidates needed to trigger |
| `custom_intent_groups` | dict | {} | Related intent groupings |
| `custom_messages` | dict | {} | Custom message key mappings |
| `bedrock_config` | BedrockDisambiguationConfig | disabled | Bedrock integration settings |

#### Bedrock Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | bool | False | Enable Bedrock text generation |
| `model_id` | str | claude-3-haiku | Bedrock model to use |
| `region_name` | str | us-east-1 | AWS region for Bedrock |
| `max_tokens` | int | 200 | Maximum tokens for responses |
| `temperature` | float | 0.3 | Randomness (0.0-1.0, lower = more deterministic) |
| `system_prompt` | str | default | System prompt for the model |
| `fallback_to_static` | bool | True | Fall back to static messages if Bedrock fails |

## Message Localization

### Message Key Mapping

The system uses a hierarchical approach to find the right message:

#### 1. Direct Intent Pair Mapping (Highest Priority)
```python
# For intents: ["BookFlight", "ChangeFlight"]
# Creates key: "BookFlight_ChangeFlight" (alphabetically sorted)
custom_messages = {
    "BookFlight_ChangeFlight": "disambiguation.airline.book_or_change"
}
```

#### 2. Intent Group Mapping (Medium Priority)
```python
# For intents in the "booking" group
# Creates key: "disambiguation.booking"
custom_messages = {
    "disambiguation.booking": "disambiguation.airline.booking_options"
}
```

#### 3. Default Mapping (Lowest Priority)
```python
# Falls back to default keys
custom_messages = {
    "disambiguation.two_options": "disambiguation.airline.two_options"
}
```

### Message Files

Add disambiguation messages to your localization files:

**messages_en_US.yaml:**
```yaml
disambiguation:
  # Default messages
  two_options: "I can help you with two things. Which would you like to do?"
  multiple_options: "I can help you with several things. What would you like to do?"

  # Custom airline messages
  airline:
    two_options: "I can help you with a couple of things. Which would you like to do?"
    booking_options: "I can help you with flight bookings. Would you like to book, change, or cancel a flight?"
    book_or_change: "Would you like to book a new flight or change an existing one?"
```

**messages_es_ES.yaml:**
```yaml
disambiguation:
  two_options: "Puedo ayudarte con dos cosas. ¿Cuál te gustaría hacer?"
  multiple_options: "Puedo ayudarte con varias cosas. ¿Qué te gustaría hacer?"

  airline:
    two_options: "Puedo ayudarte con un par de cosas. ¿Cuál te gustaría hacer?"
    booking_options: "Puedo ayudarte con reservas de vuelos. ¿Te gustaría reservar, cambiar o cancelar un vuelo?"
    book_or_change: "¿Te gustaría reservar un nuevo vuelo o cambiar uno existente?"
```

## Integration

### Handler Pipeline Integration

Disambiguation integrates seamlessly into the lex-helper pipeline:

```python
# When disambiguation is enabled, the handler pipeline becomes:
handlers = [
    disambiguation_intent_handler,  # Added automatically
    regular_intent_handler         # Existing handler
]
```

### Processing Flow

1. **Request Analysis** - Analyzer examines Lex confidence scores
2. **Disambiguation Decision** - Determines if disambiguation is needed
3. **Response Generation** - Creates user-friendly options with buttons
4. **User Selection** - Processes user's choice and routes to correct intent

### Conversation Flow Example

```
User: "I need help with my booking"

Bot: "I can help you with a couple of things. Which would you like to do?"
     [Book Flight] [Change Flight]

User clicks [Change Flight]
→ User input appears as: "Change Flight" (not "ChangeFlight")

Bot: "What is your reservation number?"
```

This natural conversation flow ensures users see human-readable text throughout their interaction.

### Response Format

Disambiguation responses include both text and interactive buttons:

```json
{
  "messages": [
    {
      "content": "I can help you with a couple of things. Which would you like to do?",
      "contentType": "PlainText"
    },
    {
      "contentType": "ImageResponseCard",
      "imageResponseCard": {
        "title": "Please choose an option:",
        "subtitle": "Select what you'd like to do",
        "buttons": [
          {"text": "Track Baggage", "value": "Track Baggage"},
          {"text": "Change Flight", "value": "Change Flight"}
        ]
      }
    }
  ]
}
```

**Note**: Button values use human-readable display names (e.g., "Track Baggage") rather than technical intent names (e.g., "TrackBaggage"). This ensures that when users click buttons, they see natural language as their input, creating a more conversational experience.
```

## Examples

### Example 1: Basic Setup

```python
# Minimal setup - just enable disambiguation
config = Config(
    session_attributes=MySessionAttributes(),
    enable_disambiguation=True
)

lex_helper = LexHelper(config=config)
```

### Example 2: Airline Bot Setup

```python
# Full airline bot configuration
disambiguation_config = DisambiguationConfig(
    confidence_threshold=0.4,
    max_candidates=2,
    custom_intent_groups={
        "booking": ["BookFlight", "ChangeFlight", "CancelFlight"],
        "status": ["FlightDelayUpdate", "TrackBaggage"]
    },
    custom_messages={
        "disambiguation.booking": "disambiguation.airline.booking_options",
        "disambiguation.status": "disambiguation.airline.status_options",
        "BookFlight_ChangeFlight": "disambiguation.airline.book_or_change"
    }
)

config = Config(
    session_attributes=AirlineBotSessionAttributes(),
    package_name="fulfillment_function",
    enable_disambiguation=True,
    disambiguation_config=disambiguation_config
)
```

### Example 3: E-commerce Bot Setup

```python
disambiguation_config = DisambiguationConfig(
    confidence_threshold=0.5,
    custom_intent_groups={
        "shopping": ["SearchProducts", "AddToCart", "Checkout"],
        "account": ["Login", "Register", "ViewOrders"],
        "support": ["ContactSupport", "ReturnItem", "TrackOrder"]
    },
    custom_messages={
        "disambiguation.shopping": "ecommerce.shopping_options",
        "disambiguation.account": "ecommerce.account_options",
        "SearchProducts_AddToCart": "ecommerce.search_or_add"
    }
)
```

## Best Practices

### 1. Threshold Configuration

- **Conservative (0.6-0.8)**: Only disambiguate when really unsure
- **Moderate (0.4-0.5)**: Good balance for most bots
- **Aggressive (0.2-0.3)**: Catch more ambiguous cases

### 2. Intent Grouping

Group related intents for better user experience:

```python
# Good grouping - related functionality
custom_intent_groups = {
    "booking": ["BookFlight", "ChangeFlight", "CancelFlight"],
    "status": ["FlightStatus", "BaggageStatus"]
}

# Avoid - unrelated intents
custom_intent_groups = {
    "mixed": ["BookFlight", "Weather", "Authenticate"]  # Don't do this
}
```

### 3. Message Design

- Keep messages **concise and clear**
- Use **action-oriented language**
- Provide **specific options** rather than generic choices
- Test with **real user scenarios**

### 4. Localization

- Always use **message keys** instead of hardcoded text
- Provide translations for **all supported locales**
- Test disambiguation in **each language**
- Consider **cultural differences** in phrasing

### 5. Testing

Test disambiguation with various scenarios:

```python
# Test cases to verify
test_cases = [
    # Low confidence scenario
    {"TrackBaggage": 0.25, "ChangeFlight": 0.23},

    # Close scores scenario
    {"BookFlight": 0.45, "ChangeFlight": 0.42},

    # Clear winner (should not disambiguate)
    {"TrackBaggage": 0.75, "ChangeFlight": 0.15},

    # Single candidate (should not disambiguate)
    {"BookFlight": 0.30}
]
```

## Troubleshooting

### Common Issues

#### 1. Disambiguation Not Triggering

**Problem**: Expected disambiguation but got fallback instead.

**Solutions**:
- Check if `enable_disambiguation=True` in config
- Verify confidence scores are within triggering range
- Ensure minimum candidates requirement is met
- Check if disambiguation components are properly imported

#### 2. Wrong Message Displayed

**Problem**: Generic message instead of custom message.

**Solutions**:
- Verify message keys exist in localization files
- Check custom_messages mapping is correct
- Ensure intent names match exactly (case-sensitive)
- Verify locale is set correctly

#### 3. Disambiguation Triggering Too Often

**Problem**: Disambiguation shows for clear intent matches.

**Solutions**:
- Increase `confidence_threshold` (try 0.6 instead of 0.4)
- Increase `similarity_threshold` (try 0.2 instead of 0.15)
- Check Lex training data quality
- Review intent utterance overlap



### Debug Information

Enable detailed logging to troubleshoot:

```python
disambiguation_config = DisambiguationConfig(
    enable_logging=True,  # Enable detailed logs
    # ... other config
)
```

Check logs for:
- Confidence scores extracted from Lex
- Disambiguation decision reasoning
- Message key resolution

### Performance Considerations

- Disambiguation adds minimal latency (~10-50ms)
- Message localization is cached by lex-helper
- Button rendering is handled by Lex UI

## Migration Guide

### From Regular lex-helper

1. **Update imports**:
```python
from lex_helper.core.disambiguation.types import DisambiguationConfig
```

2. **Add configuration**:
```python
config = Config(
    # ... existing config
    enable_disambiguation=True
)
```

3. **Add message keys** to localization files

4. **Test thoroughly** with existing intents

### Backward Compatibility

- Disambiguation is **disabled by default**
- Existing code works **without changes**
- No breaking changes to existing APIs
- Graceful fallback if disambiguation components unavailable

## API Reference

### DisambiguationConfig

```python
@dataclass
class DisambiguationConfig:
    confidence_threshold: float = 0.6
    max_candidates: int = 3
    fallback_to_original: bool = True
    min_candidates: int = 2
    similarity_threshold: float = 0.15
    enable_logging: bool = True
    custom_intent_groups: dict[str, list[str]] = field(default_factory=dict)
    custom_messages: dict[str, str] = field(default_factory=dict)
```

### Config Integration

```python
class Config:
    # ... existing fields
    enable_disambiguation: bool = False
    disambiguation_config: DisambiguationConfig | None = None
```

## Conclusion

Smart Disambiguation transforms ambiguous user interactions into clear, actionable choices. By leveraging Lex's confidence scores, it significantly improves user experience while maintaining the simplicity and power of lex-helper.

The feature is designed to be:
- **Easy to integrate** - Just set `enable_disambiguation=True`
- **Highly configurable** - Customize thresholds, messages, and behavior
- **Fully localized** - Support for multiple languages out of the box
- **Backward compatible** - No impact on existing implementations

Start with the basic configuration and gradually customize based on your bot's specific needs and user feedback.
