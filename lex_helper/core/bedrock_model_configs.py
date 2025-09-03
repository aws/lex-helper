# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Amazon Bedrock model configurations for Lex Helper.

This module provides model-specific configurations for different
Amazon Bedrock model families.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


@dataclass
class ModelConfig:
    """Configuration for a specific model family."""

    request_builder: Callable[..., dict[str, Any]]
    response_parser: Callable[[dict[str, Any]], dict[str, Any]]


class ModelFamily(Enum):
    """Supported Amazon Bedrock model families."""

    ANTHROPIC_CLAUDE = "anthropic.claude"
    AMAZON_TITAN = "amazon.titan"
    AI21_J2 = "ai21.j2"
    COHERE_COMMAND = "cohere.command"
    META_LLAMA = "meta.llama"

    @classmethod
    def from_model_id(cls, model_id: str) -> Optional["ModelFamily"]:
        """
        Get the model family from a model ID.

        Args:
            model_id: The Bedrock model identifier

        Returns:
            ModelFamily if found, None otherwise
        """
        for family in cls:
            if family.value in model_id:
                return family
        return None

    @classmethod
    def is_valid_model_id(cls, model_id: str) -> bool:
        """
        Check if a model ID belongs to a supported model family.

        Args:
            model_id: The Bedrock model identifier

        Returns:
            True if the model ID belongs to a supported family, False otherwise
        """
        return cls.from_model_id(model_id) is not None


def _anthropic_request_builder(
    prompt: str,
    max_tokens: int | None,
    temperature: float | None,
    top_p: float | None,
    stop_sequences: list[str] | None,
    **kwargs: Any,
) -> dict[str, Any]:
    return {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens or 1000,
        "anthropic_version": "bedrock-2023-05-31",
        **{
            k: v
            for k, v in {"temperature": temperature, "top_p": top_p, "stop_sequences": stop_sequences}.items()
            if v is not None
        },
        **kwargs,
    }


def _anthropic_response_parser(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "text": r.get("content", [{}])[0].get("text", ""),
        "usage": r.get("usage", {}),
        "raw_response": r,
    }


def _titan_request_builder(
    prompt: str,
    max_tokens: int | None,
    temperature: float | None,
    top_p: float | None,
    stop_sequences: list[str] | None,
    **kwargs: Any,
) -> dict[str, Any]:
    return {
        "inputText": prompt,
        "textGenerationConfig": {
            k: v
            for k, v in {
                "maxTokenCount": max_tokens,
                "temperature": temperature,
                "topP": top_p,
                "stopSequences": stop_sequences,
            }.items()
            if v is not None
        },
        **kwargs,
    }


def _titan_response_parser(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "text": r.get("results", [{}])[0].get("outputText", ""),
        "usage": r.get("inputTextTokenCount", 0) + r.get("results", [{}])[0].get("tokenCount", 0),
        "raw_response": r,
    }


def _ai21_request_builder(
    prompt: str,
    max_tokens: int | None,
    temperature: float | None,
    top_p: float | None,
    stop_sequences: list[str] | None,
    **kwargs: Any,
) -> dict[str, Any]:
    return {
        "prompt": prompt,
        **{
            k: v
            for k, v in {
                "maxTokens": max_tokens,
                "temperature": temperature,
                "topP": top_p,
                "stopSequences": stop_sequences,
            }.items()
            if v is not None
        },
        **kwargs,
    }


def _ai21_response_parser(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "text": r.get("completions", [{}])[0].get("data", {}).get("text", ""),
        "usage": r.get("prompt", {}).get("tokens", []),
        "raw_response": r,
    }


def _cohere_request_builder(
    prompt: str,
    max_tokens: int | None,
    temperature: float | None,
    top_p: float | None,
    stop_sequences: list[str] | None,
    **kwargs: Any,
) -> dict[str, Any]:
    return {
        "prompt": prompt,
        **{
            k: v
            for k, v in {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "p": top_p,
                "stop_sequences": stop_sequences,
            }.items()
            if v is not None
        },
        **kwargs,
    }


