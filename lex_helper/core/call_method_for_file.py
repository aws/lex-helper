# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import importlib
import inspect
from typing import TypeVar

from loguru import logger

from lex_helper.core.types import LexRequest, SessionAttributes
from lex_helper.utils.string import title_to_snake

T = TypeVar("T", bound=SessionAttributes)


def call_method_for_file(intent_name: str, lex_request: LexRequest[T], method: str):
    # Determine the file to import based on intent_name
    if "_" in intent_name:
        file_to_import = intent_name.lower()
    else:
        file_to_import = title_to_snake(intent_name)

    try:
        module = importlib.import_module(file_to_import)
    except ImportError as e:
        logger.exception(f'Error: Import module {file_to_import} failed due to the error "{e}"')
        raise e

    # Get the "prompt" function from the module
    if hasattr(module, method) and inspect.isfunction(module.method):
        prompt_func = module.method
    else:
        logger.error(f"Error: Unable to load handler, {file_to_import}.py does not have a 'handler' function.")
        raise ValueError(f"Error: Unable to load handler, {file_to_import}.py does not have a 'handler' function.")

    # Call the "handler" function with event and context arguments
    return prompt_func(lex_request)
