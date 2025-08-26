# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Optional


def intent_identified(intent_name: Optional[str]):
    return intent_name is not None and intent_name not in [
        "Common_Authentication",
        "FallbackIntent",
        "Common_Exit_Feedback",
        "Report_Complaint",
    ]
