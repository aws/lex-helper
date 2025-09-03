# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Any


def add_to_list(lst: list[Any], item: Any):
    """
    Add an item to a list. If the item is a list, combine the lists. If it's a singular item, append it to the list.
    If the item is None, just returns the original list.
    Returns a new list and does not modify the original list.

    Parameters:
    lst (list): The list to which the item should be added.
    item: The item to be added. Can be a list or a singular item.

    Returns:
    list: The new list.
    """
    if isinstance(item, list):
        # If the item is a list, concatenate the lists to create a new list
        return lst + item
    if item is None:
        # If the item is None, return the original list
        return lst
    else:
        # If the item is a singular item, append it to a new list that is a copy of the original list
        return lst + [item]
