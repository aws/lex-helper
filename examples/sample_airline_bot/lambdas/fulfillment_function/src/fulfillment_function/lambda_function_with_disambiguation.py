# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Example Lambda handler for the Airline-Bot with Smart Disambiguation enabled.

This demonstrates how to enable and configure the Smart Disambiguation feature
in the lex_helper framework for better handling of ambiguous user input.
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

# Configure logging for Lambda environment
logger = logging.getLogger(__name__)

# Configure basic logging for Lambda if not already configured
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

from lex_helper import Config, LexHelper
from lex_helper.core.disambiguation.types import DisambiguationConfig

# Use absolute import instead of relative import for Lambda compatibility
try:
    from .session_attributes import AirlineBotSessionAttributes
except ImportError:
    # Fallback for Lambda environment
    from session_attributes import AirlineBotSessionAttributes


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Lambda handler with Smart Disambiguation enabled.

    This example shows how to configure and enable the Smart Disambiguation
    feature for better handling of ambiguous user input in the airline bot.

    Args:
        event: The Lambda event containing the Lex request
        context: The Lambda context containing runtime information

    Returns:
        Dict[str, Any]: The Lex response formatted for Amazon Lex service
    """
    logger.debug("Initializing Airline-Bot fulfillment Lambda with Smart Disambiguation")

    # Initialize the session attributes with default values
    session_attributes = AirlineBotSessionAttributes()
    logger.debug("Initialized session attributes")

    # Configure Smart Disambiguation for airline-specific scenarios
    disambiguation_config = DisambiguationConfig(
        confidence_threshold=0.5,  # Lower threshold for travel domain
        max_candidates=2,  # Show max 2 options to avoid overwhelming users
        # Define custom intent groups for related airline operations
        custom_intent_groups={
            "booking": ["BookFlight", "ChangeFlight", "CancelFlight"],
            "status": ["FlightDelayUpdate", "TrackBaggage"],
            "account": ["Authenticate"],
        },
        # Custom clarification messages for common scenarios
        custom_messages={
            "booking_disambiguation": "I can help you book, change, or cancel a flight. Which would you like to do?",
            "status_disambiguation": "Would you like to check flight status or track your baggage?",
            "BookFlight_ChangeFlight": "Would you like to book a new flight or change an existing one?",
            "ChangeFlight_CancelFlight": "Would you like to change your flight or cancel it?",
        },
        # Enable detailed logging for monitoring
        enable_logging=True,
    )

    # Create the lex_helper configuration with disambiguation enabled
    config = Config(
        session_attributes=session_attributes,
        package_name="fulfillment_function",
        auto_handle_exceptions=True,
        error_message="general.error_generic",
        # Enable Smart Disambiguation
        enable_disambiguation=True,
        disambiguation_config=disambiguation_config,
    )

    # Initialize the LexHelper with disambiguation enabled
    lex_helper = LexHelper(config=config)
    logger.debug("Initialized LexHelper with Smart Disambiguation")

    # Process the Lex request (disambiguation will be handled automatically)
    response = lex_helper.handler(event, context)

    # Log response in development
    if not os.getenv("AWS_EXECUTION_ENV"):
        logger.debug("Response: %s", json.dumps(response, default=str))

    return response


def lambda_handler_simple_disambiguation(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Simple example with minimal disambiguation configuration.

    This shows the easiest way to enable disambiguation with default settings.
    """
    session_attributes = AirlineBotSessionAttributes()

    # Minimal configuration - just enable disambiguation with defaults
    config = Config(
        session_attributes=session_attributes,
        package_name="fulfillment_function",
        auto_handle_exceptions=True,
        enable_disambiguation=True,  # Use default disambiguation settings
    )

    lex_helper = LexHelper(config=config)
    return lex_helper.handler(event, context)
