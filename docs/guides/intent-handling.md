# Intent Handling

Learn how to organize and implement intent handlers effectively with lex-helper. This guide covers patterns, best practices, and advanced techniques for building robust conversational flows.

## Overview

Intent handlers are the core of your chatbot's business logic. lex-helper provides a structured approach to organizing handlers with automatic discovery, type safety, and powerful dialog management utilities.

## Handler Organization

### File Structure

lex-helper uses convention-based handler discovery. Organize your handlers in an `intents/` directory:

```
my_chatbot/
├── intents/
│   ├── __init__.py
│   ├── book_flight.py          # Handles BookFlight intent
│   ├── cancel_booking.py       # Handles CancelBooking intent
│   ├── check_status.py         # Handles CheckStatus intent
│   └── fallback_intent.py      # Handles FallbackIntent
├── session_attributes.py
└── lambda_function.py
```

### Handler Function Signature

Each intent handler must have a specific signature:

```python
from lex_helper import LexRequest, LexResponse, dialog
from ..session_attributes import ChatbotSessionAttributes

def handler(
    lex_request: LexRequest[ChatbotSessionAttributes]
) -> LexResponse[ChatbotSessionAttributes]:
    """Handle the intent and return a response."""
    # Your handler logic here
    pass
```

### Automatic Intent Mapping

lex-helper automatically maps intent names to handler files:

- `BookFlight` intent → `intents/book_flight.py`
- `CancelBooking` intent → `intents/cancel_booking.py`
- `CheckFlightStatus` intent → `intents/check_flight_status.py`

The mapping converts PascalCase intent names to snake_case file names.

## Basic Handler Patterns

### Simple Response Handler

For intents that provide information without collecting data:

```python
def handler(lex_request: LexRequest[MySessionAttributes]) -> LexResponse[MySessionAttributes]:
    """Provide flight information."""
    session_attrs = lex_request.sessionState.sessionAttributes

    # Access user context
    user_name = session_attrs.user_name or "valued customer"

    message = f"Hello {user_name}! Here's your flight information..."

    return dialog.close(
        messages=[LexPlainText(content=message)],
        lex_request=lex_request
    )
```

### Slot Collection Handler

For intents that need to collect information from users:

```python
from pydantic import BaseModel

class RequiredSlot(BaseModel):
    name: str
    prompt: str

def handler(lex_request: LexRequest[ChatbotSessionAttributes]) -> LexResponse[ChatbotSessionAttributes]:
    """Collect booking information step by step."""
    intent = lex_request.sessionState.intent
    session_attrs = lex_request.sessionState.sessionAttributes

    # Check global authentication status
    if not session_attrs.user_authenticated:
        return redirect_to_authentication(lex_request)

    # Define required information
    required_slots = [
        RequiredSlot(name="DepartureCity", prompt="Which city are you departing from?"),
        RequiredSlot(name="ArrivalCity", prompt="Where would you like to go?"),
        RequiredSlot(name="TravelDate", prompt="When would you like to travel?"),
        RequiredSlot(name="PassengerCount", prompt="How many passengers?")
    ]

    # Check each required slot
    for slot in required_slots:
        if not dialog.get_slot(slot.name, intent):
            return dialog.elicit_slot(
                slot_to_elicit=slot.name,
                messages=[LexPlainText(content=slot.prompt)],
                lex_request=lex_request
            )

    # All slots collected - process booking
    return process_booking(lex_request)

def process_booking(lex_request: LexRequest[ChatbotSessionAttributes]) -> LexResponse[ChatbotSessionAttributes]:
    """Process the booking with all required information."""
    intent = lex_request.sessionState.intent
    session_attrs = lex_request.sessionState.sessionAttributes

    # Extract slot values (don't store in session attributes - use temp storage)
    departure = dialog.get_slot("DepartureCity", intent)
    arrival = dialog.get_slot("ArrivalCity", intent)
    travel_date = dialog.get_slot("TravelDate", intent)
    passenger_count = dialog.get_slot("PassengerCount", intent)

    # Store booking data in global temp storage for other intents to access
    session_attrs.temp_data.update({
        "booking_departure": departure,
        "booking_arrival": arrival,
        "booking_date": travel_date,
        "booking_passengers": passenger_count
    })

    # Update global conversation context
    session_attrs.current_conversation_topic = "flight_booking"

    # Confirm booking details
    confirmation_message = (
        f"I'll book {passenger_count} ticket(s) from {departure} to {arrival} "
        f"on {travel_date}. Is this correct?"
    )

    return dialog.elicit_slot(
        slot_to_elicit="ConfirmBooking",
        messages=[
            LexPlainText(content=confirmation_message),
            LexImageResponseCard(
                title="Confirm Booking",
                buttons=[
                    {"text": "Yes, book it", "value": "yes"},
                    {"text": "No, let me change", "value": "no"}
                ]
            )
        ],
        lex_request=lex_request
    )
```

