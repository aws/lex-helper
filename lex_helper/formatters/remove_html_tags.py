# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import re


def remove_html_tags(text: str) -> str:
    """
    This function removes <p></p> HTML tags from the text and trims \r\n from the end.

    Parameters:
    text (str): The text from which <p></p> HTML tags should be removed.

    Returns:
    str: The text without the <p></p> HTML tags and trailing \r\n.
    """

    # Remove HTML tags
    text = re.sub(r"<p>(.*?)</p>", r"\1", text, flags=re.DOTALL)

    # Trim \r\n from the end of the text
    text = text.rstrip("\r\n")

    return text
