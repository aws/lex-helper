# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Bedrock-powered text generation for Smart Disambiguation.

This module provides intelligent, contextual disambiguation message generation
using Amazon Bedrock models to create more natural and helpful clarification
responses based on user input and available intent candidates.
"""

import json
import logging
from typing import Any

from lex_helper.core.invoke_bedrock import BedrockInvocationError, invoke_bedrock_simple_converse

from .types import BedrockDisambiguationConfig, IntentCandidate

logger = logging.getLogger(__name__)


class BedrockDisambiguationGenerator:
    """
    Generates disambiguation messages using Amazon Bedrock models.
    
    This class creates contextual, intelligent disambiguation messages by
    analyzing user input and available intent candidates, then using Bedrock
    to generate natural language clarification text and button labels.
    """
    
    def __init__(self, config: BedrockDisambiguationConfig):
        """
        Initialize the Bedrock disambiguation generator.
        
        Args:
            config: Configuration for Bedrock text generation
        """
        self.config = config
    
    def generate_clarification_message(
        self, 
        user_input: str, 
        candidates: list[IntentCandidate],
        context: dict[str, Any] | None = None
    ) -> str:
        """
        Generate a contextual clarification message using Bedrock.
        
        Args:
            user_input: The original user input that was ambiguous
            candidates: List of intent candidates to choose from
            context: Optional context information (session data, etc.)
            
        Returns:
            Generated clarification message text
        """
        if not self.config.enabled:
            return self._get_fallback_message(candidates)
            
        try:
            prompt = self._build_clarification_prompt(user_input, candidates, context)
            
            response = invoke_bedrock_simple_converse(
                prompt=prompt,
                model_id=self.config.model_id,
                system_prompt=self.config.system_prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                region_name=self.config.region_name,
            )
            
            generated_text = response["text"].strip()
            logger.debug("Generated clarification message: %s", generated_text)
            
            return generated_text
            
        except BedrockInvocationError as e:
            logger.warning("Bedrock clarification generation failed: %s", e)
            if self.config.fallback_to_static:
                return self._get_fallback_message(candidates)
            raise
        except Exception as e:
            logger.error("Unexpected error in Bedrock clarification generation: %s", e)
            if self.config.fallback_to_static:
                return self._get_fallback_message(candidates)
            raise
    
    def generate_button_labels(
        self, 
        candidates: list[IntentCandidate],
        user_input: str | None = None
    ) -> list[str]:
        """
        Generate improved button labels using Bedrock.
        
        Args:
            candidates: List of intent candidates
            user_input: Optional user input for context
            
        Returns:
            List of generated button labels
        """
        if not self.config.enabled:
            return [candidate.display_name for candidate in candidates]
            
        try:
            prompt = self._build_button_labels_prompt(candidates, user_input)
            
            response = invoke_bedrock_simple_converse(
                prompt=prompt,
                model_id=self.config.model_id,
                system_prompt=self.config.system_prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                region_name=self.config.region_name,
            )
            
            # Parse the JSON response to get button labels
            generated_text = response["text"].strip()
            
            # Try to parse as JSON first
            try:
                if generated_text.startswith('[') and generated_text.endswith(']'):
                    labels = json.loads(generated_text)
                    if isinstance(labels, list) and len(labels) == len(candidates):
                        logger.debug("Generated button labels: %s", labels)
                        return labels
            except json.JSONDecodeError:
                pass
            
            # If JSON parsing fails, try to extract labels from text
            labels = self._extract_labels_from_text(generated_text, len(candidates))
            if labels:
                logger.debug("Extracted button labels: %s", labels)
                return labels
                
            # Fallback to original display names
            logger.warning("Could not parse generated button labels, using fallback")
            return [candidate.display_name for candidate in candidates]
            
        except BedrockInvocationError as e:
            logger.warning("Bedrock button label generation failed: %s", e)
            if self.config.fallback_to_static:
                return [candidate.display_name for candidate in candidates]
            raise
        except Exception as e:
            logger.error("Unexpected error in Bedrock button label generation: %s", e)
            if self.config.fallback_to_static:
                return [candidate.display_name for candidate in candidates]
            raise
    
    def _build_clarification_prompt(
        self, 
        user_input: str, 
        candidates: list[IntentCandidate],
        context: dict[str, Any] | None = None
    ) -> str:
        """Build the prompt for clarification message generation."""
        candidate_descriptions = []
        for i, candidate in enumerate(candidates, 1):
            candidate_descriptions.append(
                f"{i}. {candidate.display_name}: {candidate.description}"
            )
        
        context_info = ""
        if context:
            # Add relevant context information
            if "session_attributes" in context:
                context_info = f"\nContext: {context['session_attributes']}"
        
        prompt = f"""The user said: "{user_input}"

This input is ambiguous and could match multiple intents. Here are the possible options:

{chr(10).join(candidate_descriptions)}

Generate a friendly, natural clarification message that:
1. Acknowledges what the user said
2. Explains that there are multiple ways to help
3. Asks them to choose which option they want
4. Is conversational and helpful (not robotic)
5. Is concise (1-2 sentences maximum)

Do not include numbered lists or bullet points in your response. Just provide the clarification message text.{context_info}"""

        return prompt
    
    def _build_button_labels_prompt(
        self, 
        candidates: list[IntentCandidate],
        user_input: str | None = None
    ) -> str:
        """Build the prompt for button label generation."""
        candidate_info = []
        for candidate in candidates:
            candidate_info.append(f"- {candidate.intent_name}: {candidate.description}")
        
        user_context = ""
        if user_input:
            user_context = f"\nUser's original input: \"{user_input}\""
        
        prompt = f"""Generate improved button labels for these intent options:

{chr(10).join(candidate_info)}{user_context}

Create short, clear, action-oriented button labels (2-4 words each) that users would naturally click.
Make them more conversational and user-friendly than the technical intent names.

Return your response as a JSON array of strings, like: ["Label 1", "Label 2", "Label 3"]

Only return the JSON array, nothing else."""

        return prompt
    
    def _extract_labels_from_text(self, text: str, expected_count: int) -> list[str] | None:
        """Extract button labels from generated text if JSON parsing fails."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Try to find lines that look like labels
        labels = []
        for line in lines:
            # Remove common prefixes/suffixes and clean up
            cleaned = line.strip('- •*"\'[](){}').strip()
            # Skip lines that look like headers or explanations
            if (cleaned and 
                len(cleaned) <= 50 and  # Reasonable button label length
                not cleaned.lower().startswith(('here', 'the', 'options', 'choose'))):
                labels.append(cleaned)
        
        # Return if we have the right number of labels
        if len(labels) == expected_count:
            return labels
            
        return None
    
    def _get_fallback_message(self, candidates: list[IntentCandidate]) -> str:
        """Get fallback message when Bedrock is not available or fails."""
        if len(candidates) == 2:
            return "I can help you with two things. Which would you like to do?"
        else:
            return "I can help you with several things. What would you like to do?"