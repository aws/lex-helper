<h2 align="center">Lex Helper Library</h2>

<p align="center">
<a href="https://github.com/aws/lex-helper/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/aws/lex-helper/actions/workflows/ci.yml/badge.svg"></a>
<a href="https://pypi.org/project/lex-helper/"><img alt="PyPI version" src="https://badge.fury.io/py/lex-helper.svg"></a>
<a href="https://pypi.org/project/lex-helper/"><img alt="Python versions" src="https://img.shields.io/pypi/pyversions/lex-helper.svg"></a>
<a href="https://pepy.tech/project/lex-helper"><img alt="Downloads" src="https://pepy.tech/badge/lex-helper"></a>
<a href="LICENSE"><img alt="License: Apache 2.0" src="https://img.shields.io/badge/License-Apache%202.0-blue.svg"></a>
<a href="https://github.com/astral-sh/ruff"><img alt="Code style: ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"></a>
<a href="https://github.com/aws/lex-helper"><img alt="GitHub stars" src="https://img.shields.io/github/stars/aws/lex-helper.svg?style=social&label=Star"></a>
</p>

<p align="center">
<strong>A modern, type-safe Python library for building Amazon Lex chatbots with ease</strong>
</p>

The Lex Helper library is an extensive collection of functions and classes that make it easier to work with Lex. It's designed to make building Lex fulfillment lambdas easier, more efficient, understandable, and consistent. Gone are the days of accidentally mistyping a slot name, using a dictionary within a dictionary within a dictionary, or not being able to find where the code for a specific intent is.

## Table of Contents

