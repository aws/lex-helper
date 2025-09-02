"""
Example of using MessageManager in a Lambda deployment.
"""

from typing import Any

from lex_helper import Config, LexHelper, get_message, set_locale
from lex_helper.core.session_attributes import SessionAttributes


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda handler with MessageManager usage."""

    # Set locale from Lex event
    locale = event.get("bot", {}).get("localeId", "en_US")
    set_locale(locale)

    # Use messages in your handler
    welcome_msg = get_message("welcome", "Welcome!")
    error_msg = get_message("error.general", "Something went wrong")
    
    # Example usage of the messages
    print(f"Welcome message: {welcome_msg}")
    print(f"Error message: {error_msg}")

    config = Config(session_attributes=SessionAttributes(), package_name="your_project.intents")

    lex_helper = LexHelper(config=config)
    return lex_helper.handler(event, context)


# Example intent handler using MessageManager
def handle_greeting_intent(lex_helper):
    """Example intent handler."""
    greeting = get_message("greeting.welcome")
    return lex_helper.close(greeting)
