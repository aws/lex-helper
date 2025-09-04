# Architecture Overview

## Components

### CDK Infrastructure (`lib/`)
- **lex-at-scale-stack.ts**: Main CDK stack defining Lambda, Lex bot, IAM roles, and CloudWatch logs

### Lambda Function (`lambdas/fulfillment_function/`)
- **lambda_function.py**: Entry point and request router
- **session_attributes.py**: Pydantic models for session state
- **intents/**: Intent handlers (book_flight, authenticate, etc.)
- **utils/**: Shared utilities (reservation_utils, enums)

### Lex Bot (`lex-export/`)
- Bot definition, intents, slots, and utterances

## Key Features

### Authentication Flow
- Users must authenticate before booking flights
- Callback mechanism returns to original intent after auth

### Airport Resolution
- Bedrock-powered city-to-IATA code conversion
- Multi-airport city support (e.g., Paris: CDG/ORY)
- Handles ambiguous city names with user selection

### Session Management
- Persistent user data across conversation turns
- Type-safe session attributes with Pydantic

### Type Safety
- **Auto-generated Enums**: Intent and slot enums created from bot structure
- **Slot Enums**: Per-intent enums (e.g., `BookFlightSlot.ORIGINCITY`)
- **Intent Enum**: All intents in `IntentName` enum
- **IDE Support**: Full autocomplete and compile-time validation
- **Generated Location**: `lambdas/fulfillment_function/src/fulfillment_function/classes/`
- **Generation Method**: Created by `lexcli export` command using `regenerate_enums.py`
- **Documentation**: See [tools/README.md](../../tools/README.md) for lexcli usage

## Permissions

### Lambda IAM Role
- CloudWatch Logs: Create/write log streams
- Bedrock: InvokeModel and Converse operations

### Lex IAM Role
- Polly: Speech synthesis
- CloudWatch Logs: Conversation logging
