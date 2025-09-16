# Error Handling

Implement robust error handling and recovery strategies in your lex-helper chatbots. This guide covers exception patterns, graceful degradation, and maintaining excellent user experience even when things go wrong.

## Overview

Error handling in conversational AI is critical for user experience. Users should never see technical error messages or be left confused when something goes wrong. lex-helper provides comprehensive error handling capabilities that help you build resilient chatbots.

## Exception Hierarchy

### Built-in Exception Types

lex-helper defines a hierarchy of exceptions for different error scenarios:

```python
from lex_helper.exceptions import (
    LexError,           # Base exception
    IntentNotFoundError,  # Intent handler not found
    ValidationError,      # Input validation failed
    SessionError         # Session state issues
)

# Base exception with error codes
class LexError(Exception):
    def __init__(self, message: str, error_code: str | None = None):
        super().__init__(message)
        self.error_code = error_code

# Specific exception types
class IntentNotFoundError(LexError):
    """Raised when an intent handler cannot be found."""
    pass

class ValidationError(LexError):
    """Raised when input validation fails."""
    pass

class SessionError(LexError):
    """Raised when there's an issue with the session state."""
    pass
```

### Custom Exception Types

Create domain-specific exceptions for your chatbot:

```python
from lex_helper.exceptions import LexError

class BookingError(LexError):
    """Base class for booking-related errors."""
    pass

class FlightNotFoundError(BookingError):
    """Raised when requested flight is not available."""
    pass

class PaymentError(BookingError):
    """Raised when payment processing fails."""
    pass

class ExternalServiceError(LexError):
    """Raised when external API calls fail."""
    def __init__(self, service_name: str, message: str, status_code: int = None):
        super().__init__(f"{service_name} error: {message}")
        self.service_name = service_name
        self.status_code = status_code
```

## Automatic Error Handling

### Configuration

Enable automatic error handling in your LexHelper configuration:

```python
from lex_helper import LexHelper, Config

config = Config(
    session_attributes=MySessionAttributes(),
    auto_handle_exceptions=True,  # Enable automatic error handling
    error_message="I'm sorry, something went wrong. Please try again."
)

lex_helper = LexHelper(config)
```

### How Automatic Handling Works

When enabled, lex-helper automatically:

1. **Catches all exceptions** in your intent handlers
2. **Logs the error** for debugging
3. **Preserves session state** so users don't lose context
4. **Returns user-friendly messages** instead of technical errors
5. **Maintains conversation flow** by closing gracefully

```python
def handler(lex_request: LexRequest[MySessionAttributes]) -> LexResponse[MySessionAttributes]:
    # This will be automatically caught if it fails
    result = external_api_call()

    # If an exception occurs, user sees the configured error_message
    # instead of a technical stack trace
    return process_result(result)
```

### Custom Error Messages

Provide specific error messages or use message keys for internationalization:

```python
# Direct error message
config = Config(
    auto_handle_exceptions=True,
    error_message="We're experiencing technical difficulties. Please try again in a few minutes."
)

# Message key (requires MessageManager)
config = Config(
    auto_handle_exceptions=True,
    error_message="error.technical_difficulty"  # Looks up localized message
)
```

## Manual Error Handling

### Using handle_exceptions

For more control, use the `handle_exceptions` function directly:

```python
from lex_helper.exceptions import handle_exceptions

def handler(lex_request: LexRequest[MySessionAttributes]) -> LexResponse[MySessionAttributes]:
    try:
        return process_booking_request(lex_request)

    except FlightNotFoundError as e:
        # Handle specific error with custom message
        return handle_exceptions(
            e,
            lex_request,
            error_message="I couldn't find flights for those dates. Let's try different dates."
        )

    except PaymentError as e:
        # Handle payment errors differently
        return handle_exceptions(
            e,
            lex_request,
            error_message="There was an issue processing your payment. Please check your payment method."
        )

    except Exception as e:
        # Catch-all for unexpected errors
        return handle_exceptions(e, lex_request)
```

### Exception-Specific Messages

The `handle_exceptions` function provides default messages for different exception types:

```python
# These exceptions get specific default messages:
IntentNotFoundError → "I'm not sure how to handle that request."
ValidationError → "Invalid input provided." (or the exception message)
SessionError → "There was an issue with your session. Please start over."
ValueError → "Invalid value provided."

# Other exceptions get a generic message
Exception → "I'm sorry, I encountered an error while processing your request."
```

## Error Recovery Patterns

### Retry with Backoff

