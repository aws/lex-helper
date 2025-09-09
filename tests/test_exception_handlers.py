# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for exception handling functionality."""

from typing import Any
from unittest.mock import patch

import pytest

from lex_helper import LexRequest, SessionAttributes
from lex_helper.exceptions.handlers import (
    IntentNotFoundError,
    LexError,
    SessionError,
    ValidationError,
    handle_exceptions,
    safe_execute,
    with_error_handling,
)
from tests.sample_lex_request import get_sample_request


class TestSessionAttributes(SessionAttributes):
    """Test session attributes for exception handling tests."""

    test_value: str = "test"


def create_test_lex_request(intent_name: str = "TestIntent") -> LexRequest[SessionAttributes]:
    """Create a test LexRequest for exception handling tests."""
    return get_sample_request(intent_name)


class TestHandleExceptions:
    """Test cases for the handle_exceptions function."""

    def test_handle_exceptions_with_default_behavior(self):
        """Test handle_exceptions with default exception-specific messages."""
        lex_request = create_test_lex_request()

        # Test with generic Exception
        response = handle_exceptions(Exception("test error"), lex_request)

        assert (
            response.messages[0].content
            == "I'm sorry, I encountered an error while processing your request. Please try again."
        )
        assert response.sessionState.dialogAction.type == "Close"
        assert response.sessionState.intent.name == "TestIntent"

    def test_handle_exceptions_with_intent_not_found_error(self):
        """Test handle_exceptions with IntentNotFoundError."""
        lex_request = create_test_lex_request()
        error = IntentNotFoundError("Intent not found")

        response = handle_exceptions(error, lex_request)

        assert response.messages[0].content == "I'm not sure how to handle that request."
        assert response.sessionState.dialogAction.type == "Close"

    def test_handle_exceptions_with_validation_error(self):
        """Test handle_exceptions with ValidationError."""
        lex_request = create_test_lex_request()
        error = ValidationError("Invalid input")

        response = handle_exceptions(error, lex_request)

        assert response.messages[0].content == "Invalid input"
        assert response.sessionState.dialogAction.type == "Close"

    def test_handle_exceptions_with_validation_error_no_message(self):
        """Test handle_exceptions with ValidationError that has no message."""
        lex_request = create_test_lex_request()
        error = ValidationError("")

        response = handle_exceptions(error, lex_request)

        assert response.messages[0].content == "Invalid input provided."

    def test_handle_exceptions_with_session_error(self):
        """Test handle_exceptions with SessionError."""
        lex_request = create_test_lex_request()
        error = SessionError("Session issue")

        response = handle_exceptions(error, lex_request)

        assert response.messages[0].content == "There was an issue with your session. Please start over."

    def test_handle_exceptions_with_value_error(self):
        """Test handle_exceptions with ValueError."""
        lex_request = create_test_lex_request()
        error = ValueError("Invalid value")

        response = handle_exceptions(error, lex_request)

        assert response.messages[0].content == "Invalid value provided."

    @patch("lex_helper.get_message")
    def test_handle_exceptions_with_direct_error_message(self, mock_get_message):
        """Test handle_exceptions with direct error message string."""
        # Make get_message fail so it falls back to using the string directly
        mock_get_message.side_effect = Exception("Message key not found")

        lex_request = create_test_lex_request()
        error = Exception("test error")
        custom_message = "Something went wrong with your request"

        response = handle_exceptions(error, lex_request, error_message=custom_message)

        assert response.messages[0].content == custom_message
        assert response.sessionState.dialogAction.type == "Close"

    @patch("lex_helper.get_message")
    def test_handle_exceptions_with_message_key_success(self, mock_get_message):
        """Test handle_exceptions with successful message key lookup."""
        mock_get_message.return_value = "Localized error message"
        lex_request = create_test_lex_request()
        error = Exception("test error")

        response = handle_exceptions(error, lex_request, error_message="general.error_generic")

        mock_get_message.assert_called_once_with("general.error_generic")
        assert response.messages[0].content == "Localized error message"

    @patch("lex_helper.get_message")
    def test_handle_exceptions_with_message_key_failure(self, mock_get_message):
        """Test handle_exceptions when message key lookup fails."""
        mock_get_message.side_effect = Exception("Message not found")
        lex_request = create_test_lex_request()
        error = Exception("test error")
        message_key = "general.error_generic"

        response = handle_exceptions(error, lex_request, error_message=message_key)

        # Should fall back to using the message key as a direct string
        assert response.messages[0].content == message_key

    def test_handle_exceptions_preserves_session_state(self):
        """Test that handle_exceptions preserves session state and attributes."""
        lex_request = create_test_lex_request()
        lex_request.sessionState.sessionAttributes = TestSessionAttributes(test_value="preserved")
        error = Exception("test error")

        response = handle_exceptions(error, lex_request)

        assert response.sessionState.sessionAttributes.test_value == "preserved"
        assert response.sessionState.intent.name == lex_request.sessionState.intent.name
        assert response.sessionState.originatingRequestId == lex_request.sessionId

    def test_handle_exceptions_response_structure(self):
        """Test that handle_exceptions returns properly structured response."""
        lex_request = create_test_lex_request()
        error = Exception("test error")

        response = handle_exceptions(error, lex_request)

        # Verify response structure
        assert hasattr(response, "sessionState")
        assert hasattr(response, "messages")
        assert hasattr(response, "requestAttributes")

        # Verify session state structure
        assert hasattr(response.sessionState, "dialogAction")
        assert hasattr(response.sessionState, "intent")
        assert hasattr(response.sessionState, "sessionAttributes")

        # Verify message structure
        assert len(response.messages) == 1
        assert hasattr(response.messages[0], "content")
        assert hasattr(response.messages[0], "contentType")
        assert response.messages[0].contentType == "PlainText"


