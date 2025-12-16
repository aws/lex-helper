"""
Handler for the ChangeFlight intent.
"""
from lex_helper import LexRequest, LexResponse, LexPlainText, dialog, get_message
import logging

logger = logging.getLogger(__name__)

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
    reservation_number = dialog.get_slot(intent=intent, slot_name="ReservationNumber") or ""
    new_departure_date = dialog.get_slot(intent=intent, slot_name="NewDepartureDate") or ""
    logger.debug(f"Slot values: reservation_number={reservation_number}, new_departure_date={new_departure_date}")
    
    # Store values in session attributes
    session_attrs.reservation_number = reservation_number
    session_attrs.departure_date = new_departure_date
    
    # Check if we need to elicit any slots
    if not reservation_number:
        message = "What is your reservation number?"
        try:
            message = get_message("cancel_flight.elicit_reservation_number")
        except Exception as e:
            logger.warning(f"Failed to get localized message: {e}")
        logger.debug(f"Eliciting ReservationNumber slot: {message}")
        return dialog.elicit_slot(
            slot_to_elicit="ReservationNumber",
            messages=[LexPlainText(content=message)],
            lex_request=lex_request
        )
    
    if not new_departure_date:
        message = "What is your new departure date?"
        logger.debug(f"Eliciting NewDepartureDate slot: {message}")
        return dialog.elicit_slot(
            slot_to_elicit="NewDepartureDate",
            messages=[LexPlainText(content=message)],
            lex_request=lex_request
        )
    
    # Create the response message
    message = f"I've changed your reservation {reservation_number} to depart on {new_departure_date}. You will receive a confirmation email shortly."
    logger.debug(f"Response message: {message}")
    
    # Close the dialog with the correct parameter order
    response = dialog.close(
        messages=[LexPlainText(content=message)],
        lex_request=lex_request
    )
    
    logger.debug(f"Response: {response}")
    return response