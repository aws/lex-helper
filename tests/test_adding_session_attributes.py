# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from pydantic import ConfigDict, Field

from lex_helper import LexRequest, SessionAttributes, dialog


class CustomSessionAttributes(SessionAttributes):
    """
    Custom session attributes with additional fields.
    
    Attributes:
        custom_field_1 (str): A custom string field with a default value.
        custom_field_2 (int): A custom integer field with a default value.
        current_weather (str): The weather in the city the user is currently in.
    """
    model_config = ConfigDict(extra="allow")
    custom_field_1: str = Field(default="default_value", description="A custom string field with a default value.")
    custom_field_2: int = Field(default=0, description="A custom integer field with a default value.")
    current_weather: str = Field(default="sunny", description="The weather in the city the user is currently in.")


def test_adding_session_attributes():
    data: Any = {}
    data["sessionState"] = {"intent": {"name": "BookHotel", "slots": {}}}

    lex_request: LexRequest[CustomSessionAttributes] = dialog.parse_lex_request(
        data, CustomSessionAttributes()
    )
    assert lex_request.sessionState.sessionAttributes.lex_intent is None
    assert lex_request.sessionState.sessionAttributes.channel == "lex"
    lex_request.sessionState.sessionAttributes.lex_intent = (
        "FallbackIntent"  # Make sure parent is still here
    )
    assert lex_request.sessionState.sessionAttributes.custom_field_1 == "default_value"
    lex_request.sessionState.sessionAttributes.custom_field_1 = "test"
    session_attributes = dialog.elicit_slot(
        slot_to_elicit="custom_field_1",
        messages=[],
        lex_request=lex_request,
    ).sessionState.sessionAttributes

    # Assertions

    assert session_attributes.custom_field_1 == "test"
    assert session_attributes.custom_field_2 == 0
