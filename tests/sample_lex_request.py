# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import TypeVar

from lex_helper import (
    Bot,
    Intent,
    Interpretation,
    LexRequest,
    SessionAttributes,
    SessionState,
    Transcription,
)

T = TypeVar("T", bound=SessionAttributes)


def get_sample_request(intent_name: str) -> LexRequest[SessionAttributes]:
    intent = Intent(name=intent_name)
    bot = {
        "name": "LexBot",
        "version": "DRAFT",
        "localeId": "en_US",
        "id": "ABCDEFGHIJ",
        "aliasId": "KLMNOPQRST",
        "aliasName": "TestBotAlias",
    }

    transcription = {
        "transcription": intent_name,
        "transcriptionConfidence": 1,
        "resolvedContext": {"intent": intent_name},
        "resolvedSlots": {},
    }

    return LexRequest(
        sessionId="1234567890",
        sessionState=SessionState(intent=intent, sessionAttributes=SessionAttributes()),
        inputTranscript="hello world",
        interpretations=[Interpretation(intent=intent)],
        bot=Bot(**bot),
        responseContentType="text/plain; charset=utf-8",
        messageVersion="2.0",
        invocationSource="UnitTest",
        transcriptions=[Transcription(**transcription)],  # type: ignore
        inputMode="Text",
    )
