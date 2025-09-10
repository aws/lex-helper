# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Main Lambda handler for the Airline-Bot fulfillment function.

This is the entry point for the AWS Lambda function that handles Amazon Lex bot requests.
It uses the lex_helper framework with Smart Disambiguation to provide intelligent handling
of ambiguous user input, with optional Bedrock-powered contextual responses.

Environment Variables:
    ENABLE_BEDROCK_DISAMBIGUATION: Set to 'true' to enable AI-powered disambiguation
    BEDROCK_MODEL_ID: Bedrock model ID (default: anthropic.claude-3-haiku-20240307-v1:0)
    BEDROCK_REGION: AWS region for Bedrock (default: us-east-1)
    BEDROCK_MAX_TOKENS: Maximum tokens for responses (default: 150)
    BEDROCK_TEMPERATURE: Temperature for text generation (default: 0.3)
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

    # Configure Bedrock for intelligent disambiguation (optional)
    # Set ENABLE_BEDROCK_DISAMBIGUATION=true environment variable to enable
    enable_bedrock = os.getenv("ENABLE_BEDROCK_DISAMBIGUATION", "false").lower() == "true"

    bedrock_config = BedrockDisambiguationConfig(
        enabled=enable_bedrock,
        model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"),
        region_name=os.getenv("BEDROCK_REGION", "us-east-1"),
        max_tokens=int(os.getenv("BEDROCK_MAX_TOKENS", "150")),
        temperature=float(os.getenv("BEDROCK_TEMPERATURE", "0.3")),
        system_prompt=(
            "You are a helpful airline customer service assistant. "
            "Create clear, friendly disambiguation messages that help travelers "
            "choose between flight-related options. Be concise and professional. "
            "Use airline industry terminology appropriately. "
            "Always acknowledge what the customer said and provide clear next steps."
        ),
        fallback_to_static=True,  # Always fall back gracefully
    )

    # Configure Smart Disambiguation with Bedrock integration and message keys for localization
    disambiguation_config = DisambiguationConfig(
        confidence_threshold=0.4,  # Threshold for low confidence scenarios
        max_candidates=2,  # Keep it simple with 2 options
        similarity_threshold=0.15,  # Only trigger if top scores are within 0.15 of each other
        # Define custom intent groups for related airline operations
        custom_intent_groups={
            "booking": ["BookFlight", "ChangeFlight", "CancelFlight"],
            "status": ["FlightDelayUpdate", "TrackBaggage"],
            "account": ["Authenticate"],
        },
        # Use message keys instead of hardcoded text for localization
        custom_messages={
            # General disambiguation messages (these are message keys)
            "disambiguation.two_options": "disambiguation.airline.two_options",
            "disambiguation.multiple_options": "disambiguation.airline.multiple_options",
            # Specific intent group messages
            "disambiguation.booking": "disambiguation.airline.booking_options",
            "disambiguation.status": "disambiguation.airline.status_options",
            # Specific intent pair messages
            "BookFlight_ChangeFlight": "disambiguation.airline.book_or_change",
            "ChangeFlight_CancelFlight": "disambiguation.airline.change_or_cancel",
            "FlightDelayUpdate_TrackBaggage": "disambiguation.airline.flight_or_baggage",
        },
        # Bedrock configuration for intelligent text generation
        bedrock_config=bedrock_config,
    )

    # Create the lex_helper configuration with disambiguation enabled
    config = Config(
        session_attributes=session_attributes,
        package_name="fulfillment_function",
        auto_handle_exceptions=True,  # Automatically handle exceptions
        error_message="general.error_generic",  # Custom error message key
        enable_disambiguation=True,  # Enable Smart Disambiguation
        disambiguation_config=disambiguation_config,
    )

    # Initialize the LexHelper with our configuration
    lex_helper = LexHelper(config=config)

    if enable_bedrock:
        logger.info("Bedrock-powered disambiguation enabled with model: %s", bedrock_config.model_id)
    else:
        logger.debug("Using static disambiguation messages")

    logger.debug("Initialized LexHelper with Smart Disambiguation")

    # Process the Lex request through the framework (exceptions handled automatically)
    response = lex_helper.handler(event, context)

    # Log response in development
    if not os.getenv("AWS_EXECUTION_ENV"):
        logger.debug("Response: %s", json.dumps(response, default=str))

    return response


# Usage Examples:
#
# 1. Basic disambiguation (default):
#    No environment variables needed. Uses static message templates.
#
# 2. Bedrock-powered disambiguation:
#    Set environment variable: ENABLE_BEDROCK_DISAMBIGUATION=true
#    Optionally configure: BEDROCK_MODEL_ID, BEDROCK_REGION, etc.
#
# 3. Custom Bedrock model:
#    ENABLE_BEDROCK_DISAMBIGUATION=true
#    BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
#    BEDROCK_TEMPERATURE=0.2
#
# The system gracefully falls back to static messages if Bedrock fails,
# ensuring your bot always works even if AI services are unavailable.
