# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for the DisambiguationHandler class.

Tests cover response generation, message formatting, user selection processing,
and integration with the lex-helper dialog system.
"""

import json
from unittest.mock import Mock, patch

import pytest

from lex_helper.core.disambiguation.handler import DisambiguationHandler
from lex_helper.core.disambiguation.types import (
    DisambiguationConfig,
    IntentCandidate,
)
from lex_helper.core.types import (
    Bot,
    Intent,
    LexPlainText,
    LexRequest,
    SessionAttributes,
    SessionState,
)


class TestSessionAttributes(SessionAttributes):
    """Test session attributes class."""

    pass


@pytest.fixture
def sample_candidates():
    """Sample intent candidates for testing."""
    return [
        IntentCandidate(
            intent_name="BookFlight",
            confidence_score=0.7,
            display_name="Book a Flight",
            description="Book a new flight reservation",
        ),
        IntentCandidate(
            intent_name="ChangeFlight",
            confidence_score=0.6,
            display_name="Change Flight",
            description="Modify an existing flight reservation",
        ),
        IntentCandidate(
            intent_name="CancelFlight",
            confidence_score=0.5,
            display_name="Cancel Flight",
            description="Cancel a flight reservation",
        ),
    ]


@pytest.fixture
def sample_lex_request():
    """Sample LexRequest for testing."""
    return LexRequest(
        sessionId="test-session",
        inputTranscript="I want to book a flight",
        bot=Bot(localeId="en_US"),
        sessionState=SessionState(intent=Intent(name="FallbackIntent"), sessionAttributes=TestSessionAttributes()),
    )


@pytest.fixture
def disambiguation_handler():
    """DisambiguationHandler instance for testing."""
    config = DisambiguationConfig(
        confidence_threshold=0.6,
        max_candidates=3,
        custom_messages={
            "disambiguation.booking": "I can help you book, change, or cancel a flight. Which would you like to do?"
        },
        custom_intent_groups={"booking": ["BookFlight", "ChangeFlight", "CancelFlight"]},
    )
    return DisambiguationHandler(config)


class TestDisambiguationHandler:
    """Test cases for DisambiguationHandler."""

    def test_init_with_default_config(self):
        """Test handler initialization with default config."""
        handler = DisambiguationHandler()
        assert handler.config is not None
        assert handler.config.confidence_threshold == 0.6
        assert handler.config.max_candidates == 3

    def test_init_with_custom_config(self):
        """Test handler initialization with custom config."""
        config = DisambiguationConfig(confidence_threshold=0.5, max_candidates=2)
        handler = DisambiguationHandler(config)
        assert handler.config.confidence_threshold == 0.5
        assert handler.config.max_candidates == 2

    @patch("lex_helper.core.disambiguation.handler.elicit_intent")
    @patch("lex_helper.core.disambiguation.handler.get_message")
    def test_handle_disambiguation_basic(
        self, mock_get_message, mock_elicit_intent, disambiguation_handler, sample_lex_request, sample_candidates
    ):
        """Test basic disambiguation response generation."""
        mock_get_message.return_value = "I can help you with several things. What would you like to do?"
        mock_response = Mock()
        mock_elicit_intent.return_value = mock_response

        result = disambiguation_handler.handle_disambiguation(sample_lex_request, sample_candidates)

        assert result == mock_response
        mock_elicit_intent.assert_called_once()

        # Check that disambiguation state was stored
        session_attrs = sample_lex_request.sessionState.sessionAttributes
        assert session_attrs.disambiguation_active is True

    @patch("lex_helper.core.disambiguation.handler.elicit_intent")
    def test_handle_disambiguation_limits_candidates(self, mock_elicit_intent, sample_lex_request, sample_candidates):
        """Test that handler limits candidates to max_candidates."""
        config = DisambiguationConfig(max_candidates=2)
        handler = DisambiguationHandler(config)

        mock_elicit_intent.return_value = Mock()

        handler.handle_disambiguation(sample_lex_request, sample_candidates)

        # Check stored candidates are limited
        session_attrs = sample_lex_request.sessionState.sessionAttributes
        candidates_json = session_attrs.disambiguation_candidates
        stored_candidates = json.loads(candidates_json)
        assert len(stored_candidates) == 2

    @patch("lex_helper.core.disambiguation.handler.get_message")
    def test_create_clarification_messages(self, mock_get_message, disambiguation_handler, sample_candidates):
        """Test clarification message creation."""
        # Mock the message system to return the expected message for the booking group
        mock_get_message.return_value = "I can help you book, change, or cancel a flight. Which would you like to do?"

        messages = disambiguation_handler._create_clarification_messages(sample_candidates)

        # Should have at least one plain text message
        assert len(messages) >= 1
        assert isinstance(messages[0], LexPlainText)
        # Should use the mocked message
        assert messages[0].content == "I can help you book, change, or cancel a flight. Which would you like to do?"

    @patch("lex_helper.core.disambiguation.handler.get_message")
    def test_get_custom_clarification_message(self, mock_get_message, disambiguation_handler, sample_candidates):
        """Test custom clarification message retrieval."""
        # Mock the message system to return the expected message
        mock_get_message.return_value = "I can help you book, change, or cancel a flight. Which would you like to do?"

        # Test with custom intent group message - should use the configured custom message
        result = disambiguation_handler._get_custom_clarification_message(sample_candidates)
        assert result == "I can help you book, change, or cancel a flight. Which would you like to do?"

    def test_store_and_retrieve_disambiguation_state(self, disambiguation_handler, sample_lex_request, sample_candidates):
        """Test storing and retrieving disambiguation state."""
        # Store state
        disambiguation_handler._store_disambiguation_state(sample_lex_request, sample_candidates)

        # Check state is stored
        assert disambiguation_handler._is_disambiguation_response(sample_lex_request)

        # Retrieve candidates
        retrieved = disambiguation_handler._get_stored_candidates(sample_lex_request)
        assert retrieved is not None
        assert len(retrieved) == len(sample_candidates)
        assert retrieved[0].intent_name == sample_candidates[0].intent_name

    def test_determine_selected_intent_exact_match(self, sample_candidates):
        """Test intent selection with exact matches."""
        handler = DisambiguationHandler()

        # Test exact intent name match
        result = handler._determine_selected_intent("BookFlight", sample_candidates)
        assert result == "BookFlight"

        # Test exact display name match
        result = handler._determine_selected_intent("Book a Flight", sample_candidates)
        assert result == "BookFlight"

    def test_determine_selected_intent_partial_match(self, sample_candidates):
        """Test intent selection with partial matches."""
        handler = DisambiguationHandler()

        # Test partial display name match
        result = handler._determine_selected_intent("book", sample_candidates)
        assert result == "BookFlight"

    def test_determine_selected_intent_number_selection(self, sample_candidates):
        """Test intent selection with number input."""
        handler = DisambiguationHandler()

        # Test number selection
        result = handler._determine_selected_intent("1", sample_candidates)
        assert result == "BookFlight"

        result = handler._determine_selected_intent("2", sample_candidates)
        assert result == "ChangeFlight"

    def test_determine_selected_intent_letter_selection(self, sample_candidates):
        """Test intent selection with letter input."""
        handler = DisambiguationHandler()

        # Test letter selection (a=0, b=1, c=2)
        result = handler._determine_selected_intent("a", sample_candidates)
        assert result == "BookFlight"

        result = handler._determine_selected_intent("b", sample_candidates)
        assert result == "ChangeFlight"

    def test_determine_selected_intent_no_match(self, sample_candidates):
        """Test intent selection with no match."""
        handler = DisambiguationHandler()

        result = handler._determine_selected_intent("invalid input", sample_candidates)
        assert result is None

    def test_update_request_for_selected_intent(self, sample_lex_request):
        """Test updating request for selected intent."""
        handler = DisambiguationHandler()

        handler._update_request_for_selected_intent(sample_lex_request, "BookFlight")

        assert sample_lex_request.sessionState.intent.name == "BookFlight"
        assert sample_lex_request.sessionState.intent.state == "InProgress"
        assert sample_lex_request.sessionState.intent.slots == {}

    def test_clear_disambiguation_state(self, disambiguation_handler, sample_lex_request, sample_candidates):
        """Test clearing disambiguation state."""
        # First store state
        disambiguation_handler._store_disambiguation_state(sample_lex_request, sample_candidates)
        assert disambiguation_handler._is_disambiguation_response(sample_lex_request)

        # Clear state
        disambiguation_handler._clear_disambiguation_state(sample_lex_request)
        assert not disambiguation_handler._is_disambiguation_response(sample_lex_request)

    @patch("lex_helper.core.disambiguation.handler.close")
    @patch("lex_helper.core.disambiguation.handler.get_message")
    def test_create_fallback_response(self, mock_get_message, mock_close, disambiguation_handler, sample_lex_request):
        """Test fallback response creation."""
        mock_get_message.return_value = "I'm not sure what you're looking for."
        mock_response = Mock()
        mock_close.return_value = mock_response

        result = disambiguation_handler._create_fallback_response(sample_lex_request)

        assert result == mock_response
        mock_close.assert_called_once()

    def test_process_disambiguation_response_not_disambiguation(self, disambiguation_handler, sample_lex_request):
        """Test processing when request is not a disambiguation response."""
        result = disambiguation_handler.process_disambiguation_response(sample_lex_request)
        assert result is None

    def test_process_disambiguation_response_no_candidates(self, disambiguation_handler, sample_lex_request):
        """Test processing when no stored candidates exist."""
        # Set disambiguation active but no candidates
        session_attrs = sample_lex_request.sessionState.sessionAttributes
        session_attrs.disambiguation_active = True

        with patch.object(disambiguation_handler, "_create_fallback_response") as mock_fallback:
            mock_response = Mock()
            mock_fallback.return_value = mock_response

            result = disambiguation_handler.process_disambiguation_response(sample_lex_request)
            assert result == mock_response

    def test_process_disambiguation_response_success(self, disambiguation_handler, sample_lex_request, sample_candidates):
        """Test successful disambiguation response processing."""
        # Store disambiguation state
        disambiguation_handler._store_disambiguation_state(sample_lex_request, sample_candidates)

        # Set user input to select first option
        sample_lex_request.inputTranscript = "1"

        result = disambiguation_handler.process_disambiguation_response(sample_lex_request)

        # Should return None to let regular handler process
        assert result is None

        # Should have updated intent
        assert sample_lex_request.sessionState.intent.name == "BookFlight"

        # Should have cleared disambiguation state
        assert not disambiguation_handler._is_disambiguation_response(sample_lex_request)

    def test_process_disambiguation_response_invalid_selection(
        self, disambiguation_handler, sample_lex_request, sample_candidates
    ):
        """Test disambiguation response with invalid selection."""
        # Store disambiguation state
        disambiguation_handler._store_disambiguation_state(sample_lex_request, sample_candidates)

        # Set invalid user input
        sample_lex_request.inputTranscript = "invalid"

        with patch.object(disambiguation_handler, "_create_fallback_response") as mock_fallback:
            mock_response = Mock()
            mock_fallback.return_value = mock_response

            result = disambiguation_handler.process_disambiguation_response(sample_lex_request)
            assert result == mock_response

    def test_get_clarification_text_two_options(self, disambiguation_handler):
        """Test clarification text for two options."""
        candidates = [
            IntentCandidate("Intent1", 0.7, "Option 1", "Description 1"),
            IntentCandidate("Intent2", 0.6, "Option 2", "Description 2"),
        ]

        with patch("lex_helper.core.disambiguation.handler.get_message") as mock_get_message:
            mock_get_message.return_value = "Two options message"

            result = disambiguation_handler._get_clarification_text(candidates)

            mock_get_message.assert_called_with(
                "disambiguation.two_options", "I can help you with two things. Which would you like to do?"
            )
            assert result == "Two options message"

    def test_get_clarification_text_multiple_options(self, disambiguation_handler):
        """Test clarification text for multiple options."""
        candidates = [
            IntentCandidate("Intent1", 0.7, "Option 1", "Description 1"),
            IntentCandidate("Intent2", 0.6, "Option 2", "Description 2"),
            IntentCandidate("Intent3", 0.5, "Option 3", "Description 3"),
        ]

        with patch("lex_helper.core.disambiguation.handler.get_message") as mock_get_message:
            mock_get_message.return_value = "Multiple options message"

            result = disambiguation_handler._get_clarification_text(candidates)

            mock_get_message.assert_called_with(
                "disambiguation.multiple_options", "I can help you with several things. What would you like to do?"
            )
            assert result == "Multiple options message"


if __name__ == "__main__":
    pytest.main([__file__])
