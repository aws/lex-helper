# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Main Lambda handler for the Airline-Bot fulfillment function.

This is the entry point for the AWS Lambda function that handles Amazon Lex bot requests.
It uses the lex_helper framework to simplify request processing and intent routing.
"""

import json
import logging
import os
import sys
from typing import Any

# Add the layer path to Python path for local development
if not os.getenv("AWS_EXECUTION_ENV"):
    # Get the project root directory (2 levels up from this file)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Add layer to Python path if it exists
    layer_path = os.path.join(project_root, "layers", "lex_helper", "python")
    if os.path.exists(layer_path):
        sys.path.append(layer_path)

        # For versioned packages
        for item in os.listdir(layer_path):
            item_path = os.path.join(layer_path, item)
            if os.path.isdir(item_path) and item.startswith("lex_helper"):
                sys.path.append(item_path)
    else:
        # For integration tests, lex_helper should already be in the path
        # or available from the main project
        pass

# Configure logging for Lambda environment
logger = logging.getLogger(__name__)

# Configure basic logging for Lambda if not already configured
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

from lex_helper import Config, LexHelper, LexRequest

# Use absolute import instead of relative import for Lambda compatibility
try:
    from .session_attributes import AirlineBotSessionAttributes
except ImportError:
    # Fallback for Lambda environment
    from session_attributes import AirlineBotSessionAttributes

try:
    from .utils.config import initialize_message_manager
except ImportError:
    from utils.config import initialize_message_manager


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Main Lambda handler for the Airline-Bot fulfillment function.

    This function processes Amazon Lex requests and routes them to appropriate intent handlers
    using the lex_helper framework. It handles initialization, error handling, and response
    formatting.

    Args:
        event: The Lambda event containing the Lex request with user input and session state
        context: The Lambda context containing runtime information

    Returns:
        Dict[str, Any]: The Lex response formatted for Amazon Lex service
    """
    logger.debug("Initializing Airline-Bot fulfillment Lambda")

    # Initialize the session attributes with default values
    session_attributes = AirlineBotSessionAttributes()
    logger.debug("Initialized session attributes")

    # Create the lex_helper configuration
    config = Config(session_attributes=session_attributes, package_name="fulfillment_function")

    # Initialize the LexHelper with our configuration
    lex_helper = LexHelper(config=config)
    logger.debug("Initialized LexHelper")

    try:
        # Create LexRequest and initialize MessageManager
        lex_request = LexRequest(**event)
        logger.debug("Initialized Message Manager")
        initialize_message_manager(lex_request)

        # Store locale in session attributes
        session_attributes.user_locale = (
            lex_request.bot.localeId if lex_request.bot.localeId in ["en_US", "it_IT"] else "en_US"
        )

        # Process the Lex request through the framework
        logger.debug("Processing Lex request")
        response = lex_helper.handler(event, context)

        # Log response in development
        if not os.getenv("AWS_EXECUTION_ENV"):
            logger.debug("Response: %s", json.dumps(response, default=str))

        return response

    except Exception:
        logger.exception("Error processing request")

        # Try to get localized error message
        try:
            from lex_helper import MessageManager

            msg_manager = MessageManager()
            error_message = msg_manager.get_message("general.error_generic")
        except Exception:
            # Fallback to hardcoded message if MessageManager fails
            error_message = "I'm sorry, I encountered an error while processing your request. Please try again."

        # Return a user-friendly error response
        return {
            "sessionState": {
                "dialogAction": {"type": "Close"},
                "intent": {"name": "FallbackIntent", "state": "Failed"},
                "sessionAttributes": {},
            },
            "messages": [{"contentType": "PlainText", "content": error_message}],
        }
