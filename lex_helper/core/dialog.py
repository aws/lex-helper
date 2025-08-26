# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Standard util methods to manage dialog state
"""

import json
import logging
from typing import Any, Dict, Optional, TypeVar, Union

from pydantic import BaseModel

from lex_helper.core.call_handler_for_file import call_handler_for_file
from lex_helper.core.types import (
    ActiveContexts,
    DialogAction,
    Intent,
    LexCustomPayload,
    LexImageResponseCard,
    LexMessages,
    LexPlainText,
    LexRequest,
    LexResponse,
    LexSlot,
    SessionAttributes,
    SessionState,
)

logger = logging.getLogger(__name__)


class PydanticEncoder(json.JSONEncoder):
    def default(self, o: Any):
        if isinstance(o, BaseModel):
            return o.model_dump()
        return super().default(o)


T = TypeVar("T", bound=SessionAttributes)


def get_sentiment(lex_request: LexRequest[T]) -> Optional[str]:
    """
    Extracts the sentiment from the first interpretation in a LexRequest.

    This function checks if the 'interpretations' attribute exists in the LexRequest
    and retrieves the sentiment from the first interpretation if available.

    Parameters:
    lex_request (LexRequest): The LexRequest object containing interpretations.

    Returns:
    Optional[str]: The sentiment string if available, otherwise None.

    Raises:
    AttributeError: If the 'interpretations' attribute is missing or not a list.
    """
    # Check if 'interpretations' attribute exists and it's a list
    if not hasattr(lex_request, "interpretations"):
        raise AttributeError("Invalid LexRequest: 'interpretations' attribute missing or not a list")

    interpretations = lex_request.interpretations
    if len(interpretations) > 0:
        element = interpretations[0]

        # Check if 'sentimentResponse' attribute exists in 'element'
        if not hasattr(element, "sentimentResponse"):
            return None

        if element.sentimentResponse:
            sentiment = element.sentimentResponse.sentiment
            logger.debug(f"We have a sentiment: {sentiment}")
            return sentiment
    return None


def remove_context(context_list: ActiveContexts, context_name: str) -> ActiveContexts:
    """
    Removes a specific context from the active contexts list.

    Parameters:
    context_list (ActiveContexts): The list of active contexts.
    context_name (str): The name of the context to remove.

    Returns:
    ActiveContexts: The updated list of active contexts without the specified context.
    """
    if not context_list:
        return context_list
    new_context: ActiveContexts = []
    for context in context_list:
        if not context_name == context["name"]:
            new_context.append(context)
    return new_context


def remove_inactive_context(lex_request: LexRequest[T]) -> ActiveContexts:
    """
    Removes inactive contexts from the active contexts list in a LexRequest.

    Parameters:
    lex_request (LexRequest): The LexRequest object containing session state.

    Returns:
    ActiveContexts: The updated list of active contexts with inactive ones removed.
    """
    context_list = lex_request.sessionState.activeContexts
    if not context_list:
        return context_list
    new_context: ActiveContexts = []
    for context in context_list:
        time_to_live = context.get("timeToLive")
        if time_to_live and time_to_live.get("turnsToLive") != 0:
            new_context.append(context)
    return new_context


def close(lex_request: LexRequest[T], messages: LexMessages) -> LexResponse[T]:
    """
    Closes the dialog with the user by setting the intent state to 'Fulfilled'.

    Parameters:
    lex_request (LexRequest): The LexRequest object containing session state.
    messages (LexMessages): The messages to send to the user.

    Returns:
    LexResponse: The response object to be sent back to Lex.
    """
    intent, active_contexts, session_attributes, _ = get_request_components(lex_request)

    lex_request.sessionState.activeContexts = remove_inactive_context(lex_request)
    lex_request.sessionState.intent.state = "Fulfilled"
    session_attributes.previous_dialog_action_type = "Close"
    response = LexResponse(
        sessionState=SessionState(
            activeContexts=active_contexts,
            sessionAttributes=session_attributes,
            intent=intent,
            dialogAction=DialogAction(type="Close"),
        ),
        requestAttributes={},
        messages=messages,
    )

    logger.debug("FF-LAMBDA :: DIALOG-CLOSE")

    return response


def elicit_intent(messages: LexMessages, lex_request: LexRequest[T]) -> LexResponse[T]:
    """
    Elicits the user's intent by sending a message and updating session attributes.

    Parameters:
    messages (LexMessages): The messages to send to the user.
    lex_request (LexRequest): The LexRequest object containing session state.

    Returns:
    LexResponse: The response object to be sent back to Lex.
    """
    intent, active_contexts, session_attributes, _ = get_request_components(lex_request=lex_request)

    active_contexts = remove_inactive_context(lex_request)
    intent.state = "Fulfilled"

    session_attributes.previous_dialog_action_type = "ElicitIntent"
    session_attributes.previous_slot_to_elicit = ""
    session_attributes.options_provided = get_provided_options(messages)

    logger.debug("FF-LAMBDA :: Elicit-Intent")

    return LexResponse(
        sessionState=SessionState(
            activeContexts=active_contexts,
            sessionAttributes=session_attributes,
            intent=intent,
            dialogAction=DialogAction(type="ElicitIntent"),
        ),
        requestAttributes={},
        messages=messages,
    )


def elicit_slot(slot_to_elicit: LexSlot | str, messages: LexMessages, lex_request: LexRequest[T]) -> LexResponse[T]:
    """
    Elicits a specific slot from the user by sending a message and updating session attributes.

    Parameters:
    slot_to_elicit (LexSlot | str): The slot to elicit from the user.
    messages (LexMessages): The messages to send to the user.
    lex_request (LexRequest): The LexRequest object containing session state.

    Returns:
    LexResponse: The response object to be sent back to Lex.
    """
    intent = lex_request.sessionState.intent
    session_attributes = lex_request.sessionState.sessionAttributes

    active_contexts = remove_inactive_context(lex_request)
    intent.state = "InProgress"

    # options_provided are only used by the service lambda to lookup the user's response in the event that they have only
    # provided a single character answer, i.e. A, or 1, etc.
    session_attributes.options_provided = get_provided_options(messages)
    session_attributes.previous_intent = intent.name
    session_attributes.previous_message = json.dumps(messages, cls=PydanticEncoder)
    session_attributes.previous_dialog_action_type = "ElicitSlot"
    slot_name = slot_to_elicit

    if not isinstance(slot_to_elicit, str):
        slot_name = slot_to_elicit.value

    session_attributes.previous_slot_to_elicit = (intent.name.replace("_", "") + "Slot") + "." + str(slot_name).upper()

    if "." in str(slot_name):
        raise Exception("SLOT PARSED INCORRECTLY")

    response = LexResponse(
        sessionState=SessionState(
            activeContexts=active_contexts,
            sessionAttributes=session_attributes,
            intent=intent,
            dialogAction=DialogAction(type="ElicitSlot", slotToElicit=str(slot_name)),
        ),
        requestAttributes={},
        messages=messages,
    )

    return response


def delegate(lex_request: LexRequest[T]) -> LexResponse[T]:
    """
    Delegates the dialog to Lex by updating the session state and returning a response.

    Parameters:
    lex_request (LexRequest): The LexRequest object containing session state.

    Returns:
    LexResponse: The response object to be sent back to Lex.
    """
    logger.debug("IN DELEGATE")

    updated_active_contexts = remove_inactive_context(lex_request)
    lex_request.sessionState.intent.state = "ReadyForFulfillment"
    lex_request.sessionState.sessionAttributes.previous_dialog_action_type = "Delegate"

    updated_session_state = SessionState(
        activeContexts=updated_active_contexts,
        sessionAttributes=lex_request.sessionState.sessionAttributes,
        intent=lex_request.sessionState.intent,
        dialogAction=DialogAction(type="Delegate"),
    )

    logger.debug("FF-LAMBDA :: DELEGATE")

    return LexResponse(sessionState=updated_session_state, requestAttributes={}, messages=[])


def get_provided_options(messages: LexMessages) -> str:
    """
    Extracts the text of the buttons from a list of LexImageResponseCard messages.

    This function loops through a list of messages, checks if each message is an instance of LexImageResponseCard,
    and if so, extracts the text of each button in the imageResponseCard attribute of the message. The function
    then returns a JSON-encoded list of the extracted button texts.

    Parameters:
    messages (LexMessages): The list of messages to process.

    Returns:
    str: A JSON-encoded list of the extracted button texts.
    """
    options = [
        button.text
        for message in messages
        if isinstance(message, LexImageResponseCard)
        for button in message.imageResponseCard.buttons
    ]
    logger.debug(f"FF-LAMBDA :: OPTS-PVD :: {options}")

    return json.dumps(options, cls=PydanticEncoder)


def get_intent(lex_request: LexRequest[T]) -> Intent:
    """
    Retrieves the intent from a LexRequest.

    Parameters:
    lex_request (LexRequest): The LexRequest object containing session state.

    Returns:
    Intent: The intent object from the session state.

    Raises:
    ValueError: If no intent is found in the request.
    """
    session_state = lex_request.sessionState
    if session_state:
        return session_state.intent
    else:
        raise ValueError("No intent found in request")


def get_slot(slot_name: LexSlot | str, intent: Intent, **kwargs: Any):
    """
    Retrieves the value of a slot from an intent.

    Parameters:
    slot_name (LexSlot | str): The name of the slot to retrieve.
    intent (Intent): The intent object containing the slot.
    kwargs (Any): Additional arguments for slot value preference.

    Returns:
    Any: The value of the slot if available, otherwise None.
    """
    try:
        if isinstance(slot_name, str):
            slot = intent.slots.get(slot_name)
        else:
            slot = intent.slots.get(slot_name.value)
        if not slot:
            return None
        return get_slot_value(slot, **kwargs)
    except Exception:
        logger.exception("Failed to get slot")
        return None


def get_composite_slot(
    slot_name: str, intent: Intent, preference: Optional[str] = None
) -> Optional[Dict[str, Union[str, None]]]:
    """
    Retrieves the values from sub-slots of a given slot from an intent.

    Args:
        slot_name (str): Name of the slot to be fetched.
        intent (Intent): Intent object containing the slot.
        preference (Optional[str], default=None): Preference for value type ('interpretedValue' or 'originalValue').
                                                  If no preference is provided and 'interpretedValue' is available, it's used.
                                                  Otherwise, 'originalValue' is used.

    Returns:
        Dict[str, Union[str, None]] or None: Dictionary containing the subslot names and their corresponding values,
                                             or None if the slot or subslots don't exist.

    Raises:
        Exception: Any exception that occurs while fetching the slot.
    """
    subslot_dict: dict[str, Any] = {}

    # Get the slot from the intent
    slot = intent.slots.get(slot_name)
    if not slot:
        return None

    sub_slots = slot.get("subSlots", {})
    if not sub_slots:
        return None

    # Iterate through the subslots
    for key, subslot in sub_slots.items():
        subslot_value = subslot.get("value")

        # If subslot has a value
        if subslot_value:
            interpreted_value = subslot_value.get("interpretedValue")
            original_value = subslot_value.get("originalValue")
            if preference == "interpretedValue":
                subslot_dict[key] = interpreted_value
            elif preference == "originalValue":
                subslot_dict[key] = original_value
            elif interpreted_value:
                subslot_dict[key] = interpreted_value
            else:
                subslot_dict[key] = original_value
        else:
            subslot_dict[key] = None

    return subslot_dict


def get_slot_value(slot: dict[str, Any], **kwargs: Any):
    """
    Retrieves the value from a slot dictionary.

    Parameters:
    slot (dict[str, Any]): The slot dictionary containing the value.
    kwargs (Any): Additional arguments for slot value preference.

    Returns:
    Any: The interpreted or original value of the slot if available, otherwise None.
    """
    slot_value = slot.get("value")
    if slot_value:
        interpreted_value = slot_value.get("interpretedValue")
        original_value = slot_value.get("originalValue")
        if kwargs.get("preference") == "interpretedValue":
            return interpreted_value
        elif kwargs.get("preference") == "originalValue":
            return original_value
        elif interpreted_value:
            return interpreted_value
        else:
            return original_value
    else:
        return None


def set_subslot(
    composite_slot_name: LexSlot,
    subslot_name: str,
    subslot_value: Optional[Any],
    intent: Intent,
) -> Intent:
    """
    Sets a subslot value within a composite slot in the given intent.

    Args:
        composite_slot_name (str): The name of the composite slot within the intent.
        subslot_name (str): The name of the subslot to be set.
        subslot_value (Optional[Any]): The value to be set for the subslot. If None, the subslot is set to None.
        intent (Intent): The intent containing the slots.

    Returns:
        Intent: The updated intent with the modified subslot value.
    """

    # Ensure the composite slot and its subSlots dictionary exist
    if composite_slot_name.value not in intent.slots:
        intent.slots[composite_slot_name.value] = {"subSlots": {}}

    # Determine the value to set for the subslot
    if subslot_value is None:
        intent.slots[composite_slot_name.value]["subSlots"][subslot_name] = None  # type: ignore
    else:
        intent.slots[composite_slot_name.value]["subSlots"][subslot_name] = {  # type: ignore
            "value": {
                "interpretedValue": subslot_value,
                "originalValue": subslot_value,
                "resolvedValues": [subslot_value],
            }
        }

    # Logging for debugging purposes
    logger.debug(f"Setting subslot {subslot_name} in composite slot {composite_slot_name}")
    logger.debug(f"RESULTING INTENT: {json.dumps(intent, cls=PydanticEncoder)}")

    return intent


def set_slot(slot_name: LexSlot, slot_value: Optional[str], intent: Intent) -> Intent:
    """
    Sets a slot value in the given intent.

    Parameters:
    slot_name (LexSlot): The name of the slot to set.
    slot_value (Optional[str]): The value to set for the slot.
    intent (Intent): The intent containing the slots.

    Returns:
    Intent: The updated intent with the modified slot value.
    """
    intent.slots[slot_name.value] = {
        "value": {
            "interpretedValue": slot_value,
            "originalValue": slot_value,
            "resolvedValues": [slot_value],
        }
    }
    return intent


def get_composite_slot_subslot(composite_slot: LexSlot, sub_slot: Any, intent: Intent, **kwargs: Any) -> Optional[str]:
    """
    Retrieves the value of a subslot from a composite slot in an intent.

    Parameters:
    composite_slot (LexSlot): The composite slot containing the subslot.
    sub_slot (Any): The name of the subslot to retrieve.
    intent (Intent): The intent object containing the slots.
    kwargs (Any): Additional arguments for slot value preference.

    Returns:
    Optional[str]: The value of the subslot if available, otherwise None.
    """
    try:
        slot = intent.slots[composite_slot.value]
        if not slot:
            return None
        sub_slot = slot["subSlots"][sub_slot]
        return get_slot_value(sub_slot, **kwargs)
    except Exception:
        return None


def get_active_contexts(lex_request: LexRequest[T]) -> ActiveContexts:
    """
    Retrieves the active contexts from a LexRequest.

    Parameters:
    lex_request (LexRequest): The LexRequest object containing session state.

    Returns:
    ActiveContexts: The list of active contexts.
    """
    try:
        return lex_request.sessionState.activeContexts
    except Exception:
        return []


def get_invocation_label(lex_request: LexRequest[T]) -> Optional[str]:
    """
    Retrieves the invocation label from a LexRequest.

    Parameters:
    lex_request (LexRequest): The LexRequest object containing the invocation label.

    Returns:
    str: The invocation label.
    """
    logger.debug(f"Invocation Label : {lex_request.invocationLabel}")
    return lex_request.invocationLabel


def safe_delete_session_attribute(lex_request: LexRequest[T], attribute: str) -> LexRequest[T]:
    """
    Safely deletes a session attribute from a LexRequest.

    Parameters:
    lex_request (LexRequest): The LexRequest object containing session attributes.
    attribute (str): The name of the attribute to delete.

    Returns:
    LexRequest: The updated LexRequest with the attribute deleted.
    """
    logger.debug("Deleting session attribute {}".format(attribute))
    if lex_request.sessionState.sessionAttributes and getattr(lex_request.sessionState.sessionAttributes, attribute):
        setattr(lex_request.sessionState.sessionAttributes, attribute, None)
    return lex_request


def get_request_components(
    lex_request: LexRequest[T],
) -> tuple[Intent, ActiveContexts, T, Optional[str]]:
    """
    Extracts common components from the intent request.

    Parameters:
    lex_request (LexRequest): The LexRequest object containing session state.

    Returns:
    tuple: A tuple containing the intent, active contexts, session attributes, and invocation label.
    """
    intent = get_intent(lex_request)
    active_contexts = get_active_contexts(lex_request)
    session_attributes = lex_request.sessionState.sessionAttributes
    invocation_label = get_invocation_label(lex_request)
    logger.debug(f"DLG-UTL :: INV-LBL : {invocation_label}")
    return intent, active_contexts, session_attributes, invocation_label


def any_unknown_slot_choices(lex_request: LexRequest[T]) -> bool:
    """
    Checks if there are any unknown slot choices in the LexRequest.

    Parameters:
    lex_request (LexRequest): The LexRequest object containing session state.

    Returns:
    bool: True if there are unknown slot choices, otherwise False.
    """
    intent, _, session_attributes, _ = get_request_components(lex_request)

    if "ElicitSlot" == session_attributes.previous_dialog_action_type:
        logger.debug("ElicitSlot is the previous dialog action")

        intent = get_intent(lex_request)
        previous_slot_to_elicit = session_attributes.previous_slot_to_elicit
        slot_name = previous_slot_to_elicit

        choice = get_slot(slot_name, intent)
        if not choice:
            logger.debug("Unknown slot choice")
            choice = "Unknown"
        logger.debug("Parsed choice: " + str(choice))

        if isinstance(choice, str):
            logger.debug("Slot recognized correctly, letting Lex continue with the conversation")
            lex_request.sessionState.sessionAttributes.error_count = 0
            return False

        return True

    lex_request.sessionState.sessionAttributes.error_count = 0
    return False


def handle_any_unknown_slot_choice(lex_request: LexRequest[T]) -> LexResponse[T]:
    """
    Handles any unknown slot choice in the LexRequest.

    Parameters:
    lex_request (LexRequest): The LexRequest object containing session state.

    Returns:
    LexResponse: The response object to be sent back to Lex.
    """
    intent, _, session_attributes, _ = get_request_components(lex_request)

    logger.debug(f"FF-LAMBDA :: Handle_Any_Unknown_Choice :: {session_attributes}")
    intent = get_intent(lex_request)
    previous_slot_to_elicit = session_attributes.previous_slot_to_elicit

    logger.debug("Unparsed slot name: " + previous_slot_to_elicit)
    slot_name = previous_slot_to_elicit

    logger.debug("IDENTIFIER FOR BAD SLOT {}".format(slot_name))

    choice = get_slot(slot_name, intent, preference="interpretedValue")
    logger.debug("BAD CHOICE IS {}".format(choice))
    if not isinstance(choice, str):
        logger.debug("Bad slot choice")
        return unknown_choice_handler(lex_request=lex_request, choice=choice)
    return delegate(lex_request=lex_request)


def unknown_choice_handler(
    lex_request: LexRequest[T],
    choice: str | LexSlot | None,
    handle_unknown: Optional[bool] = True,
    next_intent: Optional[str] = None,
    next_invo_label: Optional[str] = "",
) -> LexResponse[T]:
    """
    Handles an unknown choice in the LexRequest.

    Parameters:
    lex_request (LexRequest): The LexRequest object containing session state.
    choice (str | LexSlot | None): The choice to handle.
    handle_unknown (Optional[bool]): Whether to handle unknown choices.
    next_intent (Optional[str]): The next intent to transition to.
    next_invo_label (Optional[str]): The next invocation label.

    Returns:
    LexResponse: The response object to be sent back to Lex.
    """
    return delegate(lex_request=lex_request)


# def string_to_lex_slot(value: str) -> LexSlot:
#     """
#     Converts a string to a LexSlot enum member.

