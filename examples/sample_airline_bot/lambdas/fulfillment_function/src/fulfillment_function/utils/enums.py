# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Enums for the Airline-Bot fulfillment function.

This module contains enumeration classes that define constants used throughout
the fulfillment function for type safety and code clarity.
"""

from enum import Enum


class InvocationSource(Enum):
    """
    Enum for the invocation source of an Amazon Lex request.

    Amazon Lex can invoke Lambda functions at different points in the conversation
    flow. This enum defines the possible invocation sources.

    Attributes:
        DIALOG_CODE_HOOK: Request is from dialog management (slot elicitation, validation)
        FULFILLMENT_CODE_HOOK: Request is for intent fulfillment (final processing)
    """

    DIALOG_CODE_HOOK = "DialogCodeHook"
    FULFILLMENT_CODE_HOOK = "FulfillmentCodeHook"


class ConfirmationStatus(Enum):
    """
    Enum for the confirmation status of an Amazon Lex intent.

    When an intent requires confirmation, Lex tracks whether the user has
    confirmed or denied the intent. This enum defines the possible states.

    Attributes:
        NONE: The intent has not been confirmed or denied yet
        CONFIRMED: The user has confirmed the intent
        DENIED: The user has denied/rejected the intent
    """

    NONE = "None"
    CONFIRMED = "Confirmed"
    DENIED = "Denied"
