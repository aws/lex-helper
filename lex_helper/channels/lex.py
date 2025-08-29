# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Lex-specific channel implementation."""

from lex_helper.channels.base import Channel
from lex_helper.core.types import (
    LexBaseResponse,
    LexCustomPayload,
    LexImageResponseCard,
    LexMessages,
    LexPlainText,
)


class LexChannel(Channel):
    """Channel implementation for Lex-specific message formatting."""

    def format_message(self, message: LexMessages) -> LexBaseResponse:
        """Format a single Lex message.

        Args:
            message: The Lex message to format

        Returns:
            The formatted message string
        """
        if isinstance(message, LexPlainText):
            return self.format_plain_text(message)
        if isinstance(message, LexImageResponseCard):
            return self.format_image_card(message)
        if isinstance(message, LexCustomPayload):  # type: ignore
            return self.format_custom_payload(message)
        return LexPlainText(content="Unsupported message type")

    def format_messages(self, messages: list[LexMessages]) -> list[LexBaseResponse]:
        """Format a list of Lex messages.

        Args:
            messages: List of Lex messages to format

        Returns:
            List of formatted message strings
        """
        return [self.format_message(message) for message in messages]

    def format_plain_text(self, message: LexPlainText) -> LexBaseResponse:
        """Format a Lex plain text message.

        Overrides the base implementation to handle Lex-specific formatting.

        Args:
            message: The plain text message to format

        Returns:
            The formatted plain text
        """
        # For Lex, we can just use the base implementation
        return super().format_plain_text(message)

    def format_image_card(self, card: LexImageResponseCard) -> LexBaseResponse:
        """Format a Lex image response card.

        Overrides the base implementation to handle Lex-specific formatting.

        Args:
            card: The image card to format

        Returns:
            The formatted card text
        """
        # For Lex, we want to format buttons with their value rather than text
        parts = [card.imageResponseCard.title]
        if card.imageResponseCard.subtitle:
            parts.append(card.imageResponseCard.subtitle)
        if card.imageResponseCard.imageUrl:
            parts.append(f"Image: {card.imageResponseCard.imageUrl}")
        if card.imageResponseCard.buttons:
            button_texts = [f"[{btn.text} -> {btn.value}]" for btn in card.imageResponseCard.buttons]
            parts.append("Buttons: " + " ".join(button_texts))
        return LexPlainText(content="\n".join(parts))

    def format_custom_payload(self, payload: LexCustomPayload) -> LexBaseResponse:
        """Format a Lex custom payload message.

        Overrides the base implementation to handle Lex-specific formatting.

        Args:
            payload: The custom payload to format

        Returns:
            The formatted payload text
        """
        content = payload.content
        if isinstance(content, dict):
            if "text" in content:
                return str(content["text"])  # type: ignore
            if "message" in content:
                return str(content["message"])  # type: ignore
            return LexCustomPayload(content=str(content))
        return LexCustomPayload(content=str(content))
