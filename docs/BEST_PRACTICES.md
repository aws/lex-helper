# Lex Helper Library - Best Practices Guide

This guide covers detailed usage patterns and best practices for the Lex Helper library. For basic installation and setup, see [README.md](../README.md).

## Environment Variables

The following environment variables can be configured in your Lambda function:

### MessageManager
- **MESSAGES_YAML_PATH**: Custom path to messages YAML file directory
  ```bash
  MESSAGES_YAML_PATH=/opt/lambda/config/messages.yaml
  ```

### AWS Services
- **AWS_REGION**: AWS region for services (defaults to `us-east-1`)
- **AWS_DEFAULT_REGION**: Alternative AWS region setting

### Python/Lambda
- **PYTHONPATH**: Additional Python module search paths
- **LOG_LEVEL**: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)

### Example Lambda Environment Configuration
```bash
# In AWS Lambda Console or CloudFormation
MESSAGES_YAML_PATH=/opt/lambda/messages/
AWS_REGION=us-west-2
LOG_LEVEL=INFO
```

## Message Management

### Setting Up Localized Messages

Create locale-specific message files in your Lambda function:

```
your_lambda/
├── messages_en_US.yaml
├── messages_es_ES.yaml
├── messages_fr_FR.yaml
└── messages.yaml  # fallback
```

### Using MessageManager

```python
from lex_helper import set_locale, get_message

def lambda_handler(event, context):
    # Set locale from Lex event
    locale_id = event.get('bot', {}).get('localeId', 'en_US')
    set_locale(locale_id)
    
    # Get localized messages
    greeting = get_message("greeting")
    error_msg = get_message("error.general", "Something went wrong")
    
    # Override locale for specific message
    spanish_greeting = get_message("greeting", locale="es_ES")
```

### Message File Structure

```yaml
# messages_en_US.yaml
greeting: "Hello! How can I assist you today?"
agent:
  confirmation: "I understand you'd like to chat with an agent..."
  transfer: "Connecting you to an agent now."
error:
  general: "I apologize, but I encountered an error."
  validation: "Please provide valid information."
```

```yaml
# messages_es_ES.yaml
greeting: "¡Hola! ¿Cómo puedo ayudarte hoy?"
agent:
  confirmation: "Entiendo que te gustaría hablar con un agente..."
  transfer: "Te estoy conectando con un agente ahora."
error:
  general: "Me disculpo, pero encontré un error."
  validation: "Por favor proporciona información válida."
```

## Using Dialog Utilities

Import required functions from the dialog module:

```python
from lex_helper import dialog, LexPlainText, get_message

def handle_welcome_intent(lex_request):
    # Set locale from Lex request
    set_locale(lex_request.bot.localeId)
    
    # Check for unknown slot choices first
    if dialog.any_unknown_slot_choices(lex_request):
        return dialog.handle_any_unknown_slot_choice(lex_request)
    
    # Get slot values
    user_name = dialog.get_slot("user_name", dialog.get_intent(lex_request))
    
    if not user_name:
        prompt_message = get_message("prompts.name", "What's your name?")
        return dialog.elicit_slot(
            slot_to_elicit="user_name",
            messages=[LexPlainText(content=prompt_message)],
            lex_request=lex_request
        )
    
    # Set slot values with localized greeting
    greeting_template = get_message("greeting.personalized", "Hello {name}!")
    greeting = greeting_template.format(name=user_name)
    dialog.set_slot("user_greeting", greeting, dialog.get_intent(lex_request))
    return dialog.delegate(lex_request)
```

## Intent Organization

Structure your intents in an `intents/` directory:

```
your_project/
├── intents/
│   ├── __init__.py
│   ├── welcome_intent.py
│   ├── booking_intent.py
│   └── fallback_intent.py
├── session_attributes.py
└── handler.py
```

Each intent file should contain a handler function matching the intent name.

## Working with Messages

### Loading Messages from JSON
```python
from lex_helper.core.dialog import load_messages

messages_json = '[{"contentType": "PlainText", "content": "Hello!"}]'
messages = load_messages(messages_json)
```

