# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Any

import requests
from loguru import logger


def make_request(url: str, headers: dict[str, Any]) -> Any:
    INVALID_TOKEN_RESPONSE = "oauth.v2.InvalidAccessToken"
    try:
        response = requests.get(
            url, headers=headers, timeout=(5, 15)
        )  # Replace 5, 15 with connection and read timeout values
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if INVALID_TOKEN_RESPONSE in str(e):
            return "retry"
        else:
            handle_error(str(e))
            return None


def handle_error(error_message: str) -> None:
    error = {"code": "BOT50303", "message": f"Call to API failed. {error_message}"}

    json_error = json.dumps(error)
    logger.error(f"Error message: {error_message}")
    logger.error(json_error)
