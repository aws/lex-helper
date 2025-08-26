# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

def title_to_snake(title: str):
    return "".join(["_" + i.lower() if i.isupper() else i for i in title]).lstrip("_")
