# API Reference

Welcome to the comprehensive API reference for lex-helper. This documentation is automatically generated from the codebase and includes complete type information, parameter details, and usage examples.

## Overview

The lex-helper library is organized into several key modules, each serving a specific purpose in building Amazon Lex chatbots:

- **[Core](core.md)** - Main handler classes, dialog utilities, and core functionality
- **[Channels](channels.md)** - Channel-specific formatting for SMS, web, and voice interfaces  
- **[Formatters](formatters.md)** - Message formatting utilities and text processing helpers
- **[Exceptions](exceptions.md)** - Custom exceptions and error handling utilities

## Quick Reference

### Main Entry Point

The primary class you'll work with is [`LexHelper`](core.md#lex_helper.core.handler.LexHelper), which provides the main handler for processing Lex requests:

```python
from lex_helper import LexHelper, Config, SessionAttributes

class MySessionAttributes(SessionAttributes):
    user_name: str = ""

config = Config(session_attributes=MySessionAttributes())
lex_helper = LexHelper(config)

# Use as Lambda handler
def lambda_handler(event, context):
    return lex_helper.handler(event, context)
```

### Key Utilities

- **[Dialog Functions](core.md#dialog-utilities)** - Manage dialog state and responses
- **[Session Management](core.md#session-management)** - Type-safe session attributes
- **[Message Formatting](formatters.md)** - Format messages for different channels
- **[Smart Disambiguation](core.md#disambiguation)** - AI-powered intent disambiguation

## Navigation Tips

- **Search**: Use the search function (Ctrl+K) to quickly find specific APIs
- **Type Information**: All functions include complete type hints and parameter descriptions
- **Source Code**: Click the source link on any item to view the implementation
- **Cross-References**: Related functions and classes are automatically linked
- **Examples**: Most functions include usage examples in their documentation

## Module Organization

```
lex_helper/
├── core/           # Core functionality and main handler
├── channels/       # Channel-specific formatting
├── formatters/     # Text and message formatting utilities
├── exceptions/     # Custom exceptions and error handling
└── utils/          # General utility functions
```

## Getting Started

If you're new to lex-helper, we recommend starting with:

1. **[Installation Guide](../getting-started/installation.md)** - Set up lex-helper in your project
2. **[Quick Start](../getting-started/quick-start.md)** - Build your first chatbot in 5 minutes
3. **[Core Concepts](../guides/core-concepts.md)** - Understand the key concepts and architecture
4. **[Your First Chatbot](../getting-started/first-chatbot.md)** - Complete tutorial with explanations

Then return here for detailed API information as you build more complex chatbots.

## API Stability

All public APIs documented here follow semantic versioning. Breaking changes are clearly documented in the [changelog](../community/changelog.md) and [migration guides](../migration/version-upgrades.md).

---

**Next**: Explore the [Core API](core.md) to understand the main handler and dialog utilities.