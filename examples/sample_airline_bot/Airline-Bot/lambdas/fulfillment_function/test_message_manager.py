#!/usr/bin/env python3
"""
Test script to verify MessageManager initialization and message retrieval.
"""
import os
import sys

# Add the layer path to Python path for local development
if not os.getenv('AWS_EXECUTION_ENV'):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    layer_path = os.path.join(project_root, 'layers', 'lex_helper', 'python')
    if os.path.exists(layer_path):
        sys.path.append(layer_path)

        for item in os.listdir(layer_path):
            item_path = os.path.join(layer_path, item)
            if os.path.isdir(item_path) and item.startswith('lex_helper'):
                sys.path.append(item_path)

def test_message_manager():
    """Test MessageManager with mock LexRequest."""
    # Change to the fulfillment_function directory
    original_cwd = os.getcwd()
    fulfillment_dir = os.path.join(original_cwd, 'lambdas', 'fulfillment_function')
    os.chdir(fulfillment_dir)

    print(f"Changed working directory to: {os.getcwd()}")
    print(f"Messages directory exists: {os.path.exists('messages')}")

    if os.path.exists('messages/messages_en_US.yaml'):
        print("Found messages_en_US.yaml")
    else:
        print("messages_en_US.yaml not found")

    try:
        # Try to import without lex_helper first
        print("Testing basic YAML loading...")
        import yaml
        with open('messages/messages_en_US.yaml') as f:
            messages = yaml.safe_load(f)
            print(f"YAML loaded successfully: {messages.get('track_baggage', {}).get('elicit_reservation_number', 'KEY NOT FOUND')}")
    except Exception as e:
        print(f"YAML test failed: {e}")

    # Restore original directory
    os.chdir(original_cwd)

    try:
        from utils.config import initialize_message_manager

        # Mock LexRequest object
        class MockBot:
            localeId = "en_US"

        class MockLexRequest:
            bot = MockBot()

        # Initialize MessageManager
        mock_request = MockLexRequest()
        initialize_message_manager(mock_request)

        print("MessageManager initialized, testing message retrieval...")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_message_manager()
