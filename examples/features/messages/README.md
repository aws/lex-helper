# Message Manager Example

This example demonstrates localized message management with the lex-helper library.

## Features

- **Localized Messages**: Support for multiple languages
- **YAML Configuration**: Easy message management
- **Automatic Fallback**: Falls back to default locale if specific locale not found
- **Template Support**: Message templates with variable substitution

## Files

- `message_manager_example.py`: Example usage of MessageManager
- `messages.yaml`: Default English messages
- `messages_es_ES.yaml`: Spanish (Spain) messages

## Usage

```python
from lex_helper import MessageManager, get_message, set_locale

# Set locale
set_locale("es_ES")

# Get localized message
message = get_message("greeting")

# Message with variables
message = get_message("welcome", name="John")
```

## Message File Format

```yaml
greeting: "Hello!"
welcome: "Welcome, {name}!"
error:
  not_found: "Item not found"
```

## Running the Example

```bash
python message_manager_example.py
```

## Supported Locales

- `en_US` (default): English (United States)
- `es_ES`: Spanish (Spain)
- Add more by creating `messages_{locale}.yaml` files