# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import importlib
import inspect
import logging
from typing import TypeVar

from lex_helper.core.types import LexRequest, LexResponse, SessionAttributes
from lex_helper.exceptions.handlers import IntentNotFoundError, handle_exceptions
from lex_helper.utils.string import title_to_snake

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=SessionAttributes)


def call_handler_for_file(intent_name: str, lex_request: LexRequest[T], package_name: str | None = None) -> LexResponse[T]:
    if package_name is None:
        package_name = "fulfillment_function"
    # Determine the file to import based on intent_name
    logger.debug("Calling handler for %s", intent_name)

    if "_" in intent_name:
        file_to_import = intent_name.lower()
    else:
        file_to_import = title_to_snake(intent_name)

    # Prepend the module path with 'fulfillment_function.'
    file_to_import = f"{package_name}.intents.{file_to_import}"

    try:
        module = importlib.import_module(file_to_import)
    except ImportError as e:
        logger.exception('Error: Import module %s failed due to the error "%s"', file_to_import, e)
        raise IntentNotFoundError("Unable to find handler for intent") from e

    # Get the "handler" function from the module
    if hasattr(module, "handler") and inspect.isfunction(module.handler):
        handler_func = module.handler
    else:
        logger.error("Error: Unable to load handler, %s.py does not have a 'handler' function.", file_to_import)
        raise ValueError(f"Error: Unable to load handler, {file_to_import}.py does not have a 'handler' function.")

    # Call the "handler" function with event and context arguments
    try:
        return handler_func(lex_request)
    except Exception as e:
        return handle_exceptions(e, lex_request)
