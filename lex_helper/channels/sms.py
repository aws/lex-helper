# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""SMS-specific channel implementation."""

from typing import List
from urllib.parse import urlparse

from lex_helper.channels.base import Channel
from lex_helper.core.types import (
    LexBaseResponse,
    LexCustomPayload,
    LexImageResponseCard,
    LexMessages,
    LexPlainText,
)


class SMSChannel(Channel):
    """Channel implementation for SMS-specific message formatting."""

    def format_message(self, message: LexMessages) -> LexBaseResponse:
        """Format a single message for SMS.
        
        Args:
            message: The Lex message to format
            
        Returns:
            The formatted message string
        """
        if isinstance(message, LexPlainText):
            return self.format_plain_text(message)
        if isinstance(message, LexImageResponseCard):
            return self.format_image_card(message)
        if isinstance(message, LexCustomPayload):
            return self.format_custom_payload(message)
        return LexPlainText(content="Unsupported message type")

    def format_messages(self, messages: List[LexMessages]) -> List[LexBaseResponse]:
        """Format a list of messages for SMS.
        
        Args:
            messages: List of Lex messages to format
            
        Returns:
            List of formatted message strings
        """
        return [self.format_message(message) for message in messages]

    def format_plain_text(self, message: LexPlainText) -> LexBaseResponse:
        """Format a plain text message for SMS.
        
        Args:
            message: The plain text message to format
            
        Returns:
            The formatted plain text
        """
        # For SMS, we want to ensure URLs are properly formatted
        text = message.content
        if text is None:
            return LexPlainText(content="")
        words = text.split()
        formatted_words = []
        
        for word in words:
            # Check if word might be a URL
            if "." in word and "/" in word:
                try:
                    result = urlparse(word)
                    if not result.scheme:
                        # Add https:// if no scheme
                        word = "https://" + word
                except:
                    pass
            formatted_words.append(word)
        
        return LexPlainText(content=" ".join(formatted_words))

    def format_image_card(self, card: LexImageResponseCard) -> LexBaseResponse:
        """Format an image response card for SMS.
        
        Args:
            card: The image card to format
            
        Returns:
            The formatted card text
        """
        # For SMS, we want a more compact format
        parts = []
        if card.imageResponseCard.title:
            parts.append(card.imageResponseCard.title)
        if card.imageResponseCard.subtitle:
            parts.append(card.imageResponseCard.subtitle)
        if card.imageResponseCard.imageUrl:
            parts.append(card.imageResponseCard.imageUrl)  # Include raw URL for SMS
        if card.imageResponseCard.buttons:
            # For SMS, we only include the button text, not values
            button_texts = [btn.text for btn in card.imageResponseCard.buttons]
            parts.append("Options: " + ", ".join(button_texts))
        
        return LexPlainText(content=" | ".join(parts))

    def format_custom_payload(self, payload: LexCustomPayload) -> LexBaseResponse:
        """Format a custom payload message for SMS.
        
        Args:
            payload: The custom payload to format
            
        Returns:
            The formatted payload text
        """
        content = payload.content
        # Ensure content is treated as a dictionary
        if isinstance(content, dict):
            if "text" in content:
                return LexCustomPayload(content=str(content.get("text")))
            if "message" in content:
                return LexCustomPayload(content=str(content.get("message")))
            # For SMS, we don't want to dump the entire dict
            return LexCustomPayload(content="Message received")
        return LexCustomPayload(content=str(content))
