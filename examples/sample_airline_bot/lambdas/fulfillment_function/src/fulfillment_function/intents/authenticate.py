"""
Handler for the Authenticate intent.

This intent demonstrates user authentication flow before allowing access to other intents.
In a production environment, you would integrate with your actual authentication system.
"""

from loguru import logger

from lex_helper import LexPlainText, LexRequest, LexResponse, dialog, get_message

from ..session_attributes import AirlineBotSessionAttributes
from ..utils.enums import InvocationSource


def handle_dialog_hook(lex_request: LexRequest[AirlineBotSessionAttributes]) -> LexResponse[AirlineBotSessionAttributes]:
    """Handle the dialog code hook for the Authenticate intent."""
    logger.debug("Authenticate dialog code hook called")

    intent = dialog.get_intent(lex_request)
    account_id = dialog.get_slot(intent=intent, slot_name="AccountId")

    logger.debug(f"Account ID provided: {account_id}")

    # Elicit AccountId if not provided
    if not account_id:
        message = "Please provide your account ID to continue."
        try:
            message = get_message("authenticate.elicit_account_id")
        except Exception as e:
            logger.warning(f"Failed to get localized message: {e}")
        logger.debug(f"Eliciting AccountId slot: {message}")
        return dialog.elicit_slot(
            slot_to_elicit="AccountId", messages=[LexPlainText(content=message)], lex_request=lex_request
        )

    # All required slots filled, proceed to fulfillment
    return dialog.delegate(lex_request=lex_request)


def handle_fulfillment_hook(
    lex_request: LexRequest[AirlineBotSessionAttributes],
) -> LexResponse[AirlineBotSessionAttributes]:
    """Handle the fulfillment code hook for the Authenticate intent."""
    logger.debug("Authenticate fulfillment hook called")

    intent = dialog.get_intent(lex_request)
    account_id = dialog.get_slot(intent=intent, slot_name="AccountId")

    if account_id:
        # In production, validate account_id against your authentication system
        # For demo purposes, we accept any non-empty account ID
        logger.debug(f"Authenticating user with account ID: {account_id}")
        lex_request.sessionState.sessionAttributes.user_authenticated = True

        logger.debug("Authentication successful, returning to original intent")
        try:
            message = "Authentication successful. Now I can help you with your original request."
            try:
                message = get_message("authenticate.authentication_success")
            except Exception as e:
                logger.warning(f"Failed to get localized message: {e}")
            return dialog.callback_original_intent_handler(lex_request=lex_request, messages=[LexPlainText(content=message)])
        except Exception as e:
            logger.error(f"Error in callback_original_intent_handler: {e}")
            message = "Authentication completed, but there was an issue returning to the previous conversation."
            return dialog.close(messages=[LexPlainText(content=message)], lex_request=lex_request)

    # Should not reach here if dialog validation works correctly
    message = "Authentication failed. Please try again."
    try:
        message = get_message("authenticate.authentication_failed")
    except Exception as e:
        logger.warning(f"Failed to get localized message: {e}")
    return dialog.close(messages=[LexPlainText(content=message)], lex_request=lex_request)


def handler(lex_request: LexRequest[AirlineBotSessionAttributes]) -> LexResponse[AirlineBotSessionAttributes]:
    """
    Main handler for the Authenticate intent.

    This intent handles user authentication before allowing access to protected intents.
    It demonstrates the callback pattern for returning to the original intent after authentication.

    Args:
        lex_request: The Lex request containing user input and session state

    Returns:
        LexResponse: The response to send back to Amazon Lex
    """
    logger.debug("Authenticate intent handler called")

    invocation_source = lex_request.invocationSource
    logger.debug(f"Invocation source: {invocation_source}")

    if invocation_source == InvocationSource.DIALOG_CODE_HOOK.value:
        return handle_dialog_hook(lex_request)

    if (
        invocation_source == InvocationSource.FULFILLMENT_CODE_HOOK.value
        or lex_request.sessionState.intent.state == "ReadyForFulfillment"
    ):
        return handle_fulfillment_hook(lex_request)

    # Fallback - should not normally reach here
    logger.warning(f"Unrecognized invocation source: {invocation_source}")
    return dialog.delegate(lex_request=lex_request)
