# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import copy
import json

import pytest

from lex_helper import SessionAttributes
from lex_helper.core.dialog import parse_lex_request


@pytest.mark.parametrize("attributes", [{}, {"language": "fr_FR"}])
def test_parse_request_does_not_replace_input_session_attributes(attributes):
    event = {"sessionState": {"intent": {"name": "Test"}, "sessionAttributes": attributes}}
    original = copy.deepcopy(event)

    request = parse_lex_request(event, SessionAttributes())

    assert event == original
    assert json.loads(json.dumps(event)) == original
    assert request.sessionState.sessionAttributes.language == attributes.get("language")
