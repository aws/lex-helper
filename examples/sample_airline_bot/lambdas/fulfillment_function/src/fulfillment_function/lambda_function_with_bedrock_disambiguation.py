# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Example Lambda handler for the Airline-Bot with Bedrock-powered Smart Disambiguation.

This demonstrates how to enable and configure Bedrock-powered disambiguation
for generating intelligent, contextual clarification messages and button labels.
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
from lex_helper.core.disambiguation.types import BedrockDisambiguationConfig, DisambiguationConfig

# Use absolute import instead of relative import for Lambda compatibility
try:
    from .session_attributes import AirlineBotSessionAttributes
except ImportError:
    # Fallback for Lambda environment
    from session_attributes import AirlineBotSessionAttributes


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Lambda handler with Bedrock-powered Smart Disambiguation.

    This example shows how to configure Bedrock integration for generating
    intelligent, contextual disambiguation messages and button labels.

    Args:
        event: The Lambda event containing the Lex request
        context: The Lambda context containing runtime information

    Returns:
        Dict[str, Any]: The Lex response formatted for Amazon Lex service
    """
    logger.debug("Initializing Airline-Bot fulfillment Lambda with Bedrock-powered Smart Disambiguation")

    # Initialize the session attributes with default values
    session_attributes = AirlineBotSessionAttributes()
    logger.debug("Initialized session attributes")

    # Configure Bedrock for intelligent text generation
    bedrock_config = BedrockDisambiguationConfig(
        enabled=True,  # Enable Bedrock-powered disambiguation
        model_id="anthropic.claude-3-haiku-20240307-v1:0",  # Fast, cost-effective model
        region_name="us-east-1",  # Adjust to your preferred region
        max_tokens=150,  # Concise responses
        temperature=0.3,  # More deterministic for consistent UX
        system_prompt=(
            "You are a helpful airline customer service assistant. "
            "Create clear, friendly disambiguation messages that help travelers "
            "choose between flight-related options. Be concise and professional. "
            "Use airline industry terminology appropriately."
        ),
        fallback_to_static=True,  # Graceful fallback if Bedrock fails
    )

    # Configure Smart Disambiguation with Bedrock integration
    disambiguation_config = DisambiguationConfig(
        confidence_threshold=0.5,  # Lower threshold for travel domain
        max_candidates=2,  # Show max 2 options to avoid overwhelming users
        # Define custom intent groups for related airline operations
        custom_intent_groups={
            "booking": ["BookFlight", "ChangeFlight", "CancelFlight"],
            "status": ["FlightDelayUpdate", "TrackBaggage"],
            "account": ["Authenticate"],
        },
        # Custom clarification messages for fallback scenarios
        custom_messages={
            "booking_disambiguation": "I can help you book, change, or cancel a flight. Which would you like to do?",
            "status_disambiguation": "Would you like to check flight status or track your baggage?",
        },
        # Enable detailed logging for monitoring
        enable_logging=True,
        # Bedrock configuration for intelligent text generation
        bedrock_config=bedrock_config,
    )

    # Create the lex_helper configuration with Bedrock-powered disambiguation
    config = Config(
        session_attributes=session_attributes,
        package_name="fulfillment_function",
        auto_handle_exceptions=True,
        error_message="general.error_generic",
        # Enable Smart Disambiguation with Bedrock
        enable_disambiguation=True,
        disambiguation_config=disambiguation_config,
    )

    # Initialize the LexHelper with the configuration
    lex_helper = LexHelper(config)
    logger.debug("LexHelper initialized with Bedrock-powered disambiguation")

    # Process the request and return the response
    try:
        response = lex_helper.handler(event, context)
        logger.debug("Successfully processed request with response: %s", json.dumps(response, default=str))
        return response
    except Exception as e:
        logger.exception("Error processing request: %s", e)
        raise


# Example of how the Bedrock-powered disambiguation works:
#
# User input: "I need help with my flight"
# 
# Without Bedrock (static):
# "I can help you with several things. What would you like to do?"
# Buttons: ["Book Flight", "Change Flight", "Cancel Flight"]
#
# With Bedrock (intelligent):
# "I'd be happy to help with your flight! Are you looking to make changes 
# to an existing booking or book a new flight?"
# Buttons: ["Modify existing booking", "Book new flight", "Cancel booking"]
#
# The Bedrock model generates contextual, natural language that:
# 1. Acknowledges the user's specific input
# 2. Uses appropriate airline terminology
# 3. Creates more intuitive button labels
# 4. Provides a more conversational experience