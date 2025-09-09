# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Exception handling utilities."""

from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from lex_helper.core.types import (
    DialogAction,
    LexPlainText,
    LexRequest,
    LexResponse,
    SessionState,
)

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")


class LexError(Exception):
    """Base class for Lex-specific exceptions."""

    def __init__(self, message: str, error_code: str | None = None):
        super().__init__(message)
        self.error_code = error_code


class IntentNotFoundError(LexError):
    """Raised when an intent handler cannot be found."""

    pass


class ValidationError(LexError):
    """Raised when input validation fails."""

    pass


class SessionError(LexError):
    """Raised when there's an issue with the session state."""

    pass


def handle_exceptions(ex: Exception, lex_request: LexRequest[Any], error_message: str | None = None) -> LexResponse[Any]:
    """Handle exceptions and return appropriate Lex responses.

    Args:
        ex: The exception to handle
        lex_request: The original Lex request
        error_message: Error message (tries as message key first, then as direct string)

    Returns:
        A Lex response with an appropriate error message

    Examples:
        # Use default exception-specific messages
        handle_exceptions(e, request)

        # Direct error message
        handle_exceptions(e, request, error_message="Something went wrong")

        # Message key (automatically detected and localized)
        handle_exceptions(e, request, error_message="general.error_generic")
    """
    # Default fallback message
    final_message = "I'm sorry, I encountered an error while processing your request. Please try again."

    # Handle error message - try as message key first, then use as direct string
    if error_message:
        try:
            from lex_helper import get_message

            # Try to get localized message (assumes it's a message key)
            final_message = get_message(error_message)
        except Exception:
            # If localization fails, use the error_message as a direct string
            final_message = error_message

    # Use exception-specific messages if no error message provided
    else:
        if isinstance(ex, IntentNotFoundError):
            final_message = "I'm not sure how to handle that request."
        elif isinstance(ex, ValidationError):
            final_message = str(ex) or "Invalid input provided."
        elif isinstance(ex, SessionError):
            final_message = "There was an issue with your session. Please start over."
        elif isinstance(ex, ValueError):
            final_message = "Invalid value provided."

    # Create error response
    lex_response: LexResponse[Any] = LexResponse(
        sessionState=SessionState(
            dialogAction=DialogAction(
                type="Close",
            ),
            intent=lex_request.sessionState.intent,
            originatingRequestId=lex_request.sessionId,
            sessionAttributes=lex_request.sessionState.sessionAttributes or {},
        ),
        messages=[LexPlainText(content=final_message, contentType="PlainText")],
        requestAttributes={},
    )
    return lex_response


def safe_execute(func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R | None:
    """Safely execute a function and handle exceptions.

    Args:
        func: Function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or None if execution fails

    Example:
        >>> result = safe_execute(lambda x: int(x), "123")
        123
        >>> result = safe_execute(lambda x: int(x), "abc")
        None
    """
    try:
        return func(*args, **kwargs)
    except Exception:
        return None


def with_error_handling(error_type: type[Exception], error_message: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to handle specific exceptions with custom messages.

    Args:
        error_type: Type of exception to catch
        error_message: Message to use when exception occurs

    Returns:
        Decorated function

    Example:
        >>> @with_error_handling(ValueError, "Invalid number")
        ... def parse_int(s: str) -> int:
        ...     return int(s)
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except error_type as e:
                raise LexError(error_message) from e

        return wrapper

    return decorator
