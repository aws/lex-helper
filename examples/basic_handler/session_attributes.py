from pydantic import ConfigDict, Field

from lex_helper import SessionAttributes


class CustomSessionAttributes(SessionAttributes):
    """
    Custom session attributes with additional fields.

    Attributes:
        custom_field_1 (str): A custom string field with a default value.
        custom_field_2 (int): A custom integer field with a default value.
        current_weather (str): The weather in the city the user is currently in.
    """

    model_config = ConfigDict(extra="allow")
    custom_field_1: str = Field(default="default_value", description="A custom string field with a default value.")
    custom_field_2: int = Field(default=0, description="A custom integer field with a default value.")
    current_weather: str = Field(default="sunny", description="The weather in the city the user is currently in.")