def _cohere_response_parser(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "text": r.get("generations", [{}])[0].get("text", ""),
        "usage": r.get("meta", {}),
        "raw_response": r,
    }


def _llama_request_builder(
    prompt: str,
    max_tokens: int | None,
    temperature: float | None,
    top_p: float | None,
    stop_sequences: list[str] | None,
    **kwargs: Any,
) -> dict[str, Any]:
    return {
        "prompt": prompt,
        **{
            k: v for k, v in {"max_gen_len": max_tokens, "temperature": temperature, "top_p": top_p}.items() if v is not None
        },
        **kwargs,
    }


def _llama_response_parser(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "text": r.get("generation", ""),
        "usage": r.get("prompt_token_count", 0) + r.get("generation_token_count", 0),
        "raw_response": r,
    }


# Model configurations
MODEL_CONFIGS = {
    ModelFamily.ANTHROPIC_CLAUDE: ModelConfig(
        request_builder=_anthropic_request_builder,
        response_parser=_anthropic_response_parser,
    ),
    ModelFamily.AMAZON_TITAN: ModelConfig(
        request_builder=_titan_request_builder,
        response_parser=_titan_response_parser,
    ),
    ModelFamily.AI21_J2: ModelConfig(
        request_builder=_ai21_request_builder,
        response_parser=_ai21_response_parser,
    ),
    ModelFamily.COHERE_COMMAND: ModelConfig(
        request_builder=_cohere_request_builder,
        response_parser=_cohere_response_parser,
    ),
    ModelFamily.META_LLAMA: ModelConfig(
        request_builder=_llama_request_builder,
        response_parser=_llama_response_parser,
    ),
}


def _default_request_builder(
    prompt: str,
    max_tokens: int | None,
    temperature: float | None,
    top_p: float | None,
    stop_sequences: list[str] | None,
    **kwargs: Any,
) -> dict[str, Any]:
    return {
        "prompt": prompt,
        **{
            k: v
            for k, v in {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop_sequences": stop_sequences,
            }.items()
            if v is not None
        },
        **kwargs,
    }


def _default_response_parser(r: dict[str, Any]) -> dict[str, Any]:
    return {"text": str(r), "usage": {}, "raw_response": r}


# Default model configuration
def get_default_model_config() -> ModelConfig:
    """Get default configuration for unknown models."""
    return ModelConfig(
        request_builder=_default_request_builder,
        response_parser=_default_response_parser,
    )


def get_model_config(model_id: str) -> ModelConfig:
    """
    Get configuration for a model based on its ID.

    Args:
        model_id: The Bedrock model identifier

    Returns:
        ModelConfig: Configuration for the specified model family
    """
    family = ModelFamily.from_model_id(model_id)
    if family and family in MODEL_CONFIGS:
        return MODEL_CONFIGS[family]

    # Default configuration for unknown models
    return get_default_model_config()


