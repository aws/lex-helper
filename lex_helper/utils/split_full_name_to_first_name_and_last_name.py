# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0


def split_full_name_to_first_and_last_name(full_name: str) -> tuple[str | None, str | None]:
    first_name = None
    last_name = None
    words = full_name.split(" ")
    length_of_name = len(words)
    if length_of_name == 2:
        first_name = words[0]
        last_name = words[1]
    elif length_of_name > 2:
        first_name = words[0] + " " + words[1]
        last_name = " ".join(words[2:])
    elif length_of_name == 1:
        first_name = full_name

    return first_name, last_name
