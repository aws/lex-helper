<h2 align="center">Lex Helper Library</h2>

<p align="center">
<a href="LICENSE"><img alt="License: Apache 2.0" src="https://img.shields.io/badge/License-Apache%202.0-blue.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

> "This is the best thing since sliced bread" - Lex

The Lex Helper library is an extensive collection of functions and classes that make it
easier to work with Lex. It's designed to make building Lex fulfillment lambdas easier,
more efficient, understandable, and consistent. Gone are the days of accidentally
mistyping a slot name, using a dictionary within a dictionary within a dictionary, or
not being able to find where the code for a specific intent is.

## Why Use Lex Helper?

- **Simplified Intent Management**: Each intent's logic lives in its own file under an `intents/` directory, making it easy to locate, maintain, and scale your bot's capabilities without navigating complex nested handlers.  The library will dynamically load the intent handler based on the intent name. (Configurable)

![Intent Handling](docs/intent-handling.png)
- **Type-Safe Session Attributes**: Define your session attributes as a Pydantic model, eliminating runtime errors from typos or incorrect data types. Get full IDE autocomplete support and catch errors before they reach production.

![Intellisense](docs/intellisense.png)

- **Automatic Request/Response Handling**: Stop wrestling with deeply nested dictionaries. The library handles all the Lex request/response formatting, letting you focus on your bot's business logic.

- **Channel-Aware Formatting**: Built-in support for different channels (SMS, Lex console, etc.) ensures your responses are properly formatted regardless of how users interact with your bot.

- **Error Handling Made Easy**: Comprehensive exception handling and error reporting help you quickly identify and fix issues in your fulfillment logic.

- **Reduced Boilerplate**: Common Lex operations like transitioning between intents, handling dialog states, and managing session attributes are simplified into clean, intuitive methods.

- **Developer Experience**: Get the benefits of modern Python features like type hints, making your code more maintainable and easier to understand. Full IDE support means better autocomplete and fewer runtime errors.

## Dialog Utilities
### Function Overview
- **get_sentiment**: Extracts sentiment from the first interpretation in a `LexRequest`.
- **remove_context**: Removes a specific context from the list of active contexts.
- **remove_inactive_context**: Removes inactive contexts from the active contexts list in a `LexRequest`.
- **close**: Closes the dialog by setting the intent state to 'Fulfilled' and returns a `LexResponse`.
- **elicit_intent**: Elicits the user's intent by sending a message and updating session attributes.
- **elicit_slot**: Elicits a specific slot from the user by sending a message and updating session attributes.
- **delegate**: Delegates the dialog to Lex by updating the session state and returning a response.
- **get_provided_options**: Extracts button texts from `LexImageResponseCard` messages and returns them as a JSON-encoded list.
- **get_intent**: Retrieves the intent from a `LexRequest`.
- **get_slot**: Retrieves the value of a slot from an intent.
- **get_composite_slot**: Retrieves values from sub-slots of a given slot from an intent.
- **get_slot_value**: Retrieves the value from a slot dictionary, considering preferences for interpreted or original values.
- **set_subslot**: Sets a subslot value within a composite slot in the given intent.
- **set_slot**: Sets a slot value in the given intent.
- **get_composite_slot_subslot**: Retrieves the value of a subslot from a composite slot in an intent.
- **get_active_contexts**: Retrieves the active contexts from a `LexRequest`.
- **get_invocation_label**: Retrieves the invocation label from a `LexRequest`.
- **safe_delete_session_attribute**: Safely deletes a session attribute from a `LexRequest`.
- **get_request_components**: Extracts common components from the intent request, including intent, active contexts, session attributes, and invocation label.
- **any_unknown_slot_choices**: Checks if there are any unknown slot choices in the `LexRequest`.
- **handle_any_unknown_slot_choice**: Handles any unknown slot choice in the `LexRequest`.
- **unknown_choice_handler**: Handles an unknown choice in the `LexRequest`.
- **reprompt_slot**: Reprompts the user for a slot value by sending a message.
- **load_messages**: Loads messages from a JSON string into `LexMessages` objects.
- **parse_req_sess_attrs**: Parses request session attributes from a `LexRequest`.
- **parse_lex_request**: Parses a Lambda event into a `LexRequest` object, handling session attributes and inactive contexts.

## Installation & Usage

Download the latest .tar.gz file from
[https://gitlab.aws.dev/lex/lex-helper/-/releases](https://gitlab.aws.dev/lex/lex-helper/-/releases)
and copy it into your fulfillment lambda directory. Now pip install the contents of the
.tar.gz file.

```bash
pip install lex_helper-*.tar.gz
```

(Keep in mind you will need to have the package available within your deployed lambda
environment as well.)

Now within your Lex fulfillment lambda handler, reference the example handlers folder.
There are two examples, "basic" and "advanced". The basic example relies on the helper
to handle all of the Lex request/response logic, while the advanced example allows you
to maintain control of the Lex request/response logic.

- [Basic Example](./examples/basic_handler/handler.py)
- [Advanced Example](./examples/advanced_handler/handler.py)

# How do I use custom Session attributes?

Create a class that inherits from BaseSessionAttributes, in let's say,
session_attributes.py

```python
from pydantic import ConfigDict, Field

from lex_helper import SessionAttributes


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


```

Now in your main handler, here is a barebones implementation of the main handler:

```python
from typing import Any

from lex_helper import Config, LexHelper

from .session_attributes import CustomSessionAttributes


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    # We're going to customize our session attributes, you almost certainly will want to do this!
    config = Config(session_attributes=CustomSessionAttributes(), package_name="examples.basic_handler")

    # Initialize the LexHelper
    lex_helper = LexHelper(config=config)
    
    # Call the handler, this will convert the event to a LexRequest, dynamically pass it to the matching intent Python file (under "intents/")
    # and return a LexResponse.
    return lex_helper.handler(event, context)
    
```
