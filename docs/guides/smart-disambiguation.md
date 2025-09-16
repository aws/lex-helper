# Smart Disambiguation

Transform ambiguous user inputs into clear, actionable choices with lex-helper's intelligent disambiguation system. Instead of generic "I didn't understand" responses, present users with relevant options to guide them to their desired outcome.

## Overview

Smart Disambiguation is an advanced feature that analyzes Amazon Lex's confidence scores to detect ambiguous user input and automatically presents clarifying options. This dramatically improves user experience by turning confusion into clear choices.

### The Problem

Traditional chatbots often fail users with ambiguous input:

```
User: "I need help with my booking"
Bot: "I didn't understand that. Could you please rephrase your request?"
```

### The Solution

Smart Disambiguation presents clear options:

```
User: "I need help with my booking"
Bot: "I can help you with a couple of things. Which would you like to do?"
     [Book a Flight] [Change Flight]
```

## Key Concepts

### How It Works

The disambiguation system consists of three core components:

1. **DisambiguationAnalyzer** - Analyzes Lex confidence scores to identify ambiguous scenarios
2. **DisambiguationHandler** - Generates user-friendly clarification responses with interactive buttons
3. **BedrockDisambiguationGenerator** - (Optional) Uses AI to create contextual, natural language responses

### When Disambiguation Triggers

Disambiguation activates in two key scenarios:

#### 1. Low Confidence Scenario
When the top intent has low confidence but multiple viable candidates exist:

```python
# Example confidence scores
{
    "TrackBaggage": 0.25,
    "ChangeFlight": 0.23,
    "CancelFlight": 0.19
}
# Result: Triggers disambiguation with all three options
```

#### 2. Close Scores Scenario
When multiple intents have similar confidence scores:

```python
# Example confidence scores
{
    "BookFlight": 0.45,
    "ChangeFlight": 0.42,
    "CancelFlight": 0.10
}
# Result: Triggers disambiguation between BookFlight and ChangeFlight
```

#### When It Doesn't Trigger
When there's a clear winner:

```python
# Example confidence scores
{
    "TrackBaggage": 0.75,
    "ChangeFlight": 0.15,
    "Authenticate": 0.10
}
# Result: Proceeds directly to TrackBaggage
```

## Basic Setup

### Quick Start

Enable disambiguation with default settings:

```python
from lex_helper import Config, LexHelper

config = Config(
    session_attributes=MySessionAttributes(),
    enable_disambiguation=True  # Enable with defaults
)

lex_helper = LexHelper(config=config)
```

That's it! Your bot now has intelligent disambiguation with sensible defaults.

### Configuration Parameters

Customize disambiguation behavior with these key parameters:

```python
from lex_helper.core.disambiguation.types import DisambiguationConfig

disambiguation_config = DisambiguationConfig(
    confidence_threshold=0.6,      # Trigger when top score < 0.6
    similarity_threshold=0.15,     # Trigger when top scores within 0.15
    max_candidates=3,              # Show maximum 3 options
    min_candidates=2,              # Need at least 2 candidates
)

config = Config(
    session_attributes=MySessionAttributes(),
    enable_disambiguation=True,
    disambiguation_config=disambiguation_config
)
```

## Bedrock Integration

### Overview

Amazon Bedrock integration transforms static disambiguation into intelligent, contextual responses that acknowledge the user's specific input and provide natural, conversational clarification.

### Benefits of Bedrock Integration

- **Contextual messages**: Acknowledges user's specific input
- **Natural language**: More conversational than static templates
- **Smart button labels**: Generates intuitive action text
- **Adaptive responses**: Tailored to your domain and use case

### Comparison: Static vs. Bedrock-Powered

**Static disambiguation:**
```
User: "I need help with my flight"
Bot: "I can help you with several things. What would you like to do?"
Buttons: ["Book Flight", "Change Flight", "Cancel Flight"]
```

**Bedrock-powered disambiguation:**
```
User: "I need help with my flight"
Bot: "I'd be happy to help with your flight! Are you looking to make changes to an existing booking or book a new flight?"
Buttons: ["Modify existing booking", "Book new flight"]
```

### Setup and Configuration

#### Basic Bedrock Setup

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
    fallback_to_static=True,  # Graceful fallback if Bedrock fails
)

# Configure disambiguation with Bedrock
disambiguation_config = DisambiguationConfig(
    confidence_threshold=0.5,
    max_candidates=2,
    bedrock_config=bedrock_config,
)