#     Parameters:
#     value (str): The string representation of the LexSlot.

#     Returns:
#     LexSlot: The corresponding LexSlot enum member.

#     Raises:
#     ValueError: If no enum class is found for the given string.
#     """
#     class_name, member_name = value.split(".")
#     enum_class = LexSlot_Classes.get(class_name)

#     if not enum_class:
#         raise ValueError(f"No enum class named '{class_name}' found.")

#     member = enum_class[member_name]
#     return member


def reprompt_slot(lex_request: LexRequest[T]) -> LexResponse[T]:
    """
    Reprompts the user for a slot value by sending a message.

    Parameters:
    lex_request (LexRequest): The LexRequest object containing session state.

    Returns:
    LexResponse: The response object to be sent back to Lex.
    """
    logger.debug("FFL-DLG :: REPROMPT-SLOT :: START")

    session_attributes = lex_request.sessionState.sessionAttributes
    previous_slot_to_elicit = session_attributes.previous_slot_to_elicit
    if not previous_slot_to_elicit:
        return delegate(lex_request)
    logger.debug("Unparsed slot name: " + previous_slot_to_elicit)
    slot_name = previous_slot_to_elicit
    logger.debug("IDENTIFIER 3 {}".format(slot_name))
    messages = []
    logger.debug("Reprompt-Messages :: {}".format(messages))

    return elicit_slot(slot_to_elicit=slot_name, messages=messages, lex_request=lex_request)



