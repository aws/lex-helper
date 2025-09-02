# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Base channel interface for message formatting."""

from abc import ABC, abstractmethod

from lex_helper.core.types import (
    LexBaseResponse,
    LexCustomPayload,
    LexImageResponseCard,
    LexMessages,
    LexPlainText,
)


class Channel(ABC):
    """Abstract base class for channel-specific message formatting."""

    @abstractmethod
    def format_message(self, message: LexMessages) -> LexBaseResponse:
        """Format a single message for the specific channel.

        Args:
            message: The Lex message to format

        Returns:
            The formatted message string
        """
        pass

    @abstractmethod
    def format_messages(self, messages: list[LexMessages]) -> list[LexBaseResponse]:
        """Format a list of messages for the specific channel.

        Args:
            messages: List of Lex messages to format

        Returns:
            List of formatted message strings
        """
        pass

    def format_plain_text(self, message: LexPlainText) -> LexBaseResponse:
        """Format a plain text message.

        Args:
            message: The plain text message to format

        Returns:
            The formatted plain text
        """
        return LexPlainText(content=message.content or "")

    def format_image_card(self, card: LexImageResponseCard) -> LexBaseResponse:
        """Format an image response card.

        Args:
            card: The image card to format

        Returns:
            The formatted card text
        """
        parts = [card.imageResponseCard.title]
        if card.imageResponseCard.subtitle:
            parts.append(card.imageResponseCard.subtitle)
        if card.imageResponseCard.imageUrl:
            parts.append(f"Image: {card.imageResponseCard.imageUrl}")
        if card.imageResponseCard.buttons:
            button_texts = [f"[{btn.text}]" for btn in card.imageResponseCard.buttons]
            parts.append("Buttons: " + " ".join(button_texts))
        return LexPlainText(content="\n".join(parts))

    def format_custom_payload(self, payload: LexCustomPayload) -> LexBaseResponse:
        """Format a custom payload message.

        Args:
            payload: The custom payload to format

        Returns:
            The formatted payload text, or None if payload cannot be formatted
        """
        if isinstance(payload.content, str):
            return LexCustomPayload(content=payload.content)
        elif isinstance(payload.content, dict) and "text" in payload.content:  # type: ignore[unreachable]
            return LexCustomPayload(content=str(payload.content["text"]))
        return LexCustomPayload(content=str(payload.content))
