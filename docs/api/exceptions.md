# Exceptions API

The exceptions module provides custom exception classes and error handling utilities for robust chatbot development. These exceptions help you handle various error scenarios gracefully and provide meaningful feedback to users.

## Exception Handlers

The main exception handling utilities and custom exception classes.

::: lex_helper.exceptions.handlers
    options:
      filters: ["!^_"]
      show_root_heading: false
      group_by_category: true
      show_category_heading: true
      show_signature_annotations: true
      separate_signature: true
      members_order: source

## Exception Hierarchy

The lex-helper exceptions follow a clear hierarchy for easy handling:

```
Exception
└── LexHelperError (base for all lex-helper exceptions)
    ├── IntentNotFoundError
    ├── ValidationError
    └── IntegrationError
```

## Usage Examples

### Basic Exception Handling

```python
from lex_helper.exceptions.handlers import handle_exceptions, IntentNotFoundError
from lex_helper.core.types import LexRequest

try:
    # Your intent handling code
    result = process_intent(lex_request)
except IntentNotFoundError as e:
    # Handle missing intent
    error_response = handle_exceptions(e, lex_request)
    return error_response
```

### Automatic Exception Handling

The `LexHelper` class can automatically handle exceptions when configured:

```python
from lex_helper import LexHelper, Config

config = Config(
    session_attributes=MySessionAttributes(),
    auto_handle_exceptions=True,  # Enable automatic exception handling
    error_message="Sorry, something went wrong. Please try again."
)

lex_helper = LexHelper(config)
```

### Custom Error Messages

You can provide custom error messages or message keys:

```python
# Using a custom message
config = Config(
    session_attributes=MySessionAttributes(),
    auto_handle_exceptions=True,
    error_message="We're experiencing technical difficulties. Please try again later."
)

# Using a message key (requires MessageManager)
config = Config(
    session_attributes=MySessionAttributes(),
    auto_handle_exceptions=True,
    error_message="error.technical_difficulty"  # Will be looked up in messages
)
```

### Exception Context

Exceptions include context about the request and error:

```python
try:
    # Process request
    pass
except IntentNotFoundError as e:
    logger.error(f"Intent not found: {e.intent_name}")
    logger.error(f"Available intents: {e.available_intents}")
    # Handle gracefully
```

## Error Response Format

All exception handlers return properly formatted Lex responses that:

- Maintain session state
- Include appropriate error messages
- Are formatted for the correct channel
- Preserve conversation context where possible

## Best Practices

### 1. Use Automatic Exception Handling

Enable automatic exception handling in production to ensure users always receive a response:

```python
config = Config(
    auto_handle_exceptions=True,
    error_message="I'm sorry, I encountered an error. Please try again."
)
```

### 2. Provide Meaningful Error Messages

Use clear, user-friendly error messages that help users understand what went wrong:

```python
# Good: Clear and actionable
error_message = "I couldn't find that flight. Please check the flight number and try again."

# Avoid: Technical jargon
error_message = "FlightNotFoundError: Invalid flight identifier in database query"
```

### 3. Log Errors for Debugging

Always log exceptions for debugging while showing user-friendly messages:

```python
import logging

logger = logging.getLogger(__name__)

try:
    # Process request
    pass
except Exception as e:
    logger.exception("Error processing request")  # Logs full stack trace
    # Return user-friendly response
```

### 4. Handle Specific Exceptions

Catch specific exceptions when you can provide targeted handling:

```python
try:
    # Process intent
    pass
except IntentNotFoundError:
    return "I didn't understand that. Can you try rephrasing?"
except ValidationError:
    return "Please check your input and try again."
except Exception:
    return "Something went wrong. Please try again later."
```

---

**Next**: Explore the [Examples](../examples/index.md) for practical usage patterns.