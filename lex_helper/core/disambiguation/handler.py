# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Disambiguation Handler for the Smart Disambiguation feature.

This module provides the DisambiguationHandler class that orchestrates the
disambiguation process, generates user-friendly clarification responses,
and processes user selections to route to the appropriate intent.
"""

import json
import logging
from typing import TypeVar

from lex_helper.core.dialog import (
    close,
    elicit_intent,
)
from lex_helper.core.message_manager import get_message
from lex_helper.core.types import (
    LexImageResponseCard,
    LexMessages,
    LexPlainText,
    LexRequest,
    LexResponse,
    SessionAttributes,
)
from lex_helper.formatters.buttons import Button

from .bedrock_generator import BedrockDisambiguationGenerator
from .types import (
    DisambiguationConfig,
    IntentCandidate,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=SessionAttributes)


class DisambiguationHandler:
    """
    Handles disambiguation response generation and user selection processing.

    This class is responsible for creating user-friendly clarification messages
    when multiple intents are possible matches, and processing user responses
    to route them to the correct intent handler.
    """

    def __init__(self, config: DisambiguationConfig | None = None):
        """
        Initialize the disambiguation handler.

        Args:
            config: Configuration options for disambiguation behavior
        """
        self.config = config or DisambiguationConfig()

        # Initialize Bedrock generator if enabled
        self.bedrock_generator = None
        if self.config.bedrock_config.enabled:
            try:
                self.bedrock_generator = BedrockDisambiguationGenerator(self.config.bedrock_config)
                logger.debug("Bedrock disambiguation generator initialized")
            except Exception as e:
                logger.warning("Failed to initialize Bedrock generator: %s", e)
                if not self.config.bedrock_config.fallback_to_static:
                    raise

    def handle_disambiguation(self, lex_request: LexRequest[T], candidates: list[IntentCandidate]) -> LexResponse[T]:
        """
        Generate disambiguation response with clarifying questions.

        Creates a response that presents the user with options to clarify
        their intent, using buttons for easy selection.

        Args:
            lex_request: The original Lex request
            candidates: List of intent candidates to present

        Returns:
            LexResponse with disambiguation options
        """
        logger.info("Generating disambiguation response with %d candidates", len(candidates))

        # Limit candidates to configured maximum
        limited_candidates = candidates[: self.config.max_candidates]

        # Store disambiguation state in session
        self._store_disambiguation_state(lex_request, limited_candidates)

        # Create clarification messages with user input context
        messages = self._create_clarification_messages(limited_candidates, lex_request.inputTranscript)

        # Use elicit_intent to get user's clarification
        return elicit_intent(messages, lex_request)

    def process_disambiguation_response(self, lex_request: LexRequest[T]) -> LexResponse[T] | None:
        """
        Process user's response to disambiguation and route to selected intent.

        Analyzes the user's input to determine which intent they selected
        and updates the request to route to that intent.

        Args:
            lex_request: The Lex request with user's disambiguation response

        Returns:
            None if this isn't a disambiguation response, otherwise routes
            to the selected intent by updating the request
        """
        # Check if this is a disambiguation response
        if not self._is_disambiguation_response(lex_request):
            return None

        logger.debug("Processing disambiguation response")

        # Get stored candidates from session
        candidates = self._get_stored_candidates(lex_request)
        if not candidates:
            logger.warning("No stored disambiguation candidates found")
            return self._create_fallback_response(lex_request)

        # Determine selected intent
        selected_intent = self._determine_selected_intent(lex_request.inputTranscript, candidates)

        if not selected_intent:
            logger.warning("Could not determine selected intent from input: %s", lex_request.inputTranscript)
            return self._create_fallback_response(lex_request)

        # Update request to route to selected intent
        self._update_request_for_selected_intent(lex_request, selected_intent)

        # Clear disambiguation state
        self._clear_disambiguation_state(lex_request)

        logger.info("Routed disambiguation to intent: %s", selected_intent)

        # Return None to let the regular handler process the updated request
        return None

    def _create_clarification_messages(
        self, candidates: list[IntentCandidate], user_input: str | None = None
    ) -> LexMessages:
        """
        Create user-friendly clarification messages with intent options.

        Args:
            candidates: List of intent candidates to present
            user_input: Optional user input for context

        Returns:
            List of messages including text and buttons
        """
        # Get the main clarification message (potentially from Bedrock)
        main_message = self._get_clarification_text(candidates, user_input)

        # Generate button labels (potentially from Bedrock)
        button_labels = self._get_button_labels(candidates, user_input)

        # Create buttons for each candidate
        buttons = []
        for i, candidate in enumerate(candidates):
            button_text = button_labels[i] if i < len(button_labels) else candidate.display_name
            button = Button(
                text=button_text,
                value=button_text,  # Use button text as value for natural conversation flow
            )
            buttons.append(button)

        # Create image response card with buttons
        from lex_helper.core.types import ImageResponseCard
        from lex_helper.formatters.buttons import buttons_to_dicts

        if buttons:
            # Convert buttons to the format expected by ImageResponseCard
            button_dicts = buttons_to_dicts(buttons)

            image_card = ImageResponseCard(
                title="Please choose an option:",
                subtitle="Select what you'd like to do",
                buttons=[Button(text=b["text"], value=b["value"]) for b in button_dicts],
            )

            image_response = LexImageResponseCard(imageResponseCard=image_card)

            messages: LexMessages = [LexPlainText(content=main_message), image_response]
        else:
            messages: LexMessages = [LexPlainText(content=main_message)]

        return messages

    def _get_clarification_text(self, candidates: list[IntentCandidate], user_input: str | None = None) -> str:
        """
        Get the main clarification text based on candidates.

        Args:
            candidates: List of intent candidates
            user_input: Optional user input for context

        Returns:
            Clarification message text
        """
        # Try Bedrock generation first if enabled
        if self.bedrock_generator and user_input:
            try:
                return self.bedrock_generator.generate_clarification_message(user_input, candidates)
            except Exception as e:
                logger.warning("Bedrock clarification generation failed, falling back to static: %s", e)
                # Continue to static message generation

        # Try to get custom message for specific scenario
        custom_message = self._get_custom_clarification_message(candidates)
        if custom_message:
            return custom_message

        # Use default message based on number of candidates
        if len(candidates) == 2:
            base_message_key = "disambiguation.two_options"
            default = "I can help you with two things. Which would you like to do?"
        else:
            base_message_key = "disambiguation.multiple_options"
            default = "I can help you with several things. What would you like to do?"

        # Check if there's a custom message key configured for this scenario
        custom_key = self.config.custom_messages.get(base_message_key)
        if custom_key:
            # Use the custom message key
            localized_message = get_message(custom_key, None)
            if localized_message:
                return localized_message
            # If custom key doesn't resolve, use it as fallback
            return custom_key

        # Use the default message key
        return get_message(base_message_key, default)

    def _get_custom_clarification_message(self, candidates: list[IntentCandidate]) -> str | None:
        """
        Get custom clarification message for specific intent combinations.

        Args:
            candidates: List of intent candidates

        Returns:
            Custom message if available, None otherwise
        """
        # Check for custom messages in config (treat as message keys)
        intent_names = [c.intent_name for c in candidates]
        intent_key = "_".join(sorted(intent_names))

        custom_message_key = self.config.custom_messages.get(intent_key)
        if custom_message_key:
            # Try to get localized message using the key
            localized_message = get_message(custom_message_key, None)
            if localized_message:
                return localized_message
            # If no localized message found, use the key as fallback
            return custom_message_key

        # Check for intent group messages
        for group_name, group_intents in self.config.custom_intent_groups.items():
            if all(intent in group_intents for intent in intent_names):
                group_message_key = f"disambiguation.{group_name}"

                # First check if there's a custom message key for this group
                custom_group_key = self.config.custom_messages.get(group_message_key)
                if custom_group_key:
                    localized_message = get_message(custom_group_key, None)
                    if localized_message:
                        return localized_message

                # Try to get from message manager with default group key
                localized_message = get_message(group_message_key, None)
                if localized_message:
                    return localized_message

        return None

    def _get_button_labels(self, candidates: list[IntentCandidate], user_input: str | None = None) -> list[str]:
        """
        Get button labels for the candidates, potentially using Bedrock generation.

        Args:
            candidates: List of intent candidates
            user_input: Optional user input for context

        Returns:
            List of button labels
        """
        # Try Bedrock generation first if enabled
        if self.bedrock_generator:
            try:
                return self.bedrock_generator.generate_button_labels(candidates, user_input)
            except Exception as e:
                logger.warning("Bedrock button label generation failed, falling back to display names: %s", e)
                # Continue to fallback

        # Fallback to display names
        return [candidate.display_name for candidate in candidates]

    def _store_disambiguation_state(self, lex_request: LexRequest[T], candidates: list[IntentCandidate]) -> None:
        """
        Store disambiguation state in session attributes.

        Args:
            lex_request: The Lex request to update
            candidates: List of candidates to store
        """
        session_attrs = lex_request.sessionState.sessionAttributes

        # Get button labels for storage
        button_labels = self._get_button_labels(candidates, lex_request.inputTranscript)

        # Store candidates as JSON with button labels
        candidates_data = [
            {
                "intent_name": c.intent_name,
                "display_name": c.display_name,
                "button_label": button_labels[i] if i < len(button_labels) else c.display_name,
                "confidence_score": c.confidence_score,
                "description": c.description,
            }
            for i, c in enumerate(candidates)
        ]

        # Store disambiguation state in session attributes
        session_attrs.disambiguation_candidates = json.dumps(candidates_data)
        session_attrs.disambiguation_active = True

    def _is_disambiguation_response(self, lex_request: LexRequest[T]) -> bool:
        """
        Check if this request is a response to disambiguation.

        Args:
            lex_request: The Lex request to check

        Returns:
            True if this is a disambiguation response
        """
        session_attrs = lex_request.sessionState.sessionAttributes

        # Check for disambiguation state
        return session_attrs.disambiguation_active

    def _get_stored_candidates(self, lex_request: LexRequest[T]) -> list[IntentCandidate] | None:
        """
        Retrieve stored disambiguation candidates from session.

        Args:
            lex_request: The Lex request containing session state

        Returns:
            List of stored candidates or None if not found
        """
        session_attrs = lex_request.sessionState.sessionAttributes

        # Get candidates JSON
        candidates_json = session_attrs.disambiguation_candidates

        if not candidates_json:
            return None

        try:
            candidates_data = json.loads(candidates_json)
            return [
                IntentCandidate(
                    intent_name=c["intent_name"],
                    display_name=c["display_name"],
                    confidence_score=c["confidence_score"],
                    description=c["description"],
                    # Store button label in required_slots for now (we can extend IntentCandidate later if needed)
                    required_slots=[c.get("button_label", c["display_name"])],
                )
                for c in candidates_data
            ]
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Failed to parse stored disambiguation candidates: %s", e)
            return None

    def _determine_selected_intent(self, user_input: str, candidates: list[IntentCandidate]) -> str | None:
        """
        Determine which intent the user selected from their input.

        Args:
            user_input: The user's input text
            candidates: List of available candidates

        Returns:
            Selected intent name or None if not determined
        """
        user_input_lower = user_input.lower().strip()

        # Try exact match with intent names
        for candidate in candidates:
            if candidate.intent_name.lower() == user_input_lower:
                return candidate.intent_name

        # Try exact match with display names
        for candidate in candidates:
            if candidate.display_name.lower() == user_input_lower:
                return candidate.intent_name

        # Try exact match with button labels (stored in required_slots[0])
        for candidate in candidates:
            if candidate.required_slots and candidate.required_slots[0].lower() == user_input_lower:
                return candidate.intent_name

        # Try number selection (1, 2, 3, etc.)
        try:
            selection_num = int(user_input_lower)
            if 1 <= selection_num <= len(candidates):
                return candidates[selection_num - 1].intent_name
        except ValueError:
            pass

        # Try letter selection (A, B, C, etc.) - do this before partial match
        if len(user_input_lower) == 1 and user_input_lower.isalpha():
            letter_index = ord(user_input_lower) - ord("a")
            if 0 <= letter_index < len(candidates):
                return candidates[letter_index].intent_name

        # Try partial match with display names
        for candidate in candidates:
            if user_input_lower in candidate.display_name.lower():
                return candidate.intent_name

        # Try partial match with button labels
        for candidate in candidates:
            if candidate.required_slots and user_input_lower in candidate.required_slots[0].lower():
                return candidate.intent_name

        return None

    def _update_request_for_selected_intent(self, lex_request: LexRequest[T], selected_intent: str) -> None:
        """
        Update the Lex request to route to the selected intent.

        Args:
            lex_request: The request to update
            selected_intent: The intent name to route to
        """
        # Update the intent in the session state
        lex_request.sessionState.intent.name = selected_intent
        lex_request.sessionState.intent.state = "InProgress"

        # Clear any existing slots since this is a new intent
        lex_request.sessionState.intent.slots = {}

    def _clear_disambiguation_state(self, lex_request: LexRequest[T]) -> None:
        """
        Clear disambiguation state from session attributes.

        Args:
            lex_request: The request to update
        """
        session_attrs = lex_request.sessionState.sessionAttributes

        # Clear disambiguation state
        session_attrs.disambiguation_candidates = None
        session_attrs.disambiguation_active = False

    def _create_fallback_response(self, lex_request: LexRequest[T]) -> LexResponse[T]:
        """
        Create a fallback response when disambiguation fails.

        Args:
            lex_request: The original request

        Returns:
            Fallback response
        """
        fallback_message = get_message(
            "disambiguation.fallback", "I'm not sure what you're looking for. Could you be more specific?"
        )

        messages: LexMessages = [LexPlainText(content=fallback_message)]

        # Clear disambiguation state
        self._clear_disambiguation_state(lex_request)

        return close(lex_request, messages)
