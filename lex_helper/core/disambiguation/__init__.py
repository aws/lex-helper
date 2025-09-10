# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Smart Disambiguation module for lex-helper.

This module provides intelligent handling of ambiguous user input by analyzing
intent confidence scores, considering conversation context, and presenting
targeted clarifying questions to users.
"""

from .analyzer import DisambiguationAnalyzer
from .handler import DisambiguationHandler
from .types import (
    DisambiguationConfig,
    DisambiguationResult,
    IntentCandidate,
)

__all__ = [
    "DisambiguationAnalyzer",
    "DisambiguationHandler",
    "DisambiguationConfig",
    "DisambiguationResult",
    "IntentCandidate",
]
