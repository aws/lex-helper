# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Tests for disambiguation integration with LexHelper handler pipeline.
"""

from unittest.mock import patch

from lex_helper.core.disambiguation.types import DisambiguationConfig
from lex_helper.core.handler import Config, LexHelper
from lex_helper.core.types import Bot, DialogAction, Intent, Interpretation, LexRequest, SessionAttributes, SessionState


class TestSessionAttributes(SessionAttributes):
    """Test session attributes class."""

    pass


class TestDisambiguationIntegration:
    """Test disambiguation integration with LexHelper."""

    def test_disambiguation_disabled_by_default(self):
        """Test that disambiguation is disabled by default."""
        config = Config(session_attributes=TestSessionAttributes())
        helper = LexHelper(config)

        assert helper.config.enable_disambiguation is False
        assert helper.disambiguation_handler is None
        assert helper.disambiguation_analyzer is None

    def test_disambiguation_can_be_enabled(self):
        """Test that disambiguation can be enabled with configuration."""
        disambiguation_config = DisambiguationConfig(confidence_threshold=0.5, max_candidates=2)

        config = Config(
            session_attributes=TestSessionAttributes(),
            enable_disambiguation=True,
            disambiguation_config=disambiguation_config,
        )
        helper = LexHelper(config)

        assert helper.config.enable_disambiguation is True
        assert helper.disambiguation_handler is not None
        assert helper.disambiguation_analyzer is not None
        assert helper.disambiguation_analyzer.config.confidence_threshold == 0.5
        assert helper.disambiguation_analyzer.config.max_candidates == 2

    def test_disambiguation_with_default_config(self):
        """Test that disambiguation works with default configuration."""
        config = Config(session_attributes=TestSessionAttributes(), enable_disambiguation=True)
        helper = LexHelper(config)

        assert helper.disambiguation_handler is not None
        assert helper.disambiguation_analyzer.config.confidence_threshold == 0.6  # default
        assert helper.disambiguation_analyzer.config.max_candidates == 3  # default

    def test_handler_pipeline_includes_disambiguation(self):
        """Test that the handler pipeline includes disambiguation when enabled."""
        config = Config(session_attributes=TestSessionAttributes(), enable_disambiguation=True)
        helper = LexHelper(config)

        # Check that disambiguation handler method exists
        assert hasattr(helper, "disambiguation_intent_handler")
        assert callable(helper.disambiguation_intent_handler)

    def test_handler_pipeline_without_disambiguation(self):
        """Test that the handler pipeline works without disambiguation."""
        config = Config(session_attributes=TestSessionAttributes())
        helper = LexHelper(config)

        # Should still have regular handler
        assert hasattr(helper, "regular_intent_handler")
        assert callable(helper.regular_intent_handler)

    def create_test_lex_request(self, interpretations=None):
        """Create a test LexRequest with interpretations."""
        if interpretations is None:
            interpretations = [
                Interpretation(intent=Intent(name="BookFlight", slots={}), nluConfidence=0.4),
                Interpretation(intent=Intent(name="ChangeFlight", slots={}), nluConfidence=0.3),
            ]

        return LexRequest(
            sessionId="test-session",
            inputTranscript="I want to change my booking",
            interpretations=interpretations,
            bot=Bot(name="TestBot", localeId="en_US"),
            sessionState=SessionState(
                intent=Intent(name="BookFlight"),
                sessionAttributes=TestSessionAttributes(),
                dialogAction=DialogAction(type="ElicitIntent"),
            ),
        )

    def test_disambiguation_handler_can_be_called(self):
        """Test that disambiguation handler can be called without errors."""
        config = Config(session_attributes=TestSessionAttributes(), enable_disambiguation=True)
        helper = LexHelper(config)

        lex_request = self.create_test_lex_request()

        # Should be able to call the handler (may return None if no disambiguation needed)
        result = helper.disambiguation_intent_handler(lex_request)
        # Result can be None (no disambiguation) or a LexResponse
        assert result is None or hasattr(result, "sessionState")

    def test_confidence_analysis_integration(self):
        """Test that confidence analysis works through the integration."""
        config = Config(session_attributes=TestSessionAttributes(), enable_disambiguation=True)
        helper = LexHelper(config)

        # Test high confidence - should not disambiguate
        high_confidence_request = self.create_test_lex_request(
            [Interpretation(intent=Intent(name="BookFlight", slots={}), nluConfidence=0.9)]
        )

        analysis = helper.disambiguation_analyzer.analyze_request(high_confidence_request)

        assert not analysis.should_disambiguate

        # Test low confidence - should disambiguate
        low_confidence_request = self.create_test_lex_request(
            [
                Interpretation(intent=Intent(name="BookFlight", slots={}), nluConfidence=0.4),
                Interpretation(intent=Intent(name="ChangeFlight", slots={}), nluConfidence=0.3),
            ]
        )

        analysis = helper.disambiguation_analyzer.analyze_request(low_confidence_request)

        assert analysis.should_disambiguate
        assert len(analysis.candidates) > 0

    def test_fallback_when_disambiguation_unavailable(self):
        """Test that system falls back gracefully when disambiguation is unavailable."""
        # Mock the import to simulate disambiguation not being available
        with patch("lex_helper.core.handler.disambiguation_available", False):
            config = Config(
                session_attributes=TestSessionAttributes(),
                enable_disambiguation=True,  # Request disambiguation but it's not available
            )
            helper = LexHelper(config)

            # Should fall back to no disambiguation
            assert helper.disambiguation_handler is None
            assert helper.disambiguation_analyzer is None

    def test_seamless_fallback_to_existing_behavior(self):
        """Test that when disambiguation is disabled, behavior is unchanged."""
        # Create two helpers - one with and one without disambiguation
        config_without = Config(session_attributes=TestSessionAttributes())
        helper_without = LexHelper(config_without)

        config_with = Config(session_attributes=TestSessionAttributes(), enable_disambiguation=True)
        helper_with = LexHelper(config_with)

        # Both should have regular intent handler
        assert hasattr(helper_without, "regular_intent_handler")
        assert hasattr(helper_with, "regular_intent_handler")

        # Only the enabled one should have disambiguation components
        assert helper_without.disambiguation_handler is None
        assert helper_with.disambiguation_handler is not None

    def test_config_validation(self):
        """Test that configuration is properly validated."""
        # Test with custom disambiguation config
        custom_config = DisambiguationConfig(confidence_threshold=0.8, max_candidates=5)

        config = Config(
            session_attributes=TestSessionAttributes(), enable_disambiguation=True, disambiguation_config=custom_config
        )
        helper = LexHelper(config)

        # Verify the custom config is used
        assert helper.disambiguation_analyzer.config.confidence_threshold == 0.8
        assert helper.disambiguation_analyzer.config.max_candidates == 5
