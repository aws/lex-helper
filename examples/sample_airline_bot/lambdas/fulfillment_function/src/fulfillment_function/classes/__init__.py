# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Generated classes for type-safe bot interactions.

This package contains auto-generated enums for intents and slots,
providing type safety and IDE autocomplete for bot development.
"""

from .intent_name import IntentName
from .slot_enums import (
    AuthenticateSlot,
    BookFlightSlot,
    CancelFlightSlot,
    ChangeFlightSlot,
    FlightDelayUpdateSlot,
    TrackBaggageSlot,
)

__all__ = [
    "IntentName",
    "AuthenticateSlot",
    "BookFlightSlot",
    "CancelFlightSlot",
    "ChangeFlightSlot",
    "FlightDelayUpdateSlot",
    "TrackBaggageSlot",
]
