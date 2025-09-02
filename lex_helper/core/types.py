# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence
from enum import Enum
from typing import (
    Annotated,
    Any,
    Generic,
    Literal,
    TypeVar,
    cast,
)

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from lex_helper.formatters.buttons import Button


class ImageResponseCard(BaseModel):
    title: str
    subtitle: str = " "
    imageUrl: str | None = None  # noqa: N815
    buttons: list[Button] = []


class LexPlainText(BaseModel):
    content: str | None = ""
    contentType: Literal["PlainText"] = "PlainText"  # noqa: N815


class PlainText(BaseModel):
    content: str | None = ""
    contentType: Literal["PlainText"] = "PlainText"
    title: str | None = ""
    subtitle: str | None = ""


class LexCustomPayload(BaseModel):
    content: str | dict[str, Any]
    contentType: Literal["CustomPayload"] = "CustomPayload"


class LexImageResponseCard(BaseModel):
    imageResponseCard: ImageResponseCard
    contentType: Literal["ImageResponseCard"] = "ImageResponseCard"


LexBaseResponse = Annotated[
    LexPlainText | LexImageResponseCard | LexCustomPayload,
    Field(discriminator="contentType"),
]


# Web Image Carousel
class CustomPayloadImageCarousel(BaseModel):
    customContentType: Literal["CustomPayloadImageCarousel"] = "CustomPayloadImageCarousel"
    imageList: list[str] = []


LexMessages = Sequence[LexBaseResponse | PlainText]


def parse_lex_response(data: dict[str, Any]) -> LexBaseResponse:
    content_type = data.get("contentType")

    if content_type == "PlainText":
        return LexPlainText(**data)
    elif content_type == "ImageResponseCard":
        return LexImageResponseCard(**data)
    else:
        raise ValidationError("Invalid contentType", LexBaseResponse)


# Lex Payload, this is what is sent to the actual fulfillment lambda
class SentimentScore(BaseModel):
    neutral: float
    mixed: float
    negative: float
    positive: float


class SentimentResponse(BaseModel):
    sentiment: str
    sentimentScore: SentimentScore


class Intent(BaseModel):
    name: str
    slots: dict[str, Any | None] = {}
    state: str | None = None
    confirmationState: str | None = None


class Interpretation(BaseModel):
    intent: Intent
    sentimentResponse: SentimentResponse | None = None
    nluConfidence: float | None = None


class Bot(BaseModel):
    name: str = "Unknown"
    version: str = "1.0"
    localeId: str = "en_US"
    id: str = "Unknown"
    aliasId: str = "Unknown"
    aliasName: str = "Unknown"


class Prompt(BaseModel):
    attempt: str


class DialogAction(BaseModel):
    type: str | None = None
    slotToElicit: str | None = None


class ProposedNextState(BaseModel):
    prompt: Prompt
    intent: Intent
    dialogAction: DialogAction


ActiveContexts = list[dict[str, Any]] | None


APIFailMethod = Literal[
    "cah",
    "pd",
    "case_status",
    "og",
    "rcl",
    "rcl-rvl",
    "profile_lite",
    "track_bag",
    "ecredit_redemption",
    "ecredit",
]


class SessionAttributes(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    callback_event: str | None = None  # Used for saving the original event to replay
    callback_handler: str | None = None  # Used for saving the original event to replay
    error_count: int = 0  # How many times have we errored?

    # Authentication Related
    customer_type: str | None = None
    imei: str | None = None
    auth_status: str | None = None
    consumer_id: str | None = None
    auth_denied: bool = False  # Was the user denied authentication?
    user_authenticated: bool = False  # User is authenticated?

    error_number: str | None = None  # What is the error number?
    previous_dialog_action_type: str | None = None  # What was the last dialog action type?
    previous_slot_to_elicit: str | None = None  # What was the last slot to elicit?
    previous_intent: str | None = None  # To identify intent switch
    previous_message: str | None = None  # Needed for reprompt
    options_provided: str | None = None  # Options provided for "case options"

    language: str | None = None  # What language is the user using?
    next_routing_dialog: str | None = None  # What is the next routing dialog action type?
    common_greeting_count: int = 0  # How many times have we greeted the user?
    slot_error_count: int = 0  # How many times have we errored on a slot?

    # Agent Escalation
    escalate_to_agent_non_english: bool = True
    alternate_language: bool | None = (
        True  # to determine if the user wants to continue the conversation in english instead of the original non-english language
    )

    # Routing
    current_form: Any | None = None
    lex_intent: str | None = None
    routing_intent: str | None = None
    routing_dialog: str | None = None
    is_health_check: bool | None = False

    # unknown_choice
    is_lex_retry: bool | None = False
    unknown_routing_slot: str | None = None
    unknown_routing_intent: str | None = None
    is_reprompt: bool | None = False
    is_auth_request: bool | None = None
    is_unknown_choice: bool | None = None

    channel: str = "lex"

    user_text: str | None = ""

    def to_cmd_response(self):
        response = ""
        self_dict = self.model_dump()
        for key in self_dict:
            if self_dict[key] and key not in ["dispositions"]:
                response = response + f"{key} : {str(self_dict[key])}" + " \n"
        return response


T = TypeVar("T", bound=SessionAttributes)


class SessionState(BaseModel, Generic[T]):
    activeContexts: ActiveContexts = None
    sessionAttributes: T = cast(T, None)
    intent: Intent
    originatingRequestId: str | None = None
    dialogAction: DialogAction | None = None


class ResolvedContext(BaseModel):
    intent: str


class Transcription(BaseModel):
    resolvedContext: ResolvedContext
    transcription: str
    resolvedSlots: dict[str, Any]
    transcriptionConfidence: float


class LexRequest(BaseModel, Generic[T]):
    sessionId: str = "DEFAULT_SESSION_ID"
    inputTranscript: str = "DEFAULT_INPUT_TRANSCRIPT"
    interpretations: list[Interpretation] = []
    bot: Bot = Bot()
    responseContentType: str = "DEFAULT_RESPONSE_CONTENT_TYPE"
    proposedNextState: ProposedNextState | None = None
    sessionState: SessionState[T] = SessionState(intent=Intent(name="FallbackIntent"))
    messageVersion: str = "DEFAULT_MESSAGE_VERSION"
    invocationSource: str = "DEFAULT_INVOCATION_SOURCE"
    invocationLabel: str | None = None
    transcriptions: list[Transcription] = []
    inputMode: str = "DEFAULT_INPUT_MODE"
    requestAttributes: dict[str, Any] | None = None


class LexResponse(BaseModel, Generic[T]):
    sessionState: SessionState[T]
    messages: LexMessages
    requestAttributes: dict[str, Any]


class EmptySlot(Enum):
    pass


LexSlot = EmptySlot

LexSlot_Classes = {
    "EmptySlot": EmptySlot,
}
