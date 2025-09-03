# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import json
import os
from typing import Any


def test_no_unused_slot_types():
    # We should NOT have unused slot types.  If we do, we should remove them.

    all_slot_types = get_all_slot_types()
    all_slots = get_all_slots()

    # For each slot type, check to see if it's name is used in any slots "slotTypeName" field
    list_of_unused_slot_types = []
    for slot_type_name, _ in all_slot_types.items():
        found = False
        for _, slot_data in all_slots.items():
            if slot_type_name == slot_data["slotTypeName"]:
                found = True
                break
        if not found:
            list_of_unused_slot_types.append(slot_type_name)

    # Now out of those unused slot types, lets check each all_slot_types to see if it's used within another slot type.
    # If it is, we should remove it from the list of unused slot types.
    list_of_unused_slot_types_and_not_composite: list[Any] = []
    for slot_type_name in list_of_unused_slot_types:  # type: ignore
        found = False
        slot_type_identifier = all_slot_types[slot_type_name]["identifier"]
        for _, slot_data in all_slot_types.items():
            if found:
                break
            if "compositeSlotTypeSetting" in slot_data:
                for sub_slot in slot_data["compositeSlotTypeSetting"]["subSlots"]:
                    if sub_slot["slotTypeId"] == slot_type_identifier:
                        found = True
                        break
        if not found:
            list_of_unused_slot_types_and_not_composite.append(slot_type_name)

    assert len(list_of_unused_slot_types_and_not_composite) == 0, f"Unused slot types: {list_of_unused_slot_types}"


def get_all_slots() -> dict[str, Any]:
    # Get the directory of this test file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate to the sample_airline_bot root directory
    sample_airline_bot_root = os.path.dirname(current_dir)
    bot_export_folder = os.path.join(sample_airline_bot_root, "lex-export/LexBot/BotLocales/en_US")
    all_slots = {}
    for root, dirs, _ in os.walk(bot_export_folder + "/Intents"):
        for intent_directory in dirs:
            # If intent_directory contains a folder named "Slots", iterate through every subfolder within it
            if os.path.exists(os.path.join(root, intent_directory, "Slots")):
                for slot_directory in os.listdir(os.path.join(root, intent_directory, "Slots")):
                    with open(os.path.join(root, intent_directory, "Slots", slot_directory, "Slot.json")) as f:
                        slot_data = json.load(f)
                        all_slots[intent_directory + "-" + slot_data["name"]] = slot_data

    return all_slots  # type: ignore


def get_all_slot_types() -> dict[str, Any]:
    # Get the directory of this test file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate to the sample_airline_bot root directory
    sample_airline_bot_root = os.path.dirname(current_dir)
    bot_export_folder = os.path.join(sample_airline_bot_root, "lex-export/LexBot/BotLocales/en_US")
    all_slot_types = {}
    for root, dirs, _ in os.walk(bot_export_folder + "/SlotTypes"):
        for dir in dirs:
            with open(os.path.join(root, dir, "SlotType.json")) as f:
                slot_type_data = json.load(f)
                all_slot_types[slot_type_data["name"]] = slot_type_data

    return all_slot_types  # type: ignore
