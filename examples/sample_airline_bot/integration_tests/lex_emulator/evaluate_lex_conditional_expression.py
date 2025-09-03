# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from typing import Any


def evaluate_lex_conditional_expression(expression: str, slot_values: dict[str, Any]):
    expression = expression.replace("AND", "and").replace("OR", "or").replace("NOT", "not")
    expression = expression.replace("{", 'slot_values.get("')
    expression = expression.replace("}", '", {}).get("value", {}).get("interpretedValue", None)')
    expression = expression.replace("=", " == ")
    evaluated = eval(expression)
    return evaluated
