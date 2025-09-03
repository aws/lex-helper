# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from lex_helper import (
    Button,
    ImageResponseCard,
    LexImageResponseCard,
    LexMessages,
    LexPlainText,
    dialog,
)


def test_get_provided_options():
    # Test with no messages
    assert dialog.get_provided_options([]) == "[]"

    # Test with one message that is not a LexImageResponseCard
    assert dialog.get_provided_options([LexPlainText(content="")]) == "[]"

    # Test with one LexImageResponseCard with no buttons
    assert (
        dialog.get_provided_options([LexImageResponseCard(imageResponseCard=ImageResponseCard(title="testing", buttons=[]))])
        == "[]"
    )

    # Test with multiple LexImageResponseCards with multiple buttons
    messages: LexMessages = [
        LexImageResponseCard(
            imageResponseCard=ImageResponseCard(
                title="testing",
                buttons=[Button(text="Button 1", value="Button 1"), Button(text="Button 2", value="Button 2")],
            )
        ),
        LexImageResponseCard(
            imageResponseCard=ImageResponseCard(
                title="testing",
                buttons=[Button(text="Button 3", value="Button 3"), Button(text="Button 4", value="Button 4")],
            )
        ),
    ]
    assert dialog.get_provided_options(messages) == '["Button 1", "Button 2", "Button 3", "Button 4"]'
