# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from .lex_emulator import resolve_slot


def test_basic_slot_resolution():
    assert resolve_slot(
        intent_name="TrackBaggage",
        slot_to_elicit="ReservationNumber",
        slots={},
        text="123",
    ) == {
        "value": {
            "originalValue": "123",
            "interpretedValue": "123",
            "resolvedValues": ["123"],
        }
    }
