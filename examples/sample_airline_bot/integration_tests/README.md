# Integration Tests for Sample Airline Bot

This directory contains integration tests for the sample airline bot, including a Lex emulator for testing bot flows without deploying to AWS.

## Overview

The integration tests include:
- **Lex Emulator**: A local emulator that simulates AWS Lex behavior using exported bot configuration
- **Intent Validation Tests**: Tests to ensure all intents have proper sample utterances
- **Slot Type Tests**: Tests to validate slot type usage and prevent unused slot types
- **Flow Validation Tests**: Tests that validate complete conversation flows

## Important Notes

⚠️ **The Lex emulator reads data from the `lex-export` directory** to behave like Lex. If you have updated the flow within the Lex UI but have NOT exported it locally, the emulator will NOT have those changes.

## Setup

### Quick Setup (Recommended)
Run the setup script to automatically configure everything:
```bash
./setup.sh
```

### Manual Setup
1. Create a virtual environment with uv:
   ```bash
   uv venv
   ```

2. Install the required dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Install lex-helper in editable mode:
   ```bash
   uv pip install -e ../../../
   ```

4. (Optional) Install performance dependencies:
   ```bash
   uv pip install python-levenshtein
   ```

5. Ensure you have the lex-export directory with your bot configuration exported from AWS Lex.

### VS Code Setup
To use the integration tests in VS Code:
1. Run the setup script or manual setup above
2. In VS Code, press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
3. Type "Python: Select Interpreter"
4. Select the interpreter at: `examples/sample_airline_bot/integration_tests/.venv/bin/python`

## Running Tests

### Run all integration tests:
```bash
# From the project root
python -m pytest examples/sample_airline_bot/integration_tests/ -v
```

### Run specific test categories:

**Intent validation tests:**
```bash
python -m pytest examples/sample_airline_bot/integration_tests/test_all_intents_have_utterances.py -v
```

**Slot type validation tests:**
```bash
python -m pytest examples/sample_airline_bot/integration_tests/test_no_unused_slot_types.py -v
```

**Manual test cases (requires lex_helper to be installed):**
```bash
python -m pytest examples/sample_airline_bot/integration_tests/test_all_manually_written_test_cases.py -v
```

## Using the Lex Emulator

The Lex emulator can be used programmatically to test bot interactions:

```python
from lex_emulator import query

# Start a conversation
session_id = "test-session-123"
response = query("Hello", session_id)
print(response.messages[0]["content"])

# Continue the conversation
response = query("I want to book a flight", session_id)
print(response.messages[0]["content"])
```

## File Structure

- `lex_emulator/` - Contains the Lex emulator implementation
- `cases/` - Contains test case definitions for flow validation
- `fixtures/` - Contains sample data and payloads
- `test_*.py` - Various test files for different validation scenarios
- `requirements.txt` - Python dependencies for the integration tests

## Helpful Files

- `helpers.py` - Utility functions for testing
- `query_lex.py` - Interface for querying both real Lex and the emulator
- `validate_flow_with_lex.py` - Framework for validating conversation flows
