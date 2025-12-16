"""
Handler for the CancelFlight intent using MessageManager.
"""

import logging

from lex_helper import LexPlainText, LexRequest, LexResponse, dialog, get_message

logger = logging.getLogger(__name__)

from ..classes.slot_enums import CancelFlightSlot
from ..session_attributes import AirlineBotSessionAttributes


def handler(lex_request: LexRequest[AirlineBotSessionAttributes]) -> LexResponse[AirlineBotSessionAttributes]:
    """
    Handle the CancelFlight intent with internationalization support.

    Flow: Elicit reservation number → Validate format → Lookup reservation → Cancel or error

    Args:
        lex_request: The Lex request containing user input and session state

    Returns:
        The Lex response with localized messages
    """
    logger.debug("CancelFlight intent handler called")

    # Get MessageManager singleton (initialized in lambda_function.py with user's locale)
    # from lex_helper import MessageManager
    # msg_manager = MessageManager.get_instance()

    # Extract slot values from the intent
    intent = dialog.get_intent(lex_request)
    reservation_number = dialog.get_slot(intent=intent, slot_name=CancelFlightSlot.RESERVATIONNUMBER.value)

    logger.debug(f"Slot values: reservation_number={reservation_number}")

    # Persist data in session for multi-turn conversations
    lex_request.sessionState.sessionAttributes.reservation_number = reservation_number

    # STEP 1: Slot elicitation - ask for missing reservation number
    if not reservation_number:
        message = "What is your reservation number?"
        try:
            message = get_message("cancel_flight.elicit_reservation_number")
        except Exception as e:
            logger.warning(f"Failed to get localized message: {e}")
        logger.debug(f"Eliciting ReservationNumber slot: {message}")
        return dialog.elicit_slot(
            slot_to_elicit=CancelFlightSlot.RESERVATIONNUMBER.value,
            messages=[LexPlainText(content=message)],
            lex_request=lex_request,
        )

    # STEP 2: Input validation - check reservation number format
    if not _is_valid_reservation_number(reservation_number):
        message = "Please provide a valid reservation number. It should be in the format ABC123."
        try:
            message = get_message("cancel_flight.invalid_reservation_format")
        except Exception as e:
            logger.warning(f"Failed to get localized message: {e}")
        logger.debug(f"Invalid reservation format: {message}")
        return dialog.elicit_slot(
            slot_to_elicit=CancelFlightSlot.RESERVATIONNUMBER.value,
            messages=[LexPlainText(content=message)],
            lex_request=lex_request,
        )

    # STEP 3: Business logic - lookup reservation in system
    reservation_found = _lookup_reservation(reservation_number)

    # STEP 4: Generate response based on lookup result
    if reservation_found:
        message = f"I've cancelled your reservation {reservation_number}. You will receive a confirmation email shortly."
        try:
            template = get_message("cancel_flight.cancellation_success")
            message = template.format(reservation_number=reservation_number)
        except Exception as e:
            logger.warning(f"Failed to get localized message: {e}")
        logger.debug(f"Cancellation success: {message}")
    else:
        message = f"I'm sorry, I couldn't find a reservation with number {reservation_number}. Please check the number and try again."
        try:
            template = get_message("cancel_flight.cancellation_error")
            message = template.format(reservation_number=reservation_number)
        except Exception as e:
            logger.warning(f"Failed to get localized message: {e}")
        logger.debug(f"Cancellation error: {message}")

    # Close dialog with final localized response
    return dialog.close(messages=[LexPlainText(content=message)], lex_request=lex_request)


def _is_valid_reservation_number(reservation_number: str) -> bool:
    """
    Validate reservation number format.

    Args:
        reservation_number: The reservation number to validate

    Returns:
        bool: True if valid format, False otherwise
    """
    # Simple validation: should be 6 characters, alphanumeric
    return reservation_number and len(reservation_number) == 6 and reservation_number.isalnum()


def _lookup_reservation(reservation_number: str) -> bool:
    """
    Simulate reservation lookup.

    Args:
        reservation_number: The reservation number to look up

    Returns:
        bool: True if reservation found, False otherwise
    """
    # Mock implementation - in production, this would call a real reservation system
    # For demo purposes, assume reservations starting with 'A' exist
    return reservation_number.upper().startswith("A")
