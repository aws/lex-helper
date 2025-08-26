# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from enum import Enum
from typing import (
    Annotated,
    Any,
    Generic,
    Literal,
    Optional,
    Sequence,
    TypeVar,
    Union,
    cast,
)

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from typing_extensions import Annotated

from lex_helper.formatters.buttons import Button


class ImageResponseCard(BaseModel):
    title: str
    subtitle: str = " "
    imageUrl: Optional[str] = None
    buttons: list[Button] = []


class LexPlainText(BaseModel):
    content: Optional[str] = ""
    contentType: Literal["PlainText"] = "PlainText"


class PlainText(BaseModel):
    content: Optional[str] = ""
    contentType: Literal["PlainText"] = "PlainText"
    title: Optional[str] = ""
    subtitle: Optional[str] = ""


class LexCustomPayload(BaseModel):
    content: str
    contentType: Literal["CustomPayload"] = "CustomPayload"


class LexImageResponseCard(BaseModel):
    imageResponseCard: ImageResponseCard
    contentType: Literal["ImageResponseCard"] = "ImageResponseCard"


LexBaseResponse = Annotated[
    Union[LexPlainText, LexImageResponseCard, LexCustomPayload],
    Field(discriminator="contentType"),
]


# Web Image Carousel
class CustomPayloadImageCarousel(BaseModel):
    customContentType: Literal["CustomPayloadImageCarousel"] = (
        "CustomPayloadImageCarousel"
    )
    imageList: list[str] = []


LexMessages = Sequence[
    Union[
        LexBaseResponse,
        PlainText,
    ]
]


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
    slots: dict[str, Optional[Any]] = {}
    state: Optional[str] = None
    confirmationState: Optional[str] = None


class Interpretation(BaseModel):
    intent: Intent
    sentimentResponse: Optional[SentimentResponse] = None
    nluConfidence: Optional[float] = None


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
    type: Optional[str] = None
    slotToElicit: Optional[str] = None


class ProposedNextState(BaseModel):
    prompt: Prompt
    intent: Intent
    dialogAction: DialogAction


ActiveContexts = Optional[list[dict[str, Any]]]


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

    callback_event: Optional[str] = None  # Used for saving the original event to replay
    callback_handler: Optional[str] = (
        None  # Used for saving the original event to replay
    )
    error_count: int = 0  # How many times have we errored?

    # Authentication Related
    customer_type: Optional[str] = None
    imei: Optional[str] = None
    auth_status: Optional[str] = None
    consumer_id: Optional[str] = None
    auth_denied: bool = False  # Was the user denied authentication?
    user_authenticated: bool = False  # User is authenticated?

    error_number: Optional[str] = None  # What is the error number?
    previous_dialog_action_type: str = ""  # What was the last dialog action type?
    previous_slot_to_elicit: str = ""  # What was the last slot to elicit?
    options_provided: Optional[str] = None  # Options provided for "case options"

    language: Optional[str] = None  # What language is the user using?
    next_routing_dialog: Optional[str] = (
        None  # What is the next routing dialog action type?
    )
    common_greeting_count: int = (
        0  # How many times have we greeted the user?
    )
    slot_error_count: int = (
        0  # How many times have we errored on a slot?
    )
    previous_message: Optional[str] = None  # Needed for reprompt

    # Agent Escalation
    escalate_to_agent_non_english: bool = True
    alternate_language: Optional[bool] = (
        True  # to determine if the user wants to continue the conversation in english instead of the original non-english language
    )

    # Routing
    current_form: Optional[Any] = None
    lex_intent: Optional[str] = None
    routing_intent: Optional[str] = None
    routing_dialog: Optional[str] = None
    is_health_check: Optional[bool] = False

    # unknown_choice
    is_lex_retry: Optional[bool] = False
    unknown_routing_slot: Optional[str] = None
    unknown_routing_intent: Optional[str] = None
    is_reprompt: Optional[bool] = False
    is_auth_request: Optional[bool] = None
    is_unknown_choice: Optional[bool] = None

    channel: str = "lex"

    user_text: Optional[str] = ""
    previous_intent: Optional[str] = None  # To identify intent switch

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
    originatingRequestId: Optional[str] = None
    dialogAction: Optional[DialogAction] = None


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
    proposedNextState: Optional[ProposedNextState] = None
    sessionState: SessionState[T] = SessionState(intent=Intent(name="FallbackIntent"))
    messageVersion: str = "DEFAULT_MESSAGE_VERSION"
    invocationSource: str = "DEFAULT_INVOCATION_SOURCE"
    invocationLabel: Optional[str] = None
    transcriptions: list[Transcription] = []
    inputMode: str = "DEFAULT_INPUT_MODE"
    requestAttributes: Optional[dict[str, Any]] = None


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
