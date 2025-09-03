# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from urllib.parse import quote

from pydantic import AnyHttpUrl


def string_to_http_url(url: str) -> AnyHttpUrl:
    string_with_encoded_spaces = quote(url, safe="/:#[]@!$&'()*+,;=%")
    return string_with_encoded_spaces  # type: ignore
