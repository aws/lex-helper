# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for DisambiguationAnalyzer.

Tests the core functionality of analyzing Lex requests for disambiguation
including confidence score extraction, threshold-based decisions, and
candidate generation.
"""

from lex_helper.core.disambiguation import (
    DisambiguationAnalyzer,
    DisambiguationConfig,
)
from lex_helper.core.types import (
    Intent,
    Interpretation,
    LexRequest,
    SessionAttributes,
)


class TestSessionAttributes(SessionAttributes):
    """Test session attributes class."""

    pass


class TestDisambiguationAnalyzer:
    """Test cases for DisambiguationAnalyzer."""

    def test_init_with_default_config(self):
        """Test analyzer initialization with default configuration."""
        analyzer = DisambiguationAnalyzer()

        assert analyzer.config is not None
        assert analyzer.config.confidence_threshold == 0.6
        assert analyzer.config.max_candidates == 3
        assert analyzer.config.min_candidates == 2

    def test_init_with_custom_config(self):
        """Test analyzer initialization with custom configuration."""
        config = DisambiguationConfig(
            confidence_threshold=0.8,
            max_candidates=5,
            min_candidates=3,
        )
        analyzer = DisambiguationAnalyzer(config)

        assert analyzer.config.confidence_threshold == 0.8
        assert analyzer.config.max_candidates == 5
        assert analyzer.config.min_candidates == 3

    def test_extract_intent_scores_basic(self):
        """Test extracting intent scores from Lex interpretations."""
        analyzer = DisambiguationAnalyzer()

        # Create test interpretations
        interpretations = [
            Interpretation(intent=Intent(name="BookFlight"), nluConfidence=0.8),
            Interpretation(intent=Intent(name="CancelFlight"), nluConfidence=0.3),
            Interpretation(intent=Intent(name="ChangeFlight"), nluConfidence=0.1),
        ]

        lex_request = LexRequest[TestSessionAttributes](
            inputTranscript="I want to book a flight", interpretations=interpretations
        )

        scores = analyzer.extract_intent_scores(lex_request)

        assert scores["BookFlight"] == 0.8
        assert scores["CancelFlight"] == 0.3
        assert scores["ChangeFlight"] == 0.1

    def test_extract_intent_scores_missing_confidence(self):
        """Test extracting scores when nluConfidence is None."""
        analyzer = DisambiguationAnalyzer()

        interpretations = [
            Interpretation(intent=Intent(name="BookFlight"), nluConfidence=None),
        ]

        lex_request = LexRequest[TestSessionAttributes](interpretations=interpretations)

        scores = analyzer.extract_intent_scores(lex_request)

        assert scores["BookFlight"] == 0.0

    def test_should_disambiguate_high_confidence(self):
        """Test that high confidence scores don't trigger disambiguation."""
        analyzer = DisambiguationAnalyzer()

        scores = {
            "BookFlight": 0.9,
            "CancelFlight": 0.1,
            "ChangeFlight": 0.05,
        }

        result = analyzer.should_disambiguate(scores, 0.6)

        assert result is False

    def test_should_disambiguate_low_confidence(self):
        """Test that low confidence scores trigger disambiguation."""
        analyzer = DisambiguationAnalyzer()

        scores = {
            "BookFlight": 0.4,
            "CancelFlight": 0.3,
            "ChangeFlight": 0.2,
        }

        result = analyzer.should_disambiguate(scores, 0.6)

        assert result is True

    def test_should_disambiguate_similar_high_scores(self):
        """Test that similar high scores trigger disambiguation."""
        analyzer = DisambiguationAnalyzer()

        scores = {
            "BookFlight": 0.7,
            "CancelFlight": 0.65,
            "ChangeFlight": 0.1,
        }

        result = analyzer.should_disambiguate(scores, 0.6)

        assert result is True

    def test_should_disambiguate_insufficient_candidates(self):
        """Test that insufficient candidates don't trigger disambiguation."""
        analyzer = DisambiguationAnalyzer()

        scores = {
            "BookFlight": 0.4,
        }

        result = analyzer.should_disambiguate(scores, 0.6)

        assert result is False

    def test_should_disambiguate_empty_scores(self):
        """Test behavior with empty scores."""
        analyzer = DisambiguationAnalyzer()

        scores = {}

        result = analyzer.should_disambiguate(scores, 0.6)

        assert result is False

    def test_analyze_request_no_disambiguation_needed(self):
        """Test full analysis when no disambiguation is needed."""
        analyzer = DisambiguationAnalyzer()

        interpretations = [
            Interpretation(intent=Intent(name="BookFlight"), nluConfidence=0.9),
            Interpretation(intent=Intent(name="CancelFlight"), nluConfidence=0.1),
        ]

        lex_request = LexRequest[TestSessionAttributes](
            inputTranscript="I want to book a flight", interpretations=interpretations
        )

        result = analyzer.analyze_request(lex_request)

        assert result.should_disambiguate is False
        assert len(result.candidates) == 0
        assert result.confidence_scores["BookFlight"] == 0.9
        assert result.confidence_scores["CancelFlight"] == 0.1

    def test_analyze_request_disambiguation_needed(self):
        """Test full analysis when disambiguation is needed."""
        analyzer = DisambiguationAnalyzer()

        interpretations = [
            Interpretation(intent=Intent(name="BookFlight", slots={"OriginCity": None}), nluConfidence=0.4),
            Interpretation(intent=Intent(name="CancelFlight", slots={"ReservationNumber": None}), nluConfidence=0.3),
        ]

        lex_request = LexRequest[TestSessionAttributes](
            inputTranscript="I need help with my flight", interpretations=interpretations
        )

        result = analyzer.analyze_request(lex_request)

        assert result.should_disambiguate is True
        assert len(result.candidates) == 2
        assert result.candidates[0].intent_name == "BookFlight"
        assert result.candidates[0].confidence_score == 0.4
        assert result.candidates[1].intent_name == "CancelFlight"
        assert result.candidates[1].confidence_score == 0.3

    def test_generate_candidates_with_slots(self):
        """Test candidate generation includes slot information."""
        analyzer = DisambiguationAnalyzer()

        scores = {
            "BookFlight": 0.4,
            "CancelFlight": 0.3,
        }

        interpretations = [
            Interpretation(
                intent=Intent(name="BookFlight", slots={"OriginCity": None, "DestinationCity": None}), nluConfidence=0.4
            ),
            Interpretation(intent=Intent(name="CancelFlight", slots={"ReservationNumber": None}), nluConfidence=0.3),
        ]

        lex_request = LexRequest[TestSessionAttributes](interpretations=interpretations)

        candidates = analyzer._generate_candidates(scores, lex_request)

        assert len(candidates) == 2
        assert candidates[0].required_slots == ["OriginCity", "DestinationCity"]
        assert candidates[1].required_slots == ["ReservationNumber"]

    def test_get_display_name_camel_case(self):
        """Test display name generation for CamelCase intents."""
        analyzer = DisambiguationAnalyzer()

        display_name = analyzer._get_display_name("BookFlight")

        assert display_name == "Book Flight"

    def test_get_display_name_snake_case(self):
        """Test display name generation for snake_case intents."""
        analyzer = DisambiguationAnalyzer()

        display_name = analyzer._get_display_name("book_flight")

        assert display_name == "Book Flight"

    def test_get_display_name_mixed_case(self):
        """Test display name generation for mixed case intents."""
        analyzer = DisambiguationAnalyzer()

        display_name = analyzer._get_display_name("BookFlight_Request")

        assert display_name == "Book Flight Request"

    def test_find_interpretation_by_intent(self):
        """Test finding interpretation by intent name."""
        analyzer = DisambiguationAnalyzer()

        interpretations = [
            Interpretation(intent=Intent(name="BookFlight"), nluConfidence=0.8),
            Interpretation(intent=Intent(name="CancelFlight"), nluConfidence=0.3),
        ]

        lex_request = LexRequest[TestSessionAttributes](interpretations=interpretations)

        interpretation = analyzer._find_interpretation_by_intent(lex_request, "CancelFlight")

        assert interpretation is not None
        assert interpretation.intent.name == "CancelFlight"
        assert interpretation.nluConfidence == 0.3

    def test_find_interpretation_by_intent_not_found(self):
        """Test finding interpretation when intent doesn't exist."""
        analyzer = DisambiguationAnalyzer()

        interpretations = [
            Interpretation(intent=Intent(name="BookFlight"), nluConfidence=0.8),
        ]

        lex_request = LexRequest[TestSessionAttributes](interpretations=interpretations)

        interpretation = analyzer._find_interpretation_by_intent(lex_request, "NonExistentIntent")

        assert interpretation is None