### Creating Messages
```python
from lex_helper import LexPlainText, LexImageResponseCard

# Plain text message
text_msg = LexPlainText(content="How can I help you?")

# Image response card with buttons
card_msg = LexImageResponseCard(
    imageResponseCard={
        "title": "Choose an option",
        "buttons": [
            {"text": "Option A", "value": "A"},
            {"text": "Option B", "value": "B"}
        ]
    }
)
```

## Error Handling and Unknown Choices

Handle invalid user responses:

```python
def handle_booking_intent(lex_request):
    # Always check for unknown choices first
    if dialog.any_unknown_slot_choices(lex_request):
        return dialog.handle_any_unknown_slot_choice(lex_request)
    
    # Your intent logic here
    return dialog.delegate(lex_request)
```

## Intent Transitions

### Basic Transition
```python
return dialog.transition_to_intent(
    intent_name="authenticate",
    lex_request=lex_request,
    messages=[LexPlainText(content="Please authenticate first")]
)
```

### Callback Pattern
```python
# Set up callback before transitioning
lex_request.sessionState.sessionAttributes.callback_handler = lex_request.sessionState.intent.name
lex_request.sessionState.sessionAttributes.callback_event = json.dumps(lex_request, default=str)

# Transition to authentication
return dialog.transition_to_intent(
    intent_name="authenticate",
    lex_request=lex_request,
    messages=[LexPlainText(content="Authentication required")]
)

# In the authentication intent, return to original:
return dialog.callback_original_intent_handler(lex_request)
```

## Best Practices

### Code Organization
- Keep intent handlers focused on business logic
- Use one file per intent in the `intents/` directory
- Implement custom session attributes for type safety

### Error Handling
- Always check for unknown slot choices at the start of intent handlers
- Implement comprehensive error handling with try-catch blocks
- Use the provided dialog utilities for consistent responses

### Type Safety
- Use type hints consistently throughout your code
- Define custom session attributes with Pydantic models
- Leverage IDE autocomplete with proper typing

### Testing
- Test your bot across different channels (SMS, web, voice)
- Validate slot elicitation and dialog flows
- Test error scenarios and fallback behaviors

### Performance
- Use the delegate function when Lex can handle the dialog
- Minimize session attribute size for better performance
- Cache frequently accessed data appropriately

## Advanced Usage

### Custom Unknown Choice Handling
```python
def custom_unknown_choice_handler(lex_request, choice):
    error_count = getattr(lex_request.sessionState.sessionAttributes, 'error_count', 0)
    
    if error_count > 2:
        return dialog.transition_to_intent("human_agent", lex_request, 
                                         [LexPlainText(content="Let me connect you to an agent")])
    
    return dialog.elicit_slot("destination", 
                            [LexPlainText(content="Please choose A, B, or C")], 
                            lex_request)
```

### Context Management
```python
# Remove specific contexts
contexts = dialog.remove_context(lex_request.sessionState.activeContexts, "unwanted_context")

# Get active contexts
active_contexts = dialog.get_active_contexts(lex_request)
```

## Examples and References

- **Basic Example**: See `examples/basic_handler/` for a simple implementation
- **Comprehensive Example**: Check out the [Airline-Bot](https://gitlab.aws.dev/lex/Airline-Bot) for production-ready patterns including:
  - Advanced intent organization and management
  - Complex session attribute handling
  - Multi-turn conversation flows
  - Error handling and fallback strategies
  - Best practices for bot architecture
  - Production deployment patterns

## Common Patterns

### Slot Validation
```python
def validate_email_slot(lex_request):
    email = dialog.get_slot("email", dialog.get_intent(lex_request))
    if email and "@" not in email:
        return dialog.elicit_slot("email", 
                                [LexPlainText(content="Please enter a valid email")], 
                                lex_request)
    return dialog.delegate(lex_request)
```

### Session State Management
```python
def track_conversation_state(lex_request):
    session_attrs = lex_request.sessionState.sessionAttributes
    session_attrs.visit_count += 1
    session_attrs.last_intent = lex_request.sessionState.intent.name
```

Remember to consult the library documentation and example implementations for detailed information on each utility function and advanced usage scenarios.