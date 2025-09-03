# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import os
import sys
from collections.abc import Callable
from functools import cache
from typing import Any
from uuid import uuid4

from fuzzywuzzy import fuzz
from loguru import logger

from .emu_classes import IntentData, Slot, SlotType, Utterance
from .evaluate_lex_conditional_expression import evaluate_lex_conditional_expression

# Get the path to the current directory
base_path = os.path.dirname(os.path.abspath(__file__))

# Navigate to the sample_airline_bot root directory
# From integration_tests/lex_emulator/ -> integration_tests/ -> sample_airline_bot/
sample_airline_bot_root = os.path.dirname(os.path.dirname(base_path))

# Add the fulfillment function source to sys.path
fulfillment_src_path = os.path.join(sample_airline_bot_root, "lambdas", "fulfillment_function", "src")
sys.path.insert(0, fulfillment_src_path)

# Set the messages path for MessageManager
messages_path = os.path.join(
    sample_airline_bot_root, "lambdas", "fulfillment_function", "src", "fulfillment_function", "messages"
)
os.environ["MESSAGES_YAML_PATH"] = messages_path

# Make sample_airline_bot_root available globally for other functions
globals()["sample_airline_bot_root"] = sample_airline_bot_root
import json  # noqa: E402

from aws_lambda_powertools.utilities.typing import LambdaContext  # noqa: E402
from fulfillment_function.lambda_function import lambda_handler

from lex_helper import (
    Bot,
    DialogAction,
    Intent,
    LexRequest,
    LexResponse,
    SessionAttributes,
    SessionState,
)

# Fake Sessions managed by Fake Lex Emulator
sessions: dict[str, Any] = {}


def generate_session_id(length: int = 32):
    logger.trace(f"convo-uuid : {length}")  # log to supress the unused parameter warning
    return str(uuid4())


def get_session(session_id: str, text: str | None = None):
    """
    Function to retrieve a session from global sessions.
    """
    current_session = sessions.get(session_id, None)
    intent_name = "Greeting"  # Default

    if current_session is None and text is not None:
        # Use this for getting FallbackIntent
        intent_name = find_intent_by_utterance(text=text)

    current_session = sessions.get(
        session_id,
        {
            "dialogAction": {"type": "Delegate", "slotToElicit": None},
            "intent": {
                "name": intent_name,
                "slots": {},
                "state": "InProgress",
                "confirmationState": "None",
            },
            "activeContexts": [],
            "sessionAttributes": {},
        },
    )

    if "reprompt-" in session_id:
        set_session(session_id, current_session)

    return current_session


def set_session(session_id: str, session_data: dict[Any, Any]):
    """
    Function to set a session in global sessions.
    """
    sessions[session_id] = session_data


def remove_session(session_id: str):
    """
    Function to remove a session from global sessions.
    """
    if session_id in sessions:
        del sessions[session_id]


def update_session_variable(session_id: str, session_attributes: dict[str, Any]):
    session_state = get_session(session_id)
    session_state["sessionAttributes"] = session_attributes
    set_session(session_id=session_id, session_data=session_state)


def query(text: str, session_id: str, req_attr: dict[str, Any] | None = None) -> LexResponse[SessionAttributes]:
    # This is a helper function for people that want to use the Lex emulator and receive the response as a LexResponse object
    response = query_lex_emulator(text=text, session_id=session_id, req_attr=req_attr)
    return LexResponse(**response)


