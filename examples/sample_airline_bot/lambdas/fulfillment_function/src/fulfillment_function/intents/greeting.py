"""
Handler for the Greeting intent.

This intent handles user greetings and provides a welcoming introduction to the bot's
capabilities. It tracks greeting count to provide different responses for repeat visitors.
"""
from lex_helper import LexRequest, LexResponse, LexPlainText, dialog, get_message
import logging

from ..session_attributes import AirlineBotSessionAttributes

logger = logging.getLogger(__name__)


def handler(lex_request: LexRequest[AirlineBotSessionAttributes]) -> LexResponse[AirlineBotSessionAttributes]:
    """
    Handle the Greeting intent.
    
    This intent welcomes users to the airline bot and provides an overview of available
    services. It tracks how many times the user has been greeted in the current session
    to provide appropriate responses.
    
    Args:
        lex_request: The Lex request containing user input and session state
        
    Returns:
        LexResponse: The response to send back to Amazon Lex
    """
    logger.debug("Greeting intent handler called")
    
    # Get and update session attributes
    session_attrs = lex_request.sessionState.sessionAttributes
    session_attrs.common_greeting_count += 1
    
    logger.debug(f"Greeting count: {session_attrs.common_greeting_count}")
    
    # Provide different messages based on greeting count
    if session_attrs.common_greeting_count == 1:
        message = "Hello! Welcome to Airline-Bot. I can help you with booking flights, checking flight status, tracking baggage, and managing your reservations. How can I assist you today?"
        try:
            message = get_message("greeting.first_time")
        except Exception as e:
            logger.warning(f"Failed to get localized message: {e}")
        logger.debug("Providing first-time greeting")
    else:
        message = "Hello again! How can I help you today?"
        try:
            message = get_message("greeting.returning")
        except Exception as e:
            logger.warning(f"Failed to get localized message: {e}")
        logger.debug("Providing repeat greeting")

    logger.debug(f"Greeting message: {message}")
    
    # Elicit the user's intent after greeting
    return dialog.elicit_intent(
        messages=[LexPlainText(content=message)],
        lex_request=lex_request
    )