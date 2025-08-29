"""
Custom session attributes for the Airline-Bot.

This module defines the session attributes that persist across conversation turns
in the Amazon Lex bot. These attributes store user data and conversation state
to enable multi-turn conversations and context awareness.
"""
from pydantic import Field

from lex_helper import SessionAttributes


class AirlineBotSessionAttributes(SessionAttributes):
    """
    Custom session attributes for the Airline-Bot.
    
    This class extends the base SessionAttributes from lex_helper to include
    airline-specific attributes for managing flight bookings, user authentication,
    and conversation state.
    
    Attributes:
        # Common interaction attributes
        common_greeting_count: Counter for greeting interactions
        
        # Flight booking attributes
        origin_city: The departure city for flight booking
        destination_city: The arrival city for flight booking
        departure_date: The departure date for flight booking
        return_date: The return date for round-trip bookings (optional)
        number_of_passengers: Number of passengers for the booking
        trip_type: Type of trip (one-way or round-trip)
        
        # Flight management attributes
        reservation_number: Confirmation number for flight operations
        flight_number: Flight number for status inquiries
        departure_airport: Airport code for flight status updates
        
        # Authentication and callback attributes
        user_authenticated: Whether the user has been authenticated
        callback_handler: Original intent handler for post-authentication callback
        callback_event: Serialized original request for callback processing
        
        # Error handling attributes
        error_count: Count of consecutive errors for unknown slot choices
    """

    # Common interaction attributes
    common_greeting_count: int = Field(
        default=0,
        description="Counter for greeting interactions"
    )

    # Flight booking attributes
    origin_city: str = Field(
        default="",
        description="The departure city for flight booking"
    )
    destination_city: str = Field(
        default="",
        description="The arrival city for flight booking"
    )
    departure_date: str = Field(
        default="",
        description="The departure date for flight booking"
    )
    return_date: str = Field(
        default="",
        description="The return date for round-trip bookings (optional)"
    )
    number_of_passengers: int = Field(
        default=1,
        description="Number of passengers for the booking"
    )
    trip_type: str = Field(
        default="one-way",
        description="Type of trip (one-way or round-trip)"
    )

    # Flight management attributes
    reservation_number: str = Field(
        default="",
        description="Confirmation number for flight operations"
    )
    flight_number: str = Field(
        default="",
        description="Flight number for status inquiries"
    )
    departure_airport: str = Field(
        default="",
        description="Airport code for flight status updates"
    )

    # Authentication and callback attributes
    user_authenticated: bool = Field(
        default=False,
        description="Whether the user has been authenticated"
    )
    callback_handler: str = Field(
        default="",
        description="Original intent handler for post-authentication callback"
    )
    callback_event: str = Field(
        default="",
        description="Serialized original request for callback processing"
    )

    # Error handling attributes
    error_count: int = Field(
        default=0,
        description="Count of consecutive errors for unknown slot choices"
    )

    # IATA airport code attributes
    origin_iata_code: str = Field(
        default="",
        description="IATA airport code for origin city"
    )
    destination_iata_code: str = Field(
        default="",
        description="IATA airport code for destination city"
    )

    # Internationalization attributes
    user_locale: str = Field(
        default="en_US",
        description="User's preferred locale for messages"
    )
