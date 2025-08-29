# Internationalization with lex_helper v0.0.18 message_manager

This document explains how to use the new `message_manager` feature in lex_helper v0.0.18 for internationalization support in the Airline-Bot project.

## Overview

The `message_manager` allows you to:
- Store all user-facing messages in YAML files
- Support multiple languages/locales
- Use parameter substitution in messages
- Automatically detect user locale from Lex requests
- Provide fallback messages for missing translations

## File Structure

```
Airline-Bot/
├── messages_en_US.yaml           # English (US) messages
├── messages_it_IT.yaml           # Italian messages
└── lambdas/fulfillment_function/
    └── intents/
        └── cancel_flight.py           # MessageManager usage example
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

### 1. Direct message_manager Usage (Recommended)

For more control, use the message_manager directly:

```python
from lex_helper import message_manager
import os

def handler(lex_request):
    # Get locale from request
    locale = getattr(lex_request, 'locale', 'en_US')
    
    # Initialize message manager
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    message_file = os.path.join(project_root, f"messages_{locale}.yaml")
    msg_manager = message_manager.MessageManager(message_file, locale)
    
    # Get message
    message = msg_manager.get_message("cancel_flight.elicit_reservation_number")
```

### 2. Advanced Usage with Configuration

For more complex scenarios, you can implement custom locale detection:

```python
from lex_helper import message_manager

def get_user_locale(lex_request):
    # Custom locale detection logic
    return getattr(lex_request, 'locale', 'en_US')

def handler(lex_request):
    locale = get_user_locale(lex_request)
    message_file = f"messages_{locale}.yaml"
    msg_manager = message_manager.MessageManager(message_file, locale)
    
    message = msg_manager.get_message(
        "cancel_flight.cancellation_success",
        reservation_number="ABC123"
    )
```

## Locale Detection

The system detects user locale from multiple sources in order of priority:

1. `lex_request.locale` attribute
2. `lex_request.bot.localeId` from bot context
3. `lex_request.sessionState.sessionAttributes.user_locale` from session
4. `lex_request.requestAttributes['locale']` from request attributes
5. Default fallback to `en_US`

## Configuration

The `message_config.yaml` file controls message manager behavior:

```yaml
default:
  locale: en_US
  fallback_locale: en_US
  
supported_locales:
  - en_US
  - it_IT
  
locale_mappings:
  "en": "en_US"      # Map generic 'en' to 'en_US'
  "it": "it_IT"      # Map generic 'it' to 'it_IT'
```

## Adding New Languages

1. **Create Message File**: Add `messages_{locale}.yaml` with all required messages
2. **Update Configuration**: Add the locale to `supported_locales` in `message_config.yaml`
3. **Add Locale Mapping**: Map any variations in `locale_mappings`
4. **Test**: Verify all message keys exist in the new language file

Example for Spanish:

```bash
# 1. Create messages_es_ES.yaml
cp messages_en_US.yaml messages_es_ES.yaml
# Edit messages_es_ES.yaml with Spanish translations

# 2. Update message_config.yaml
supported_locales:
  - en_US
  - it_IT
  - es_ES  # Add Spanish

locale_mappings:
  "es": "es_ES"  # Add mapping
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
2. **Add to YAML**: Add messages to language files with appropriate keys
3. **Update Code**: Replace hardcoded strings with `get_localized_message()` calls
4. **Test**: Verify functionality with different locales

Example migration:
```python
# Before
message = "What is your reservation number?"

# After  
message = get_localized_message(
    lex_request,
    "cancel_flight.elicit_reservation_number"
)
```

## Troubleshooting

### Common Issues

1. **Message Not Found**: Check that the key exists in the YAML file
2. **Parameter Substitution Fails**: Verify parameter names match exactly
3. **Locale Not Detected**: Check locale detection logic and fallbacks
4. **File Not Found**: Verify message file paths and naming conventions

### Debug Logging
Enable debug logging to troubleshoot:
```python
import logging
logging.getLogger('lex_helper.message_manager').setLevel(logging.DEBUG)
```

## Performance Considerations

- **Caching**: Message managers cache loaded messages
- **Initialization**: Initialize message managers once per locale
- **File Loading**: YAML files are loaded once and cached
- **Memory Usage**: Each locale requires separate message storage

## Examples

See the following file for complete example:
- `lambdas/fulfillment_function/intents/cancel_flight.py` - MessageManager usage with internationalization