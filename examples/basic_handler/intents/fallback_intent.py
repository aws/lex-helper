from lex_helper import LexPlainText, LexRequest, LexResponse, dialog

from ..session_attributes import CustomSessionAttributes


def handler(lex_request: LexRequest[CustomSessionAttributes]) -> LexResponse[CustomSessionAttributes]:
    weather = lex_request.sessionState.sessionAttributes.current_weather
    messages = [
        LexPlainText(content=f"Hello, it sure is sunny in {weather} today! This is Fallback Intent!"),
    ]

    return dialog.close(
        messages=messages,
        lex_request=lex_request,
    )
