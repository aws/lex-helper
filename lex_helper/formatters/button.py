# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from pydantic import BaseModel


class Button(BaseModel):
    text: str
    value: str | None = None

    def set_value(self, v: Any, values: dict[str, Any]):
        if "text" in values and v is None:
            return values["text"]
        return v
