"""
Amazon Bedrock invocation utilities for Lex Helper.

This module provides functionality to invoke Amazon Bedrock models
with proper error handling and response formatting.
"""

import json
import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError

# Import from bedrock_model_configs
from .bedrock_model_configs import get_model_config

logger = logging.getLogger(__name__)


class BedrockInvocationError(Exception):
    """Custom exception for Bedrock invocation errors."""

    pass


def invoke_bedrock(
    prompt: str,
    model_id: str,
    max_tokens: int | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    stop_sequences: list[str] | None = None,
    region_name: str = "us-east-1",
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Invoke Bedrock model using InvokeModel API.

    Args:
        prompt: Input prompt
        model_id: Bedrock model identifier
        max_tokens: Maximum tokens to generate
        temperature: Randomness control (0.0-1.0)
        top_p: Nucleus sampling (0.0-1.0)
        stop_sequences: Stop generation sequences
        region_name: AWS region
        **kwargs: Additional model parameters

    Returns:
        Dict with text, usage, raw_response
    """
    try:
        bedrock_runtime = boto3.client("bedrock-runtime", region_name=region_name)

        config = get_model_config(model_id)
        request_body = config.request_builder(prompt, max_tokens, temperature, top_p, stop_sequences, **kwargs)

        response = _try_with_fallback(
            bedrock_runtime,
            model_id,
            lambda mid: bedrock_runtime.invoke_model(
                modelId=mid, body=json.dumps(request_body), contentType="application/json", accept="application/json"
            ),
        )

        response_body = json.loads(response["body"].read())
        return config.response_parser(response_body)

    except Exception as e:
        logger.error(f"Bedrock invocation failed: {e}")
        raise BedrockInvocationError(f"Invocation failed: {e}") from e


def invoke_bedrock_converse(
    messages: list[dict[str, Any]],
    model_id: str,
    max_tokens: int | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    stop_sequences: list[str] | None = None,
    system_prompt: str | None = None,
    region_name: str = "us-east-1",
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Invoke Bedrock model using Converse API with full message support.

    Args:
        messages: List of message dicts with role and content
        model_id: Bedrock model identifier
        max_tokens: Maximum tokens to generate
        temperature: Randomness control (0.0-1.0)
        top_p: Nucleus sampling (0.0-1.0)
        stop_sequences: Stop generation sequences
        system_prompt: System prompt for conversation
        region_name: AWS region
        **kwargs: Additional parameters

    Returns:
        Dict with text, usage, raw_response

    Example:
        >>> messages = [
        ...     {"role": "user", "content": [{"text": "Hello"}]},
        ...     {"role": "assistant", "content": [{"text": "Hi there!"}]},
        ...     {"role": "user", "content": [{"text": "How are you?"}]}
        ... ]
        >>> response = invoke_bedrock_converse(
        ...     messages=messages,
        ...     model_id="anthropic.claude-3-haiku-20240307-v1:0",
        ...     system_prompt="You are a helpful assistant"
        ... )
    """
    try:
        bedrock_runtime = boto3.client("bedrock-runtime", region_name=region_name)

        inference_config = {
            k: v
            for k, v in {
                "maxTokens": max_tokens or 1000,
                "temperature": temperature,
                "topP": top_p,
                "stopSequences": stop_sequences,
            }.items()
            if v is not None
        }

        converse_params = {"messages": messages, "inferenceConfig": inference_config, **kwargs}

        if system_prompt:
            converse_params["system"] = [{"text": system_prompt}]

        response = _try_with_fallback(
            bedrock_runtime, model_id, lambda mid: bedrock_runtime.converse(modelId=mid, **converse_params)
        )

        return {
            "text": response["output"]["message"]["content"][0]["text"],
            "usage": response.get("usage", {}),
            "raw_response": response,
        }

    except Exception as e:
        logger.error(f"Bedrock converse failed: {e}")
        raise BedrockInvocationError(f"Converse failed: {e}") from e


def invoke_bedrock_simple_converse(
    prompt: str,
    model_id: str,
    max_tokens: int | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    stop_sequences: list[str] | None = None,
    system_prompt: str | None = None,
    region_name: str = "us-east-1",
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Simple converse wrapper that converts prompt to messages format.

    Args:
        prompt: Single user prompt
        model_id: Bedrock model identifier
        system_prompt: System prompt for conversation
        (other args same as invoke_bedrock_converse)

    Returns:
        Dict with text, usage, raw_response
    """
    messages = [{"role": "user", "content": [{"text": prompt}]}]

    return invoke_bedrock_converse(
        messages=messages,
        model_id=model_id,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stop_sequences=stop_sequences,
        system_prompt=system_prompt,
        region_name=region_name,
        **kwargs,
    )


def _try_with_fallback(bedrock_runtime, model_id: str, invoke_func):
    """Try invocation with fallback to inference profile if needed."""
    try:
        return invoke_func(model_id)
    except ClientError as e:
        if "on-demand throughput isn" in str(e) and not model_id.startswith("us."):
            logger.info(f"Trying inference profile for {model_id}")
            return invoke_func(f"us.{model_id}")
        raise e
