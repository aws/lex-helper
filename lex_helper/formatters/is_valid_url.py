# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

def is_valid_url(url_string: str) -> bool:
    return url_string.startswith("http")
