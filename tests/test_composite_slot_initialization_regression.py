# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest

from lex_helper import Intent, LexSlot
from lex_helper.core.dialog import set_subslot


class AddressSlot(LexSlot):
    ADDRESS = "address"


@pytest.mark.parametrize(
    "slots",
    [
        {},
        {"address": None},
        {"address": {}},
        {"address": {"shape": "Composite"}},
        {"address": {"shape": "Composite", "subSlots": None}},
    ],
)
@pytest.mark.parametrize("value", [None, "Paris"])
def test_set_subslot_initializes_empty_slot_maps(slots, value):
    intent = Intent(name="Test", slots=slots)
    result = set_subslot(AddressSlot.ADDRESS, "city", value, intent)

    assert result is intent
    subslot = result.slots["address"]["subSlots"]["city"]
    if value is None:
        assert subslot is None
    else:
        assert subslot["value"]["interpretedValue"] == value
    if slots.get("address") and "shape" in slots["address"]:
        assert result.slots["address"]["shape"] == "Composite"
