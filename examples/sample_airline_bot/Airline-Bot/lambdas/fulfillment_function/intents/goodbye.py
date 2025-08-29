"""
Handler for the Goodbye intent.
"""
from loguru import logger

from lex_helper import LexPlainText, LexRequest, LexResponse, dialog, get_message

from ..session_attributes import AirlineBotSessionAttributes


def handler(lex_request: LexRequest[AirlineBotSessionAttributes]) -> LexResponse[AirlineBotSessionAttributes]:
    """
    Handle the Goodbye intent.
    
    Args:
        lex_request: The Lex request
        
    Returns:
        The Lex response
    """
    logger.debug("Goodbye intent handler called")

    # Create the response message
    message = "Thank you for using Airline-Bot. Have a great day!"
    try:
        message = get_message("general.goodbye")
    except Exception as e:
        logger.warning(f"Failed to get localized message: {e}")
    logger.debug(f"Response message: {message}")

    # Create a message list with a single plain text message
    messages = [LexPlainText(content=message)]

    # Close the dialog with the correct parameter order
    response = dialog.close(
        messages=messages,
        lex_request=lex_request

    )

    logger.debug(f"Response: {response}")
    return response