class TestLexErrorClasses:
    """Test cases for custom Lex exception classes."""

    def test_lex_error_creation(self):
        """Test LexError creation with message and error code."""
        error = LexError("Test error", "TEST_001")

        assert str(error) == "Test error"
        assert error.error_code == "TEST_001"

    def test_lex_error_creation_without_code(self):
        """Test LexError creation without error code."""
        error = LexError("Test error")

        assert str(error) == "Test error"
        assert error.error_code is None

    def test_intent_not_found_error(self):
        """Test IntentNotFoundError creation."""
        error = IntentNotFoundError("Intent not found", "INTENT_001")

        assert isinstance(error, LexError)
        assert str(error) == "Intent not found"
        assert error.error_code == "INTENT_001"

    def test_validation_error(self):
        """Test ValidationError creation."""
        error = ValidationError("Validation failed", "VALID_001")

        assert isinstance(error, LexError)
        assert str(error) == "Validation failed"
        assert error.error_code == "VALID_001"

    def test_session_error(self):
        """Test SessionError creation."""
        error = SessionError("Session expired", "SESSION_001")

        assert isinstance(error, LexError)
        assert str(error) == "Session expired"
        assert error.error_code == "SESSION_001"


class TestSafeExecute:
    """Test cases for the safe_execute utility function."""

    def test_safe_execute_success(self):
        """Test safe_execute with successful function execution."""

        def test_func(x: int, y: int) -> int:
            return x + y

        result = safe_execute(test_func, 2, 3)
        assert result == 5

    def test_safe_execute_with_kwargs(self):
        """Test safe_execute with keyword arguments."""

        def test_func(x: int, y: int = 10) -> int:
            return x + y

        result = safe_execute(test_func, 5, y=15)
        assert result == 20

    def test_safe_execute_with_exception(self):
        """Test safe_execute when function raises exception."""

        def failing_func() -> int:
            raise ValueError("This function always fails")

        result = safe_execute(failing_func)
        assert result is None

    def test_safe_execute_with_lambda(self):
        """Test safe_execute with lambda function."""
        result = safe_execute(lambda x: int(x), "123")
        assert result == 123

        result = safe_execute(lambda x: int(x), "abc")
        assert result is None


class TestWithErrorHandling:
    """Test cases for the with_error_handling decorator."""

    def test_with_error_handling_success(self):
        """Test with_error_handling decorator with successful execution."""

        @with_error_handling(ValueError, "Invalid number")
        def parse_int(s: str) -> int:
            return int(s)

        result = parse_int("123")
        assert result == 123

    def test_with_error_handling_catches_specified_error(self):
        """Test with_error_handling decorator catches specified error type."""

        @with_error_handling(ValueError, "Invalid number")
        def parse_int(s: str) -> int:
            return int(s)

        with pytest.raises(LexError, match="Invalid number"):
            parse_int("abc")

    def test_with_error_handling_preserves_other_errors(self):
        """Test with_error_handling decorator doesn't catch other error types."""

        @with_error_handling(ValueError, "Invalid number")
        def risky_function() -> int:
            raise TypeError("This is not a ValueError")

        with pytest.raises(TypeError, match="This is not a ValueError"):
            risky_function()

    def test_with_error_handling_chaining(self):
        """Test chaining multiple with_error_handling decorators."""

        @with_error_handling(ValueError, "Invalid value")
        @with_error_handling(TypeError, "Invalid type")
        def multi_error_func(value: Any) -> str:
            if isinstance(value, int):
                raise ValueError("No integers allowed")
            if not isinstance(value, str):
                raise TypeError("Must be string")
            return value.upper()

        # Test successful execution
        result = multi_error_func("hello")
        assert result == "HELLO"

        # Test ValueError handling
        with pytest.raises(LexError, match="Invalid value"):
            multi_error_func(123)

        # Test TypeError handling
        with pytest.raises(LexError, match="Invalid type"):
            multi_error_func([1, 2, 3])


class TestIntegrationScenarios:
    """Integration test scenarios for exception handling."""

    @patch("lex_helper.get_message")
    def test_real_world_lambda_error_scenario(self, mock_get_message):
        """Test realistic Lambda error handling scenario."""
        mock_get_message.return_value = "We're experiencing technical difficulties. Please try again later."

        lex_request = create_test_lex_request("BookFlight")
        lex_request.sessionState.sessionAttributes = TestSessionAttributes(test_value="booking_in_progress")

        # Simulate a real error that might occur in Lambda
        error = ConnectionError("Database connection failed")

        response = handle_exceptions(error, lex_request, error_message="general.error_generic")

        # Verify the response
        assert response.messages[0].content == "We're experiencing technical difficulties. Please try again later."
        assert response.sessionState.intent.name == "BookFlight"
        assert response.sessionState.sessionAttributes.test_value == "booking_in_progress"
        assert response.sessionState.dialogAction.type == "Close"

    def test_multiple_error_types_in_sequence(self):
        """Test handling different error types in sequence."""
        lex_request = create_test_lex_request()

        # Test different error types
        errors_and_expected = [
            (IntentNotFoundError("Unknown intent"), "I'm not sure how to handle that request."),
            (ValidationError("Bad input"), "Bad input"),
            (SessionError("Session expired"), "There was an issue with your session. Please start over."),
            (ValueError("Invalid value"), "Invalid value provided."),
            (
                Exception("Generic error"),
                "I'm sorry, I encountered an error while processing your request. Please try again.",
            ),
        ]

        for error, expected_message in errors_and_expected:
            response = handle_exceptions(error, lex_request)
            assert response.messages[0].content == expected_message
            assert response.sessionState.dialogAction.type == "Close"
