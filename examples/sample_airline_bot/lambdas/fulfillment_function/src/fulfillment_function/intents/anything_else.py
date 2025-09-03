# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Handler for the AnythingElse intent.
"""

import logging

logger = logging.getLogger(__name__)

from lex_helper import LexPlainText, LexRequest, LexResponse, dialog, get_message

from ..session_attributes import AirlineBotSessionAttributes


def handler(lex_request: LexRequest[AirlineBotSessionAttributes]) -> LexResponse[AirlineBotSessionAttributes]:
    """
    Handle the AnythingElse intent.

    Args:
        lex_request: The Lex request

    Returns:
        The Lex response
    """
    logger.debug("AnythingElse intent handler called")

    # Create the response message
    message = "Is there anything else I can help you with today?"
    try:
        message = get_message("general.anything_else")
    except Exception as e:
        logger.warning("Failed to get localized message: %s", e)
    logger.debug("Response message: %s", message)

    # Create a message list with a single plain text message
    messages = [LexPlainText(content=message)]

    # Elicit the next intent with the correct parameter order
    response = dialog.elicit_intent(
        messages=messages,  # First parameter is messages
        lex_request=lex_request,  # Second parameter is lex_request
    )

    logger.debug("Response: %s", response)
    return response
