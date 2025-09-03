# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import json
import os

import pytest

# Get the directory of this test file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate to the sample_airline_bot root directory
sample_airline_bot_root = os.path.dirname(current_dir)
BASE_DIR = os.path.join(sample_airline_bot_root, "lex-export/LexBot/BotLocales/en_US/Intents")


def collect_intents() -> list[str]:
    intents: list[str] = []
    for root, _, files in os.walk(BASE_DIR):
        if "FallbackIntent" in root:  # Skip if "FallbackIntent" is in the path
            continue
        if "Intent.json" in files:
            intents.append(os.path.join(root, "Intent.json"))
    return intents


@pytest.mark.parametrize("intent", collect_intents())
def test_intent_has_sample_utterances(intent: str):
    with open(intent) as file:
        data = json.load(file)
        assert "sampleUtterances" in data, f"'sampleUtterances' not found in {intent}"


@pytest.mark.parametrize("intent", collect_intents())
def test_sample_utterances_not_null(intent: str):
    # Skip if intent contains "Flight_Change_Reshop" in the path
    with open(intent) as file:
        data = json.load(file)
        assert data["sampleUtterances"] is not None, f"'sampleUtterances' is None in {intent}"


@pytest.mark.parametrize("intent", collect_intents())
def test_sample_utterances_has_at_least_3_items(intent: str):
    with open(intent) as file:
        data = json.load(file)
        assert len(data["sampleUtterances"]) >= 3, f"'sampleUtterances' has less than 3 items in {intent}"
