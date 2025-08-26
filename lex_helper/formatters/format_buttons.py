# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from lex_helper import Button


def format_buttons(buttons: list[Button]) -> list[Button]:
    """
    This function formats Button objects.

    Parameters:
    buttons (List[Button]): A list of Button objects to be formatted.

    Returns:
    List[Button]: A list of formatted Button objects.
    """
    return [
        Button(text=button.text, value=(button.value if button.value is not None else button.text)) for button in buttons
    ]