def load_messages(messages: str) -> LexMessages:
    """
    Loads messages from a JSON string into LexMessages objects.

    Parameters:
    messages (str): The JSON string containing messages.

    Returns:
    LexMessages: The list of LexMessages objects.
    """
    res: LexMessages = []
    temp: list[Any] = json.loads(messages)

    for msg in temp:
        content_type: str = msg.get("contentType", "_")
        match content_type:  # type: ignore
            case "ImageResponseCard":
                res.append(LexImageResponseCard.model_validate_json(json.dumps(msg)))
            case "CustomPayload":
                res.append(LexCustomPayload.model_validate_json(json.dumps(msg)))
            case "PlainText":
                res.append(LexPlainText.model_validate_json(json.dumps(msg)))
            case _:
                res.append(msg)

    logger.debug(f"PARSED-PREV-MSG :: {res}")
    return res


def parse_req_sess_attrs(lex_payload: LexRequest[T]) -> LexRequest[T]:
    logger.debug(f"LEX-PAYLOAD : {lex_payload.model_dump_json(exclude_none=True)}")
    # parsing core_data from session-state from 2nd messages

    channel_string = ""

    if lex_payload.requestAttributes:
        logger.debug("FFL :: CREATING NEW SESS ATTRS")
        if "channel" in lex_payload.requestAttributes:
            channel_string = lex_payload.requestAttributes["channel"]
            logger.info(f"User passed in channel: {channel_string}")
        else:
            channel_string = "lex"

        # For 1st mesage, request attribute is set to session attribute. IGNORED from 2nd message
        for key, value in lex_payload.requestAttributes.items():
            # For every session attribute, if it's 'true', or 'True', or 'false', or 'False', set it as a boolean
            # Pydantic should do this but appears to not be.
            if value in ["true", "True", "false", "False"]:
                setattr(
                    lex_payload.sessionState.sessionAttributes,
                    key,
                    value == "true" or value == "True",
                )
            else:
                setattr(lex_payload.sessionState.sessionAttributes, key, value)

    return lex_payload