def query_lex_emulator(text: str, session_id: str, req_attr: dict[str, Any] | None = None):
    request_attributes = req_attr or {}
    session_state = get_session(session_id=session_id, text=text)
    dialog_action_type = None
    slot_to_elicit = ""
    slots: dict[str, Any] = {}
    if session_state is None or session_state.get("intent", None) is None:
        intent_name = find_intent_by_utterance(text=text)
        if intent_name:
            logger.trace(f"The intent for the utterance '{text}' is: {intent_name}")
            # Get slots for the intent if the utterances had slots in them
            slots = resolve_slots_within_utterance(intent_name=intent_name, text=text, slots=slots)
        else:
            logger.warning("No matching intent found.")
    else:
        intent_name = session_state["intent"]["name"]
        dialog_action_type = session_state["dialogAction"]["type"]
        slot_to_elicit = str(session_state.get("dialogAction", {}).get("slotToElicit", None))
        slots = session_state["intent"]["slots"]

    if dialog_action_type == "ElicitSlot":
        invocation_label = find_slot_invocation_label(intent_name=intent_name, slot_name=slot_to_elicit)
        slots[slot_to_elicit] = resolve_slot(
            intent_name=intent_name,
            slot_to_elicit=slot_to_elicit,
            text=text,
            slots=slots,
        )
    elif dialog_action_type == "ElicitIntent":
        intent_name = find_intent_by_utterance(text=text)
        if intent_name != "FallbackIntent":
            logger.trace(f"The intent for the utterance '{text}' is: {intent_name}")
            # Get slots for the intent if the utterances had slots in them
            slots = resolve_slots_within_utterance(intent_name=intent_name, text=text, slots=slots)
        session_state["intent"]["name"] = intent_name
        invocation_label = find_invocation_label(intent_name=intent_name)
    else:
        invocation_label = find_invocation_label(intent_name=intent_name)

    session_attributes = SessionAttributes()
    if session_state is not None:
        session_attributes = session_state.get("sessionAttributes", {})

    # Ensure session_attributes is a dict, not None
    if session_attributes is None:
        session_attributes = {}

    if intent_name:
        session_attributes["intent_id"] = intent_name  # type: ignore

    # Ensure required fields for AirlineBotSessionAttributes are present
    if "callback_event" not in session_attributes:
        session_attributes["callback_event"] = ""
    if "callback_handler" not in session_attributes:
        session_attributes["callback_handler"] = ""
    lex_request = LexRequest(
        responseContentType="PlainText",
        invocationSource="DialogCodeHook",
        invocationLabel=invocation_label,
        inputMode="Text",
        transcriptions=[],
        messageVersion="1.0",
        sessionState=SessionState(
            dialogAction=DialogAction(type=dialog_action_type, slotToElicit=slot_to_elicit),
            intent=Intent(
                name=intent_name,
                slots=slots,
                state="InProgress",
                confirmationState="None",
            ),
            activeContexts=session_state.get("activeContexts", []),
            sessionAttributes=session_attributes,
        ),
        sessionId=session_id,
        inputTranscript=text,
        interpretations=[],
        bot=Bot(
            name="Emulator",
            version="1",
            localeId="en_US",
            id="Emulator",
            aliasId="Emulator",
            aliasName="Emulator",
        ),
        requestAttributes=request_attributes,
    )

    # Fake Context
    context: LambdaContext = LambdaContext()
    context._function_name = "Placeholder"  # type: ignore
    context._memory_limit_in_mb = 128  # type: ignore
    context._invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:Placeholder"  # type: ignore
    context._aws_request_id = "12345678-1234-1234-1234-123456789012"  # type: ignore

    lex_response = lambda_handler(event=lex_request.model_dump(), context=context)
    messages = []

    if lex_response:
        set_session(session_id=session_id, session_data=lex_response["sessionState"])
        messages = lex_response["messages"]
    session_attributes = lex_response.get("sessionState", None).get("sessionAttributes", None)

    # See if the dialogAction type is Close, if so, see if we're going to another intent
    if lex_response["sessionState"]["dialogAction"]["type"] == "Close":
        lex_request.sessionState.sessionAttributes = session_attributes
        closing_intent = resolve_closing_intent(lex_response=lex_response, intent_name=intent_name)
        if closing_intent:
            lex_request.sessionState.intent.name = closing_intent
            invocation_label = find_invocation_label(intent_name=closing_intent)
            lex_request.invocationLabel = invocation_label
            lex_response = lambda_handler(lex_request.model_dump(), context)
            messages = messages + lex_response["messages"]

    response = LexResponse(
        sessionState=SessionState(
            dialogAction=DialogAction(
                type=lex_response["sessionState"]["dialogAction"].get("type", None),
                slotToElicit=lex_response["sessionState"]["dialogAction"].get("slotToElicit", None),
            ),
            intent=Intent(
                name=intent_name,
                slots=slots,
                state="InProgress",
                confirmationState="None",
            ),
            activeContexts=[],
            sessionAttributes=session_attributes,
        ),
        messages=messages,
        requestAttributes=lex_response.get("requestAttributes", {}),  # type: ignore
    )
    dict_response = response.model_dump(exclude_unset=True, exclude_none=True)
    return remove_none_values(dict_response)


