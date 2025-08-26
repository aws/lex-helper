# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from enum import Enum
from typing import Any


class ExtendedEnum(Enum):
    def __getitem__(self, item: Any) -> Any:
        try:
            return super().__getitem__(item)  # type: ignore
        except Exception:
            for key in self._member_map_.keys():  # type: ignore
                if key.casefold() == item.casefold():
                    return super().__getitem__(key)  # type: ignore

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
