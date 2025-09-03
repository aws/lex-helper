# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import os
import re
from typing import Any, TypeVar
from uuid import uuid4

from loguru import logger

from lex_helper import SessionAttributes

from .query_lex import query_lex, update_lex_session_variable

EXPRESSION_PARSE_FAIL = "failed to parse expression as key/value pair"


def validate_flow_with_lex(expected_flow_path: str):
    session_id = "pytest-" + str(uuid4())

    responses_from_lex = []

    text = open(expected_flow_path, encoding="utf-8")

    lines = text.readlines()

    # Has the user spoken yet?  If not, don't test.  Must begin with User utterance!\
    user_has_spoken = False
    set_all_session_variables(lines, session_id)

    for line in lines:
        if line.startswith("**Common Greeting**"):
            logger.debug("Saying 'Hi' to the bot, skipping validation of common greeting")
            submit_user_input("Hi", session_id)
            continue
        if line.startswith("\n"):
            continue
        if line.startswith("#"):
            continue
        if line.startswith("- *"):
            continue
        if line.startswith("`") or line.startswith("- `"):
            continue

        if line.startswith("**User:**"):
            assert len(responses_from_lex) == 0, (
                f"Expected to have no remaining bot responses to process because we're at user input ({line}) now, but still have the following that could not be matched in the markdown: {responses_from_lex}"
            )
            if line.startswith("**User:**  >Jump"):
                continue
            user_has_spoken = True
            responses_from_lex = submit_user_input(sanitize_line(line), session_id)
        elif user_has_spoken:
            if line.startswith("**Bot:**"):
                validate_response(sanitize_line(line), responses_from_lex, expected_flow_path)
            if line.startswith("-"):
                responses_from_lex = validate_button(sanitize_line(line), responses_from_lex)
            if line.startswith("!["):
                responses_from_lex = validate_image(responses_from_lex)


def set_all_session_variables(lines: list[str], session_id: str):
    for line in lines:
        if line.startswith("`") or line.startswith("- `"):
            update_session_variable(line, session_id)


def update_session_variable(line: str, session_id: str):
    logger.trace(line)
    # First, remove whitespace
    line = line.strip()
    line = line.replace("`", "")
    line = line.replace("-", "")
    line = line.replace("{", "")
    line = line.replace("}", "")
    line = line.replace("==", "=")

    if "&&" in line:
        variables = line.split("&&")
        for variable in variables:
            variable_name = variable.split(" = ")[0].strip()
            variable_value = variable.split(" = ")[1].strip()
            update_lex_session_variable(variable_name, variable_value, session_id)
    else:
        # For channel check
        if "Channel is" in line:
            variable_name = "channel"
            variable_value = line.split(" is ")[1].lower()
            if "or" in variable_value:
                variable_value = variable_value.split(" or ")[0]
        elif "Default" in line:
            variable_name = "channel"
            variable_value = "lex"
        else:
            variable_name = line.split(" = ")[0].strip()
            variable_value = line.split(" = ")[1]

        if "or" in variable_value:
            variable_value = variable_value.split(" or ")[0]

        # Determine if variable_value is a string, number, or boolean.  If string, remove quotes
        if variable_value.startswith('"') and variable_value.endswith('"'):
            variable_value = variable_value.replace('"', "")
        elif variable_value.startswith("'") and variable_value.endswith("'"):
            variable_value = variable_value.replace("'", "")

        # Now call Lex to update the session variable
        update_lex_session_variable(variable_name, variable_value, session_id)


def validate_image(responses_from_lex: list[dict[str, Any]]):
    image_url = responses_from_lex[0]["imageResponseCard"]["imageUrl"].replace("_", "%20")

    if not is_valid_image_url(image_url):
        raise UnexpectedBotImageError("Expected a valid image url stored in dam", image_url)

    responses_from_lex.pop(0)
    return responses_from_lex


T = TypeVar("T", bound=SessionAttributes)