- [Why Use Lex Helper?](#why-use-lex-helper)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [1. Create Session Attributes](#1-create-session-attributes)
  - [2. Create Main Handler](#2-create-main-handler)
  - [3. Create Intent Handlers](#3-create-intent-handlers)
- [Core Features](#core-features)
  - [Dialog Utilities](#dialog-utilities)
  - [Message Management](#message-management)
  - [Smart Disambiguation](#smart-disambiguation)
  - [Bedrock Integration](#bedrock-integration)
- [Bedrock Usage Examples](#bedrock-usage-examples)
  - [Basic InvokeModel API](#basic-invokemodel-api)
  - [Converse API with System Prompt](#converse-api-with-system-prompt)
- [Smart Disambiguation](#smart-disambiguation-1)
  - [Basic Setup](#basic-setup)
  - [AI-Powered Disambiguation](#ai-powered-disambiguation)
  - [Example Interaction](#example-interaction)
- [Examples](#examples)
- [Documentation](#documentation)
- [Development Setup](#development-setup)
  - [Prerequisites](#prerequisites)
  - [Quick Setup](#quick-setup)
  - [Development Commands](#development-commands)

## Why Use Lex Helper?

- **Simplified Intent Management**: Each intent's logic lives in its own file under an `intents/` directory, making it easy to locate, maintain, and scale your bot's capabilities without navigating complex nested handlers. The library will dynamically load the intent handler based on the intent name.

![Intent Handling](docs/intent-handling.png)

- **Type-Safe Session Attributes**: Define your session attributes as a Pydantic model, eliminating runtime errors from typos or incorrect data types. Get full IDE autocomplete support and catch errors before they reach production.

![Intellisense](docs/intellisense.png)

- **Automatic Request/Response Handling**: Stop wrestling with deeply nested dictionaries. The library handles all the Lex request/response formatting, letting you focus on your bot's business logic.

- **Channel-Aware Formatting**: Built-in support for different channels (SMS, Lex console, etc.) ensures your responses are properly formatted regardless of how users interact with your bot.

- **Error Handling Made Easy**: Comprehensive exception handling and error reporting help you quickly identify and fix issues in your fulfillment logic.

- **Reduced Boilerplate**: Common Lex operations like transitioning between intents, handling dialog states, and managing session attributes are simplified into clean, intuitive methods.

- **Smart Disambiguation**: Automatically handle ambiguous user input with intelligent clarification prompts. Optional AI-powered responses using Amazon Bedrock create natural, contextual disambiguation messages that improve user experience.

- **Developer Experience**: Get the benefits of modern Python features like type hints, making your code more maintainable and easier to understand. Full IDE support means better autocomplete and fewer runtime errors.

## Installation

```bash
pip install lex-helper
```

For Lambda deployment, see [Lambda Layer Deployment Guide](docs/LAMBDA_LAYER_DEPLOYMENT.md).

## Development Setup

This project uses modern Python tooling for development:

### Prerequisites
- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) for dependency management

### Quick Setup
```bash
# Install uv (if not already installed)
pip install uv

# Clone the repository and install dependencies
git clone <repository-url>
cd lex-helper
uv sync --dev

# Install pre-commit hooks for code quality
uv run pre-commit install
```

### Development Commands
```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=lex_helper

# Code linting and formatting
uv run ruff check .          # Check for issues
uv run ruff check --fix .    # Fix issues automatically
uv run ruff format .         # Format code

# Type checking
pyright

# Run all quality checks
uv run pre-commit run --all-files
```

For detailed migration information from older tooling, see the [Migration Guide](docs/MIGRATION_GUIDE.md).

## Quick Start

### 1. Create Session Attributes

```python
from pydantic import ConfigDict, Field
from lex_helper import SessionAttributes

class CustomSessionAttributes(SessionAttributes):
    model_config = ConfigDict(extra="allow")
    user_name: str = Field(default="", description="User's name")
    visit_count: int = Field(default=0, description="Number of visits")
```

### 2. Create Main Handler

```python
from typing import Any
from lex_helper import Config, LexHelper
from .session_attributes import CustomSessionAttributes

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    config = Config(
        session_attributes=CustomSessionAttributes(),
        package_name="your_project.intents"
    )
    lex_helper = LexHelper(config=config)
    return lex_helper.handler(event, context)
```

### 3. Create Intent Handlers

Structure your intents in an `intents/` directory:

```
your_project/
├── intents/
│   ├── __init__.py
│   ├── welcome_intent.py
│   └── booking_intent.py
├── session_attributes.py
└── handler.py
```

## Core Features

### Dialog Utilities
- **get_intent**, **get_slot**, **set_slot**: Manage intent and slot data
- **elicit_intent**, **elicit_slot**, **delegate**: Control dialog flow
- **close**: Complete dialog interactions
- **transition_to_intent**: Navigate between intents
- **any_unknown_slot_choices**, **handle_any_unknown_slot_choice**: Handle invalid inputs
- **get_active_contexts**, **remove_context**: Manage conversation context
- **load_messages**: Parse message data

### Message Management
- **MessageManager**: Centralized message management with locale support
- **get_message**, **set_locale**: Load and retrieve localized messages from YAML files
- Supports `messages_{localeId}.yaml` files (e.g., `messages_en_US.yaml`, `messages_es_ES.yaml`)
- Automatic fallback to `messages.yaml` for missing locales

### Smart Disambiguation
- **Intelligent Intent Resolution**: Automatically detects ambiguous user input and presents clarifying options
- **AI-Powered Responses**: Optional Bedrock integration for contextual, natural language disambiguation messages
- **Configurable Thresholds**: Fine-tune when disambiguation triggers based on confidence scores and similarity
- **Multi-Selection Support**: Users can choose via text, numbers, letters, or button clicks
- **Graceful Fallbacks**: Seamless fallback to static messages if AI services are unavailable

### Bedrock Integration
- **invoke_bedrock**: Direct integration with Amazon Bedrock models
- Supports multiple model families (Claude, Titan, Jurassic, Cohere, Llama)
- Automatic fallback between on-demand and inference profile modes
- **Converse API**: Unified interface for model interactions with system prompt support
- **InvokeModel API**: Traditional model invocation (default behavior)

## Documentation

**Recommended Reading Order:**
1. **[Best Practices Guide](docs/BEST_PRACTICES.md)**: Start here for detailed usage patterns, advanced examples, and code organization
2. **[Testing Guide](docs/TESTING_GUIDE.md)**: Then learn comprehensive testing strategies for your Lex bots
3. **[Lambda Layer Deployment](docs/LAMBDA_LAYER_DEPLOYMENT.md)**: Finally, deploy as Lambda layers for better performance

**Development Documentation:**
- **[Development Guide](docs/DEVELOPMENT.md)**: Complete development workflow, testing, and contribution guidelines

## Bedrock Usage Examples

### Basic InvokeModel API
```python
from lex_helper import invoke_bedrock

response = invoke_bedrock(
    prompt="What are the airports in Los Angeles?",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    max_tokens=200,
    temperature=0.1
)
print(response['text'])
```

### Converse API with System Prompt
```python
response = invoke_bedrock(
    prompt="What are the airports in Los Angeles?",
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    max_tokens=200,
    temperature=0.1,
    use_converse=True,
    system_prompt="You are a travel expert. Provide accurate airport information."
)
print(response['text'])
```

## Smart Disambiguation

Handle ambiguous user input intelligently with automatic clarification prompts:

### Basic Setup
```python
from lex_helper import Config, LexHelper
from lex_helper.core.disambiguation.types import DisambiguationConfig

# Enable disambiguation with default settings
config = Config(
    session_attributes=CustomSessionAttributes(),
    enable_disambiguation=True,
    disambiguation_config=DisambiguationConfig(
        confidence_threshold=0.5,  # Trigger when confidence < 50%
        max_candidates=2,          # Show up to 2 options
    )
)
```

### AI-Powered Disambiguation
```python
from lex_helper.core.disambiguation.types import BedrockDisambiguationConfig

# Enable Bedrock for intelligent, contextual responses
bedrock_config = BedrockDisambiguationConfig(
    enabled=True,
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    system_prompt="You are a helpful assistant that creates clear, "
                 "friendly disambiguation messages for users."
)

disambiguation_config = DisambiguationConfig(
    confidence_threshold=0.5,
    bedrock_config=bedrock_config,  # AI-powered responses
)
```

### Example Interaction
```
User: "I need help with my booking"

Static Response:
"I can help you with several things. What would you like to do?"
Buttons: ["Book Flight", "Change Flight", "Cancel Flight"]

AI-Powered Response:
"I'd be happy to help with your booking! Are you looking to make
changes to an existing reservation or book a new flight?"
Buttons: ["Modify existing booking", "Book new flight"]
```

For detailed configuration options, see [Smart Disambiguation Documentation](docs/smart-disambiguation.md).

## Examples

- **Basic Example**: See `examples/basic_handler/` for a simple implementation
- **Comprehensive Example**: For production-ready patterns, see the documentation for:
  - Advanced intent organization and management
  - Complex session attribute handling
  - Multi-turn conversation flows
  - Error handling and fallback strategies
  - Best practices for bot architecture
  - Production deployment patterns
