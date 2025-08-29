# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from collections.abc import Callable
from typing import Any, TypeVar

from lex_helper.channels.base import Channel
from lex_helper.channels.lex import LexChannel
from lex_helper.channels.sms import SMSChannel
from lex_helper.core.types import (
    LexImageResponseCard,
    LexPlainText,
    LexResponse,
    PlainText,
    SessionAttributes,
)
from lex_helper.utils.add_to_list import add_to_list

T = TypeVar("T", bound=SessionAttributes)


def format_for_channel(response: LexResponse[T], channel_string: str = "lex"):
    content_process_map: dict[type, Callable[[Any, Channel, list[str], list[Any]], list[Any]]] = {
        PlainText: _format_plain_text,
        LexPlainText: _format_plain_text,
        LexImageResponseCard: _format_image_card,
    }

    channel = _get_channel(channel_string)
    formatted_response = response.model_copy(deep=True)
    formatted_messages = []
    options_provided = []
    for message in response.messages:
        fn = content_process_map.get(type(message))
        if fn is not None:
            formatted_messages = fn(message, channel, options_provided, formatted_messages)
        else:
            raise Exception("No formatter was found for this message type")

    # If the channel is Lex, and the response only has a single message, if it's an imageResponseCard, prepend a new PlainText message with the imageResponseCard title.
    # This is SPECIFICALLY only for the Lex UI and Recognize Text, as Lex throws an error if you ONLY return an imageResponseCard.  This is NOT what the documentation says.
    if len(formatted_messages) == 1 and isinstance(formatted_messages[0], LexImageResponseCard):
        formatted_messages.insert(
            0,
            LexPlainText(
                content=formatted_messages[0].imageResponseCard.title,
                contentType="PlainText",
                image_url=None,  # type: ignore
            ),
        )
        # Remove title from the imageResponseCard
        formatted_messages[1].imageResponseCard.title = " "  # type: ignore

    if len(options_provided) > 0:
        formatted_response.sessionState.sessionAttributes.options_provided = json.dumps(options_provided)
        options_provided.clear()

    formatted_response.messages = formatted_messages

    # On dumped_response['sessionState']['sessionAttributes'], convert all values to string
    dumped_response = formatted_response.model_dump(exclude_none=True, by_alias=True)
    _stringify_session_attributes(session_attributes=dumped_response)

    return dumped_response


def _stringify_session_attributes(session_attributes: dict[str, Any]):
    for key in session_attributes["sessionState"]["sessionAttributes"]:
        session_attributes["sessionState"]["sessionAttributes"][key] = str(
            session_attributes["sessionState"]["sessionAttributes"][key]
        )


def _get_channel(channel_string: str) -> Channel:
    channels = {
        "sms": SMSChannel,
        "lex": LexChannel,
    }
    channel = channels.get(channel_string.lower(), LexChannel)  # Get the channel, default to Lex

    return channel()  # type: ignore


def _format_plain_text(
    message: LexPlainText,
    channel: Channel,
    options_provided: list[str],
    formatted_messages: list[Any],
) -> list[Any]:
    return add_to_list(lst=formatted_messages, item=channel.format_plain_text(message))


def _format_image_card(
    message: LexImageResponseCard,
    channel: Channel,
    options_provided: list[str],
    formatted_messages: list[Any],
) -> list[Any]:
    return add_to_list(lst=formatted_messages, item=message)
