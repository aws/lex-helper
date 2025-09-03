# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from typing import Any

from pydantic import BaseModel


class Message(BaseModel):
    value: str | None


class PlainTextMessage(BaseModel):
    plainTextMessage: Message | None


class MessageGroup(BaseModel):
    message: PlainTextMessage
    variations: str | None


class AllowedInputTypes(BaseModel):
    allowAudioInput: bool
    allowDTMFInput: bool


class AudioSpecification(BaseModel):
    endTimeoutMs: int
    maxLengthMs: int


class DTMFSpecification(BaseModel):
    deletionCharacter: str
    endCharacter: str
    endTimeoutMs: int
    maxLength: int


class AudioAndDTMFInputSpecification(BaseModel):
    audioSpecification: AudioSpecification
    dtmfSpecification: DTMFSpecification
    startTimeoutMs: int


class TextInputSpecification(BaseModel):
    startTimeoutMs: int


class PromptAttemptsSpecification(BaseModel):
    Initial: dict[str, Any] | None = None
    Retry1: dict[str, Any] | None = None
    Retry2: dict[str, Any] | None = None
    Retry3: dict[str, Any] | None = None
    Retry4: dict[str, Any] | None = None


class PromptSpecification(BaseModel):
    allowInterrupt: bool
    maxRetries: int
    messageGroupsList: list[MessageGroup]
    messageSelectionStrategy: str
    promptAttemptsSpecification: PromptAttemptsSpecification


class ElicitationCodeHook(BaseModel):
    enableCodeHookInvocation: bool
    invocationLabel: str | None


class EmuDialogAction(BaseModel):
    slotToElicit: str | None
    suppressNextMessage: str | None
    type: str


class Intent(BaseModel):
    name: str | None
    slots: dict[str, str] | None = None


class NextStep(BaseModel):
    dialogAction: EmuDialogAction
    intent: Intent | None
    sessionAttributes: dict[str, str] | None = None


class FailureOrSuccessResponse(BaseModel):
    allowInterrupt: bool
    messageGroupsList: list[dict[str, Any]]


class PostCodeHookSpecification(BaseModel):
    failureConditional: str | None = None
    failureNextStep: NextStep
    failureResponse: FailureOrSuccessResponse | None = None
    successConditional: str | None = None
    successNextStep: NextStep
    successResponse: FailureOrSuccessResponse | None = None
    timeoutConditional: str | None = None
    timeoutNextStep: NextStep
    timeoutResponse: Any | None = None


class CodeHook(BaseModel):
    enableCodeHookInvocation: bool
    invocationLabel: str | None = None
    isActive: bool
    postCodeHookSpecification: PostCodeHookSpecification


class CaptureNextStep(BaseModel):
    dialogAction: EmuDialogAction
    intent: Intent | None
    sessionAttributes: dict[str, Any] | None


class SlotCaptureSetting(BaseModel):
    captureConditional: str | None = None
    captureNextStep: CaptureNextStep | None = None
    captureResponse: str | None = None
    codeHook: CodeHook | None = None
    elicitationCodeHook: ElicitationCodeHook
    failureConditional: str | None = None
    failureNextStep: NextStep | None = None
    failureResponse: FailureOrSuccessResponse | None = None
    successResponse: FailureOrSuccessResponse | None = None


class ValueElicitationSetting(BaseModel):
    defaultValueSpecification: str | None = None
    promptSpecification: PromptSpecification
    sampleUtterances: str | None = None
    slotCaptureSetting: SlotCaptureSetting | None = None
    slotConstraint: str
    waitAndContinueSpecification: str | None = None


class MultipleValuesSetting(BaseModel):
    allowMultipleValues: bool


class Slot(BaseModel):
    description: str | None = None
    identifier: str
    multipleValuesSetting: MultipleValuesSetting | None = None
    name: str
    obfuscationSetting: Any | None = None
    slotTypeName: str
    valueElicitationSetting: ValueElicitationSetting | None


class ValueSelectionSetting(BaseModel):
    regexFilterPattern: str | None = None
    resolutionStrategy: str
    valueSelectionStrategy: str | None = None


class SampleValue(BaseModel):
    value: str


class Synonym(BaseModel):
    value: str


class SlotTypeValue(BaseModel):
    synonyms: list[Synonym] | None = None
    sampleValue: SampleValue


class SubSlot(BaseModel):
    name: str
    slotTypeId: str


class CompositeSlotTypeSetting(BaseModel):
    subSlots: list[SubSlot]


class SlotType(BaseModel):
    description: str | None
    identifier: str
    name: str
    slotTypeValues: list[SlotTypeValue] | None = None
    valueSelectionSetting: ValueSelectionSetting
    compositeSlotTypeSetting: CompositeSlotTypeSetting | None = None


class DialogCodeHook(BaseModel):
    enabled: bool


class Utterance(BaseModel):
    utterance: str


class SlotPriority(BaseModel):
    priority: int
    slotName: str


class DialogAction(BaseModel):
    slotToElicit: str | None
    suppressNextMessage: str | None
    type: str


class InitialResponseSetting(BaseModel):
    codeHook: CodeHook
    conditional: str | None
    initialResponse: str | None
    nextStep: NextStep


class IntentData(BaseModel):
    description: str | None
    dialogCodeHook: DialogCodeHook
    fulfillmentCodeHook: Any | None = None
    identifier: str
    initialResponseSetting: InitialResponseSetting | None = None
    inputContexts: Any | None = None
    intentClosingSetting: Any | None = None
    intentConfirmationSetting: Any | None
    kendraConfiguration: str | None
    name: str
    outputContexts: Any | None = None
    parentIntentSignature: str | None
    qnAIntentConfiguration: str | None
    sampleUtterances: list[Utterance] | None = None
    slotPriorities: list[SlotPriority]