def parse_lex_request(
    data: dict[str, Any],
    sessionAttributes: T,
) -> LexRequest[T]:
    """
    Use this to parse a Lambda event into a LexRequest object.

    Parameters:
    data (dict[str, Any]): The Lambda event data.
    sessionAttributes (Optional[T]): The session attributes to use.

    Returns:
    LexRequest[T]: The parsed LexRequest object.
    """
    # Create a copy of the data to modify
    data_copy = data.copy()
    
    # If there are session attributes in the event, convert them to the proper model
    if data_copy.get("sessionState", {}).get("sessionAttributes"):
        event_attrs = data_copy["sessionState"]["sessionAttributes"]
        # Create a new instance of the session attributes model with the event data
        model_attrs = type(sessionAttributes)(**event_attrs)
        data_copy["sessionState"]["sessionAttributes"] = model_attrs
    else:
        # If no session attributes in event, use the provided ones
        if "sessionState" not in data_copy:
            data_copy["sessionState"] = {}
        data_copy["sessionState"]["sessionAttributes"] = sessionAttributes

    lex_request: LexRequest[T] = LexRequest(**data_copy)
    lex_request.sessionState.activeContexts = remove_inactive_context(lex_request)  # Remove inactive contexts
    lex_request = parse_req_sess_attrs(lex_request)  # Parse Session Attributes
    return lex_request