# Common model IDs for easy access
class BedrockModel:
    """Common Amazon Bedrock model IDs."""

    # Anthropic Claude models
    # Claude 3 models
    # Amazon Titan models
    TITAN_TEXT_LITE = "amazon.titan-text-lite-v1"
    TITAN_TEXT_EXPRESS = "amazon.titan-text-express-v1"
    TITAN_TEXT_PREMIER = "amazon.titan-text-premier-v1:0"
    TITAN_EMBEDDINGS = "amazon.titan-embed-text-v1"
    TITAN_EMBEDDINGS_V2 = "amazon.titan-embed-text-v2:0"
    TITAN_MULTIMODAL = "amazon.titan-image-generator-v1"

    # AI21 models
    JURASSIC_2_ULTRA = "ai21.j2-ultra-v1"
    JURASSIC_2_MID = "ai21.j2-mid-v1"
    JURASSIC_2_LIGHT = "ai21.j2-light-v1"
    JAMBA_INSTRUCT = "ai21.jamba-instruct-v1:0"

    # Anthropic Claude models (with inference profiles)
    CLAUDE_3_5_SONNET_V2 = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"  # Profile required
    CLAUDE_3_5_SONNET = "anthropic.claude-3-5-sonnet-20240620-v1:0"  # ON_DEMAND or Profile
    CLAUDE_3_5_HAIKU = "us.anthropic.claude-3-5-haiku-20241022-v1:0"  # Profile required
    CLAUDE_3_7_SONNET = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"  # Profile required
    CLAUDE_3_OPUS = "us.anthropic.claude-3-opus-20240229-v1:0"  # Profile required
    CLAUDE_3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"  # ON_DEMAND available
    CLAUDE_3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"  # ON_DEMAND available
    CLAUDE_OPUS_4 = "us.anthropic.claude-opus-4-20250514-v1:0"  # Profile required
    CLAUDE_OPUS_4_1 = "us.anthropic.claude-opus-4-1-20250805-v1:0"  # Profile required
    CLAUDE_SONNET_4 = "us.anthropic.claude-sonnet-4-20250514-v1:0"  # Profile required

    # Cohere models
    COMMAND = "cohere.command-text-v14"
    COMMAND_LIGHT = "cohere.command-light-text-v14"
    COMMAND_R = "cohere.command-r-v1:0"
    COMMAND_R_PLUS = "cohere.command-r-plus-v1:0"
    EMBED = "cohere.embed-english-v3"
    EMBED_MULTILINGUAL = "cohere.embed-multilingual-v3"

    # Meta models
    LLAMA_2_70B = "meta.llama2-70b-chat-v1"
    LLAMA_2_13B = "meta.llama2-13b-chat-v1"
    LLAMA_3_70B = "meta.llama3-70b-instruct-v1:0"
    LLAMA_3_8B = "meta.llama3-8b-instruct-v1:0"
    LLAMA_3_1_70B = "meta.llama3-1-70b-instruct-v1:0"
    LLAMA_3_1_8B = "meta.llama3-1-8b-instruct-v1:0"
    LLAMA_3_2_90B = "meta.llama3-2-90b-instruct-v1:0"
    LLAMA_3_2_11B = "meta.llama3-2-11b-instruct-v1:0"
    LLAMA_3_2_3B = "meta.llama3-2-3b-instruct-v1:0"
    LLAMA_3_2_1B = "meta.llama3-2-1b-instruct-v1:0"

    # Mistral AI models
    MISTRAL_7B = "mistral.mistral-7b-instruct-v0:2"
    MISTRAL_LARGE = "mistral.mistral-large-2407-v1:0"
    MISTRAL_SMALL = "mistral.mistral-small-2402-v1:0"
    MIXTRAL_8X7B = "mistral.mixtral-8x7b-instruct-v0:1"

    # Stability AI models
    STABLE_DIFFUSION_XL = "stability.stable-diffusion-xl-v1"
    STABLE_IMAGE_CORE = "stability.stable-image-core-v1:0"
    STABLE_IMAGE_ULTRA = "stability.stable-image-ultra-v1:0"

    @classmethod
    def get_all_models(cls) -> list[str]:
        """Get a list of all predefined model IDs."""
        return [value for name, value in vars(cls).items() if not name.startswith("_") and isinstance(value, str)]

    @classmethod
    def is_valid_model_id(cls, model_id: str) -> bool:
        """
        Check if a model ID is supported.

        Args:
            model_id: The Bedrock model identifier

        Returns:
            True if the model ID is supported, False otherwise
        """
        # Check if it's a predefined model ID
        if model_id in cls.get_all_models():
            return True

        # Check if it belongs to a supported model family
        return ModelFamily.is_valid_model_id(model_id)
