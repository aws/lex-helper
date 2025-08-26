# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import re

from lex_helper import SessionAttributes


def substitute_keys_in_text(input_text: str, session_attributes: SessionAttributes):
    item = input_text
    placeholders = contains_placeholders(input_text)

    # Lowercase all session_attribute keys
    lower_session_attributes = {k.lower(): v for k, v in session_attributes.model_dump().items()}
    if placeholders:
        for ph in placeholders:
            if ph.lower() in lower_session_attributes:
                value = lower_session_attributes[ph.lower()]
                if value:
                    item = item.replace("{" + ph + "}", value)
    return item


def contains_placeholders(response_text: str) -> list[str]:
    pattern = "\{([a-zA-Z]+)\}"  # type: ignore
    return re.findall(pattern, response_text)
