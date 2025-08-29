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
from utils.config import configure_message_paths


def test_local_development():
    """Test configuration in local development environment."""
    # Ensure we're in local development mode
    if "AWS_EXECUTION_ENV" in os.environ:
        del os.environ["AWS_EXECUTION_ENV"]
    if "MESSAGES_DIR" in os.environ:
        del os.environ["MESSAGES_DIR"]

    # Configure message paths
    configure_message_paths()

    # Check that the current directory is in the Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assert current_dir in sys.path, f"Expected {current_dir} to be in sys.path"
    logger.info(f"Local development: Current directory {current_dir} is in Python path")

    # Check that the messages directory exists
    messages_dir = os.path.join(current_dir, "messages")
    assert os.path.exists(messages_dir), f"Messages directory does not exist: {messages_dir}"
    logger.info(f"Local development: Messages directory exists at {messages_dir}")


def test_custom_messages_dir():
    """Test configuration with custom MESSAGES_DIR environment variable."""
    # Set custom messages directory
    test_path = "/tmp/test_messages"
    os.environ["MESSAGES_DIR"] = test_path

    # Configure message paths
    configure_message_paths()

    # Check that MESSAGES_YAML_PATH is set correctly
    assert "MESSAGES_YAML_PATH" in os.environ, "MESSAGES_YAML_PATH not set"
    expected_path = os.path.join(test_path, "messages.yaml")
    assert os.environ["MESSAGES_YAML_PATH"] == expected_path, (
        f"Expected {expected_path}, got {os.environ['MESSAGES_YAML_PATH']}"
    )
    logger.info(f"Custom directory: MESSAGES_YAML_PATH set to {os.environ['MESSAGES_YAML_PATH']}")

    # Clean up
    del os.environ["MESSAGES_DIR"]
    if "MESSAGES_YAML_PATH" in os.environ:
        del os.environ["MESSAGES_YAML_PATH"]


def test_lambda_environment():
    """Test configuration in Lambda environment."""
    # Simulate Lambda environment
    os.environ["AWS_EXECUTION_ENV"] = "AWS_Lambda_python3.8"
    if "MESSAGES_DIR" in os.environ:
        del os.environ["MESSAGES_DIR"]

    # Configure message paths
    configure_message_paths()

    # In Lambda, we don't set any special paths as the default paths work
    logger.info("Lambda environment: Using default Lambda paths")

    # Clean up
    del os.environ["AWS_EXECUTION_ENV"]


if __name__ == "__main__":
    logger.info("Testing configuration utilities...")
    test_local_development()
    test_custom_messages_dir()
    test_lambda_environment()
    logger.info("All tests passed!")