config = Config(
    session_attributes=MySessionAttributes(),
    enable_disambiguation=True,
    disambiguation_config=disambiguation_config
)
```

#### Advanced Bedrock Configuration

```python
bedrock_config = BedrockDisambiguationConfig(
    enabled=True,
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    region_name="us-east-1",
    max_tokens=200,
    temperature=0.3,
    system_prompt=(
        "You are a helpful airline customer service assistant. "
        "When users provide ambiguous input, help them choose between "
        "available options with friendly, professional language. "
        "Keep responses concise and action-oriented."
    ),
    fallback_to_static=True,
)
```

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

### Supported Models

lex-helper supports all Amazon Bedrock text generation models:

#### Recommended Models

- **Claude 3 Haiku** (`anthropic.claude-3-haiku-20240307-v1:0`) - Fast, cost-effective, great for disambiguation
- **Claude 3 Sonnet** (`anthropic.claude-3-sonnet-20240229-v1:0`) - Higher quality, more nuanced responses
- **Titan Text** (`amazon.titan-text-express-v1`) - AWS native option

#### Model Selection Guidelines

- **For high-volume bots**: Use Claude 3 Haiku for speed and cost efficiency
- **For premium experiences**: Use Claude 3 Sonnet for higher quality responses
- **For AWS-only environments**: Use Titan Text models

### IAM Permissions

Ensure your Lambda execution role has the necessary Bedrock permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            ]
        }
    ]
}
```

## Configuration Examples

### Example 1: E-commerce Bot

```python
disambiguation_config = DisambiguationConfig(
    confidence_threshold=0.5,
    max_candidates=2,
    custom_intent_groups={
        "shopping": ["SearchProducts", "AddToCart", "Checkout"],
        "account": ["Login", "Register", "ViewOrders"],
        "support": ["ContactSupport", "ReturnItem", "TrackOrder"]
    },
    custom_messages={
        "disambiguation.shopping": "ecommerce.shopping_options",
        "disambiguation.account": "ecommerce.account_options",
        "SearchProducts_AddToCart": "ecommerce.search_or_add"
    },
    bedrock_config=BedrockDisambiguationConfig(
        enabled=True,
        system_prompt="You are a helpful e-commerce assistant...",
        fallback_to_static=True
    )
)
```

### Example 2: Banking Bot

```python
disambiguation_config = DisambiguationConfig(
    confidence_threshold=0.6,  # Higher threshold for financial accuracy
    max_candidates=2,
    custom_intent_groups={
        "transactions": ["CheckBalance", "TransferMoney", "PayBills"],
        "cards": ["ReportLostCard", "ActivateCard", "CheckCardStatus"],
        "loans": ["ApplyLoan", "CheckLoanStatus", "MakePayment"]
    },
    bedrock_config=BedrockDisambiguationConfig(
        enabled=True,
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",  # Higher quality for banking
        system_prompt=(
            "You are a professional banking assistant. "
            "Provide clear, secure, and helpful disambiguation options. "
            "Use formal but friendly language appropriate for financial services."
        ),
        temperature=0.1,  # Lower temperature for consistency
        fallback_to_static=True
    )
)
```

### Example 3: Healthcare Bot

```python
disambiguation_config = DisambiguationConfig(
    confidence_threshold=0.7,  # Very high threshold for healthcare
    max_candidates=2,
    custom_intent_groups={
        "appointments": ["BookAppointment", "CancelAppointment", "RescheduleAppointment"],
        "prescriptions": ["RefillPrescription", "CheckPrescriptionStatus"],
        "emergency": ["FindEmergencyRoom", "CallEmergencyServices"]
    },
    bedrock_config=BedrockDisambiguationConfig(
        enabled=True,
        system_prompt=(
            "You are a healthcare assistant. Provide clear, empathetic "
            "disambiguation options. Always prioritize patient safety and "
            "direct urgent matters to appropriate resources."
        ),
        temperature=0.2,
        fallback_to_static=True
    )
)
```

## Use Cases and Scenarios

### Scenario 1: Multi-Intent Utterances

**User Input**: "I want to book and also check my existing reservation"

**Without Disambiguation**:
```
Bot: "I didn't understand. Please try again."
```

**With Smart Disambiguation**:
```
Bot: "I can help you with booking or checking reservations. Which would you like to do first?"
Buttons: ["Book new flight", "Check existing reservation"]
```

### Scenario 2: Ambiguous Keywords

**User Input**: "Status"

**Confidence Scores**:
```python
{
    "FlightStatus": 0.35,
    "BaggageStatus": 0.32,
    "ReservationStatus": 0.28
}
```

**Response**:
```
Bot: "What status would you like to check?"
Buttons: ["Flight Status", "Baggage Status", "Reservation Status"]
```

### Scenario 3: Partial Information

**User Input**: "Change my"

**With Bedrock Enhancement**:
```
Bot: "I can help you make changes. What would you like to change?"
Buttons: ["Change flight", "Change seat", "Change contact info"]
```

## Message Localization

### Message Key Hierarchy

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

### Localization Files