### State Machine Handler

For complex intents with multiple states:

```python
from enum import Enum

class BookingState(str, Enum):
    COLLECTING_INFO = "collecting_info"
    SEARCHING_FLIGHTS = "searching_flights"
    CONFIRMING_SELECTION = "confirming_selection"
    PROCESSING_PAYMENT = "processing_payment"
    COMPLETED = "completed"

def handler(lex_request: LexRequest[ChatbotSessionAttributes]) -> LexResponse[ChatbotSessionAttributes]:
    """Handle booking with state machine pattern."""
    session_attrs = lex_request.sessionState.sessionAttributes

    # Get current state from global temp storage
    current_state = session_attrs.temp_data.get('booking_state', BookingState.COLLECTING_INFO.value)

    # Route to appropriate handler based on state
    match current_state:
        case BookingState.COLLECTING_INFO.value:
            return collect_booking_info(lex_request)
        case BookingState.SEARCHING_FLIGHTS.value:
            return search_and_present_flights(lex_request)
        case BookingState.CONFIRMING_SELECTION.value:
            return confirm_flight_selection(lex_request)
        case BookingState.PROCESSING_PAYMENT.value:
            return process_payment(lex_request)
        case BookingState.COMPLETED.value:
            return booking_completed(lex_request)
        case _:
            # Reset to initial state on unknown state
            session_attrs.temp_data['booking_state'] = BookingState.COLLECTING_INFO.value
            return collect_booking_info(lex_request)

def collect_booking_info(lex_request: LexRequest[ChatbotSessionAttributes]) -> LexResponse[ChatbotSessionAttributes]:
    """Collect basic booking information."""
    # ... slot collection logic ...

    # Transition to next state when complete
    session_attrs = lex_request.sessionState.sessionAttributes
    session_attrs.temp_data['booking_state'] = BookingState.SEARCHING_FLIGHTS.value
    session_attrs.current_conversation_topic = "flight_booking"

    return search_and_present_flights(lex_request)
```

## Advanced Handler Patterns

### Validation and Error Recovery

Implement robust validation with user-friendly error messages:

```python
import re
from datetime import datetime, timedelta

def handler(lex_request: LexRequest[ChatbotSessionAttributes]) -> LexResponse[ChatbotSessionAttributes]:
    """Handle booking with validation."""
    intent = lex_request.sessionState.intent
    session_attrs = lex_request.sessionState.sessionAttributes

    # Check global authentication
    if not session_attrs.user_authenticated:
        return redirect_to_authentication(lex_request)

    # Validate travel date
    travel_date = dialog.get_slot("TravelDate", intent)
    if travel_date:
        validation_result = validate_travel_date(travel_date)
        if not validation_result.is_valid:
            # Track validation errors globally
            session_attrs.error_count += 1
            # Clear invalid slot and re-prompt
            dialog.set_slot("TravelDate", None, intent)
            return dialog.elicit_slot(
                slot_to_elicit="TravelDate",
                messages=[LexPlainText(content=validation_result.error_message)],
                lex_request=lex_request
            )

    # Validate passenger count
    passenger_count = dialog.get_slot("PassengerCount", intent)
    if passenger_count:
        validation_result = validate_passenger_count(passenger_count)
        if not validation_result.is_valid:
            session_attrs.error_count += 1
            dialog.set_slot("PassengerCount", None, intent)
            return dialog.elicit_slot(
                slot_to_elicit="PassengerCount",
                messages=[LexPlainText(content=validation_result.error_message)],
                lex_request=lex_request
            )

    # Reset error count on successful validation
    session_attrs.error_count = 0

    # Continue with normal flow
    return continue_booking_flow(lex_request)

class ValidationResult:
    def __init__(self, is_valid: bool, error_message: str = ""):
        self.is_valid = is_valid
        self.error_message = error_message

def validate_travel_date(date_str: str) -> ValidationResult:
    """Validate travel date is in the future and reasonable."""
    try:
        travel_date = datetime.fromisoformat(date_str)
        now = datetime.now()

        if travel_date < now:
            return ValidationResult(False, "Travel date cannot be in the past. When would you like to travel?")

        if travel_date > now + timedelta(days=365):
            return ValidationResult(False, "We can only book flights up to one year in advance. Please choose a closer date.")

        return ValidationResult(True)

    except ValueError:
        return ValidationResult(False, "I didn't understand that date. Please provide a date like 'March 15' or '2024-03-15'.")

def validate_passenger_count(count_str: str) -> ValidationResult:
    """Validate passenger count is reasonable."""
    try:
        count = int(count_str)

        if count < 1:
            return ValidationResult(False, "You need at least one passenger. How many people will be traveling?")

        if count > 9:
            return ValidationResult(False, "For groups larger than 9, please call our group booking line. How many passengers (1-9)?")

        return ValidationResult(True)

    except ValueError:
        return ValidationResult(False, "Please provide a number for passenger count.")
```

