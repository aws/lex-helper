# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from pydantic import BaseModel

from lex_helper import Intent, LexPlainText, LexRequest, LexResponse, dialog

from ..session_attributes import CustomSessionAttributes


class Question(BaseModel):
    text: str  # The question to ask
    slot: str  # The slot to elicit


def question_not_answered(slot_name: str, intent: Intent) -> bool:
    return not dialog.get_slot(slot_name=slot_name, intent=intent)


def handler(lex_request: LexRequest[CustomSessionAttributes]) -> LexResponse[CustomSessionAttributes]:
    slots_to_answer = [
        Question(text="In what city do you need to rent a car?", slot="PickUpCity"),
        Question(text="When do you need to pick up the car?", slot="PickUpDate"),
        Question(text="How old are you?", slot="DriverAge"),
        Question(text="What type of car would you like to rent?", slot="CarType"),
    ]
    for question in slots_to_answer:
        if question_not_answered(slot_name=question.slot, intent=lex_request.sessionState.intent):
            return dialog.elicit_slot(
                slot_to_elicit=question.slot,
                messages=[LexPlainText(content=question.text)],
                lex_request=lex_request,
            )

    return dialog.elicit_slot(
        slot_to_elicit="PickUpCity",
        messages=[
            LexPlainText(
                content="Okay, I have you down for a {CarType} rental in {PickUpCity} from {PickUpDate} to {ReturnDate}.  Should I book the reservation?"
            )
        ],
        lex_request=lex_request,
    )
