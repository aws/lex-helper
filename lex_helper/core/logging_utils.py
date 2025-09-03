# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Logging utilities for the lex-helper library.

This module provides consistent logging functionality across the library,
following Python logging best practices for libraries.
"""

import logging
from typing import Any

from lex_helper.core.types import LexRequest


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for the given module name.

    Args:
        name: The module name, typically __name__

    Returns:
        A logger instance configured for the module
    """
    return logging.getLogger(name)


def log_request_debug(logger: logging.Logger, request: LexRequest[Any]) -> None:
    """
    Log request details at DEBUG level.

    Args:
        logger: The logger instance to use
        request: The Lex request to log
    """
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "Processing Lex request - Intent: %s, Session ID: %s, User ID: %s",
            request.sessionState.intent.name if request.sessionState.intent else "None",
            request.sessionId,
            request.sessionState.sessionAttributes.get("userId", "Unknown")
            if request.sessionState.sessionAttributes
            else "Unknown",
        )


def log_exception(logger: logging.Logger, exc: Exception, context: str) -> None:
    """
    Log exception with context at ERROR level.

    Args:
        logger: The logger instance to use
        exc: The exception that occurred
        context: Additional context about where the exception occurred
    """
    logger.exception("%s: %s", context, str(exc))


def log_handler_invocation(logger: logging.Logger, handler_name: str, intent_name: str | None = None) -> None:
    """
    Log handler invocation at DEBUG level.

    Args:
        logger: The logger instance to use
        handler_name: Name of the handler being invoked
        intent_name: Name of the intent being handled (if applicable)
    """
    if intent_name:
        logger.debug("Invoking handler '%s' for intent '%s'", handler_name, intent_name)
    else:
        logger.debug("Invoking handler '%s'", handler_name)


def log_http_request(
    logger: logging.Logger, method: str, url: str, status_code: int | None = None, response_time: float | None = None
) -> None:
    """
    Log HTTP request details at DEBUG level.

    Args:
        logger: The logger instance to use
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        status_code: HTTP response status code (if available)
        response_time: Request response time in seconds (if available)
    """
    if status_code is not None:
        if response_time is not None:
            logger.debug("HTTP %s %s - Status: %d, Time: %.3fs", method, url, status_code, response_time)
        else:
            logger.debug("HTTP %s %s - Status: %d", method, url, status_code)
    else:
        logger.debug("HTTP %s %s", method, url)


def log_bedrock_invocation(logger: logging.Logger, model_id: str, success: bool, error_message: str | None = None) -> None:
    """
    Log Bedrock model invocation at appropriate level.

    Args:
        logger: The logger instance to use
        model_id: The Bedrock model ID being invoked
        success: Whether the invocation was successful
        error_message: Error message if invocation failed
    """
    if success:
        logger.debug("Successfully invoked Bedrock model: %s", model_id)
    else:
        logger.error("Failed to invoke Bedrock model '%s': %s", model_id, error_message or "Unknown error")


def log_session_attribute_update(logger: logging.Logger, attribute_name: str, old_value: Any, new_value: Any) -> None:
    """
    Log session attribute updates at DEBUG level.

    Args:
        logger: The logger instance to use
        attribute_name: Name of the session attribute
        old_value: Previous value
        new_value: New value
    """
    logger.debug("Session attribute '%s' updated: %s -> %s", attribute_name, repr(old_value), repr(new_value))
