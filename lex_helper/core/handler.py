# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable
from typing import Any, Generic, TypeVar

from loguru import logger
from pydantic import BaseModel

from lex_helper.channels.channel_formatting import format_for_channel
from lex_helper.core.call_handler_for_file import call_handler_for_file
from lex_helper.core.dialog import (
    any_unknown_slot_choices,
    get_intent,
    handle_any_unknown_slot_choice,
    parse_lex_request,
)
from lex_helper.core.types import (
    LexMessages,
    LexRequest,
    LexResponse,
    SessionAttributes,
)
from lex_helper.exceptions.handlers import IntentNotFoundError, handle_exceptions

T = TypeVar("T", bound=SessionAttributes)


class Config(BaseModel, Generic[T]):
    session_attributes: T
    package_name: str | None = (
        "fulfillment_function"  # This is the name of the package to import the intents from.  Should be the same as the name of the package you're running the handler from.
    )


class LexHelper(Generic[T]):
    def __init__(self, config: Config[T]):
        self.config = config

    def handler(self, event: dict[str, Any], context: Any) -> dict[str, Any]:
        """
        Primary entry point for the lex_helper library.

        This function is designed to handle AWS Lambda events triggered by Amazon Lex. It processes the incoming
        event and context, and utilizes custom session attributes if provided. The function orchestrates the
        entire flow, including parsing the Lex request, handling intents, managing session state, and formatting
        the response for the channel.

        Args:
            event (dict[str, Any]): The event data from AWS Lambda, typically containing the Lex request.
            context (Any): The context object provided by AWS Lambda, containing runtime information.

        Returns:
            dict[str, Any]: A formatted response ready to be sent back to Amazon Lex.
        """
        logger.trace("START")
        session_attributes: T = self.config.session_attributes
        logger.debug(f"SessionAttributes type: {type(session_attributes)}")
        lex_payload: LexRequest[T] = parse_lex_request(event, session_attributes)
        with logger.contextualize(
            sessionId=lex_payload.sessionId,
            utterance=lex_payload.inputTranscript,
            sessionAttributes=lex_payload.sessionState.sessionAttributes.model_dump(exclude_none=True),
        ):
            return self._main_handler(lex_payload)

    def _main_handler(self, lex_payload: LexRequest[T]) -> dict[str, Any]:
        """
        Core handler for processing Lex requests.

        This function takes a parsed LexRequest object and manages the flow of handling the request. It determines
        the appropriate intent handler, manages session state, and processes any callbacks. It also handles
        exceptions and formats the final response for the channel.

        Args:
            lex_payload (LexRequest[T]): The parsed Lex request containing session and intent information.

        Returns:
            dict[str, Any]: A formatted response ready to be sent back to Amazon Lex.
        """
        messages: LexMessages = []

        # Display Intent for Debug Purposes
        lex_intent = get_intent(lex_payload)
        lex_intent_name = lex_intent.name
        logger.debug(f"Lex-Intent : {lex_intent_name}")

        # Handlers is a list of functions that take a LexRequest and return a LexResponse
        handlers: list[Callable[[LexRequest[T]], LexResponse[T] | None]] = [
            self.regular_intent_handler,
        ]

        try:
            response = None
            for message_handler in handlers:
                try:
                    response = message_handler(lex_payload)
                    if response:
                        break
                except IntentNotFoundError:
                    raise
                except Exception as e:
                    logger.exception(f"Handler failed: {e}")
                    continue

            if not response:
                raise ValueError(f"Unable to find handler for intent : {lex_intent_name}")

            if not hasattr(response, "sessionState"):
                raise ValueError(f"SessionState not found in response : {response}")

            lex_payload.sessionState = response.sessionState
            lex_payload.requestAttributes = response.requestAttributes

            messages: LexMessages = []

            messages += response.messages
            if response.requestAttributes and "callback" in response.requestAttributes:
                callback_name = response.requestAttributes["callback"]
                logger.debug(f"CALLBACK FOUND : {callback_name}")
                response.requestAttributes.pop("callback")
                response = call_handler_for_file(
                    intent_name=callback_name, lex_request=lex_payload, package_name=self.config.package_name
                )
                lex_payload.sessionState = response.sessionState
                messages += response.messages
            response.messages = messages

        except IntentNotFoundError:
            raise
        except Exception as e:
            response = handle_exceptions(e, lex_payload)

        formatted_response: dict[str, Any] = {}

        try:
            formatted_response = format_for_channel(response=response, channel_string="lex")
            return formatted_response

        except Exception as e:
            logger.exception(e)
            raise e

    def regular_intent_handler(self, lex_payload: LexRequest[T]) -> LexResponse[T] | None:
        """
        Route the incoming request based on intent.
        The JSON body of the request is provided in the event slot.
        """
        logger.trace(f"Payload from Lex : {lex_payload}")
        intent = get_intent(lex_payload)
        intent_name = intent.name
        lex_payload.sessionState.sessionAttributes.lex_intent = intent.name

        response: LexResponse[T] | None = None

        if not intent_name.__contains__("Common_Exit_Feedback"):
            lex_payload.sessionState.activeContexts = [
                {
                    "name": "transition_to_exit",
                    "contextAttributes": {},
                    "timeToLive": {"timeToLiveInSeconds": 900, "turnsToLive": 20},
                }
            ]

        if any_unknown_slot_choices(lex_request=lex_payload):
            response = handle_any_unknown_slot_choice(lex_request=lex_payload)

        else:
            intent_name = lex_payload.sessionState.intent.name
            logger.debug(f"Calling handler for intent : {intent_name}")
            response = call_handler_for_file(
                intent_name=intent_name, lex_request=lex_payload, package_name=self.config.package_name
            )
        return response
