"""
Configuration utilities for the Airline-Bot fulfillment function.

This module provides MessageManager initialization for the Airline-Bot.
"""
from loguru import logger

from lex_helper import set_locale


def initialize_message_manager(lex_request) -> None:
    """Initialize MessageManager singleton with locale from request."""
    try:


        locale = lex_request.bot.localeId

        set_locale(locale)
        logger.debug(f"MessageManager initialized for locale: {locale}")

    except Exception as e:
        logger.warning(f"Failed to initialize MessageManager: {e}")
        pass