Implement retry logic for transient failures:

```python
import time
from typing import Optional

def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    session_attrs = lex_request.sessionState.sessionAttributes

    # Track retry attempts
    retry_count = getattr(session_attrs, 'api_retry_count', 0)

    try:
        result = call_external_api()

        # Reset retry count on success
        session_attrs.api_retry_count = 0
        return process_successful_result(result, lex_request)

    except ExternalServiceError as e:
        if retry_count < 3:
            # Increment retry count and try again
            session_attrs.api_retry_count = retry_count + 1

            # Exponential backoff
            time.sleep(2 ** retry_count)

            return dialog.elicit_intent(
                messages=[LexPlainText(content="Let me try that again...")],
                lex_request=lex_request
            )
        else:
            # Max retries reached
            session_attrs.api_retry_count = 0
            return handle_exceptions(
                e,
                lex_request,
                error_message="I'm having trouble connecting to our booking system. Please try again later."
            )
```

### Graceful Degradation

Provide alternative functionality when primary features fail:

```python
def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    try:
        # Try primary booking flow
        return book_flight_online(lex_request)

    except ExternalServiceError:
        # Fall back to offline booking
        return offer_offline_booking(lex_request)

def offer_offline_booking(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    """Offer alternative when online booking fails."""
    session_attrs = lex_request.sessionState.sessionAttributes

    # Store user's request for later processing
    session_attrs.offline_booking_request = {
        "departure": session_attrs.departure_city,
        "arrival": session_attrs.arrival_city,
        "date": session_attrs.travel_date
    }

    return dialog.close(
        messages=[
            LexPlainText(
                content="Our booking system is temporarily unavailable. "
                       "I've saved your request and our team will contact you within 2 hours to complete your booking."
            )
        ],
        lex_request=lex_request
    )
```

### Context Preservation

Maintain conversation context even when errors occur:

```python
def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    session_attrs = lex_request.sessionState.sessionAttributes

    try:
        return process_payment(lex_request)

    except PaymentError as e:
        # Preserve booking details even when payment fails
        session_attrs.payment_failed = True
        session_attrs.payment_error_reason = str(e)

        # Offer alternative payment methods
        return dialog.elicit_slot(
            slot_to_elicit="PaymentMethod",
            messages=[
                LexPlainText(content="That payment method didn't work. Would you like to try a different card?"),
                LexImageResponseCard(
                    title="Payment Options",
                    buttons=[
                        {"text": "Try Different Card", "value": "different_card"},
                        {"text": "PayPal", "value": "paypal"},
                        {"text": "Call to Pay", "value": "phone_payment"}
                    ]
                )
            ],
            lex_request=lex_request
        )
```

## Validation Error Handling

### Input Validation

Validate user input and provide helpful feedback:

```python
import re
from datetime import datetime, timedelta

def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format."""
    if not email:
        return False, "Please provide an email address."

    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return False, "Please provide a valid email address like user@example.com."

    return True, ""

def validate_travel_date(date_str: str) -> tuple[bool, str]:
    """Validate travel date."""
    try:
        travel_date = datetime.fromisoformat(date_str)
        now = datetime.now()

        if travel_date < now:
            return False, "Travel date cannot be in the past. When would you like to travel?"

        if travel_date > now + timedelta(days=365):
            return False, "We can only book flights up to one year in advance."

        return True, ""

    except ValueError:
        return False, "I didn't understand that date. Please use a format like 'March 15' or '2024-03-15'."

def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    intent = lex_request.sessionState.intent

    # Validate email if provided
    email = dialog.get_slot("Email", intent)
    if email:
        is_valid, error_message = validate_email(email)
        if not is_valid:
            # Clear invalid slot and re-prompt
            dialog.set_slot("Email", None, intent)
            return dialog.elicit_slot(
                slot_to_elicit="Email",
                messages=[LexPlainText(content=error_message)],
                lex_request=lex_request
            )

    # Continue with valid input
    return process_booking(lex_request)
```

### Session Attribute Validation

Handle Pydantic validation errors gracefully:

