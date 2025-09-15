# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Lex Helper - A package for building Amazon Lex chatbots.

This package provides tools and utilities for creating and managing
Amazon Lex chatbots with a focus on maintainability and ease of use.
"""

__version__ = "0.0.2"

import logging

# Add NullHandler to prevent unwanted output when no logging is configured
# This follows Python library logging best practices
logging.getLogger(__name__).addHandler(logging.NullHandler())

from lex_helper.channels.base import Channel
from lex_helper.channels.channel_formatting import format_for_channel
from lex_helper.channels.lex import LexChannel
from lex_helper.channels.sms import SMSChannel
from lex_helper.core import dialog
from lex_helper.core.disambiguation import (
    BedrockDisambiguationConfig,
    BedrockDisambiguationGenerator,
    DisambiguationConfig,
    DisambiguationResult,
    IntentCandidate,
)
from lex_helper.core.handler import Config, LexHelper
from lex_helper.core.invoke_bedrock import (
    BedrockInvocationError,
    invoke_bedrock,
    invoke_bedrock_converse,
    invoke_bedrock_simple_converse,
)
from lex_helper.core.message_manager import MessageManager, get_message, set_locale
from lex_helper.core.types import (
    Bot,
    DialogAction,
    ImageResponseCard,
    Intent,
    Interpretation,
    LexBaseResponse,
    LexCustomPayload,
    LexImageResponseCard,
    LexMessages,
    LexPlainText,
    LexRequest,
    LexResponse,
    LexSlot,
    PlainText,
    SentimentResponse,
    SentimentScore,
    SessionAttributes,
    SessionState,
    Transcription,
)
from lex_helper.exceptions.handlers import handle_exceptions
from lex_helper.formatters.buttons import Button

__all__ = [
    "__version__",
    "BedrockDisambiguationConfig",
    "BedrockDisambiguationGenerator",
    "BedrockInvocationError",
    "Bot",
    "Button",
    "Channel",
    "Config",
    "DialogAction",
    "dialog",
    "DisambiguationConfig",
    "DisambiguationResult",
    "format_for_channel",
    "get_message",
    "handle_exceptions",
    "ImageResponseCard",
    "Intent",
    "IntentCandidate",
    "Interpretation",
    "invoke_bedrock",
    "invoke_bedrock_converse",
    "invoke_bedrock_simple_converse",
    "LexBaseResponse",
    "LexChannel",
    "LexCustomPayload",
    "LexHelper",
    "LexImageResponseCard",
    "LexMessages",
    "LexPlainText",
    "LexRequest",
    "LexResponse",
    "LexSlot",
    "MessageManager",
    "PlainText",
    "SentimentResponse",
    "SentimentScore",
    "SessionAttributes",
    "SessionState",
    "set_locale",
    "SMSChannel",
    "Transcription",
]
