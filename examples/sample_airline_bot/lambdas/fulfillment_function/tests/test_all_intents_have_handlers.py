# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import os
from typing import Any

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from fulfillment_function.lambda_function import lambda_handler

# Get the directory of this test file and build paths relative to the sample_airline_bot directory
test_dir = os.path.dirname(os.path.abspath(__file__))
sample_bot_dir = os.path.join(test_dir, "..", "..", "..")
bot_export_dir = os.path.join(sample_bot_dir, "lex-export", "LexBot", "BotLocales", "en_US", "Intents")
lambdas_dir = os.path.join(sample_bot_dir, "lambdas", "fulfillment_function", "src", "fulfillment_function", "intents")

# Check if directories exist before trying to list them
bot_folders = []
lambda_files = []

if os.path.exists(bot_export_dir):
    bot_folders = [f for f in os.listdir(bot_export_dir) if os.path.isdir(os.path.join(bot_export_dir, f))]

if os.path.exists(lambdas_dir):
    lambda_files = [
        os.path.splitext(f)[0]
        for f in os.listdir(lambdas_dir)
        if os.path.isfile(os.path.join(lambdas_dir, f)) and f.endswith(".py")
    ]


def camel_to_snake_case(name: str):
    return "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip("_")


# Skip tests if bot export directory doesn't exist
@pytest.mark.skipif(not os.path.exists(bot_export_dir), reason="Bot export directory not found")
@pytest.mark.parametrize(
    "bot_folder",
    [f for f in bot_folders if f != "FallbackIntent" and f != "Debug"],
)
def test_bot_export_sample(bot_folder: str):
    assert camel_to_snake_case(bot_folder) in lambda_files, (
        f"No matching Python file found for {camel_to_snake_case(bot_folder)}"
    )

    sample_event: dict[str, Any] = {
        "sessionId": "731776342393712",
        "requestAttributes": {},
        "inputTranscript": "book a flight",
        "interpretations": [
            {
                "intent": {
                    "name": bot_folder,
                    "slots": {"Flight_Booked": None, "More_info": None},
                    "state": "InProgress",
                    "confirmationState": "None",
                },
                "sentimentResponse": {
                    "sentiment": "NEUTRAL",
                    "sentimentScore": {
                        "neutral": 0.6004214882850647,
                        "mixed": 0.0010255359811708331,
                        "negative": 0.37515789270401,
                        "positive": 0.02339508943259716,
                    },
                },
                "nluConfidence": 0.95,
            },
        ],
        "bot": {
            "name": "LexBot",
            "version": "DRAFT",
            "localeId": "en_US",
            "id": "ABCDEFGHIJ",
            "aliasId": "KLMNOPQRST",
            "aliasName": "TestBotAlias",
        },
        "responseContentType": "text/plain; charset=utf-8",
        "proposedNextState": {
            "prompt": {"attempt": "Initial"},
            "intent": {
                "name": bot_folder,
                "slots": {"Flight_Booked": None, "More_info": None},
                "state": "InProgress",
                "confirmationState": "None",
            },
            "dialogAction": {"type": "ElicitSlot", "slotToElicit": "Flight_Booked"},
        },
        "sessionState": {
            "sessionAttributes": {},
            "intent": {
                "name": bot_folder,
                "slots": {"Flight_Booked": None, "More_info": None},
                "state": "InProgress",
                "confirmationState": "None",
            },
            "originatingRequestId": "b3b66b7a-33dd-4fab-85a1-8d0c1b790eb8",
        },
        "messageVersion": "1.0",
        "invocationSource": "DialogCodeHook",
        "invocationLabel": "test",
        "transcriptions": [
            {
                "resolvedContext": {"intent": bot_folder},
                "transcription": "book a flight",
                "resolvedSlots": {},
                "transcriptionConfidence": 1.0,
            }
        ],
        "inputMode": "Text",
    }

    # Fake Context
    context: LambdaContext = LambdaContext()
    context._function_name = bot_folder  # type: ignore
    context._memory_limit_in_mb = 128  # type: ignore
    context._invoked_function_arn = f"arn:aws:lambda:us-east-1:123456789012:function:{bot_folder}"  # type: ignore
    context._aws_request_id = "12345678-1234-1234-1234-123456789012"  # type: ignore
    response: Any = lambda_handler(sample_event, context)
    assert response["sessionState"]["intent"]["name"] != "FallbackIntent"  # type: ignore