### Multi-Turn Conversations

Handle complex conversations that span multiple turns:

```python
def handler(lex_request: LexRequest[ChatbotSessionAttributes]) -> LexResponse[ChatbotSessionAttributes]:
    """Handle multi-turn flight modification conversation."""
    session_attrs = lex_request.sessionState.sessionAttributes
    intent = lex_request.sessionState.intent

    # Check if this is a continuation of a previous conversation
    modification_in_progress = session_attrs.temp_data.get('modification_in_progress', False)
    if modification_in_progress:
        return continue_modification_flow(lex_request)

    # Start new modification flow
    booking_reference = dialog.get_slot("BookingReference", intent)
    if not booking_reference:
        return dialog.elicit_slot(
            slot_to_elicit="BookingReference",
            messages=[LexPlainText(content="What's your booking reference number?")],
            lex_request=lex_request
        )

    # Look up booking
    booking = lookup_booking(booking_reference)
    if not booking:
        return dialog.elicit_slot(
            slot_to_elicit="BookingReference",
            messages=[LexPlainText(content="I couldn't find that booking. Please check your reference number.")],
            lex_request=lex_request
        )

    # Store booking details in session
    session_attrs.current_booking = booking
    session_attrs.modification_in_progress = True

    # Present modification options
    return present_modification_options(lex_request)

def continue_modification_flow(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    """Continue an in-progress modification."""
    session_attrs = lex_request.sessionState.sessionAttributes
    intent = lex_request.sessionState.intent

    modification_type = dialog.get_slot("ModificationType", intent)

    if modification_type == "change_date":
        return handle_date_change(lex_request)
    elif modification_type == "change_seat":
        return handle_seat_change(lex_request)
    elif modification_type == "cancel":
        return handle_cancellation(lex_request)
    else:
        return present_modification_options(lex_request)
```

### Integration with External Services

Handle external API calls and service integration:

```python
import asyncio
import aiohttp
from typing import Optional

async def search_flights_async(departure: str, arrival: str, date: str) -> list[dict]:
    """Search for flights using external API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.flights.com/search",
            params={"from": departure, "to": arrival, "date": date}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("flights", [])
            return []

def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    """Handle flight search with external API integration."""
    intent = lex_request.sessionState.intent
    session_attrs = lex_request.sessionState.sessionAttributes

    # Collect required information first
    departure = dialog.get_slot("DepartureCity", intent)
    arrival = dialog.get_slot("ArrivalCity", intent)
    travel_date = dialog.get_slot("TravelDate", intent)

    if not all([departure, arrival, travel_date]):
        return collect_missing_slots(lex_request)

    # Search for flights
    try:
        # Note: In Lambda, you'd use synchronous requests or boto3
        flights = search_flights(departure, arrival, travel_date)

        if not flights:
            return dialog.close(
                messages=[LexPlainText(content=f"Sorry, no flights found from {departure} to {arrival} on {travel_date}.")],
                lex_request=lex_request
            )

        # Store results in session
        session_attrs.available_flights = flights[:5]  # Limit to top 5

        # Present options to user
        return present_flight_options(lex_request, flights[:3])

    except Exception as e:
        logger.exception("Flight search failed")
        return dialog.close(
            messages=[LexPlainText(content="I'm having trouble searching for flights right now. Please try again later.")],
            lex_request=lex_request
        )

def search_flights(departure: str, arrival: str, date: str) -> list[dict]:
    """Synchronous flight search (for Lambda environment)."""
    import requests

    response = requests.get(
        "https://api.flights.com/search",
        params={"from": departure, "to": arrival, "date": date},
        timeout=10
    )

    if response.status_code == 200:
        return response.json().get("flights", [])
    return []
```

