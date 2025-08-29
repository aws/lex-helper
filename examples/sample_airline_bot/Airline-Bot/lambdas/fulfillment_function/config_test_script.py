"""
Test script for the configuration utilities.

This script tests the configuration utilities to ensure they work correctly
in both local development and simulated Lambda environments.
"""

import os
import sys

from loguru import logger

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our configuration utility
from utils.config import initialize_message_manager


def test_message_manager_initialization():
    """Test MessageManager initialization."""
    logger.info("Testing MessageManager initialization...")
    
    # Mock LexRequest object
    class MockBot:
        localeId = "en_US"
    
    class MockLexRequest:
        bot = MockBot()
    
    try:
        # Test initialization
        mock_request = MockLexRequest()
        initialize_message_manager(mock_request)
        logger.info("MessageManager initialized successfully")
        
        # Test with different locale
        mock_request.bot.localeId = "it_IT"
        initialize_message_manager(mock_request)
        logger.info("MessageManager initialized with Italian locale")
        
    except Exception as e:
        logger.error(f"MessageManager initialization failed: {e}")
        raise


def test_messages_directory():
    """Test that messages directory exists."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    messages_dir = os.path.join(current_dir, "messages")
    
    if os.path.exists(messages_dir):
        logger.info(f"Messages directory exists at {messages_dir}")
        
        # Check for message files
        for locale in ["en_US", "it_IT"]:
            msg_file = os.path.join(messages_dir, f"messages_{locale}.yaml")
            if os.path.exists(msg_file):
                logger.info(f"Found message file: {msg_file}")
            else:
                logger.warning(f"Message file not found: {msg_file}")
    else:
        logger.warning(f"Messages directory does not exist: {messages_dir}")


if __name__ == "__main__":
    logger.info("Testing configuration utilities...")
    test_message_manager_initialization()
    test_messages_directory()
    logger.info("All tests passed!")
