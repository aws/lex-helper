# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import configparser
import os
from typing import Dict, Optional


def common_steps_for_secret_retrieval(
    account_id: Optional[str] = None,
    path: str = "../properties",
) -> configparser.ConfigParser:
    """
    Retrieves the configuration object based on the AWS account ID.

    Returns:
        configparser.ConfigParser: The configuration object.
    """

    account_environment_map: Dict[str, str] = {}  # Configure this for your environment

    config_obj = configparser.ConfigParser()
    if account_id is None:
        env: str = os.environ.get("APP_NAME", "dev")
        if env not in ["dev", "si", "prd"]:
            env = "dev"
    else:
        env = account_environment_map.get(account_id, "si")

    config_obj.read(os.path.join(os.path.dirname(__file__), path, f"configFile-{env}.ini"))
    return config_obj