## Dialog Management

### Using Dialog Utilities

lex-helper provides powerful dialog management utilities:

```python
from lex_helper import dialog

def handler(lex_request: LexRequest[MySessionAttributes]) -> LexResponse[MySessionAttributes]:
    # Close the conversation
    return dialog.close(
        messages=[LexPlainText(content="Thank you! Your booking is confirmed.")],
        lex_request=lex_request
    )

    # Ask for a specific slot
    return dialog.elicit_slot(
        slot_to_elicit="DepartureCity",
        messages=[LexPlainText(content="Which city are you departing from?")],
        lex_request=lex_request
    )

    # Ask for any intent (open-ended)
    return dialog.elicit_intent(
        messages=[LexPlainText(content="How else can I help you today?")],
        lex_request=lex_request
    )

    # Let Lex handle the next step
    return dialog.delegate(lex_request)
```

### Handling Unknown Slot Choices

Handle cases where users provide invalid responses:

```python
def handler(lex_request: LexRequest[MySessionAttributes]) -> LexResponse[MySessionAttributes]:
    # Check for invalid responses to previous prompts
    if dialog.any_unknown_slot_choices(lex_request):
        return dialog.handle_any_unknown_slot_choice(lex_request)

    # Continue with normal intent logic
    return process_intent(lex_request)
```

### Intent Transitions

Transition between intents for complex workflows:

```python
def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    """Handle booking that requires authentication."""
    session_attrs = lex_request.sessionState.sessionAttributes

    # Check if user is authenticated
    if not session_attrs.user_authenticated:
        # Save current context for later
        session_attrs.callback_handler = "BookFlight"
        session_attrs.callback_event = lex_request.model_dump_json()

        # Transition to authentication
        return transition_to_intent(
            intent_name="Authenticate",
            lex_request=lex_request,
            messages=[LexPlainText(content="I need to verify your identity first.")]
        )

    # User is authenticated, continue with booking
    return continue_booking_flow(lex_request)

def transition_to_intent(
    intent_name: str,
    lex_request: LexRequest[MySessionAttributes],
    messages: list[LexPlainText]
) -> LexResponse[MySessionAttributes]:
    """Transition to a different intent."""
    # Update intent name
    lex_request.sessionState.intent.name = intent_name

    # Clear slots for new intent
    lex_request.sessionState.intent.slots = {}

    return dialog.elicit_intent(messages=messages, lex_request=lex_request)
```

## Error Handling in Handlers

### Graceful Error Recovery

Handle errors gracefully while maintaining conversation flow:

```python
def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    """Handle booking with error recovery."""
    try:
        return process_booking_request(lex_request)

    except ValidationError as e:
        # Handle validation errors with specific guidance
        return dialog.elicit_slot(
            slot_to_elicit=e.field_name,
            messages=[LexPlainText(content=f"Please provide a valid {e.field_name}: {e.message}")],
            lex_request=lex_request
        )

    except ExternalServiceError as e:
        # Handle external service failures
        session_attrs = lex_request.sessionState.sessionAttributes
        session_attrs.error_count += 1

        if session_attrs.error_count < 3:
            return dialog.elicit_intent(
                messages=[LexPlainText(content="I'm having trouble with that request. Let me try a different approach. What would you like to do?")],
                lex_request=lex_request
            )
        else:
            return dialog.close(
                messages=[LexPlainText(content="I'm experiencing technical difficulties. Please try again later or contact support.")],
                lex_request=lex_request
            )

    except Exception as e:
        # Log unexpected errors
        logger.exception("Unexpected error in booking handler")

        return dialog.close(
            messages=[LexPlainText(content="I apologize, but something went wrong. Please try again.")],
            lex_request=lex_request
        )
```

## Testing Intent Handlers

### Unit Testing

Write comprehensive unit tests for your handlers:

