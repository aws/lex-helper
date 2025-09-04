# Lex Helper Development Tools

This directory contains powerful CLI tools for managing Amazon Lex bots and keeping your local development environment in sync with AWS.

## Overview

**lexcli** is the main command-line interface that orchestrates bot management workflows. It uses helper modules to provide a seamless development experience for Lex bot projects.

## Tool Architecture

```
lexcli.py (Main CLI Interface)
├── export command
│   ├── bot_export_helpers.py → AWS Lex V2 API operations
│   └── regenerate_enums.py → Generate type-safe Python enums
└── ping command → boto3 → Real-time bot health monitoring
```

## Core Tools

### 🚀 lexcli.py - Main CLI Interface

**Purpose**: High-level command-line tool for bot development workflows

**Commands**:
- `export <env>` - Sync AWS bot configuration to local files
- `ping <bot_id> <alias_id>` - Monitor bot health in real-time

### 🔧 bot_export_helpers.py - AWS API Wrapper

**Purpose**: Internal module providing AWS Lex V2 API operations

**Key Functions**:
- `bot_start_export()` - Initiate bot export from AWS
- `wait_on_export()` - Wait for export completion
- `get_export_url()` - Download bot configuration
- `list_bots()` - Find bots by name
- `delete_bot_export()` - Cleanup export jobs

### 📝 regenerate_enums.py - Type Safety Generator

**Purpose**: Generate Python enums from Lex bot structure for type safety

**What it generates**:
- **Slot Enums**: One enum per intent containing all slot names
- **Intent Enum**: Single enum with all intent names
- **Union Types**: Combined types for type checking
- **Lookup Dictionaries**: Runtime slot class resolution

### 📊 ping command - Bot Health Monitor

**Purpose**: Real-time monitoring of deployed Lex bots

**What it does**:
- Sends test messages to bot every second
- Reports UP/DOWN status with timestamps
- Logs results to `status-of-bot.txt`
- Uses boto3 directly (no dependency on other tools)

## How lexcli Export Works

### 1. **Bot Discovery & Export**
```bash
python lexcli.py export dev
```

**Process**:
1. Finds bot named `devLexBot` in AWS using `bot_export_helpers`
2. Initiates export and downloads JSON configuration
3. Extracts bot files to temporary directory

### 2. **Intelligent Sync**

**Compares** exported bot with local `lex-export/` directory:
- **New intents/slots**: Automatically added to local files
- **Modified intents/slots**: Interactive conflict resolution
- **Deleted intents/slots**: User confirmation before removal

### 3. **Type Safety Generation**

**Generates** Python enums in `lambdas/fulfillment_function/src/fulfillment_function/classes/`:

```python
# slot_enums.py (auto-generated)
class BookFlightSlot(Enum):
    ORIGINCITY = "OriginCity"
    DESTINATIONCITY = "DestinationCity"
    DEPARTUREDATE = "DepartureDate"
    # ... more slots

# intent_name.py (auto-generated)
class IntentName(Enum):
    BOOK_FLIGHT = "book_flight"
    CANCEL_FLIGHT = "cancel_flight"
    # ... more intents
```

## Why This Matters

### 🎯 **Development Workflow Benefits**

1. **Version Control**: Bot configurations stored as readable JSON files
2. **Team Collaboration**: Share bot changes through git commits
3. **Environment Sync**: Keep dev/staging/prod bots in sync
4. **Change Tracking**: See exactly what changed in bot configuration

### 🛡️ **Type Safety Benefits**

```python
# Before: Error-prone string literals
slot_value = get_slot("OriginCity")  # Typo risk!

# After: Type-safe enum usage
slot_value = get_slot(BookFlightSlot.ORIGINCITY)  # IDE autocomplete + validation
```

### 📊 **Monitoring Benefits**

```bash
# Real-time bot health monitoring
python lexcli.py ping <BOT_ID> <ALIAS_ID>
# 2024-01-15 10:30:15: Bot is UP
# 2024-01-15 10:30:16: Bot is UP
```

## Usage Examples

### Export Bot Configuration
```bash
# Export from default project location
python lexcli.py export dev

# Export from custom project location
python lexcli.py export prod --project-root /path/to/project
```

### Monitor Bot Health
```bash
# Continuous monitoring (Ctrl+C to stop)
python lexcli.py ping <BOT_ID> <ALIAS_ID>

# Check log file
tail -f status-of-bot.txt
```

### Standalone Enum Generation
```bash
# Generate enums from existing bot files
python regenerate_enums.py
```

## Installation

```bash
cd tools

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Prerequisites

- **AWS Credentials**: `ada credentials update --account=<account> --role=<role>`
- **Bot Deployed**: Target bot must exist in AWS Lex
- **Project Structure**: Must run from project with `lex-export/` and `lambdas/` directories
- **Permissions**: Lex read/export permissions, Bedrock access (for runtime testing)

## Generated Files

The export process creates/updates:

```
project/
├── lex-export/LexBot/BotLocales/en_US/
│   ├── Intents/           # Intent definitions
│   └── SlotTypes/         # Slot type definitions
└── lambdas/fulfillment_function/src/fulfillment_function/classes/
    ├── slot_enums.py      # Type-safe slot enums
    └── intent_name.py     # Type-safe intent enum
```

## Troubleshooting

**"No such file or directory"**: Ensure you're running from correct directory with `--project-root`

**"Bot not found"**: Check bot name follows pattern `{environment}LexBot` (e.g., `devLexBot`)

**"Permission denied"**: Verify AWS credentials and Lex permissions