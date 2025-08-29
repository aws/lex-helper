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


def handle_exceptions(ex: Exception, lex_request: LexRequest[Any]) -> LexResponse[Any]:
    """Handle exceptions and return appropriate Lex responses.

    Args:
        ex: The exception to handle
        lex_request: The original Lex request

    Returns:
        A Lex response with an appropriate error message
    """
    error_message = "An error occurred. Please try again."

    if isinstance(ex, IntentNotFoundError):
        error_message = "I'm not sure how to handle that request."
    elif isinstance(ex, ValidationError):
        error_message = str(ex) or "Invalid input provided."
    elif isinstance(ex, SessionError):
        error_message = "There was an issue with your session. Please start over."
    elif isinstance(ex, ValueError):
        error_message = "Invalid value provided."

    # Create error response
    lex_response: LexResponse[Any] = LexResponse(
        sessionState=SessionState(
            dialogAction=DialogAction(
                type="Close",
            ),
            intent=lex_request.sessionState.intent,
            originatingRequestId=lex_request.sessionId,
            sessionAttributes=lex_request.sessionState.sessionAttributes,
        ),
        messages=[LexPlainText(content=error_message, contentType="PlainText")],
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