```python
import pytest
from unittest.mock import Mock, patch
from lex_helper import LexRequest, SessionState, Intent
from my_chatbot.intents.book_flight import handler
from my_chatbot.session_attributes import BookingSessionAttributes

def test_book_flight_collects_departure_city():
    """Test that handler asks for departure city when missing."""
    # Arrange
    session_attrs = BookingSessionAttributes()
    lex_request = LexRequest(
        sessionState=SessionState(
            intent=Intent(name="BookFlight", slots={}),
            sessionAttributes=session_attrs
        )
    )

    # Act
    response = handler(lex_request)

    # Assert
    assert response.sessionState.dialogAction.type == "ElicitSlot"
    assert response.sessionState.dialogAction.slotToElicit == "DepartureCity"
    assert "departing from" in response.messages[0].content.lower()

def test_book_flight_processes_complete_request():
    """Test that handler processes booking when all slots are provided."""
    # Arrange
    session_attrs = BookingSessionAttributes()
    lex_request = LexRequest(
        sessionState=SessionState(
            intent=Intent(
                name="BookFlight",
                slots={
                    "DepartureCity": {"value": {"interpretedValue": "New York"}},
                    "ArrivalCity": {"value": {"interpretedValue": "Los Angeles"}},
                    "TravelDate": {"value": {"interpretedValue": "2024-03-15"}},
                    "PassengerCount": {"value": {"interpretedValue": "2"}}
                }
            ),
            sessionAttributes=session_attrs
        )
    )

    # Act
    with patch('my_chatbot.intents.book_flight.search_flights') as mock_search:
        mock_search.return_value = [{"flight": "UA123", "price": 299}]
        response = handler(lex_request)

    # Assert
    assert response.sessionState.dialogAction.type == "ElicitSlot"
    assert "confirm" in response.messages[0].content.lower()
```

### Integration Testing

Test handlers with realistic Lex payloads:

```python
def test_book_flight_integration():
    """Test handler with realistic Lex payload."""
    # Load real Lex payload from file
    with open('tests/fixtures/book_flight_payload.json') as f:
        lex_payload = json.load(f)

    # Parse into LexRequest
    session_attrs = BookingSessionAttributes()
    lex_request = LexRequest(**lex_payload)
    lex_request.sessionState.sessionAttributes = session_attrs

    # Test handler
    response = handler(lex_request)

    # Validate response structure
    assert isinstance(response, LexResponse)
    assert response.sessionState
    assert response.messages
```

## Best Practices

### 1. Keep Handlers Focused

Each handler should have a single responsibility:

```python
# Good: Focused on one intent
def book_flight_handler(lex_request):
    """Handle flight booking only."""
    pass

# Avoid: Handling multiple intents
def travel_handler(lex_request):
    """Handle flights, hotels, and cars."""  # Too broad
    pass
```

### 2. Use Type Hints Consistently

```python
def handler(
    lex_request: LexRequest[BookingSessionAttributes]
) -> LexResponse[BookingSessionAttributes]:
    """Type hints provide IDE support and catch errors early."""
    pass
```

### 3. Validate Input Early

```python
def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    # Validate critical inputs first
    if not validate_user_input(lex_request):
        return handle_invalid_input(lex_request)

    # Continue with business logic
    return process_valid_request(lex_request)
```

### 4. Use Session Attributes Effectively

```python
def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    session_attrs = lex_request.sessionState.sessionAttributes

    # Track conversation state
    session_attrs.current_step = "collecting_preferences"
    session_attrs.attempts += 1

    # Store context for later use
    session_attrs.search_results = flight_results
```

### 5. Provide Clear Error Messages

```python
def handler(lex_request: LexRequest[BookingSessionAttributes]) -> LexResponse[BookingSessionAttributes]:
    try:
        return process_booking(lex_request)
    except ValidationError as e:
        # Specific, actionable error messages
        return dialog.elicit_slot(
            slot_to_elicit=e.field,
            messages=[LexPlainText(content=f"Please provide a valid {e.field}. {e.guidance}")],
            lex_request=lex_request
        )
```

## Related Topics

- **[Core Concepts](core-concepts.md)** - Understanding lex-helper architecture
- **[Session Attributes](session-attributes.md)** - Managing conversation state
- **[Channel Formatting](channel-formatting.md)** - Multi-channel response formatting
- **[Error Handling](error-handling.md)** - Robust error handling strategies
- **[API Reference](../api/core.md)** - Complete dialog utilities documentation

---

**Next**: Learn about [Error Handling](error-handling.md) strategies and patterns.
