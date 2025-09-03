# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Configuration utilities for the Airline-Bot fulfillment function.

This module provides MessageManager initialization for the Airline-Bot.
"""

import logging

logger = logging.getLogger(__name__)

from lex_helper import set_locale


def initialize_message_manager(lex_request) -> None:
    """Initialize MessageManager singleton with locale from request."""
    try:
        locale = lex_request.bot.localeId

        set_locale(locale)
        logger.debug("MessageManager initialized for locale: %s", locale)

    except Exception as e:
        logger.warning("Failed to initialize MessageManager: %s", e)
        pass