```python
from pydantic import ValidationError

def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    try:
        session_attrs = lex_request.sessionState.sessionAttributes

        # This might trigger Pydantic validation
        session_attrs.passenger_count = int(user_input)
        session_attrs.email = user_email

        return continue_booking_flow(lex_request)

    except ValidationError as e:
        # Convert Pydantic errors to user-friendly messages
        error_messages = []
        for error in e.errors():
            field = error['loc'][0] if error['loc'] else 'input'
            message = error['msg']

            # Customize messages for better UX
            if 'email' in field.lower():
                error_messages.append("Please provide a valid email address.")
            elif 'passenger_count' in field.lower():
                error_messages.append("Passenger count must be between 1 and 9.")
            else:
                error_messages.append(f"{field}: {message}")

        return dialog.elicit_intent(
            messages=[LexPlainText(content=f"Please correct: {', '.join(error_messages)}")],
            lex_request=lex_request
        )
```

## Logging and Monitoring

### Structured Logging

Implement comprehensive logging for error tracking:

```python
import logging
import json
from datetime import datetime

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    session_id = lex_request.sessionId
    intent_name = lex_request.sessionState.intent.name

    try:
        logger.info(
            "Processing intent",
            extra={
                "session_id": session_id,
                "intent": intent_name,
                "user_input": lex_request.inputTranscript
            }
        )

        result = process_booking_request(lex_request)

        logger.info(
            "Intent processed successfully",
            extra={
                "session_id": session_id,
                "intent": intent_name,
                "response_type": result.sessionState.dialogAction.type
            }
        )

        return result

    except Exception as e:
        logger.error(
            "Intent processing failed",
            extra={
                "session_id": session_id,
                "intent": intent_name,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "user_input": lex_request.inputTranscript
            },
            exc_info=True
        )

        return handle_exceptions(e, lex_request)
```

### Error Metrics

Track error rates and patterns:

```python
import boto3
from datetime import datetime

cloudwatch = boto3.client('cloudwatch')

def log_error_metric(error_type: str, intent_name: str):
    """Log error metrics to CloudWatch."""
    try:
        cloudwatch.put_metric_data(
            Namespace='Chatbot/Errors',
            MetricData=[
                {
                    'MetricName': 'ErrorCount',
                    'Dimensions': [
                        {'Name': 'ErrorType', 'Value': error_type},
                        {'Name': 'Intent', 'Value': intent_name}
                    ],
                    'Value': 1,
                    'Unit': 'Count',
                    'Timestamp': datetime.utcnow()
                }
            ]
        )
    except Exception:
        # Don't let metric logging break the main flow
        logger.exception("Failed to log error metric")

def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    intent_name = lex_request.sessionState.intent.name

    try:
        return process_booking_request(lex_request)

    except ValidationError as e:
        log_error_metric("ValidationError", intent_name)
        return handle_exceptions(e, lex_request)

    except ExternalServiceError as e:
        log_error_metric("ExternalServiceError", intent_name)
        return handle_exceptions(e, lex_request)

    except Exception as e:
        log_error_metric("UnexpectedError", intent_name)
        return handle_exceptions(e, lex_request)
```

## Testing Error Scenarios

### Unit Testing Error Handling

Test your error handling logic thoroughly:

```python
import pytest
from unittest.mock import Mock, patch
from lex_helper.exceptions import ValidationError, ExternalServiceError

def test_handler_validates_email():
    """Test that handler validates email input."""
    # Arrange
    lex_request = create_test_request(slots={"Email": {"value": {"interpretedValue": "invalid-email"}}})

    # Act
    response = handler(lex_request)

    # Assert
    assert response.sessionState.dialogAction.type == "ElicitSlot"
    assert response.sessionState.dialogAction.slotToElicit == "Email"
    assert "valid email" in response.messages[0].content.lower()

def test_handler_retries_on_service_error():
    """Test that handler retries on external service errors."""
    # Arrange
    lex_request = create_test_request()

    with patch('my_chatbot.intents.book_flight.call_external_api') as mock_api:
        # First call fails, second succeeds
        mock_api.side_effect = [ExternalServiceError("API", "Timeout"), {"success": True}]

        # Act
        response = handler(lex_request)

        # Assert
        assert mock_api.call_count == 2
        assert response.sessionState.dialogAction.type == "Close"

def test_handler_handles_max_retries():
    """Test that handler gives up after max retries."""
    # Arrange
    lex_request = create_test_request()
    lex_request.sessionState.sessionAttributes.api_retry_count = 3

    with patch('my_chatbot.intents.book_flight.call_external_api') as mock_api:
        mock_api.side_effect = ExternalServiceError("API", "Persistent failure")

        # Act
        response = handler(lex_request)

        # Assert
        assert "try again later" in response.messages[0].content.lower()
        assert response.sessionState.sessionAttributes.api_retry_count == 0
```

### Integration Testing

Test error scenarios with realistic conditions:

