# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Tests for Bedrock-powered disambiguation functionality.
"""

from unittest.mock import patch

import pytest

from lex_helper.core.disambiguation.bedrock_generator import BedrockDisambiguationGenerator
from lex_helper.core.disambiguation.types import BedrockDisambiguationConfig, IntentCandidate


class TestBedrockDisambiguationGenerator:
    """Test the Bedrock disambiguation generator."""

    @pytest.fixture
    def bedrock_config(self):
        """Create a test Bedrock configuration."""
        return BedrockDisambiguationConfig(
            enabled=True,
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            max_tokens=150,
            temperature=0.3,
            fallback_to_static=True,
        )

    @pytest.fixture
    def disabled_bedrock_config(self):
        """Create a disabled Bedrock configuration."""
        return BedrockDisambiguationConfig(enabled=False)

    @pytest.fixture
    def sample_candidates(self):
        """Create sample intent candidates."""
        return [
            IntentCandidate(
                intent_name="BookFlight",
                confidence_score=0.4,
                display_name="Book Flight",
                description="Book a new flight reservation",
            ),
            IntentCandidate(
                intent_name="ChangeFlight",
                confidence_score=0.35,
                display_name="Change Flight",
                description="Modify an existing flight booking",
            ),
        ]

    def test_generator_initialization_enabled(self, bedrock_config):
        """Test generator initialization when enabled."""
        generator = BedrockDisambiguationGenerator(bedrock_config)
        assert generator.config == bedrock_config

    def test_generator_initialization_disabled(self, disabled_bedrock_config):
        """Test generator initialization when disabled."""
        generator = BedrockDisambiguationGenerator(disabled_bedrock_config)
        assert generator.config == disabled_bedrock_config

    def test_generate_clarification_message_disabled(self, disabled_bedrock_config, sample_candidates):
        """Test clarification message generation when Bedrock is disabled."""
        generator = BedrockDisambiguationGenerator(disabled_bedrock_config)

        result = generator.generate_clarification_message("I need help", sample_candidates)

        assert result == "I can help you with two things. Which would you like to do?"

    @patch("lex_helper.core.disambiguation.bedrock_generator.invoke_bedrock_simple_converse")
    def test_generate_clarification_message_success(self, mock_invoke, bedrock_config, sample_candidates):
        """Test successful clarification message generation."""
        mock_invoke.return_value = {
            "text": "I can help you book a new flight or change your existing booking. Which would you prefer?",
            "usage": {},
        }

        generator = BedrockDisambiguationGenerator(bedrock_config)
        result = generator.generate_clarification_message("I need help with my flight", sample_candidates)

        assert "book a new flight or change" in result
        mock_invoke.assert_called_once()

    @patch("lex_helper.core.disambiguation.bedrock_generator.invoke_bedrock_simple_converse")
    def test_generate_clarification_message_bedrock_error_with_fallback(
        self, mock_invoke, bedrock_config, sample_candidates
    ):
        """Test clarification message generation with Bedrock error and fallback enabled."""
        from lex_helper.core.invoke_bedrock import BedrockInvocationError

        mock_invoke.side_effect = BedrockInvocationError("Model not available")

        generator = BedrockDisambiguationGenerator(bedrock_config)
        result = generator.generate_clarification_message("I need help", sample_candidates)

        # Should fall back to static message
        assert result == "I can help you with two things. Which would you like to do?"

    @patch("lex_helper.core.disambiguation.bedrock_generator.invoke_bedrock_simple_converse")
    def test_generate_clarification_message_bedrock_error_no_fallback(self, mock_invoke, sample_candidates):
        """Test clarification message generation with Bedrock error and no fallback."""
        from lex_helper.core.invoke_bedrock import BedrockInvocationError

        config = BedrockDisambiguationConfig(enabled=True, fallback_to_static=False)
        mock_invoke.side_effect = BedrockInvocationError("Model not available")

        generator = BedrockDisambiguationGenerator(config)

        with pytest.raises(BedrockInvocationError):
            generator.generate_clarification_message("I need help", sample_candidates)

    def test_generate_button_labels_disabled(self, disabled_bedrock_config, sample_candidates):
        """Test button label generation when Bedrock is disabled."""
        generator = BedrockDisambiguationGenerator(disabled_bedrock_config)

        result = generator.generate_button_labels(sample_candidates)

        assert result == ["Book Flight", "Change Flight"]

    @patch("lex_helper.core.disambiguation.bedrock_generator.invoke_bedrock_simple_converse")
    def test_generate_button_labels_success_json(self, mock_invoke, bedrock_config, sample_candidates):
        """Test successful button label generation with JSON response."""
        mock_invoke.return_value = {
            "text": '["Book new flight", "Modify booking"]',
            "usage": {},
        }

        generator = BedrockDisambiguationGenerator(bedrock_config)
        result = generator.generate_button_labels(sample_candidates, "I need help with my flight")

        assert result == ["Book new flight", "Modify booking"]
        mock_invoke.assert_called_once()

    @patch("lex_helper.core.disambiguation.bedrock_generator.invoke_bedrock_simple_converse")
    def test_generate_button_labels_success_text_extraction(self, mock_invoke, bedrock_config, sample_candidates):
        """Test button label generation with text extraction fallback."""
        mock_invoke.return_value = {
            "text": "Here are the options:\n- Book new flight\n- Modify booking",
            "usage": {},
        }

        generator = BedrockDisambiguationGenerator(bedrock_config)
        result = generator.generate_button_labels(sample_candidates)

        assert result == ["Book new flight", "Modify booking"]

    @patch("lex_helper.core.disambiguation.bedrock_generator.invoke_bedrock_simple_converse")
    def test_generate_button_labels_parsing_failure(self, mock_invoke, bedrock_config, sample_candidates):
        """Test button label generation when parsing fails."""
        mock_invoke.return_value = {
            "text": "Some unparseable response that doesn't match expected format",
            "usage": {},
        }

        generator = BedrockDisambiguationGenerator(bedrock_config)
        result = generator.generate_button_labels(sample_candidates)

        # Should fall back to display names
        assert result == ["Book Flight", "Change Flight"]

    def test_extract_labels_from_text_success(self, bedrock_config):
        """Test successful label extraction from text."""
        generator = BedrockDisambiguationGenerator(bedrock_config)

        text = "- Book new flight\n- Modify booking"
        result = generator._extract_labels_from_text(text, 2)

        assert result == ["Book new flight", "Modify booking"]

    def test_extract_labels_from_text_wrong_count(self, bedrock_config):
        """Test label extraction with wrong number of labels."""
        generator = BedrockDisambiguationGenerator(bedrock_config)

        text = "- Book new flight"  # Only one label, expecting two
        result = generator._extract_labels_from_text(text, 2)

        assert result is None

    def test_build_clarification_prompt(self, bedrock_config, sample_candidates):
        """Test clarification prompt building."""
        generator = BedrockDisambiguationGenerator(bedrock_config)

        prompt = generator._build_clarification_prompt("I need help", sample_candidates)

        assert "I need help" in prompt
        assert "Book Flight" in prompt
        assert "Change Flight" in prompt
        assert "ambiguous" in prompt

    def test_build_button_labels_prompt(self, bedrock_config, sample_candidates):
        """Test button labels prompt building."""
        generator = BedrockDisambiguationGenerator(bedrock_config)

        prompt = generator._build_button_labels_prompt(sample_candidates, "I need help")

        assert "BookFlight" in prompt
        assert "ChangeFlight" in prompt
        assert "I need help" in prompt
        assert "JSON array" in prompt

    def test_get_fallback_message_two_candidates(self, bedrock_config, sample_candidates):
        """Test fallback message for two candidates."""
        generator = BedrockDisambiguationGenerator(bedrock_config)

        result = generator._get_fallback_message(sample_candidates)

        assert result == "I can help you with two things. Which would you like to do?"

    def test_get_fallback_message_multiple_candidates(self, bedrock_config):
        """Test fallback message for multiple candidates."""
        candidates = [
            IntentCandidate("Intent1", 0.3, "Display 1", "Desc 1"),
            IntentCandidate("Intent2", 0.3, "Display 2", "Desc 2"),
            IntentCandidate("Intent3", 0.3, "Display 3", "Desc 3"),
        ]

        generator = BedrockDisambiguationGenerator(bedrock_config)
        result = generator._get_fallback_message(candidates)

        assert result == "I can help you with several things. What would you like to do?"
