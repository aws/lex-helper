# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import Any
from uuid import uuid4


def construct_headers(token: str) -> dict[str, Any]:
    app_id = "BOT"  # Replace with actual values
    channel_id = "CHATBOT"
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Date": datetime.now().isoformat(),
        "X-App-Id": app_id,
        "X-Channel-Id": channel_id,
        "X-Request-Id": str(uuid4()),
    }
