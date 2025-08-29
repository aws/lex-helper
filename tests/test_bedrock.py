#!/usr/bin/env python3
"""
Test script for invoke_bedrock functionality.
"""

import argparse
import logging
import os
import sys

# Add the parent directory to Python path to import from local development version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lex_helper.core.invoke_bedrock import BedrockInvocationError, invoke_bedrock


def test_bedrock_invoke(model_id: str, debug: bool = False, use_converse: bool = False):
    """Test Bedrock invocation with specified model."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    
    prompt = "translate the city name of Los Angeles to its airport name and IATA code. If multiple airports, provide the comprehensive list. Package response in a json"
    api_type = "Converse API" if use_converse else "InvokeModel API"
    
    try:
        print(f"Testing Bedrock with model: {model_id} using {api_type}")
        print(f"Prompt: {prompt}")
        print("-" * 50)
        
        response = invoke_bedrock(
            prompt=prompt,
            model_id=model_id,
            max_tokens=200,
            temperature=0.1,
            use_converse=use_converse
        )
        
        print("Response received:")
        print(f"Text: {response['text']}")
        print(f"Usage: {response['usage']}")
        print("-" * 50)
        print("Test completed successfully!")
        
    except BedrockInvocationError as e:
        print(f"Bedrock error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def example_converse_api():
    """Example of using Converse API with system prompt."""
    print("Example: Converse API with System Prompt")
    print("=" * 50)
    
    system_prompt = """
You are an expert travel assistant with comprehensive knowledge of airports worldwide.
Provide accurate information about airport codes, names, and locations.
"""
    
    try:
        response = invoke_bedrock(
            prompt="What are the main airports in Los Angeles with their IATA codes?",
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
            max_tokens=150,
            temperature=0.1,
            use_converse=True,
            system_prompt=system_prompt
        )
        
        print("Converse API with System Prompt:")
        print(f"Response: {response['text']}")
        print(f"Usage: {response['usage']}")
        
    except BedrockInvocationError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Bedrock invocation")
    parser.add_argument(
        "--model", 
        default="anthropic.claude-3-sonnet-20240229-v1:0",
        help="Model ID to test (default: Claude 3 Sonnet)"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--converse",
        action="store_true",
        help="Use Converse API instead of InvokeModel API"
    )

    
    parser.add_argument(
        "--example",
        action="store_true",
        help="Run the converse API with caching example"
    )
    
    args = parser.parse_args()
    
    if args.example:
        example_converse_api()
    else:
        test_bedrock_invoke(args.model, args.debug, args.converse)