```python
def test_error_handling_integration():
    """Test error handling with full request flow."""
    # Create realistic error scenario
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout()

        # Process request
        event = load_test_event('book_flight_complete.json')
        response = lambda_handler(event, {})

        # Verify graceful error handling
        assert response['sessionState']['dialogAction']['type'] == 'Close'
        assert 'try again' in response['messages'][0]['content']
```

## Best Practices

### 1. Fail Gracefully

Always provide a path forward for users:

```python
def handler(lex_request: LexRequest[MySessionAttributes]) -> LexResponse[MySessionAttributes]:
    try:
        return process_primary_flow(lex_request)
    except Exception:
        # Always provide an alternative
        return offer_alternative_or_escalation(lex_request)
```

### 2. Preserve User Context

Don't lose user progress when errors occur:

```python
def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    session_attrs = lex_request.sessionState.sessionAttributes

    try:
        return complete_booking(lex_request)
    except PaymentError:
        # Keep booking details, just retry payment
        session_attrs.booking_ready = True
        return retry_payment_flow(lex_request)
```

### 3. Use Specific Error Messages

Provide actionable guidance in error messages:

```python
# Good: Specific and actionable
"Please provide a valid email address like user@example.com"

# Avoid: Vague and unhelpful
"Invalid input"
```

### 4. Log Errors Appropriately

Log enough information for debugging without exposing sensitive data:

```python
logger.error(
    "Booking failed",
    extra={
        "session_id": lex_request.sessionId,
        "intent": intent_name,
        "error_type": type(e).__name__,
        # Don't log sensitive data like credit card numbers
        "booking_details": {
            "departure": session_attrs.departure_city,
            "arrival": session_attrs.arrival_city
        }
    }
)
```

### 5. Test Error Scenarios

Include error scenarios in your test suite:

```python
def test_all_error_paths():
    """Test various error conditions."""
    test_cases = [
        (ValidationError("Invalid email"), "valid email"),
        (ExternalServiceError("API", "Timeout"), "try again"),
        (PaymentError("Card declined"), "payment method")
    ]

    for error, expected_message in test_cases:
        with patch('handler.process_request', side_effect=error):
            response = handler(create_test_request())
            assert expected_message in response.messages[0].content.lower()
```

## Advanced Error Handling

### Circuit Breaker Pattern

Prevent cascading failures with circuit breakers:

```python
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise ExternalServiceError("Circuit breaker", "Service unavailable")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)
        )

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
flight_api_circuit = CircuitBreaker(failure_threshold=3, timeout=30)

def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    try:
        flights = flight_api_circuit.call(search_flights, departure, arrival, date)
        return present_flight_options(flights, lex_request)

    except ExternalServiceError:
        return offer_callback_booking(lex_request)
```

### Error Recovery Workflows

Implement sophisticated error recovery:

```python
def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    session_attrs = lex_request.sessionState.sessionAttributes

    # Check if we're in error recovery mode
    if session_attrs.error_recovery_active:
        return handle_error_recovery(lex_request)

    try:
        return normal_booking_flow(lex_request)

    except Exception as e:
        # Enter error recovery mode
        session_attrs.error_recovery_active = True
        session_attrs.original_error = str(e)
        session_attrs.recovery_options = determine_recovery_options(e)

        return present_recovery_options(lex_request)

def handle_error_recovery(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    """Handle user's choice of recovery option."""
    session_attrs = lex_request.sessionState.sessionAttributes
    intent = lex_request.sessionState.intent

    recovery_choice = dialog.get_slot("RecoveryChoice", intent)

    if recovery_choice == "retry":
        # Clear error state and retry
        session_attrs.error_recovery_active = False
        return normal_booking_flow(lex_request)

    elif recovery_choice == "alternative":
        # Offer alternative booking method
        return offer_phone_booking(lex_request)

    elif recovery_choice == "later":
        # Save progress and exit gracefully
        return save_progress_and_exit(lex_request)
```

## Related Topics

- **[Core Concepts](core-concepts.md)** - Understanding lex-helper architecture
- **[Session Attributes](session-attributes.md)** - Managing conversation state safely
- **[Intent Handling](intent-handling.md)** - Implementing robust intent handlers
- **[API Reference](../api/exceptions.md)** - Complete exception handling API
- **[Advanced Topics](../advanced/troubleshooting.md)** - Advanced debugging techniques

---

**Next**: Explore [Smart Disambiguation](smart-disambiguation.md) for AI-powered intent resolution.
