# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Handler for the BookFlight intent.

This intent handles comprehensive flight booking requests with sophisticated airport resolution.
It collects trip type, origin/destination cities with IATA airport code resolution,
departure/return dates, and passenger count before processing the booking.

Key Features:
- Authentication flow integration with callback support
- Dual-slot approach: city names + specific airport codes (Origin_Airport_Code, Destination_Airport_Code)
- Bedrock-powered city-to-IATA resolution using invoke_bedrock_converse
- Multi-airport city support (e.g., Paris: CDG/ORY, London: LHR/LGW/STN/LTN)
- Localized messaging with get_message() fallbacks
- Comprehensive error handling and validation
"""

import logging

logger = logging.getLogger(__name__)

from lex_helper import LexPlainText, LexRequest, LexResponse, dialog, get_message

from ..session_attributes import AirlineBotSessionAttributes
from ..utils.enums import InvocationSource
from ..utils.reservation_utils import ReservationUtils


def handle_dialog_hook(lex_request: LexRequest[AirlineBotSessionAttributes]) -> LexResponse[AirlineBotSessionAttributes]:
    """Handle the dialog code hook for the BookFlight intent."""
    logger.debug("BookFlight dialog code hook called")

    # Authentication check - redirect to Authenticate intent if needed
    if not lex_request.sessionState.sessionAttributes.user_authenticated:
        logger.debug("User not authenticated, redirecting to Authenticate intent")

        # Store callback information for returning after authentication
        lex_request.sessionState.sessionAttributes.callback_handler = lex_request.sessionState.intent.name
        lex_request.sessionState.sessionAttributes.callback_event = lex_request.model_dump_json()

        message = "Before I can help with booking a flight, you will need to authenticate."
        try:
            message = get_message("book_flight.authentication_required")
        except Exception as e:
            logger.warning("Failed to get localized message: %s", e)
        return dialog.transition_to_intent(
            intent_name="Authenticate", lex_request=lex_request, messages=[LexPlainText(content=message)]
        )

    # Get current slot values
    intent = dialog.get_intent(lex_request)
    trip_type = dialog.get_slot(intent=intent, slot_name="TripType")
    origin_city = dialog.get_slot(intent=intent, slot_name="OriginCity")
    destination_city = dialog.get_slot(intent=intent, slot_name="DestinationCity")
    departure_date = dialog.get_slot(intent=intent, slot_name="DepartureDate")
    return_date = dialog.get_slot(intent=intent, slot_name="ReturnDate")
    number_of_passengers = dialog.get_slot(intent=intent, slot_name="NumberOfPassengers")
    origin_airport_code = dialog.get_slot(intent=intent, slot_name="Origin_Airport_Code")
    destination_airport_code = dialog.get_slot(intent=intent, slot_name="Destination_Airport_Code")

    # Handle origin airport code selection
    if origin_airport_code:
        if not origin_city:
            return ReservationUtils.handle_city_resolution(
                origin_airport_code, "Origin_Airport_Code", "OriginCity", "origin_city", lex_request
            )

        lex_request.sessionState.sessionAttributes.origin_iata_code = ReservationUtils.parse_airport_code(
            origin_airport_code
        )

    # Handle destination airport code selection
    if destination_airport_code:
        if not destination_city:
            return ReservationUtils.handle_city_resolution(
                destination_airport_code, "Destination_Airport_Code", "DestinationCity", "destination_city", lex_request
            )
        lex_request.sessionState.sessionAttributes.destination_iata_code = ReservationUtils.parse_airport_code(
            destination_airport_code
        )

    logger.debug(
        "Current slot values: trip_type=%s, origin_city=%s, destination_city=%s, departure_date=%s, return_date=%s, number_of_passengers=%s",
        trip_type,
        origin_city,
        destination_city,
        departure_date,
        return_date,
        number_of_passengers,
    )

    # Elicit missing required slots in order of priority
    if not trip_type:
        message = "Is this a one-way or round trip?"
        try:
            message = get_message("book_flight.elicit_trip_type")
        except Exception as e:
            logger.warning("Failed to get localized message: %s", e)
        logger.debug("Eliciting TripType slot: %s", message)
        return dialog.elicit_slot(
            slot_to_elicit="TripType", messages=[LexPlainText(content=message)], lex_request=lex_request
        )

    if not origin_city:
        message = "From which city would you like to depart?"
        try:
            message = get_message("book_flight.elicit_origin_city")
        except Exception as e:
            logger.warning("Failed to get localized message: %s", e)
        logger.debug("Eliciting OriginCity slot: %s", message)
        return dialog.elicit_slot(
            slot_to_elicit="OriginCity", messages=[LexPlainText(content=message)], lex_request=lex_request
        )

    # Resolve origin city to IATA code if not already resolved
    if origin_city and not lex_request.sessionState.sessionAttributes.origin_iata_code:
        try:
            return ReservationUtils.handle_city_resolution(
                origin_city, "OriginCity", "Origin_Airport_Code", "origin_iata_code", lex_request
            )
        except Exception as e:
            logger.error("Error resolving origin city: %s", e)
            # Continue without resolution on error
            pass

    if not destination_city:
        message = "To which city would you like to travel?"
        try:
            message = get_message("book_flight.elicit_destination_city")
        except Exception as e:
            logger.warning("Failed to get localized message: %s", e)
        logger.debug("Eliciting DestinationCity slot: %s", message)
        return dialog.elicit_slot(
            slot_to_elicit="DestinationCity", messages=[LexPlainText(content=message)], lex_request=lex_request
        )

    # Resolve destination city to IATA code if not already resolved
    if destination_city and not lex_request.sessionState.sessionAttributes.destination_iata_code:
        try:
            response = ReservationUtils.handle_city_resolution(
                destination_city, "DestinationCity", "Destination_Airport_Code", "destination_iata_code", lex_request
            )
            if response:
                return response
        except Exception as e:
            logger.error("Error resolving destination city: %s", e)
            # Continue without resolution on error
            pass

    if not departure_date:
        message = "On what date would you like to depart?"
        try:
            message = get_message("book_flight.elicit_departure_date")
        except Exception as e:
            logger.warning("Failed to get localized message: %s", e)
        logger.debug("Eliciting DepartureDate slot: %s", message)
        return dialog.elicit_slot(
            slot_to_elicit="DepartureDate", messages=[LexPlainText(content=message)], lex_request=lex_request
        )

    # ReturnDate is optional for one-way trips

    if not number_of_passengers or number_of_passengers == "0":
        message = "How many passengers will be traveling?"
        try:
            message = get_message("book_flight.elicit_passengers")
        except Exception as e:
            logger.warning("Failed to get localized message: %s", e)
        logger.debug("Eliciting NumberOfPassengers slot: %s", message)
        return dialog.elicit_slot(
            slot_to_elicit="NumberOfPassengers", messages=[LexPlainText(content=message)], lex_request=lex_request
        )

    # All required slots filled, proceed to fulfillment
    logger.debug("All required slots filled, delegating to Lex for confirmation")
    return dialog.delegate(lex_request=lex_request)


def handle_fulfillment_hook(
    lex_request: LexRequest[AirlineBotSessionAttributes],
) -> LexResponse[AirlineBotSessionAttributes]:
    """Handle the fulfillment code hook for the BookFlight intent."""
    logger.debug("BookFlight fulfillment hook called")

    # Get confirmed slot values
    intent = dialog.get_intent(lex_request)
    trip_type = dialog.get_slot(intent=intent, slot_name="TripType")
    origin_city = dialog.get_slot(intent=intent, slot_name="OriginCity")
    destination_city = dialog.get_slot(intent=intent, slot_name="DestinationCity")
    departure_date = dialog.get_slot(intent=intent, slot_name="DepartureDate")
    return_date = dialog.get_slot(intent=intent, slot_name="ReturnDate")
    number_of_passengers = dialog.get_slot(intent=intent, slot_name="NumberOfPassengers")

    logger.debug(
        "Processing booking with: trip_type=%s, origin_city=%s, destination_city=%s, departure_date=%s, return_date=%s, number_of_passengers=%s",
        trip_type,
        origin_city,
        destination_city,
        departure_date,
        return_date,
        number_of_passengers,
    )

    # In production, this would integrate with your booking system
    # For demo purposes, generate a mock reservation number
    reservation_number = "ABC123"

    # Store booking details in session attributes for potential future reference
    lex_request.sessionState.sessionAttributes.reservation_number = reservation_number
    lex_request.sessionState.sessionAttributes.origin_city = origin_city
    lex_request.sessionState.sessionAttributes.destination_city = destination_city
    lex_request.sessionState.sessionAttributes.departure_date = departure_date
    lex_request.sessionState.sessionAttributes.return_date = return_date

    # Get resolved IATA codes with fallbacks
    origin_code = lex_request.sessionState.sessionAttributes.origin_iata_code or origin_city or "N/A"
    destination_code = lex_request.sessionState.sessionAttributes.destination_iata_code or destination_city or "N/A"

    # Create confirmation message based on trip type
    if trip_type and trip_type.lower() in ["round trip", "round", "two way"]:
        message = (
            f"I've booked your round trip from {origin_city} ({origin_code}) to {destination_city} ({destination_code}). "
            f"Departing on {departure_date} and returning on {return_date} "
            f"for {number_of_passengers} passenger(s). "
            f"Your reservation number is {reservation_number}."
        )
        try:
            template = get_message("book_flight.booking_success_roundtrip")
            message = template.format(
                origin_city=f"{origin_city} ({origin_code})",
                destination_city=f"{destination_city} ({destination_code})",
                departure_date=departure_date,
                return_date=return_date,
                number_of_passengers=number_of_passengers,
                reservation_number=reservation_number,
            )
        except Exception as e:
            logger.warning("Failed to get localized message: %s", e)
    else:
        message = (
            f"I've booked your one-way trip from {origin_city} ({origin_code}) to {destination_city} ({destination_code}) "
            f"departing on {departure_date} "
            f"for {number_of_passengers} passenger(s). "
            f"Your reservation number is {reservation_number}."
        )
        try:
            template = get_message("book_flight.booking_success_oneway")
            message = template.format(
                origin_city=f"{origin_city} ({origin_code})",
                destination_city=f"{destination_city} ({destination_code})",
                departure_date=departure_date,
                number_of_passengers=number_of_passengers,
                reservation_number=reservation_number,
            )
        except Exception as e:
            logger.warning("Failed to get localized message: %s", e)

    logger.debug("Booking completed: %s", message)

    # Transition to AnythingElse intent to offer additional assistance
    return dialog.transition_to_intent(
        intent_name="AnythingElse", lex_request=lex_request, messages=[LexPlainText(content=message)]
    )


def handler(lex_request: LexRequest[AirlineBotSessionAttributes]) -> LexResponse[AirlineBotSessionAttributes]:
    """
    Main handler for the BookFlight intent.

    This intent manages the complete flight booking process, including user authentication,
    slot collection for trip details, and booking confirmation. It demonstrates proper
    use of dialog management and intent transitions.

    Args:
        lex_request: The Lex request containing user input and session state

    Returns:
        LexResponse: The response to send back to Amazon Lex
    """
    logger.debug("BookFlight intent handler called")

    invocation_source = lex_request.invocationSource
    logger.debug("Invocation source: %s", invocation_source)

    if invocation_source == InvocationSource.DIALOG_CODE_HOOK.value:
        return handle_dialog_hook(lex_request)

    if (
        invocation_source == InvocationSource.FULFILLMENT_CODE_HOOK.value
        or lex_request.sessionState.intent.state == "ReadyForFulfillment"
    ):
        return handle_fulfillment_hook(lex_request)

    # Fallback - should not normally reach here
    logger.warning("Unrecognized invocation source: %s", invocation_source)
    return dialog.delegate(lex_request=lex_request)
