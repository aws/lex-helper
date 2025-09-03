from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

from lex_helper import LexRequest, LexResponse


class DialogRoutingAction(BaseModel):
    """A class to define a given routing action for an intent handler.
    The variables dictionary is for Global Variables set in the intent handler.
    '[Tt]rue' or '[Ff]alse' values are converted to bools, so a True/False value can be provided in the test.

    Args:
        invocation_label (str): The Invocation Label to where we want to route
        slot_key (str): The slot we're expecting to find the output from the bot
        slot_value (str): The value from the slot we're expecting
        variables (dict[str, Any]): A dictionary of global variables to test against. Default is empty.  See note in summary
    """

    invocation_label: str
    slot_key: str
    slot_value: str
    subslot_key: str | None = None
    subslot_value: str | None = None
    variables: dict[str, Any] = {}
    routing_handler: Callable[[LexRequest], LexResponse] | None = None


def run_test(
    dialog_routing_actions: list[DialogRoutingAction],
    start_invocation_label: str,
    request: LexRequest,
    handler: Callable[[LexRequest], LexResponse],  # type: ignore
    success_dialog_action_type: str = "ElicitSlot",
    success_intent_state: str = "InProgress",
):
    """Set up a Unit Test with a given set of Dialog routing actions and
    a given intent handler function

    Args:
        dialog_routing_actions (list[DialogRoutingAction]): Actions for routing the dialog and expected outcomes
        start_invocation_label (str): The Invocation Label for the part of the intent where you want to start
        request (LexRequest): A lex request to pass to the handler
        handler (Callable[[Any], LexResponse]): The handler defined in the intent.py script
        terminal_invocation_label (str|None): If the intent routes to this label, it will fail the test
    """
    # given this invocation label, examine actual response state
    # initial utterance from customer
    request.invocationLabel = start_invocation_label

    # process initial utterance
    response = handler(request)

    # followup utterance from customer
    for action in dialog_routing_actions:
        # response should be "InProgress"
        assert response.sessionState.intent.state == success_intent_state
        assert response.sessionState.dialogAction is not None
        assert response.sessionState.dialogAction.type == success_dialog_action_type

        # expected slot
        slot = action.slot_key

        # compare expected slot to elicit-slot in response
        assert response.sessionState.dialogAction is not None

        # supply a customer response, so the intent can route to the next prompt
        request.sessionState.intent.slots[slot] = {"value": {"interpretedValue": action.slot_value}}
        if action.subslot_key and action.subslot_value:
            request.sessionState.intent.slots[slot] = {
                "value": {"interpretedValue": action.slot_value},
                "subSlots": {action.subslot_key: {"value": {"interpretedValue": action.subslot_value}}},
            }

        # simulates user input -> next invocation label from Lex
        request.invocationLabel = action.invocation_label

        # execute next route in dialog
        if action.routing_handler is not None:
            response = action.routing_handler(lex_request=request)  # type: ignore
        else:
            response = handler(request)

        assert response.messages is not None

        # check vars if provided
        if len(action.variables.items()) > 0:
            session_vars = response.sessionState.sessionAttributes  # type: ignore
            for key, val in action.variables.items():
                session_value = getattr(session_vars, key)
                assert session_value == val