def remove_none_values(data: dict[str, Any] | list[Any] | Any) -> Any:
    if isinstance(data, dict):
        return {k: remove_none_values(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_none_values(v) for v in data if v is not None]
    else:
        return data


def resolve_closing_intent(lex_response: dict[str, Any], intent_name: str):
    # If an intent has a closing intent, return the name of the closing intent
    json_file_path = os.path.join(
        sample_airline_bot_root, f"lex-export/LexBot/BotLocales/en_US/Intents/{intent_name}/Intent.json"
    )

    # open and parse the JSON file
    with open(json_file_path) as json_file:
        data = json.load(json_file)
    intent_closing_setting = data.get("intentClosingSetting", None)
    if intent_closing_setting is not None:
        if "nextStep" in intent_closing_setting:
            if "dialogAction" in intent_closing_setting["nextStep"]:
                if "type" in intent_closing_setting["nextStep"]["dialogAction"]:
                    if intent_closing_setting["nextStep"]["dialogAction"]["type"] == "EvaluateConditional":
                        conditional = intent_closing_setting["conditional"]
                        if conditional["isActive"]:
                            for condition in conditional["conditionalBranches"]:
                                expression = condition["condition"]["expressionString"]
                                expression_matches = evaluate_lex_conditional_expression(
                                    expression=expression,
                                    slot_values=lex_response["sessionState"]["intent"]["slots"],
                                )
                                if expression_matches:
                                    return condition["nextStep"]["intent"]["name"]
                    else:
                        return intent_closing_setting["nextStep"]["intent"]["name"]

    else:
        return None


@cache
def get_slot(intent_name: str, slot_name: str) -> Slot:
    # Returns the slot data for a given intent and slot name
    slot_file_path = os.path.join(
        sample_airline_bot_root, f"lex-export/LexBot/BotLocales/en_US/Intents/{intent_name}/Slots/{slot_name}/Slot.json"
    )
    with open(slot_file_path) as json_file:
        data = json.load(json_file)
        return Slot(**data)


@cache
def get_slot_type(slot_type_name: str) -> SlotType:
    # Returns the slot type data for a given slot type name
    slot_type_file_path = os.path.join(
        sample_airline_bot_root, f"lex-export/LexBot/BotLocales/en_US/SlotTypes/{slot_type_name}/SlotType.json"
    )
    with open(slot_type_file_path) as json_file:
        data = json.load(json_file)
        return SlotType(**data)


def resolve_slot(intent_name: str, slot_to_elicit: str, text: str, slots: dict[str, Any]):
    slot = get_slot(intent_name=intent_name, slot_name=slot_to_elicit)

    # Get the slot type name
    slot_type_name = slot.slotTypeName

    # Resolvers is a list of functions that can resolve a slot
    resolvers: list[Callable[[str, str, str, dict[str, Any]], dict[str, Any] | None]] = [
        resolve_amazon_freeform_slot,  # Resolve an AMAZON.AlphaNumeric or AMAZON.FreeFormInput slot
        resolve_amazon_name_slot,  # Resolve an AMAZON.FirstName or AMAZON.LastName slot
        resolve_amazon_other_slot,  # Resolve any other AMAZON slot
        resolve_custom_slot,  # Resolve a custom slot
    ]

    for resolver in resolvers:
        response = resolver(slot_type_name, slot_to_elicit, text, slots)
        if response:
            return response


def resolve_custom_slot(slot_type_name: str, slot_to_elicit: str, text: str, slots: dict[str, Any]):
    slot_type = get_slot_type(slot_type_name)
    interpreted_value = get_sample_value(slot_type_name, text)
    sub_slots: dict[str, Any] | None = None

    if slot_type.compositeSlotTypeSetting:
        # todo: Need to make this work for all composites, NOT just first name last name
        sub_slots = {}
        for sub_slot in slot_type.compositeSlotTypeSetting.subSlots:
            logger.trace(sub_slot)
            if sub_slot.slotTypeId == "AMAZON.AlphaNumeric" or sub_slot.slotTypeId == "AMAZON.FreeFormInput":
                sub_slots[sub_slot.name] = {
                    "value": {
                        "originalValue": text,
                        "interpretedValue": text,
                        "resolvedValues": [text],
                    }
                }
            elif sub_slot.slotTypeId == "AMAZON.FirstName":
                if slot_to_elicit in slots and slots[slot_to_elicit]["value"]["originalValue"]:
                    # If the slot_to_elicit is already filled, then we don't need to ask for it again
                    first_name = slots[slot_to_elicit]["value"]["originalValue"]
                else:
                    # first_name is everything in text.split(" ") except the last element
                    split_name = text.split(" ")
                    # But ONLY if there is more than one element.  If just one, return it as the name.
                    if len(split_name) > 1:
                        first_name = " ".join(split_name[:-1])
                    else:
                        first_name = text

                sub_slots[sub_slot.name] = {
                    "value": {
                        "originalValue": first_name,
                        "interpretedValue": first_name,
                        "resolvedValues": first_name,
                    },
                }
            elif sub_slot.slotTypeId == "AMAZON.LastName":
                split_name = text.split(" ")
                # todo: This is a highly flawed way of doing this.  Need to make this work for all composites, NOT
                # just first name last name.  Basically, this is a workaround so that if someone answers with first
                # name, they will get reprompted, then answer with last name.  This will then be able to resolve the
                # slot.  The way lex works though is for a composite slot, it checks to see WHAT is already filled,
                # this is a terrible way to emulate it, but it would be a lot of work to fully flesh it out.
                if slot_to_elicit in slots and slots[slot_to_elicit]["value"]["originalValue"]:
                    last_name = split_name[-1]
                elif len(split_name) > 1:
                    last_name = split_name[-1]
                else:
                    last_name = None
                sub_slots[sub_slot.name] = {
                    "value": {
                        "originalValue": last_name,
                        "interpretedValue": last_name,
                        "resolvedValues": last_name,
                    }
                }
            else:
                regular_slot_id = sub_slot.slotTypeId
                # For every folder in lex-export/LexBot/BotLocales/en_US/SlotTypes/, load the SlotType.json file within the subfolder.
                folder = os.path.join(sample_airline_bot_root, "lex-export/LexBot/BotLocales/en_US/SlotTypes/")
                for subfolder in os.listdir(folder):
                    slot_type = get_slot_type(subfolder)
                    if slot_type.identifier == regular_slot_id:
                        interpreted_value = get_sample_value(subfolder, text)
                        sub_slots[sub_slot.name] = {
                            "value": {
                                "originalValue": text,
                                "interpretedValue": interpreted_value,
                                "resolvedValues": [interpreted_value],
                            },
                            "shape": "Scalar",
                        }
                        break
    if interpreted_value is None and sub_slots:
        # Loop through each subslot, and return the first interpreted value that is not None
        for sub_slot in sub_slots:
            if sub_slots[sub_slot]["value"]["interpretedValue"]:
                interpreted_value = sub_slots[sub_slot]["value"]["interpretedValue"]
                break
    return_value = {
        "value": {
            "originalValue": text,
            "interpretedValue": interpreted_value,
            "resolvedValues": [interpreted_value],
        }
    }
    if sub_slots is not None:
        return_value["subSlots"] = sub_slots
    return return_value


def resolve_amazon_other_slot(slot_type_name: str, slot_to_elicit: str, text: str, slots: dict[str, Any]):
    # Resolve any other AMAZON slot.  It is likely that new types will be added, and this function will need to be updated
    if slot_type_name.startswith("AMAZON."):
        logger.warning("Unknown builtin slot_type_name")
        interpreted_value = {
            "value": {
                "originalValue": text,
                "interpretedValue": text,
                "resolvedValues": [text],
            }
        }
        return {
            "value": {
                "originalValue": text,
                "interpretedValue": interpreted_value,
                "resolvedValues": [interpreted_value],
            }
        }
    return None


def resolve_amazon_name_slot(slot_type_name: str, slot_to_elicit: str, text: str, slots: dict[str, Any]):
    # Amazon name slots are actually extremely complex.  This is a very basic implementation that only works for the most
    # basic of cases.  Things like if Lex already thinks it has a name saved in a slot will impact the resolution.
    # Right now, neither is used at all, and hopefully it stays that way.
    if slot_type_name == "AMAZON.FirstName":
        return {
            "value": {
                "originalValue": text.split(" ")[0],
                "interpretedValue": text.split(" ")[0],
                "resolvedValues": [text.split(" ")[0]],
            }
        }
    elif slot_type_name == "AMAZON.LastName":
        return {
            "value": {
                "originalValue": text.split(" ")[1],
                "interpretedValue": text.split(" ")[1],
                "resolvedValues": [text.split(" ")[1]],
            }
        }
    else:
        return None


def resolve_amazon_freeform_slot(slot_type_name: str, slot_to_elicit: str, text: str, slots: dict[str, Any]):
    # Resolve an AMAZON.AlphaNumeric or AMAZON.FreeFormInput slot, they are a special case because no interpretation is
    # done, just a return of the utterance as-is.
    if slot_type_name == "AMAZON.AlphaNumeric" or slot_type_name == "AMAZON.FreeFormInput":
        return {
            "value": {
                "originalValue": text,
                "interpretedValue": text,
                "resolvedValues": [text],
            }
        }
    return None


@cache
def get_sample_value(slot_type_name: str, text: str):
    slot_type = get_slot_type(slot_type_name=slot_type_name)
    best_match = None
    best_ratio = 0

    if slot_type.slotTypeValues is None:
        logger.trace("No slot type values found.")
        return None
    for slot_type_value in slot_type.slotTypeValues:
        synonyms = [slot_type_value.sampleValue]  # Add the actual value as a synonym
        if slot_type_value.synonyms:
            synonyms = synonyms + (slot_type_value.synonyms)
        for synonym in synonyms:
            ratio = fuzz.ratio(synonym.value.lower(), text.lower())
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = slot_type_value.sampleValue.value
    if best_ratio >= 60:  # Adjust this threshold according to your needs
        return best_match
    else:
        logger.warning("No matching slot type value found.")
        return None


@cache
def find_slot_invocation_label(intent_name: str, slot_name: str):
    slot = get_slot(intent_name=intent_name, slot_name=slot_name)

    # iterate over the sample utterances
    if slot.valueElicitationSetting is not None:
        slot_capture_setting = slot.valueElicitationSetting.slotCaptureSetting
        if slot_capture_setting is not None:
            if slot_capture_setting.codeHook is not None:
                return slot_capture_setting.codeHook.invocationLabel
            elif slot_capture_setting.elicitationCodeHook:
                return slot_capture_setting.elicitationCodeHook.invocationLabel
    logger.warning("No matching slot invocation label found.")
    return None


@cache
def get_intent(intent_name: str) -> IntentData:
    json_file_path = os.path.join(
        sample_airline_bot_root, f"lex-export/LexBot/BotLocales/en_US/Intents/{intent_name}/Intent.json"
    )

    # open and parse the JSON file
    with open(json_file_path) as json_file:
        data = json.load(json_file)
        intent = IntentData(**data)

        intent.sampleUtterances = get_populated_utterances(intent)

        return intent


def get_populated_utterances(intent: IntentData) -> list[Utterance]:
    # Within intent.sampleUtterances, for each utterance, see if it contains a slot (e.g. {SlotName}).
    # The SlotName must match the name of a slot under intent.slotPriorities.  Once we have that, we need to get the slot_type, and replace the utterance with each of the slot_type_values.  This will give us a list of all possible utterances for the intent.
    populated_utterances: list[Utterance] = []
    if intent.sampleUtterances:
        # If there are no slots, just return the original utterances
        if not intent.slotPriorities:
            return intent.sampleUtterances

        for sample in intent.sampleUtterances:
            # Check if this utterance contains any slots
            has_slots = False
            for slot in intent.slotPriorities:
                slot_name = slot.slotName
                slot = get_slot(intent_name=intent.name, slot_name=slot_name)
                slot_type_name = slot.slotTypeName
                if "{" + slot_type_name + "}" in sample.utterance:
                    has_slots = True
                    slot_type = get_slot_type(slot_type_name=slot_type_name)
                    if slot_type.slotTypeValues:
                        for slot_type_value in slot_type.slotTypeValues:
                            populated_utterances.append(
                                Utterance(
                                    utterance=sample.utterance.replace(
                                        "{" + slot_type_name + "}",
                                        slot_type_value.sampleValue.value,
                                    )
                                )
                            )
                            if slot_type_value.synonyms:
                                for synonym in slot_type_value.synonyms:
                                    populated_utterances.append(
                                        Utterance(
                                            utterance=sample.utterance.replace(
                                                "{" + slot_type_name + "}",
                                                synonym.value,
                                            )
                                        )
                                    )

            # If this utterance doesn't contain slots, add it as-is
            if not has_slots:
                populated_utterances.append(sample)

    # Keep single copy of each sample.utterance in populated_utterances
    populated_utterances = list({v.utterance: v for v in populated_utterances}.values())

    return populated_utterances


@cache
def find_invocation_label(intent_name: str):
    intent = get_intent(intent_name)

    # iterate over the sample utterances
    if intent.initialResponseSetting:
        return intent.initialResponseSetting.codeHook.invocationLabel

    # if no match was found, return None
    return "FallbackIntent"


def resolve_slots_within_utterance(intent_name: str, text: str, slots: dict[str, Any]) -> dict[str, Any]:
    if intent_name == "FallbackIntent":
        logger.error("Arrived at FallbackIntent")
        return {}
    slot_type = ""
    json_file_path = os.path.join(
        sample_airline_bot_root, "lex-export/LexBot/BotLocales/en_US/Intents/" + intent_name + "/Slots"
    )
    # iterate over each subfolder (intent) in the base directory
    if os.path.isdir(json_file_path):
        for slot in os.listdir(json_file_path):
            slots[slot_type] = resolve_slot(intent_name=intent_name, slot_to_elicit=slot, text=text, slots=slots)
        return slots
    return {}


@cache
def find_intent_by_utterance(text: str):
    base_dir = os.path.join(sample_airline_bot_root, "lex-export/LexBot/BotLocales/en_US/Intents")
    intent_ratio_map = {}
    sorted_intent_ratio_map = {}
    # iterate over each subfolder (intent) in the base directory
    for intent in os.listdir(base_dir):
        intent_path = os.path.join(base_dir, intent)

        # check if it is a folder (directory)
        if os.path.isdir(intent_path):
            data = get_intent(intent)

            # iterate over the sample utterances
            if data.sampleUtterances:
                for sample in data.sampleUtterances:
                    # if this utterance matches the text, return the intent name
                    if str(sample.utterance).lower() == str(text).lower():
                        return intent

                    # Using fuzzy, return the intent name if the ratio is above 60
                    ratio = fuzz.ratio(sample.utterance.lower(), text.lower())
                    intent_ratio_map = update_map(intent_ratio_map, intent, ratio)

    sorted_intent_ratio_map = sort_dict_by_value(intent_ratio_map, reverse=True)
    if len(sorted_intent_ratio_map) > 0:
        return list(sorted_intent_ratio_map.keys())[0]
    # if no match was found, return None
    return "FallbackIntent"


def update_map(d: dict[str, int], key: str, new_value: int) -> dict[str, int]:
    existing_val = d.get(key, 0)
    if existing_val < new_value:
        d[key] = new_value
    return d


def sort_dict_by_value(d: dict[str, int], reverse: bool = False) -> dict[str, int]:
    if len(d) == 0:
        return d
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=reverse))
