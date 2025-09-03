# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


def make_request(url: str, headers: dict[str, Any]) -> Any:
    invalid_token_response = "oauth.v2.InvalidAccessToken"
    try:
        response = requests.get(
            url, headers=headers, timeout=(5, 15)
        )  # Replace 5, 15 with connection and read timeout values
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if invalid_token_response in str(e):
            return "retry"
        else:
            handle_error(str(e))
            return None


def handle_error(error_message: str) -> None:
    error = {"code": "BOT50303", "message": f"Call to API failed. {error_message}"}

    json_error = json.dumps(error)
    logger.error("Error message: %s", error_message)
    logger.error(json_error)
