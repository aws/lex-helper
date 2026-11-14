# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest

from lex_helper.core.dialog import any_unknown_slot_choices, elicit_slot, reprompt_slot
from lex_helper.core.types import Intent, LexPlainText, LexRequest, SessionAttributes, SessionState


@pytest.mark.parametrize("slot_name", ["destination", "Destination"])
@pytest.mark.parametrize("recognized", [False, True])
def test_slot_elicitation_metadata_supports_next_turn(slot_name, recognized):
    request = LexRequest(
        sessionState=SessionState(
            intent=Intent(name="BookTrip"), sessionAttributes=SessionAttributes(previous_dialog_action_type="ElicitIntent")
        )
    )
    response = elicit_slot(slot_name, [LexPlainText(content="Where?")], request)
    attributes = response.sessionState.sessionAttributes
    assert attributes.previous_dialog_action_type == "ElicitSlot"
    assert attributes.previous_slot_to_elicit == slot_name

    request.sessionState.intent.slots[slot_name] = {"value": {"interpretedValue": "Paris"}} if recognized else None
    assert any_unknown_slot_choices(request) is not recognized
    retry = reprompt_slot(request)
    assert retry.sessionState.dialogAction.slotToElicit == slot_name
