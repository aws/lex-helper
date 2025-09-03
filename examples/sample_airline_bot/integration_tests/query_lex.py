# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import sys
from collections.abc import Iterable
from typing import Any, TypeVar
from unittest import TestCase

import boto3
from botocore.config import Config
from loguru import logger

from lex_helper import SessionAttributes

# Get the path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate to the sample_airline_bot root directory
sample_airline_bot_root = os.path.dirname(current_dir)

# Add the fulfillment function source to sys.path
fulfillment_src_path = os.path.join(sample_airline_bot_root, "lambdas", "fulfillment_function", "src")
sys.path.insert(0, fulfillment_src_path)

# Add the integration_tests directory to sys.path for lex_emulator import
sys.path.insert(0, current_dir)

from lex_emulator import query_lex_emulator, update_session_variable

my_config = Config(
    region_name="us-east-1",
    signature_version="v4",
    retries={"max_attempts": 10, "mode": "standard"},
)

client = boto3.client("lexv2-runtime", config=my_config)


def sort_recursive(item: Any) -> Any:
    if isinstance(item, dict):
        return sorted((k, sort_recursive(v)) for k, v in item.items())  # type: ignore
    elif isinstance(item, Iterable) and not isinstance(item, str):
        return sorted(sort_recursive(x) for x in item)  # type: ignore
    else:
        return item


def get_session_attributes(session_id: str) -> dict[str, Any]:
    cdk_outputs = {}
    session_attributes: dict[str, Any] = {}

    with open("cdk-outputs.json") as json_file:
        cdk_outputs = json.load(json_file)
        first_key = list(cdk_outputs.keys())[0]
        va_bot = cdk_outputs.get(first_key)
        try:
            # Get current session state
            current_session = client.get_session(
                botId=va_bot.get("LexBotId"),  # type: ignore
                botAliasId=va_bot.get("LexBotAliasId"),  # type: ignore
                localeId="en_US",
                sessionId=session_id,
            )
        except Exception as e:
            logger.warning(f"Error getting Lex session for session_id: {session_id}, {e}")
            current_session = {}

        # Updated session state
        session_state: Any = current_session.get("sessionState", {})
        session_attributes: dict[str, Any] = dict(session_state.get("sessionAttributes", {}))

    return session_attributes


def update_lex_session_variable(variable_name: str, variable_value: Any, session_id: str) -> None:
    cdk_outputs = {}
    with open("cdk-outputs.json") as json_file:
        cdk_outputs = json.load(json_file)
        first_key = list(cdk_outputs.keys())[0]
        va_bot = cdk_outputs.get(first_key)
        try:
            # Get current session state
            current_session = client.get_session(
                botId=va_bot.get("LexBotId"),  # type: ignore
                botAliasId=va_bot.get("LexBotAliasId"),  # type: ignore
                localeId="en_US",
                sessionId=session_id,
            )
        except Exception as e:
            logger.warning(f"Error getting Lex session for session_id: {session_id}, {e}")
            current_session = {}

        # Updated session state
        session_state = current_session.get("sessionState", {})  # type: ignore
        session_attributes = session_state.get("sessionAttributes", {})  # type: ignore

        session_attributes[variable_name] = variable_value

        # Remove any session_attributes that are None
        session_attributes = remove_none_values(session_attributes)  # type: ignore

        session_state["sessionAttributes"] = session_attributes
        # Update real lex session
        response = client.put_session(
            botId=va_bot.get("LexBotId"),  # type: ignore
            botAliasId=va_bot.get("LexBotAliasId"),  # type: ignore
            localeId="en_US",
            messages=current_session.get("messages", []),
            sessionId=session_id,
            sessionState=session_state,  # type: ignore
        )
        logger.trace(response)
        logger.trace(current_session)

        # Update emulator session
        update_session_variable(session_id, session_attributes)


T = TypeVar("T", bound=SessionAttributes)


def query_lex(text: str, session_id: str, session_attributes: dict[str, Any] | None = None) -> dict[str, Any]:
    emulator_response = query_lex_emulator(text, session_id, session_attributes)

    # Check if cdk-outputs.json exists for real Lex comparison
    if not os.path.exists("cdk-outputs.json"):
        # If no CDK outputs file, just return the emulator response
        return emulator_response

    cdk_outputs = {}
    with open("cdk-outputs.json") as json_file:
        cdk_outputs = json.load(json_file)
        first_key = list(cdk_outputs.keys())[0]
        va_bot = cdk_outputs.get(first_key)
        try:
            response: dict[str, Any] = client.recognize_text(
                botId=va_bot.get("LexBotId"),  # type: ignore
                botAliasId=va_bot.get("LexBotAliasId"),  # type: ignore
                localeId="en_US",
                text=text,
                sessionId=session_id,
            )
            # Compare the response from Lex with the response from the emulator, for coverage
            emu_state = emulator_response["sessionState"]
            lex_state = remove_none_values(response["sessionState"])  # type: ignore
            emu_dialog_action = emu_state["dialogAction"]["type"]
            lex_dialog_action = lex_state["dialogAction"]["type"]  # type: ignore
            try:
                tc = TestCase()
                tc.assertEqual(sort_recursive(emulator_response["messages"]), sort_recursive(response["messages"]))
            except AssertionError as e:
                received_from_real_lex: Any = sort_recursive(response["messages"])
                received_from_emulator: Any = sort_recursive(emulator_response["messages"])

                logger.bind(real_lex=received_from_real_lex, emulator=received_from_emulator).error(
                    "Your real Lex bot returned a different message from what the emulator provided, you either need to redeploy or the emulator has a bug."
                )
                logger.error(f"Real Lex response: {received_from_real_lex}")
                logger.error(f"Emulator response: {received_from_emulator}")
                assert emu_dialog_action == lex_dialog_action, "dialogAction type is different"
                raise e

            return response
        except AssertionError as e:
            raise e
        except Exception as e:
            logger.warning(f"Error querying Lex for text: {text}")
            raise e


def remove_none_values(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: remove_none_values(v) for k, v in data.items() if v is not None}  # type: ignore
    elif isinstance(data, list):
        return [remove_none_values(v) for v in data if v is not None]  # type: ignore
    else:
        return data
