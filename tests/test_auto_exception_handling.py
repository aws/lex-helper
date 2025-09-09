# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for automatic exception handling functionality."""

from typing import Any
from unittest.mock import patch

import pytest

from lex_helper import Config, LexHelper, SessionAttributes


class TestSessionAttributes(SessionAttributes):
    """Test session attributes for auto exception handling tests."""

    test_value: str = "test"


def create_test_event(locale_id: str = "en_US") -> dict[str, Any]:
    """Create a test event with specified locale."""
    return {
        "sessionId": "test",
        "bot": {
            "name": "test",
            "aliasId": "test",
            "version": "test",
            "localeId": locale_id,
        },
        "inputTranscript": "test",
        "inputMode": "test",
        "invocationSource": "test",
        "messageVersion": "test",
        "transcriptions": [],
        "responseContentType": "test",
        "sessionState": {
            "sessionAttributes": {"test_value": "test"},
            "activeContexts": [],
            "intent": {
                "name": "TestIntent",
                "slots": {},
                "state": "Fulfilled",
                "confirmationState": "None",
            },
        },
    }


class TestAutoExceptionHandling:
    """Test cases for automatic exception handling."""

    def test_auto_exception_handling_enabled_by_default(self):
        """Test that auto exception handling is enabled by default."""
        config = Config(session_attributes=TestSessionAttributes(), package_name="examples.basic_handler")

        # Should be enabled by default
        assert config.auto_handle_exceptions is True

    def test_auto_exception_handling_can_be_disabled(self):
        """Test that auto exception handling can be disabled."""
        config = Config(
            session_attributes=TestSessionAttributes(), package_name="examples.basic_handler", auto_handle_exceptions=False
        )

        assert config.auto_handle_exceptions is False

    def test_custom_error_message_configuration(self):
        """Test that custom error messages can be configured."""
        config = Config(
            session_attributes=TestSessionAttributes(),
            package_name="examples.basic_handler",
            error_message="custom.error.message",
        )

        assert config.error_message == "custom.error.message"

    def test_config_with_all_options(self):
        """Test Config with all auto-handling options."""
        config = Config(
            session_attributes=TestSessionAttributes(),
            package_name="examples.basic_handler",
            auto_initialize_messages=True,
            auto_handle_exceptions=True,
            error_message="general.error_generic",
        )

        assert config.auto_initialize_messages is True
        assert config.auto_handle_exceptions is True
        assert config.error_message == "general.error_generic"

    def test_auto_exception_handling_with_valid_event(self):
        """Test auto exception handling with a valid event that will fail on intent handler."""
        config = Config(
            session_attributes=TestSessionAttributes(),
            package_name="examples.basic_handler",
            auto_handle_exceptions=True,
            error_message="general.error_generic",
        )

        lex_helper = LexHelper(config=config)
        event = create_test_event()

        # This should not raise an exception, even though intent handler will fail
        response = lex_helper.handler(event, {})

        # Should return a valid error response
        assert isinstance(response, dict)
        assert "sessionState" in response
        assert "messages" in response
        assert response["sessionState"]["dialogAction"]["type"] == "Close"

    @patch("lex_helper.get_message")
    def test_auto_exception_handling_with_invalid_event(self, mock_get_message):
        """Test auto exception handling with an invalid event."""
        mock_get_message.side_effect = Exception("Message not found")

        config = Config(
            session_attributes=TestSessionAttributes(),
            package_name="examples.basic_handler",
            auto_handle_exceptions=True,
            error_message="custom.error.message",
        )

        lex_helper = LexHelper(config=config)
        invalid_event = {"invalid": "event"}

        # Should not raise an exception, should return error response
        response = lex_helper.handler(invalid_event, {})

        # Should return a minimal error response
        assert isinstance(response, dict)
        assert "sessionState" in response
        assert "messages" in response
        assert response["sessionState"]["dialogAction"]["type"] == "Close"
        assert response["messages"][0]["content"] == "custom.error.message"

    @patch("lex_helper.get_message")
    def test_auto_exception_handling_with_message_key(self, mock_get_message):
        """Test auto exception handling with message key lookup."""
        mock_get_message.return_value = "Localized error message"

        config = Config(
            session_attributes=TestSessionAttributes(),
            package_name="examples.basic_handler",
            auto_handle_exceptions=True,
            error_message="general.error_generic",
        )

        lex_helper = LexHelper(config=config)
        invalid_event = {"invalid": "event"}

        response = lex_helper.handler(invalid_event, {})

        # Should use localized message
        assert response["messages"][0]["content"] == "Localized error message"
        mock_get_message.assert_called_with("general.error_generic")

    @patch("lex_helper.get_message")
    def test_auto_exception_handling_message_key_fallback(self, mock_get_message):
        """Test auto exception handling falls back to direct string when message key fails."""
        mock_get_message.side_effect = Exception("Message not found")

        config = Config(
            session_attributes=TestSessionAttributes(),
            package_name="examples.basic_handler",
            auto_handle_exceptions=True,
            error_message="Direct error message",
        )

        lex_helper = LexHelper(config=config)
        invalid_event = {"invalid": "event"}

        response = lex_helper.handler(invalid_event, {})

        # Should fall back to using the string directly
        assert response["messages"][0]["content"] == "Direct error message"

    def test_disabled_auto_exception_handling_raises_exception(self):
        """Test that disabling auto exception handling allows exceptions to propagate."""
        config = Config(
            session_attributes=TestSessionAttributes(), package_name="examples.basic_handler", auto_handle_exceptions=False
        )

        lex_helper = LexHelper(config=config)
        invalid_event = {"invalid": "event"}

        # Should raise an exception when auto handling is disabled
        with pytest.raises(Exception):  # noqa: B017
            lex_helper.handler(invalid_event, {})

    @patch("lex_helper.get_message")
    def test_create_minimal_error_response_method(self, mock_get_message):
        """Test the _create_minimal_error_response method."""
        mock_get_message.side_effect = Exception("Message not found")

        config = Config(
            session_attributes=TestSessionAttributes(),
            package_name="examples.basic_handler",
            error_message="Test error message",
        )

        lex_helper = LexHelper(config=config)

        response = lex_helper._create_minimal_error_response()

        assert isinstance(response, dict)
        assert "sessionState" in response
        assert "messages" in response
        assert response["sessionState"]["dialogAction"]["type"] == "Close"
        assert response["sessionState"]["intent"]["name"] == "FallbackIntent"
        assert response["messages"][0]["contentType"] == "PlainText"
        assert response["messages"][0]["content"] == "Test error message"

    def test_create_minimal_error_response_without_custom_message(self):
        """Test _create_minimal_error_response without custom error message."""
        config = Config(session_attributes=TestSessionAttributes(), package_name="examples.basic_handler")

        lex_helper = LexHelper(config=config)

        response = lex_helper._create_minimal_error_response()

        # Should use default error message
        expected_message = "I'm sorry, I encountered an error while processing your request. Please try again."
        assert response["messages"][0]["content"] == expected_message


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_existing_config_usage_still_works(self):
        """Test that existing Config usage without new parameters still works."""
        # This is how Config was used before the enhancement
        config = Config(session_attributes=TestSessionAttributes(), package_name="examples.basic_handler")

        # Should work and have auto-exception handling enabled by default
        assert hasattr(config, "auto_handle_exceptions")
        assert config.auto_handle_exceptions is True
        assert config.error_message is None

        # Should be able to create LexHelper
        lex_helper = LexHelper(config=config)
        assert lex_helper.config.auto_handle_exceptions is True

    def test_manual_exception_handling_still_possible(self):
        """Test that users can still manually handle exceptions if they want."""
        config = Config(
            session_attributes=TestSessionAttributes(),
            package_name="examples.basic_handler",
            auto_handle_exceptions=False,  # Disable auto-handling
        )

        # Users can still manually handle exceptions in their lambda
        assert config.auto_handle_exceptions is False

    def test_all_config_options_work_together(self):
        """Test that all config options work together properly."""
        config = Config(
            session_attributes=TestSessionAttributes(),
            package_name="examples.basic_handler",
            auto_initialize_messages=False,
            auto_handle_exceptions=True,
            error_message="custom.error",
        )

        lex_helper = LexHelper(config=config)

        assert lex_helper.config.auto_initialize_messages is False
        assert lex_helper.config.auto_handle_exceptions is True
        assert lex_helper.config.error_message == "custom.error"
