# Examples

This directory contains examples demonstrating various features of the lex-helper library.

## Structure

```
examples/
├── basic_handler/                   # Simple bot implementation
│   ├── intents/                     # Intent handlers
│   ├── handler.py                   # Main Lambda handler
│   └── session_attributes.py        # Session state management
├── features/                        # Feature-specific examples
│   ├── bedrock/                     # Amazon Bedrock integration
│   │   ├── bedrock_example.py       # Usage examples
│   │   └── README.md                # Documentation
│   └── messages/                    # Localized message management
│       ├── message_manager_example.py
│       ├── messages.yaml            # Default messages
│       ├── messages_es_ES.yaml      # Spanish messages
│       └── README.md                # Documentation
├── sample_airline_bot/              # Comprehensive airline bot
│   ├── lambdas/                     # Lambda functions
│   ├── lex-export/                  # Lex bot definition
│   ├── lib/                         # CDK infrastructure
│   └── docs/                        # Documentation
└── __init__.py
```

## Getting Started

1. **Basic Handler**: Start with `basic_handler/` for simple bot patterns
2. **Feature Examples**: Explore `features/` for specific functionality
3. **Complete Implementation**: Study `sample_airline_bot/` for production patterns

## Feature Examples

- **[Bedrock Integration](features/bedrock/)**: AI-powered responses using Amazon Bedrock
- **[Message Management](features/messages/)**: Localized message handling with YAML configuration

## Sample Airline Bot

The `sample_airline_bot/` provides a comprehensive example with:
- Authentication flows
- Multi-turn conversations
- Airport resolution with Bedrock
- CDK deployment
- Integration tests

See the [airline bot README](sample_airline_bot/README.md) for detailed documentation.