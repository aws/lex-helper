#!/usr/bin/env python3
"""
Example usage of invoke_bedrock with both InvokeModel and Converse APIs.
"""

from lex_helper import BedrockInvocationError, invoke_bedrock


def example_invoke_model():
    """Example using the traditional InvokeModel API."""
    print("=== InvokeModel API Example ===")
    
    try:
        response = invoke_bedrock(
            prompt="List the major airports in New York with their IATA codes.",
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            max_tokens=150,
            temperature=0.1
        )
        
        print(f"Response: {response['text']}")
        print(f"Usage: {response['usage']}")
        
    except BedrockInvocationError as e:
        print(f"Error: {e}")


def example_converse_api():
    """Example using the Converse API with system prompt."""
    print("\n=== Converse API Example ===")
    
    system_prompt = """
    You are a helpful travel assistant. Provide accurate information about airports,
    including IATA codes, locations, and brief descriptions. Format responses clearly.
    """
    
    try:
        response = invoke_bedrock(
            prompt="What are the main airports serving the San Francisco Bay Area?",
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
            max_tokens=200,
            temperature=0.1,
            use_converse=True,
            system_prompt=system_prompt
        )
        
        print(f"Response: {response['text']}")
        print(f"Usage: {response['usage']}")
        
    except BedrockInvocationError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    example_invoke_model()
    example_converse_api()