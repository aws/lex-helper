#!/usr/bin/env python3
"""
Test script for invoke_bedrock functionality.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from lex_helper.core.invoke_bedrock import BedrockInvocationError, invoke_bedrock, invoke_bedrock_simple_converse


def test_bedrock_invoke_mock():
    """Test Bedrock invocation with mocked responses."""
    prompt = "translate the city name of Los Angeles to its airport name and IATA code"
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

    mock_response_body = {
        "content": [{"text": "Los Angeles International Airport (LAX)"}],
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }

    with patch("lex_helper.core.invoke_bedrock.boto3.client") as mock_client:
        mock_bedrock = MagicMock()
        mock_client.return_value = mock_bedrock

        mock_bedrock.invoke_model.return_value = {"body": MagicMock()}
        mock_bedrock.invoke_model.return_value["body"].read.return_value = json.dumps(mock_response_body).encode()

        response = invoke_bedrock(prompt=prompt, model_id=model_id, max_tokens=200, temperature=0.1)

        assert "text" in response
        assert "usage" in response
        assert response["text"] == "Los Angeles International Airport (LAX)"


def test_bedrock_converse_mock():
    """Test Bedrock converse invocation with mocked responses."""
    prompt = "translate the city name of Los Angeles to its airport name and IATA code"
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

    mock_response = {
        "output": {"message": {"content": [{"text": "Los Angeles International Airport (LAX)"}]}},
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }

    with patch("lex_helper.core.invoke_bedrock.boto3.client") as mock_client:
        mock_bedrock = MagicMock()
        mock_client.return_value = mock_bedrock
        mock_bedrock.converse.return_value = mock_response

        response = invoke_bedrock_simple_converse(prompt=prompt, model_id=model_id, max_tokens=200, temperature=0.1)

        assert "text" in response
        assert "usage" in response
        assert response["text"] == "Los Angeles International Airport (LAX)"


def test_bedrock_error_handling():
    """Test Bedrock error handling."""
    with patch("lex_helper.core.invoke_bedrock.boto3.client") as mock_client:
        mock_bedrock = MagicMock()
        mock_client.return_value = mock_bedrock
        mock_bedrock.invoke_model.side_effect = Exception("AWS Error")

        with pytest.raises(BedrockInvocationError):
            invoke_bedrock(prompt="test", model_id="anthropic.claude-3-sonnet-20240229-v1:0", max_tokens=100)
