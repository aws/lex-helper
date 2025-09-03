# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#!/usr/bin/env python3
"""
Basic test to verify the Lex emulator can be imported and used.
This test doesn't require lex_helper to be installed in the main environment.
"""

import os
import sys

# Add the integration_tests directory to sys.path for lex_emulator import
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def test_lex_emulator_import():
    """Test that the lex emulator can be imported successfully."""
    from lex_emulator.lex_emulator import generate_session_id, query_lex_emulator

    # If we get here without an ImportError, the test passes
    assert query_lex_emulator is not None
    assert generate_session_id is not None


def test_basic_emulator_functionality():
    """Test basic emulator functionality without requiring full lex_helper."""
    from lex_emulator.lex_emulator import generate_session_id, get_session, set_session

    # Test session management
    session_id = generate_session_id()
    assert len(session_id) > 0, "Session ID should not be empty"

    # Test session storage
    test_session_data = {"test": "data"}
    set_session(session_id, test_session_data)
    retrieved_session = get_session(session_id)
    assert retrieved_session == test_session_data, "Session data should match"


if __name__ == "__main__":
    print("Testing Lex Emulator Basic Functionality...")

    try:
        test_lex_emulator_import()
        test_basic_emulator_functionality()
        print("\n🎉 All basic tests passed! The integration tests paths have been fixed.")
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        sys.exit(1)
