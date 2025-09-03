import os
from typing import Any

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from fulfillment_function.lambda_function import lambda_handler

bot_export_dir = "lex-export/LexBot/BotLocales/en_US/Intents"
lambdas_dir = "lambdas/fulfillment_function/src/fulfillment_function/intents"
bot_folders = [f for f in os.listdir(bot_export_dir) if os.path.isdir(os.path.join(bot_export_dir, f))]
lambda_files = [
    os.path.splitext(f)[0]
    for f in os.listdir(lambdas_dir)
    if os.path.isfile(os.path.join(lambdas_dir, f)) and f.endswith(".py")
]


def camel_to_snake_case(name: str):
    return "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip("_")


# Parametrize the bot_folders.
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
        "inputTranscript": "peanut",
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
            {
                "intent": {
                    "name": "Special_Meal",
                    "slots": {"Flight_Booked": None, "More_Info": None},
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
                "nluConfidence": 0.79,
            },
            {
                "intent": {
                    "name": "Escalate_To_Agent",
                    "slots": {},
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
                "nluConfidence": 0.79,
            },
            {
                "intent": {
                    "name": "Pets",
                    "slots": {
                        "shipping": None,
                        "Carry_on_pet_options": None,
                        "Pet_Options": None,
                    },
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
                "nluConfidence": 0.76,
            },
            {
                "intent": {
                    "name": "Baggage_Bring_Item",
                    "slots": {},
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
                "nluConfidence": 0.73,
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
                "transcription": "peanut",
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
