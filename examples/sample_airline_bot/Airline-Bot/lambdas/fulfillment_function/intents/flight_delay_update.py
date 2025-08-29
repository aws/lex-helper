"""
Handler for the FlightDelayUpdate intent.

This intent provides flight delay information by collecting the flight number
and departure airport, then returning mock delay data. In production, this would
integrate with real flight tracking APIs.
"""
from loguru import logger

from lex_helper import LexPlainText, LexRequest, LexResponse, dialog, get_message

from ..session_attributes import AirlineBotSessionAttributes


def handler(lex_request: LexRequest[AirlineBotSessionAttributes]) -> LexResponse[AirlineBotSessionAttributes]:
    """
    Handle the FlightDelayUpdate intent.
    
    This intent collects flight number and departure airport information,
    then provides delay status. In a production environment, this would
    integrate with airline APIs or flight tracking services.
    
    Args:
        lex_request: The Lex request containing user input and session state
        
    Returns:
        LexResponse: The response to send back to Amazon Lex
    """
    logger.debug("FlightDelayUpdate intent handler called")

    # Get current slot values
    intent = dialog.get_intent(lex_request)
    flight_number = dialog.get_slot(intent, "FlightNumber") or ""
    departure_airport = dialog.get_slot(intent, "DepartureAirport") or ""

    logger.debug(f"Current slot values: flight_number={flight_number}, departure_airport={departure_airport}")

    # Store values in session attributes for potential future use
    session_attrs = lex_request.sessionState.sessionAttributes
    session_attrs.flight_number = flight_number
    session_attrs.departure_airport = departure_airport

    # Elicit missing required slots
    if not flight_number:
        message = "What is your flight number? For example, 'AA123' or 'DL456'."
        try:
            message = get_message("flight_delay.elicit_flight_number")
        except Exception as e:
            logger.warning(f"Failed to get localized message: {e}")
        logger.debug(f"Eliciting FlightNumber slot: {message}")
        return dialog.elicit_slot(
            slot_to_elicit="FlightNumber",
            messages=[LexPlainText(content=message)],
            lex_request=lex_request
        )

    if not departure_airport:
        message = "What is your departure airport? Please provide the airport code like 'JFK', 'LAX', or 'ORD'."
        try:
            message = get_message("flight_delay.elicit_departure_airport")
        except Exception as e:
            logger.warning(f"Failed to get localized message: {e}")
        logger.debug(f"Eliciting DepartureAirport slot: {message}")
        return dialog.elicit_slot(
            slot_to_elicit="DepartureAirport",
            messages=[LexPlainText(content=message)],
            lex_request=lex_request
        )

    # All required information collected - provide delay information
    # In production, integrate with flight tracking APIs here
    delay_minutes = 30  # Mock delay for demonstration

    message = f"Flight {flight_number} departing from {departure_airport} is currently delayed by {delay_minutes} minutes. Please check your airline's app or website for the most up-to-date information."
    try:
        template = get_message("flight_delay.delay_info")
        message = template.format(flight_number=flight_number, departure_airport=departure_airport, delay_minutes=delay_minutes)
    except Exception as e:
        logger.warning(f"Failed to get localized message: {e}")

    logger.debug(f"Providing delay information: {message}")

    # Close the dialog with the delay information
    return dialog.close(
        messages=[LexPlainText(content=message)],
        lex_request=lex_request
    )
