"""
Handler for the FallbackIntent.
"""
from loguru import logger

from lex_helper import LexPlainText, LexRequest, LexResponse, dialog, get_message

from ..session_attributes import AirlineBotSessionAttributes


def handler(lex_request: LexRequest[AirlineBotSessionAttributes]) -> LexResponse[AirlineBotSessionAttributes]:
    """
    Handle the FallbackIntent.
    
    Args:
        lex_request: The Lex request
        
    Returns:
        The Lex response
    """
    logger.debug("FallbackIntent handler called")

    # Create the response message
    message = "I didn't understand that. Could you please rephrase your request?"
    try:
        message = get_message("general.fallback")
    except Exception as e:
        logger.warning(f"Failed to get localized message: {e}")
    logger.debug(f"Response message: {message}")

    # Create a message list with a single plain text message
    messages = [LexPlainText(content=message)]

    # Elicit the next intent with the correct parameter order
    response = dialog.elicit_intent(
        messages=messages,  # First parameter is messages
        lex_request=lex_request  # Second parameter is lex_request
    )

    logger.debug(f"Response: {response}")
    return response
