# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Handler for the ChangeFlight intent.
"""

import logging

logger = logging.getLogger(__name__)

from lex_helper import LexPlainText, LexRequest, LexResponse, dialog, get_message

from ..classes.slot_enums import ChangeFlightSlot
from ..session_attributes import AirlineBotSessionAttributes


def handler(lex_request: LexRequest[AirlineBotSessionAttributes]) -> LexResponse[AirlineBotSessionAttributes]:
    """
    Handle the ChangeFlight intent.

    Args:
        lex_request: The Lex request

    Returns:
        The Lex response
    """
    logger.debug("ChangeFlight intent handler called")

    # Get the intent and session attributes
    intent = dialog.get_intent(lex_request)
    session_attrs = lex_request.sessionState.sessionAttributes

    # Get slot values
    reservation_number = dialog.get_slot(slot_name=ChangeFlightSlot.RESERVATIONNUMBER.value, intent=intent) or ""
    new_departure_date = dialog.get_slot(slot_name=ChangeFlightSlot.NEWDEPARTUREDATE.value, intent=intent) or ""
    logger.debug("Slot values: reservation_number=%s, new_departure_date=%s", reservation_number, new_departure_date)

    # Store values in session attributes
    session_attrs.reservation_number = reservation_number
    session_attrs.departure_date = new_departure_date

    # Check if we need to elicit any slots
    if not reservation_number:
        message = "What is your reservation number?"
        try:
            message = get_message("cancel_flight.elicit_reservation_number")
        except Exception as e:
            logger.warning("Failed to get localized message: %s", e)
        logger.debug("Eliciting ReservationNumber slot: %s", message)
        return dialog.elicit_slot(
            slot_to_elicit=ChangeFlightSlot.RESERVATIONNUMBER.value,
            messages=[LexPlainText(content=message)],
            lex_request=lex_request,
        )

    if not new_departure_date:
        message = "What is your new departure date?"
        logger.debug("Eliciting NewDepartureDate slot: %s", message)
        return dialog.elicit_slot(
            slot_to_elicit=ChangeFlightSlot.NEWDEPARTUREDATE.value,
            messages=[LexPlainText(content=message)],
            lex_request=lex_request,
        )

    # Create the response message with proper formatting
    # Convert date to ISO format if needed
    formatted_date = new_departure_date
    try:
        from datetime import datetime

        # Try to parse the date and convert to ISO format
        if isinstance(new_departure_date, str):
            # Handle common date formats
            for fmt in ["%B %d, %Y", "%m/%d/%Y", "%Y-%m-%d"]:
                try:
                    parsed_date = datetime.strptime(new_departure_date, fmt)
                    formatted_date = parsed_date.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
    except Exception:
        # If date parsing fails, use original value
        formatted_date = new_departure_date

    message = f"I've changed your reservation {reservation_number}. to depart on {formatted_date}. You will receive a confirmation email shortly."
    logger.debug("Response message: %s", message)

    # Close the dialog with the correct parameter order
    response = dialog.close(messages=[LexPlainText(content=message)], lex_request=lex_request)

    logger.debug("Response: %s", response)
    return response