**messages_en_US.yaml:**
```yaml
disambiguation:
  # Default messages
  two_options: "I can help you with two things. Which would you like to do?"
  multiple_options: "I can help you with several things. What would you like to do?"
  fallback: "I'm not sure what you're looking for. Could you be more specific?"

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
  fallback: "No estoy seguro de lo que buscas. ¿Podrías ser más específico?"

  airline:
    two_options: "Puedo ayudarte con un par de cosas. ¿Cuál te gustaría hacer?"
    booking_options: "Puedo ayudarte con reservas de vuelos. ¿Te gustaría reservar, cambiar o cancelar un vuelo?"
    book_or_change: "¿Te gustaría reservar un nuevo vuelo o cambiar uno existente?"
```

## Best Practices

### 1. Threshold Configuration

Choose thresholds based on your use case:

- **Conservative (0.6-0.8)**: Only disambiguate when really unsure (banking, healthcare)
- **Moderate (0.4-0.5)**: Good balance for most bots (e-commerce, travel)
- **Aggressive (0.2-0.3)**: Catch more ambiguous cases (general purpose bots)

### 2. Intent Grouping Strategy

Group related intents for better user experience:

```python
# ✅ Good grouping - related functionality
custom_intent_groups = {
    "booking": ["BookFlight", "ChangeFlight", "CancelFlight"],
    "status": ["FlightStatus", "BaggageStatus"]
}

# ❌ Avoid - unrelated intents
custom_intent_groups = {
    "mixed": ["BookFlight", "Weather", "Authenticate"]  # Don't do this
}
```

### 3. Message Design Guidelines

- **Keep messages concise and clear** - Users should understand options immediately
- **Use action-oriented language** - "Book a flight" vs "Flight booking"
- **Provide specific options** - Avoid generic choices like "Option A"
- **Test with real user scenarios** - Use actual user utterances in testing

### 4. Bedrock Optimization

- **Use appropriate models** - Haiku for speed, Sonnet for quality
- **Optimize system prompts** - Include domain-specific context
- **Set reasonable token limits** - 150-200 tokens for disambiguation
- **Enable fallback** - Always set `fallback_to_static=True`

### 5. Testing Strategy

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

**Symptoms**: Expected disambiguation but got fallback instead.

**Diagnostic Steps**:
```python
# Enable detailed logging
disambiguation_config = DisambiguationConfig(
    enable_logging=True,
    # ... other config
)
```

**Common Causes & Solutions**:
- ✅ Verify `enable_disambiguation=True` in config
- ✅ Check confidence scores are within triggering range
- ✅ Ensure minimum candidates requirement is met (default: 2)
- ✅ Confirm disambiguation components are properly imported

#### 2. Wrong Message Displayed

**Symptoms**: Generic message instead of custom message.

**Solutions**:
- ✅ Verify message keys exist in localization files
- ✅ Check `custom_messages` mapping is correct
- ✅ Ensure intent names match exactly (case-sensitive)
- ✅ Verify locale is set correctly in session

#### 3. Disambiguation Triggering Too Often

**Symptoms**: Disambiguation shows for clear intent matches.

**Solutions**:
- ✅ Increase `confidence_threshold` (try 0.6 instead of 0.4)
- ✅ Increase `similarity_threshold` (try 0.2 instead of 0.15)
- ✅ Review Lex training data quality
- ✅ Check for intent utterance overlap

#### 4. Bedrock Integration Issues

**Symptoms**: Bedrock responses not generating or errors in logs.

**Diagnostic Steps**:
```python
# Test Bedrock connectivity
from lex_helper.core.invoke_bedrock import invoke_bedrock_simple_converse

try:
    response = invoke_bedrock_simple_converse(
        prompt="Test prompt",
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        region_name="us-east-1"
    )
    print("Bedrock working:", response)
except Exception as e:
    print("Bedrock error:", e)
```

**Common Causes & Solutions**:
- ✅ Verify IAM permissions for Bedrock
- ✅ Check model availability in your region
- ✅ Confirm model ID is correct
- ✅ Ensure `fallback_to_static=True` for graceful degradation

#### 5. Button Selection Not Working

**Symptoms**: User clicks button but intent not recognized.

**Solutions**:
- ✅ Verify button values use display names, not technical intent names
- ✅ Check disambiguation state is properly stored in session
- ✅ Ensure disambiguation handler is processing responses
- ✅ Review button text matching logic

### Debug Information

Enable detailed logging to troubleshoot:

```python
import logging

# Enable lex-helper disambiguation logging
logging.getLogger("lex_helper.core.disambiguation").setLevel(logging.DEBUG)

disambiguation_config = DisambiguationConfig(
    enable_logging=True,
    # ... other config
)
```

**Log Information Includes**:
- Confidence scores extracted from Lex
- Disambiguation decision reasoning
- Message key resolution process
- Bedrock generation attempts and results

### Performance Considerations

