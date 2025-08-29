# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Button formatting utilities."""

from dataclasses import dataclass


@dataclass
class Button:
    """Button configuration for response cards."""

    text: str
    value: str

    def to_dict(self) -> dict[str, str]:
        """Convert button to dictionary format.

        Returns:
            Dictionary representation of the button
        """
        return {"text": self.text, "value": self.value}


def create_button(text: str, value: str | None = None) -> Button:
    """Create a button with text and optional value.

    Args:
        text: The button text to display
        value: The button value (defaults to text if not provided)

    Returns:
        A Button instance
    """
    return Button(text=text, value=value or text)


def create_buttons(texts: list[str], values: list[str] | None = None) -> list[Button]:
    """Create multiple buttons from lists of texts and optional values.

    Args:
        texts: List of button texts
        values: Optional list of button values (must match length of texts if provided)

    Returns:
        List of Button instances

    Raises:
        ValueError: If values list is provided but length doesn't match texts
    """
    if values and len(values) != len(texts):
        raise ValueError("Values list must match length of texts list")

    if not values:
        return [create_button(text) for text in texts]

    return [create_button(text, value) for text, value in zip(texts, values)]


def format_buttons_for_display(buttons: list[Button], style: str = "default") -> str:
    """Format buttons for display in a consistent way.

    Args:
        buttons: List of buttons to format
        style: Display style ("default", "compact", or "verbose")

    Returns:
        Formatted string representation of buttons
    """
    if not buttons:
        return ""

    if style == "compact":
        return ", ".join(button.text for button in buttons)

    if style == "verbose":
        return "\n".join(f"[{button.text}] -> {button.value}" for button in buttons)

    # Default style
    return " | ".join(f"[{button.text}]" for button in buttons)


def buttons_to_dicts(buttons: list[Button]) -> list[dict[str, str]]:
    """Convert a list of buttons to list of dictionaries.

    Args:
        buttons: List of Button instances

    Returns:
        List of button dictionaries
    """
    return [button.to_dict() for button in buttons]
