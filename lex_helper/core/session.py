# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, ConfigDict


class BaseSessionAttributes(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="allow")
    is_unknown_choice: bool = False
    new_flow: bool = False
    options_provided: list[str] = []
    previous_dialog_action_type: str = ""
    previous_slot_to_elicit: str = ""
    error_count: int = 0

    def to_cmd_response(self) -> str:
        response = ""
        self_dict = self.model_dump()
        for key in self_dict:
            if self_dict[key] and key not in ["dispositions"]:
                response += f"{key} : {str(self_dict[key])} \n"
        return response