- **Latency Impact**: Disambiguation adds 10-50ms to response time
- **Bedrock Latency**: AI generation adds 200-500ms but provides better UX
- **Memory Usage**: Minimal impact on Lambda memory
- **Cost**: Bedrock usage is typically $0.001-0.01 per disambiguation

### Error Recovery

The system includes multiple fallback layers:

1. **Bedrock Failure** → Falls back to static messages
2. **Message Key Missing** → Uses default messages
3. **Disambiguation Failure** → Falls back to original Lex behavior
4. **Complete Failure** → Returns generic fallback response

## Migration Guide

### From Basic lex-helper

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

### Enabling Bedrock

If you already have disambiguation enabled and want to add Bedrock:

```python
# Add Bedrock configuration to existing setup
bedrock_config = BedrockDisambiguationConfig(
    enabled=True,
    fallback_to_static=True  # Ensures no breaking changes
)

# Update existing disambiguation config
disambiguation_config.bedrock_config = bedrock_config
```

### Backward Compatibility

- ✅ Disambiguation is **disabled by default**
- ✅ Existing code works **without changes**
- ✅ No breaking changes to existing APIs
- ✅ Graceful fallback if disambiguation components unavailable

## Complete Example: Airline Bot

Here's a complete implementation example from the sample airline bot:

```python
import os
from lex_helper import Config, LexHelper
from lex_helper.core.disambiguation.types import (
    BedrockDisambiguationConfig,
    DisambiguationConfig
)

# Environment-based configuration for flexibility
enable_bedrock = os.getenv("ENABLE_BEDROCK_DISAMBIGUATION", "false").lower() == "true"

# Bedrock configuration (optional)
bedrock_config = BedrockDisambiguationConfig(
    enabled=enable_bedrock,
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    region_name="us-east-1",
    max_tokens=150,
    temperature=0.3,
    system_prompt=(
        "You are a helpful airline customer service assistant. "
        "When users provide ambiguous input about flights, bookings, or travel, "
        "help them choose between available options with friendly, professional language. "
        "Keep responses concise and action-oriented."
    ),
    fallback_to_static=True,
)

# Full airline bot disambiguation configuration
disambiguation_config = DisambiguationConfig(
    confidence_threshold=0.4,
    max_candidates=2,
    similarity_threshold=0.15,

    # Group related intents for better messaging
    custom_intent_groups={
        "booking": ["BookFlight", "ChangeFlight", "CancelFlight"],
        "status": ["FlightDelayUpdate", "TrackBaggage"],
        "account": ["Authenticate", "CreateAccount"]
    },

    # Custom message mappings for airline domain
    custom_messages={
        "disambiguation.booking": "disambiguation.airline.booking_options",
        "disambiguation.status": "disambiguation.airline.status_options",
        "BookFlight_ChangeFlight": "disambiguation.airline.book_or_change",
        "disambiguation.two_options": "disambiguation.airline.two_options"
    },

    bedrock_config=bedrock_config,
    enable_logging=True
)

# Main configuration
config = Config(
    session_attributes=AirlineBotSessionAttributes(),
    package_name="fulfillment_function",
    enable_disambiguation=True,
    disambiguation_config=disambiguation_config
)

# Initialize lex-helper
lex_helper = LexHelper(config=config)

def lambda_handler(event, context):
    """Lambda handler with smart disambiguation enabled."""
    return lex_helper.handle_request(event, context)
```

**Usage Examples**:

```bash
# Run with static disambiguation
python lambda_function.py

# Run with Bedrock-powered disambiguation
ENABLE_BEDROCK_DISAMBIGUATION=true python lambda_function.py
```

**Message Files** (`messages_en_US.yaml`):
```yaml
disambiguation:
  two_options: "I can help you with two things. Which would you like to do?"
  multiple_options: "I can help you with several things. What would you like to do?"
  fallback: "I'm not sure what you're looking for. Could you be more specific?"

  airline:
    two_options: "I can help you with a couple of things. Which would you like to do?"
    booking_options: "I can help you with flight bookings. Would you like to book, change, or cancel a flight?"
    status_options: "What status would you like to check?"
    book_or_change: "Would you like to book a new flight or change an existing one?"
```

## Related Topics

- [Bedrock Integration](bedrock-integration.md) - Learn more about AI-powered features
- [Core Concepts](core-concepts.md) - Understand lex-helper fundamentals
- [Message Management](message-management.md) - Advanced localization techniques
- [Session Attributes](session-attributes.md) - Managing conversation state
- [Error Handling](error-handling.md) - Robust error handling patterns

---

Smart Disambiguation transforms ambiguous interactions into clear, actionable choices, significantly improving user experience while maintaining the simplicity and power of lex-helper. Start with basic configuration and gradually customize based on your bot's specific needs and user feedback.
