# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest

from lex_helper.core.dialog import close
from lex_helper.core.types import Intent, LexPlainText, LexRequest, SessionAttributes, SessionState


@pytest.mark.parametrize("turns", [[], [0], [0, 3]])
def test_close_returns_only_active_contexts(turns):
    contexts = [
        {"name": f"context-{i}", "timeToLive": {"turnsToLive": turn, "timeToLiveInSeconds": 300}}
        for i, turn in enumerate(turns)
    ]
    request = LexRequest(
        sessionState=SessionState(intent=Intent(name="Test"), sessionAttributes=SessionAttributes(), activeContexts=contexts)
    )

    response = close(request, [LexPlainText(content="Done")])

    expected = [context for context in contexts if context["timeToLive"]["turnsToLive"] > 0]
    assert response.sessionState.activeContexts == expected
    assert request.sessionState.activeContexts == expected
