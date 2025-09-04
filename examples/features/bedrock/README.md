# Bedrock Integration Example

This example demonstrates how to use Amazon Bedrock with the lex-helper library.

## Features

- **InvokeModel API**: Traditional model invocation
- **Converse API**: Unified interface with system prompt support
- **Multiple Models**: Claude, Titan, Jurassic, Cohere, Llama support
- **Automatic Fallback**: Between on-demand and inference profile modes

## Usage

```python
from lex_helper import invoke_bedrock

# Basic InvokeModel API
response = invoke_bedrock(
    prompt="What are the airports in Los Angeles?",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    max_tokens=200,
    temperature=0.1
)

# Converse API with system prompt
response = invoke_bedrock(
    prompt="What are the airports in Los Angeles?",
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    max_tokens=200,
    temperature=0.1,
    use_converse=True,
    system_prompt="You are a travel expert."
)
```

## Running the Example

```bash
python bedrock_example.py
```

## Prerequisites

- AWS credentials with Bedrock permissions
- Access to Bedrock models in your region
