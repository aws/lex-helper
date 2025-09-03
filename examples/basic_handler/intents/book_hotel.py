# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from lex_helper import LexPlainText, LexRequest, LexResponse, dialog

from ..session_attributes import CustomSessionAttributes


def handler(lex_request: LexRequest[CustomSessionAttributes]) -> LexResponse[CustomSessionAttributes]:
    weather = lex_request.sessionState.sessionAttributes.current_weather
    messages = [
        LexPlainText(content=f"Hello, it sure is {weather} today!  Good luck booking a hotel!"),
    ]

    return dialog.close(
        messages=messages,
        lex_request=lex_request,
    )