def submit_user_input(line: str, session_id: str, session_attributes: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    # Your implementation for handling user input
    logger.info(f"Simulated User Input: {line}")
    lex_response = query_lex(text=line, session_id=session_id, session_attributes=session_attributes)
    if "messages" in lex_response:
        return lex_response["messages"]
    return []


def validate_button(line: str, responses_from_lex: list[dict[str, Any]]):
    if len(responses_from_lex) == 0:
        # Skipping, as this is most likely the initial message, before any user input
        return responses_from_lex
    buttons = responses_from_lex

    if "imageResponseCard" in buttons[0]:
        if "buttons" in buttons[0]["imageResponseCard"]:
            # Add buttons to the responses_from_lex array
            for button in buttons[0]["imageResponseCard"]["buttons"]:
                responses_from_lex.append(button)
        # Pop the image response card from the array
        responses_from_lex.pop(0)

    expected_button_text = line.strip().replace("- ", "", 1)

    # Skip if the expected button text is "No match"
    if expected_button_text == "No match":
        return responses_from_lex

    # Ensure that the expected button text is present in the response from Lex
    button_texts = [button.get("text") for button in buttons]
    assert expected_button_text in button_texts, f"Expected button text: {expected_button_text}, but got: {button_texts}"

    # Assert the button text matches the button value
    for button in buttons:
        button_text = button.get("text", "UNKNOWN BUTTON TEXT")
        button_value = button.get("value", "UNKNOWN BUTTON VALUE")

        if button_text == expected_button_text:
            assert button_text == button_value, f"Button text: {button_text} does not match button value: {button_value}"

    # Remove that button from the array
    responses_from_lex = [item for item in buttons if item.get("text") != expected_button_text]

    return responses_from_lex


def process_lines(lines: list[str]):
    grouped_lines: list[list[str]] = []
    temp_group: list[str] = []

    for line in lines:
        if line.startswith("-"):
            temp_group.append(line)
        else:
            if temp_group:
                grouped_lines.append(temp_group)
                temp_group = []

    if temp_group:
        grouped_lines.append(temp_group)

    return grouped_lines


def sanitize_line(line: str):
    return (
        line.replace("**Bot:**", "")
        .replace("**User:**", "")
        .replace("&amp;", "&")
        .replace("&quot;", '"')
        .strip()
        .replace("&nbsp;", "")
        .replace("<br/>", "")
        .replace("<br />", "")
    )


def get_url_from_markdown_link(markdown_link: str):
    pattern = r"\[(.*?)\]\((.*?)\)"
    match = re.search(pattern, markdown_link)
    if match:
        return match.group(2)
    else:
        return None


def is_markdown_link(s: str):
    pattern = r"^\[(.+?)\]\((.+?)\)$"
    return bool(re.match(pattern, s))


class UnexpectedBotImageError(Exception):
    "Raised when the image from the bot does not match what was expected"

    def __init__(self, expected_response: str, response_from_bot: str):
        self.expected_response = expected_response
        self.response_from_bot = response_from_bot

        super().__init__(f'Expected: "{expected_response}" image.  Actual image response from lex: "{response_from_bot}"')


class UnexpectedBotResponseError(Exception):
    "Raised when the response from the bot does not match what was expected"

    def __init__(self, expected_response: str, response_from_bot: str, flow_path: str):
        self.expected_response = expected_response
        self.response_from_bot = response_from_bot
        self.flow_path = flow_path
        error_message = f'Expected: "{expected_response}", based on the flow in file "{flow_path}".  Actual response from lex: "{response_from_bot}"'
        logger.exception(error_message)
        super().__init__(error_message)


def validate_response(line: str, responses_from_lex: list[dict[str, Any]], expected_flow_path: str):
    if line != "👋 Hi, I'm a greeting message?!":
        if not responses_from_lex:
            raise UnexpectedBotResponseError(
                expected_response=line,
                response_from_bot="Expected line, received no response from Lex!",
                flow_path=expected_flow_path,
            )
        if "content" in responses_from_lex[0]:
            lex_response = responses_from_lex[0]["content"].replace("&nbsp;", "").replace("&amp;", "&").replace("\xa0", " ")
        else:
            lex_response = (
                responses_from_lex[0]["imageResponseCard"]["title"]
                .replace("&nbsp;", "")
                .replace("&amp;", "&")
                .replace("\xa0", " ")
            )

        # Standardize line breaks
        if "\\n" in line:
            line = line.replace("\\n", "\n")
        if "\r\n" in lex_response:
            lex_response = lex_response.replace("\r\n", "\n")

        # For any line breaks ("\n") within line or lex_response, if the line break is preceded by a space, remove the space
        if ". \n" in line:
            line = line.replace(". \n", ".\n")
        if ". \n" in lex_response:
            lex_response = lex_response.replace(". \n", ".\n")

        if line.startswith("Title:"):
            url = get_url_from_text(line)
            if line != lex_response:
                assert url in lex_response, f"Expected link: {url}, but got: {lex_response}"

        elif is_markdown_link(line):
            url_from_markdown = get_url_from_markdown_link(line)
            # We often have a marketing campaign in the URL, so we need to remove it, as we don't care about it
            lex_response_without_marketing_campaign = lex_response.split("?")[0]
            assert url_from_markdown == lex_response_without_marketing_campaign, (
                f"Expected link: {url_from_markdown}, but got: {lex_response_without_marketing_campaign}"
            )
        else:
            if line != lex_response:
                raise UnexpectedBotResponseError(
                    expected_response=line,
                    response_from_bot=lex_response,
                    flow_path=expected_flow_path,
                )

        if "imageResponseCard" in responses_from_lex[0]:
            if "buttons" in responses_from_lex[0]["imageResponseCard"]:
                # Add buttons to the responses_from_lex array
                for button in responses_from_lex[0]["imageResponseCard"]["buttons"]:
                    responses_from_lex.append(button)
        # Pop the image response card from the array
        responses_from_lex.pop(0)


def find_md_files(directory: str) -> list[str]:
    md_files: list[str] = []

    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            md_files.append(filename)

    return md_files


def is_valid_image_url(url: str) -> bool:
    return url.startswith("https://")


def get_url_from_text(text: str) -> str:
    pattern = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    match = re.search(pattern, text)
    if match:
        return match.group()
    else:
        return ""
