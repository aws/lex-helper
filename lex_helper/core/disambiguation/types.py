# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Type definitions for the Smart Disambiguation feature.

This module contains all the data classes and type definitions needed for
intelligent disambiguation of ambiguous user input in lex-helper.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IntentCandidate:
    """
    Represents a potential intent match for disambiguation.

    Contains the intent information along with confidence scoring and
    user-friendly display information for presenting options to users.
    """

    intent_name: str
    """Technical name of the intent (e.g., 'BookFlight')"""

    confidence_score: float
    """Confidence score between 0.0 and 1.0 for this intent match"""

    display_name: str
    """User-friendly name for display (e.g., 'Book a Flight')"""

    description: str
    """Brief description of what this intent does"""

    required_slots: list[str] = field(default_factory=lambda: [])
    """List of required slot names for this intent"""


@dataclass
class DisambiguationResult:
    """
    Result of disambiguation analysis.

    Contains the decision on whether disambiguation should occur and
    all the information needed to present options to the user.
    """

    should_disambiguate: bool
    """Whether disambiguation should be triggered based on analysis"""

    candidates: list[IntentCandidate] = field(default_factory=lambda: [])
    """List of intent candidates to present to the user"""

    confidence_scores: dict[str, float] = field(default_factory=lambda: {})
    """Raw confidence scores for all analyzed intents"""


@dataclass
class BedrockDisambiguationConfig:
    """
    Configuration for Bedrock-powered disambiguation text generation.

    Allows using Amazon Bedrock models to generate contextual and intelligent
    disambiguation messages and button text based on the user's input and
    available intent candidates.
    """

    enabled: bool = False
    """Whether to use Bedrock for generating disambiguation text"""

    model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    """Bedrock model ID to use for text generation"""

    region_name: str = "us-east-1"
    """AWS region for Bedrock service"""

    max_tokens: int = 200
    """Maximum tokens for generated response"""

    temperature: float = 0.3
    """Temperature for text generation (0.0-1.0, lower = more deterministic)"""

    system_prompt: str = field(
        default_factory=lambda: (
            "You are a helpful assistant that creates clear, concise disambiguation messages "
            "for chatbot users. When users provide ambiguous input, help them choose between "
            "available options with friendly, natural language."
        )
    )
    """System prompt for the Bedrock model"""

    fallback_to_static: bool = True
    """Whether to fall back to static messages if Bedrock fails"""


@dataclass
class DisambiguationConfig:
    """
    Configuration options for the disambiguation system.

    Allows developers to customize disambiguation behavior including
    thresholds, candidate limits, and custom intent groupings.
    """

    confidence_threshold: float = 0.6
    """Minimum confidence score to avoid disambiguation (0.0-1.0)"""

    max_candidates: int = 3
    """Maximum number of intent candidates to present to users"""

    fallback_to_original: bool = True
    """Whether to fall back to original behavior if disambiguation fails"""

    min_candidates: int = 2
    """Minimum number of candidates required to trigger disambiguation"""

    similarity_threshold: float = 0.15
    """Maximum difference between top scores to trigger disambiguation (0.0-1.0)"""

    enable_logging: bool = True
    """Whether to enable detailed logging of disambiguation events"""

    custom_intent_groups: dict[str, list[str]] = field(default_factory=lambda: {})
    """Custom groupings of related intents for better disambiguation"""

    custom_messages: dict[str, str] = field(default_factory=lambda: {})
    """Custom clarification messages for specific disambiguation scenarios"""

    bedrock_config: BedrockDisambiguationConfig = field(default_factory=BedrockDisambiguationConfig)
    """Configuration for Bedrock-powered text generation"""


# Type aliases for better code readability
IntentScores = dict[str, float]
"""Type alias for intent name to confidence score mapping"""

DisambiguationMessages = dict[str, str]
"""Type alias for disambiguation message templates"""
