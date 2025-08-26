# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

def replace_special_characters(text: str) -> str:
    """
    This function replaces &amp,&quot; from the text.

    Parameters:
    text (str): The text from which special characters should be removed.

    Returns:
    str: The text without the special characters.
    """

    # Replace special characters
    text = (
        text.replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("\u00a0", " ")
        .strip()
        .replace("&nbsp;", "")
        .replace("<br/>", "")
        .replace("<br />", "")
    )

    return text
