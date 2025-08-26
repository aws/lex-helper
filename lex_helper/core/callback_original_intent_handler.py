# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from typing import TypeVar

from loguru import logger

from lex_helper import LexRequest, LexResponse, SessionAttributes

from .call_handler_for_file import call_handler_for_file

T = TypeVar("T", bound=SessionAttributes)


def callback_original_intent_handler(lex_request: LexRequest[T]) -> LexResponse[T]:
    logger.debug("CALLING BACK ORIGINAL HANDLER")

    callback_event = lex_request.sessionState.sessionAttributes.callback_event
    callback_handler = lex_request.sessionState.sessionAttributes.callback_handler or ""
    if not callback_event and not callback_handler:
        logger.debug("NO CALLBACK EVENT OR HANDLER")
        return call_handler_for_file("common_greeting_auth", lex_request)

    if callback_event:
        callback_request = json.loads(callback_event)
        logger.debug("THIS IS THE CALLBACK REQUEST {}".format(callback_request))
        del lex_request.sessionState.sessionAttributes.callback_event
        del lex_request.sessionState.sessionAttributes.callback_handler
        lex_payload: LexRequest[T] = LexRequest(**callback_request)
        # TODO update callback request session attrs with the more recent ones
        logger.debug("MERGING SESSION ATTRIBUTES")
        lex_payload.sessionState.sessionAttributes = lex_request.sessionState.sessionAttributes
    else:
        lex_payload = lex_request
        lex_payload.sessionState.intent.slots = {}
        lex_payload.sessionState.intent.name = callback_handler

    return call_handler_for_file(callback_handler, lex_payload)
