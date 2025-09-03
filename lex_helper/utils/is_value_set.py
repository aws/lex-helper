# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any


def is_value_set(my_dict: dict[str, Any], key: str):
    value = my_dict.get(key)
    return value not in [None, "", "null"]
