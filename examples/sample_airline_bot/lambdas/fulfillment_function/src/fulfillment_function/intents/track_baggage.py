# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Handler for the TrackBaggage intent
"""

import logging

logger = logging.getLogger(__name__)

from lex_helper import LexPlainText, LexRequest, LexResponse, dialog, get_message

from ..classes.slot_enums import TrackBaggageSlot
from ..session_attributes import AirlineBotSessionAttributes


def handler(lex_request: LexRequest[AirlineBotSessionAttributes]) -> LexResponse[AirlineBotSessionAttributes]:
    """
    Handle the TrackBaggage intent with localized messages.

    Args:
        lex_request: The Lex request

    Returns:
        The Lex response
    """
    logger.debug("TrackBaggage intent handler called")

    # Get intent and slots
    intent = dialog.get_intent(lex_request)
    reservation_number = dialog.get_slot(intent=intent, slot_name=TrackBaggageSlot.RESERVATIONNUMBER.value)

    logger.debug("Slot values: reservation_number=%s", reservation_number)

    # Store in session attributes
    lex_request.sessionState.sessionAttributes.reservation_number = reservation_number

    # STEP 1: Slot elicitation with localized message
    if not reservation_number:
        message = "DEFAULT: What is your reservation number?"  # Default fallback
        try:
            # Try to get localized message
            message = get_message(key="track_baggage.elicit_reservation_number", locale=lex_request.bot.localeId)
        except Exception as e:
            logger.warning("Failed to get localized message: %s", e)
            # Keep default fallback message
        logger.debug("Eliciting ReservationNumber slot: %s", message)
        return dialog.elicit_slot(
            slot_to_elicit=TrackBaggageSlot.RESERVATIONNUMBER.value,
            messages=[LexPlainText(content=message)],
            lex_request=lex_request,
        )

    # STEP 2: Business logic - mock baggage lookup
    baggage_status = "in transit"

    # STEP 3: Response with parameter substitution
    message = f"DEFAULT Your baggage for reservation {reservation_number} is currently {baggage_status}. It should arrive at your destination shortly."
    try:
        template = get_message("track_baggage.status_response")
        message = template.format(reservation_number=reservation_number, status=baggage_status)
    except Exception as e:
        logger.warning("Failed to get localized message: %s", e)
        # Keep default fallback message
    logger.debug("Response message: %s", message)

    return dialog.close(messages=[LexPlainText(content=message)], lex_request=lex_request)
