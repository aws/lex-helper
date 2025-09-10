# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
DisambiguationAnalyzer for intelligent intent disambiguation.

This module provides the core analysis functionality for determining when
disambiguation should occur and which intent candidates to present to users.
"""

import logging
from typing import Any

from lex_helper.core.types import LexRequest, SessionAttributes

from .types import (
    DisambiguationConfig,
    DisambiguationResult,
    IntentCandidate,
    IntentScores,
)

logger = logging.getLogger(__name__)

# Constants
MIN_MEANINGFUL_SCORE = 0.1  # Minimum score to consider an intent meaningful
MIN_REASONABLE_SCORE = 0.15  # Minimum score to consider for similarity comparison


class DisambiguationAnalyzer:
    """
    Analyzes user input to determine disambiguation candidates.

    The analyzer uses Lex's NLU confidence scores to identify potential
    intent matches and determine when disambiguation should be triggered
    based on configurable thresholds.
    """

    def __init__(self, config: DisambiguationConfig | None = None):
        """
        Initialize the DisambiguationAnalyzer.

        Args:
            config: Configuration options for disambiguation behavior.
                   If None, uses default configuration.
        """
        self.config = config or DisambiguationConfig()

    def analyze_request(
        self,
        lex_request: LexRequest[SessionAttributes],
    ) -> DisambiguationResult:
        """
        Analyze Lex request and return disambiguation candidates.

        Args:
            lex_request: The Lex request containing interpretations with confidence scores

        Returns:
            DisambiguationResult containing analysis results and candidates
        """
        logger.debug("Analyzing Lex request for disambiguation: %s", lex_request.inputTranscript)

        # Extract confidence scores from Lex interpretations
        confidence_scores = self.extract_intent_scores(lex_request)

        # Determine if disambiguation should occur
        should_disambiguate = self.should_disambiguate(confidence_scores, self.config.confidence_threshold)

        # Generate candidates if disambiguation is needed
        candidates = []
        if should_disambiguate:
            candidates = self._generate_candidates(confidence_scores, lex_request)

        result = DisambiguationResult(
            should_disambiguate=should_disambiguate,
            candidates=candidates,
            confidence_scores=confidence_scores,
        )

        logger.debug(
            "Disambiguation analysis complete: should_disambiguate=%s, candidates=%d", should_disambiguate, len(candidates)
        )

        return result

    def extract_intent_scores(self, lex_request: LexRequest[SessionAttributes]) -> IntentScores:
        """
        Extract confidence scores from Lex interpretations.

        Args:
            lex_request: The Lex request containing interpretations

        Returns:
            Dictionary mapping intent names to confidence scores (0.0-1.0)
        """
        scores: dict[str, float] = {}

        for interpretation in lex_request.interpretations:
            intent_name = interpretation.intent.name
            confidence = interpretation.nluConfidence or 0.0
            scores[intent_name] = confidence

        logger.debug("Extracted intent scores from Lex: %s", scores)
        return scores

    def should_disambiguate(self, scores: IntentScores, threshold: float) -> bool:
        """
        Determine if disambiguation is needed based on confidence scores.

        Args:
            scores: Dictionary of intent names to confidence scores
            threshold: Minimum confidence threshold to avoid disambiguation

        Returns:
            True if disambiguation should be triggered, False otherwise
        """
        if not scores:
            return False

        # Get the highest scoring intents
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Filter out very low scores
        meaningful_scores = [score for _, score in sorted_scores if score > MIN_MEANINGFUL_SCORE]
        if len(meaningful_scores) < self.config.min_candidates:
            return False

        # Get top scores for comparison
        if len(sorted_scores) < 2:
            return False

        top_score = sorted_scores[0][1]
        second_score = sorted_scores[1][1]

        # Case 1: Top score is very low (below threshold) AND we have multiple candidates
        if top_score < threshold and len(meaningful_scores) >= self.config.min_candidates:
            return True

        # Case 2: Multiple scores are close to each other (ambiguous case)
        # Only disambiguate if the difference between top scores is small
        score_difference = top_score - second_score

        # If the top two scores are within similarity_threshold of each other, consider it ambiguous
        # AND both scores are reasonably high
        similarity_threshold = self.config.similarity_threshold
        if (
            score_difference <= similarity_threshold
            and top_score >= MIN_REASONABLE_SCORE
            and second_score >= MIN_REASONABLE_SCORE
            and len(meaningful_scores) >= self.config.min_candidates
        ):
            return True

        return False

    def _generate_candidates(
        self, scores: IntentScores, lex_request: LexRequest[SessionAttributes]
    ) -> list[IntentCandidate]:
        """
        Generate intent candidates for disambiguation.

        Args:
            scores: Intent confidence scores
            lex_request: The Lex request containing interpretation details

        Returns:
            List of IntentCandidate objects for presentation to user
        """
        # Sort intents by score and take top candidates
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Filter to meaningful scores and limit to max candidates
        candidates: list[IntentCandidate] = []
        for intent, score in sorted_intents[: self.config.max_candidates]:
            if score > MIN_MEANINGFUL_SCORE:
                # Find the corresponding interpretation for slot information
                interpretation = self._find_interpretation_by_intent(lex_request, intent)

                candidate = IntentCandidate(
                    intent_name=intent,
                    confidence_score=score,
                    display_name=self._get_display_name(intent),
                    description=self._get_intent_description(intent),
                    required_slots=self._get_required_slots_from_interpretation(interpretation),
                )
                candidates.append(candidate)

        return candidates

    def _find_interpretation_by_intent(self, lex_request: LexRequest[SessionAttributes], intent_name: str):
        """
        Find the interpretation that matches the given intent name.

        Args:
            lex_request: The Lex request containing interpretations
            intent_name: The intent name to find

        Returns:
            The matching interpretation or None if not found
        """
        for interpretation in lex_request.interpretations:
            if interpretation.intent.name == intent_name:
                return interpretation
        return None

    def _get_display_name(self, intent: str) -> str:
        """
        Get user-friendly display name for an intent.

        Converts technical intent names to user-friendly format.

        Args:
            intent: Technical intent name

        Returns:
            User-friendly display name
        """
        # Convert CamelCase and snake_case to readable format
        # Replace underscores with spaces and add spaces before capital letters
        import re

        # Handle snake_case
        readable = intent.replace("_", " ")

        # Handle CamelCase - add space before capital letters
        readable = re.sub(r"([a-z])([A-Z])", r"\1 \2", readable)

        # Capitalize each word
        return readable.title()

    def _get_intent_description(self, intent: str) -> str:
        """
        Get description for an intent.

        Generates a generic description based on the intent name.

        Args:
            intent: Intent name

        Returns:
            Brief description of what the intent does
        """
        # Generate a generic description based on intent name
        display_name = self._get_display_name(intent).lower()
        return f"Handle requests related to {display_name}"

    def _get_required_slots_from_interpretation(self, interpretation: Any) -> list[str]:
        """
        Get required slots from the interpretation.

        Args:
            interpretation: The Lex interpretation object

        Returns:
            List of slot names from the interpretation
        """
        if not interpretation or not interpretation.intent:
            return []

        # Return the slot names from the intent
        slot_names: list[str] = list(interpretation.intent.slots.keys()) if interpretation.intent.slots else []
        return slot_names
