# Internationalization with lex-helper

This document explains how to use the message management features in lex-helper for internationalization support in the Airline-Bot project.

## Overview

The lex-helper library provides:
- Store all user-facing messages in YAML files
- Support multiple languages/locales
- Use parameter substitution in messages
- Simple `get_message()` function for message retrieval
- Automatic fallback to default locale

## File Structure

```
sample_airline_bot/
└── lambdas/fulfillment_function/
    ├── messages/
    │   ├── messages.yaml           # Default English messages
    │   └── messages_es_ES.yaml     # Spanish messages
    └── src/fulfillment_function/
        └── intents/
            └── book_flight.py      # get_message() usage example
```

## Message File Format

Messages are stored in YAML files with hierarchical keys:

```yaml
# messages_en_US.yaml
cancel_flight:
  elicit_reservation_number: "What is your reservation number?"
  cancellation_success: "I've cancelled your reservation {reservation_number}."

book_flight:
  elicit_origin_city: "From which city would you like to depart?"
```

### Parameter Substitution

Use `{parameter_name}` syntax for dynamic values:

```yaml
booking_success: "Your reservation {reservation_number} for {passengers} passenger(s) is confirmed."
```

## Usage Patterns

### 1. Basic Usage (Recommended)

Use the simple `get_message()` function:

```python
from lex_helper import get_message

def handler(lex_request):
    # Get simple message
    message = get_message("book_flight.elicit_origin_city")

    # Get message with fallback
    try:
        message = get_message("book_flight.authentication_required")
    except Exception as e:
        message = "Authentication is required to proceed."
```

### 2. Messages with Parameters

Use template formatting for dynamic content:

```python
from lex_helper import get_message

def handler(lex_request):
    try:
        template = get_message("book_flight.booking_success_oneway")
        message = template.format(
            origin_city="Los Angeles (LAX)",
            destination_city="New York (JFK)",
            departure_date="2024-01-15",
            number_of_passengers="2",
            reservation_number="ABC123"
        )
    except Exception as e:
        # Fallback message
        message = "Your booking has been confirmed."
```

## Locale Management

The lex-helper library uses a simple locale system:

```python
from lex_helper import set_locale, get_message

# Set locale for the session
set_locale("es_ES")

# Get localized message
message = get_message("greeting")
```

### Automatic Locale Detection

The system automatically detects locale from:
1. Lex bot `localeId` (e.g., "en_US", "es_ES")
2. Falls back to default `messages.yaml` if specific locale not found

### Supported File Naming

- `messages.yaml` - Default/fallback messages
- `messages_{localeId}.yaml` - Locale-specific messages (e.g., `messages_es_ES.yaml`)

## Adding New Languages

1. **Create Message File**: Add `messages_{locale}.yaml` in the `messages/` directory
2. **Copy Structure**: Use existing `messages.yaml` as template
3. **Translate Messages**: Replace message values with translations
4. **Test**: Verify the bot works with the new locale

Example for French:

```bash
# 1. Create messages file
cp lambdas/fulfillment_function/messages/messages.yaml \
   lambdas/fulfillment_function/messages/messages_fr_FR.yaml

# 2. Edit messages_fr_FR.yaml with French translations
# 3. Test with Lex bot configured for fr_FR locale
```

## Best Practices

### 1. Message Key Naming
Use hierarchical naming with intent prefixes:
```yaml
intent_name:
  action_type: "Message text"

# Examples:
cancel_flight:
  elicit_reservation_number: "What is your reservation number?"
  cancellation_success: "Reservation cancelled successfully."
```

### 2. Parameter Naming
Use descriptive parameter names:
```yaml
# Good
booking_success: "Booked flight from {origin_city} to {destination_city}"

# Avoid
booking_success: "Booked flight from {param1} to {param2}"
```

### 3. Fallback Messages
Always provide fallback handling:
```python
try:
    message = get_localized_message(lex_request, "cancel_flight.success")
except Exception:
    message = "Operation completed successfully."  # Fallback
```

### 4. Message Validation
Validate that all required messages exist in all language files:
```bash
# Compare message keys across files
python -c "
import yaml
en = yaml.safe_load(open('messages_en_US.yaml'))
it = yaml.safe_load(open('messages_it_IT.yaml'))
# Add validation logic
"
```

## Testing Internationalization

### 1. Unit Testing
Test message retrieval for different locales:
```python
def test_cancel_flight_messages():
    # Test English
    lex_request.locale = 'en_US'
    message = get_localized_message(lex_request, 'cancel_flight.elicit_reservation_number')
    assert "What is your reservation number?" in message

    # Test Italian
    lex_request.locale = 'it_IT'
    message = get_localized_message(lex_request, 'cancel_flight.elicit_reservation_number')
    assert "Qual è il numero" in message
```

### 2. Integration Testing
Test with different Lex locale configurations:
```bash
# Test with English locale
aws lexv2-runtime recognize-text \
  --bot-id <bot-id> \
  --bot-alias-id <alias-id> \
  --locale-id en_US \
  --text "Cancel my reservation"

# Test with Italian locale
aws lexv2-runtime recognize-text \
  --bot-id <bot-id> \
  --bot-alias-id <alias-id> \
  --locale-id it_IT \
  --text "Cancella la mia prenotazione"
```

## Migration from Hardcoded Messages

To migrate existing intents:

1. **Extract Messages**: Identify all hardcoded strings in intent handlers
2. **Add to YAML**: Add messages to `messages.yaml` with appropriate keys
3. **Update Code**: Replace hardcoded strings with `get_message()` calls
4. **Test**: Verify functionality works as expected

Example migration:
```python
# Before
message = "What is your reservation number?"

# After
try:
    message = get_message("cancel_flight.elicit_reservation_number")
except Exception:
    message = "What is your reservation number?"  # Fallback
```

## Troubleshooting

### Common Issues

1. **Message Not Found**: Check that the key exists in the YAML file
2. **Parameter Substitution Fails**: Verify parameter names match exactly in `template.format()`
3. **File Not Found**: Verify message files are in `lambdas/fulfillment_function/messages/`
4. **Locale Not Working**: Ensure `messages_{locale}.yaml` file exists

### Best Practices

- Always use try/except blocks with fallback messages
- Use descriptive message keys (e.g., `book_flight.elicit_origin_city`)
- Test with multiple locales during development
- Keep message files in sync across locales

## Examples

See the following files for complete examples:
- `lambdas/fulfillment_function/src/fulfillment_function/intents/book_flight.py` - get_message() usage
- `lambdas/fulfillment_function/messages/messages.yaml` - Message file structure
- `examples/features/messages/` - Standalone message management examples