def transition_to_intent(
    intent_name: str,
    lex_request: LexRequest[T],
    messages: LexMessages,
    invocation_label: Optional[str] = None,
    clear_slots: bool = True,
) -> LexResponse[T]:
    if clear_slots:
        _clear_slots(intent_name=intent_name, lex_request=lex_request, invocation_label=invocation_label)

    # logger.debug(f"TRANSITION :: SESS-STATE : {lex_request.sessionState.sessionAttributes}")
    # Call the intent handler and get its response
    response = call_handler_for_file(intent_name=intent_name, lex_request=lex_request)
    
    # Prepend the messages passed to transition_to_intent to the response messages
    if messages:
        response.messages = list(messages) + list(response.messages)

    return response


def transition_to_callback(
    intent_name: str, lex_request: LexRequest[T], messages: LexMessages, clear_slots: bool = True
) -> LexResponse[T]:
    if clear_slots:
        _clear_slots(intent_name=intent_name, lex_request=lex_request)
    # If requestAttributes is None, create a new dictionary
    if lex_request.requestAttributes is None:
        lex_request.requestAttributes = {}
    lex_request.requestAttributes["callback"] = intent_name

    return LexResponse(
        sessionState=lex_request.sessionState, messages=messages, requestAttributes=lex_request.requestAttributes
    )


def _clear_slots(intent_name: str, lex_request: LexRequest[T], invocation_label: Optional[str] = None):
    lex_request.sessionState.intent.slots = {}
    lex_request.sessionState.intent.name = intent_name

    if invocation_label is not None:
        lex_request.invocationLabel = invocation_label
