# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for automatic MessageManager initialization."""

from typing import Any
from unittest.mock import patch

from lex_helper import Config, LexHelper, SessionAttributes


class TestSessionAttributes(SessionAttributes):
    """Test session attributes for message manager tests."""

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


class TestMessageManagerAutoInitialization:
    """Test cases for automatic MessageManager initialization."""

    def test_config_model_validation(self):
        """Test that Config model validates auto_initialize_messages parameter."""
        # Test with boolean True
        config1 = Config(session_attributes=TestSessionAttributes(), auto_initialize_messages=True)
        assert config1.auto_initialize_messages is True

        # Test with boolean False
        config2 = Config(session_attributes=TestSessionAttributes(), auto_initialize_messages=False)
        assert config2.auto_initialize_messages is False

        # Test default value
        config3 = Config(session_attributes=TestSessionAttributes())
        assert config3.auto_initialize_messages is True

    def test_auto_initialization_enabled_by_default(self):
        """Test that MessageManager auto-initialization is enabled by default."""
        config = Config(session_attributes=TestSessionAttributes(), package_name="examples.basic_handler")

        # Should be enabled by default
        assert config.auto_initialize_messages is True

        lex_helper = LexHelper(config=config)
        assert lex_helper.config.auto_initialize_messages is True

    def test_auto_initialization_can_be_disabled(self):
        """Test that MessageManager auto-initialization can be disabled."""
        config = Config(
            session_attributes=TestSessionAttributes(), package_name="examples.basic_handler", auto_initialize_messages=False
        )

        assert config.auto_initialize_messages is False

        lex_helper = LexHelper(config=config)
        assert lex_helper.config.auto_initialize_messages is False

    def test_initialize_message_manager_method_exists(self):
        """Test that the _initialize_message_manager method exists and is callable."""
        config = Config(session_attributes=TestSessionAttributes(), package_name="examples.basic_handler")

        lex_helper = LexHelper(config=config)

        # Method should exist
        assert hasattr(lex_helper, "_initialize_message_manager")
        assert callable(lex_helper._initialize_message_manager)

    @patch("lex_helper.set_locale")
    def test_initialize_message_manager_calls_set_locale(self, mock_set_locale):
        """Test that _initialize_message_manager calls set_locale with correct locale."""
        config = Config(session_attributes=TestSessionAttributes(), package_name="examples.basic_handler")

        lex_helper = LexHelper(config=config)

        # Create a mock lex_payload
        from lex_helper import LexRequest

        event = create_test_event(locale_id="es_ES")
        lex_payload = LexRequest(**event)

        # Call the method directly
        lex_helper._initialize_message_manager(lex_payload)

        # Verify set_locale was called with correct locale
        mock_set_locale.assert_called_once_with("es_ES")

    @patch("lex_helper.set_locale")
    @patch("lex_helper.core.handler.logger")
    def test_initialize_message_manager_handles_errors(self, mock_logger, mock_set_locale):
        """Test that _initialize_message_manager handles errors gracefully."""
        # Make set_locale raise an exception
        mock_set_locale.side_effect = Exception("MessageManager initialization failed")

        config = Config(session_attributes=TestSessionAttributes(), package_name="examples.basic_handler")

        lex_helper = LexHelper(config=config)

        # Create a mock lex_payload
        from lex_helper import LexRequest

        event = create_test_event(locale_id="en_US")
        lex_payload = LexRequest(**event)

        # Should not raise exception
        lex_helper._initialize_message_manager(lex_payload)

        # Verify error was logged
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0]
        assert "Failed to initialize MessageManager" in warning_call[0]


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_existing_config_still_works(self):
        """Test that existing Config usage without auto_initialize_messages still works."""
        # This is how Config was used before the enhancement
        config = Config(session_attributes=TestSessionAttributes(), package_name="examples.basic_handler")

        # Should work and have auto-initialization enabled by default
        assert hasattr(config, "auto_initialize_messages")
        assert config.auto_initialize_messages is True

        # Should be able to create LexHelper
        lex_helper = LexHelper(config=config)
        assert lex_helper.config.auto_initialize_messages is True

    def test_manual_message_manager_initialization_still_possible(self):
        """Test that users can still manually initialize MessageManager if they want."""
        config = Config(
            session_attributes=TestSessionAttributes(),
            package_name="examples.basic_handler",
            auto_initialize_messages=False,  # Disable auto-initialization
        )

        # Users can still manually call set_locale if they want
        from lex_helper import set_locale

        set_locale("en_US")

        # This should work without auto-initialization
        assert config.auto_initialize_messages is False
