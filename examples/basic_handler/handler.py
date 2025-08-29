from typing import Any

from lex_helper.core.handler import Config, LexHelper

from .session_attributes import CustomSessionAttributes


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    # We're going to customize our session attributes, you almost certainly will want to do this!
    config = Config(session_attributes=CustomSessionAttributes(), package_name="examples.basic_handler")

    # Initialize the LexHelper
    lex_helper = LexHelper(config=config)

    # Call the handler, this will convert the event to a LexRequest, dynamically pass it to the matching intent Python file (under "intents/")
    # and return a LexResponse.
    return lex_helper.handler(event, context)
