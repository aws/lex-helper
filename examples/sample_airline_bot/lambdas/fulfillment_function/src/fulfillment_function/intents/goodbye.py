# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Handler for the Goodbye intent.
"""

import logging

logger = logging.getLogger(__name__)

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
        logger.warning("Failed to get localized message: %s", e)
    logger.debug("Response message: %s", message)

    # Create a message list with a single plain text message
    messages = [LexPlainText(content=message)]

    # Close the dialog with the correct parameter order
    response = dialog.close(messages=messages, lex_request=lex_request)

    logger.debug("Response: %s", response)
    return response
