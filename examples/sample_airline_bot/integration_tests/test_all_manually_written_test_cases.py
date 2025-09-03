# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import os

import pytest

from .validate_flow_with_lex import validate_flow_with_lex


def is_known_exception(flow_name: str, expected_flow_path: str) -> bool:
    return expected_flow_path.startswith("failing_")


def find_md_files(directory: str) -> list[str]:
    md_files: list[str] = []

    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            md_files.append(str(filename))

    return md_files


def get_flow_paths() -> list[tuple[str, str]]:
    flow_paths: list[tuple[str, str]] = []

    # For every folder name under "cases"
    get_all_folders = os.listdir(os.path.dirname(os.path.abspath(__file__)) + "/cases")
    for flow_name in get_all_folders:
        # For every file name under the folder
        all_paths = find_md_files(os.path.dirname(os.path.abspath(__file__)) + f"/cases/{flow_name}")
        for expected_flow_path in all_paths:
            flow_paths.append((flow_name, expected_flow_path))

    return flow_paths


# We use pytest.mark.parametrize with the get_flow_paths method
@pytest.mark.parametrize("flow_name,expected_flow_path", get_flow_paths())  # type: ignore
def test_validate(flow_name: str, expected_flow_path: str):
    # if flow_name contains "failing_", then we expect the test to fail
    if is_known_exception(flow_name=flow_name, expected_flow_path=expected_flow_path):
        pytest.xfail("Known failing test case")
    else:
        validate_flow_with_lex(os.path.dirname(os.path.abspath(__file__)) + f"/cases/{flow_name}" + "/" + expected_flow_path)
